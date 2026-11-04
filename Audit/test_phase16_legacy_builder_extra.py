#!/usr/bin/env python3
"""Extra offline P2 builder boundary controls. No Max or installed skill is used.

Run from the repository root: python -B Audit/test_phase16_legacy_builder_extra.py -v
All builds use private temporary copies. The scripts are snapshotted once, and
both source and fixture drift during a run are errors. Old output comparison uses
the two builder files from commit 6c0f27b. The wall fixture is synthetic input.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
WALL_FIXTURE = ROOT / "specs/fixtures/poly-shell-input/walls.json"
SCRIPTS = ("place_components.py", "validate_specs.py", "wall_cell_coverage.py",
           "scene_units.py", "curve_gen.py")
OUTPUTS = ("assembly.json", "assembly.ms")
SENTINEL = b"-- PHASE16 EXTRA TEST SENTINEL: DO NOT ALTER\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_hashes() -> dict[str, str]:
    files = [p for p in EXAMPLES.rglob("*") if p.is_file()] + [WALL_FIXTURE]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(files)}


def tree(path: Path) -> dict[str, bytes | str]:
    if not path.exists():
        return {}
    result: dict[str, bytes | str] = {}
    for p in sorted(path.rglob("*")):
        key = str(p.relative_to(path))
        if p.is_symlink():
            result[key] = "LINK:" + os.readlink(p)
        elif p.is_file():
            result[key] = p.read_bytes()
        elif p.is_dir():
            result[key] = "DIRECTORY"
        else:
            raise AssertionError(f"unexpected entry: {p}")
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, obj: dict) -> None:
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))


class ExtraLegacyBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        cls.parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        cls.source_owner = tempfile.TemporaryDirectory(prefix="p16-extra-source-", dir=cls.parent)
        cls.addClassCleanup(cls.source_owner.cleanup)
        cls.source_dir = Path(cls.source_owner.name) / "scripts"
        cls.source_dir.mkdir()
        cls.source_hashes = {}
        for name in SCRIPTS:
            data = (ROOT / "scripts" / name).read_bytes()
            cls.source_hashes[name] = hashlib.sha256(data).hexdigest()
            (cls.source_dir / name).write_bytes(data)
        cls.fixture_hashes = fixture_hashes()
        print("extra-test source snapshot: " + ", ".join(
            f"{k}={v}" for k, v in cls.source_hashes.items()), file=sys.stderr)

        cls.old_dir = Path(cls.source_owner.name) / "old"
        cls.old_dir.mkdir()
        for name in ("place_components.py", "scene_units.py"):
            result = subprocess.run(["git", "show", f"6c0f27b:scripts/{name}"], cwd=ROOT,
                                    capture_output=True, check=False, timeout=30)
            if result.returncode:
                raise RuntimeError(f"historical source unavailable: {result.stderr!r}")
            (cls.old_dir / name).write_bytes(result.stdout)

        # Import the frozen code, never the concurrently editable working copy.
        sys.path.insert(0, str(cls.source_dir))
        import place_components as builder
        from wall_cell_coverage import check_wall_cell_coverage
        cls.builder_module = builder
        cls.oracle = staticmethod(check_wall_cell_coverage)

    @classmethod
    def tearDownClass(cls) -> None:
        now = {name: digest(ROOT / "scripts" / name) for name in SCRIPTS}
        if cls.source_hashes != now:
            raise AssertionError(f"scripts changed during test: before={cls.source_hashes}, after={now}")
        if cls.fixture_hashes != fixture_hashes():
            raise AssertionError("source fixture files changed during the test")

    def setUp(self) -> None:
        owner = tempfile.TemporaryDirectory(prefix="p16-extra-case-", dir=self.parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.index = 0

    def fresh(self) -> Path:
        self.index += 1
        path = self.temp / f"case-{self.index:03d}"
        path.mkdir()
        return path

    def project(self, *, explicit: bool = False, registry_source: bool = False) -> Path:
        pipeline = self.fresh() / "pipeline"
        shutil.copytree(EXAMPLES, pipeline)
        self.assertFalse((pipeline / "walls.json").exists())
        if explicit:
            walls = load(WALL_FIXTURE)
            walls["wall_technique"] = "legacy_cells_v1"
            if registry_source:
                # Existing size_cm provenance is cyclic in the checked-in example;
                # use a distinct acyclic registry origin as the calibrated control.
                walls["origin_inputs"] = ["components[0].layer"]
            save(pipeline / "walls.json", walls)
            assembly = load(pipeline / "assembly.json")
            assembly["wall_technique"] = "legacy_cells_v1"
            save(pipeline / "assembly.json", assembly)
        return pipeline

    def run_builder(self, project: Path, out: Path, *flags: str, old: bool = False):
        script = (self.old_dir if old else self.source_dir) / "place_components.py"
        return subprocess.run([sys.executable, "-B", str(script), "--in", str(project),
                               "--out", str(out), "--json", *flags], cwd=self.temp,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"),
                              text=True, encoding="utf-8", errors="replace", capture_output=True,
                              timeout=120, check=False)

    def output_sentinels(self, project: Path, *, include_walls: bool = False) -> Path:
        out = self.fresh()
        shutil.copyfile(project / "assembly.json", out / "assembly.json")
        (out / "assembly.ms").write_bytes(SENTINEL)
        if include_walls:
            shutil.copyfile(project / "walls.json", out / "walls.json")
        return out

    def assert_refused_without_changes(self, project: Path, out: Path, *flags: str,
                                      old: bool = False, contains: str = "") -> None:
        before_in, before_out = tree(project), tree(out)
        result = self.run_builder(project, out, *flags, old=old)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if contains:
            self.assertIn(contains, result.stderr)
        self.assertEqual(tree(project), before_in, "refusal changed input bytes")
        self.assertEqual(tree(out), before_out, "refusal changed output/sentinel bytes")

    def test_historical_same_and_separate_out_match_old_bytes(self) -> None:
        for mode in ((), ("--build",)):
            with self.subTest(mode=mode):
                old_in, new_in = self.project(), self.project()
                old_out, new_out = self.fresh(), self.fresh()
                old = self.run_builder(old_in, old_out, *mode, old=True)
                new = self.run_builder(new_in, new_out, *mode)
                self.assertEqual(old.returncode, 0, old.stderr)
                self.assertEqual(new.returncode, 0, new.stderr)
                self.assertEqual(tree(old_out), tree(new_out))
                self.assertEqual(set(tree(new_out)), set(OUTPUTS))
                self.assertNotIn("wall_technique", load(new_out / "assembly.json"))
                same = self.run_builder(new_in, new_in, *mode)
                self.assertEqual(same.returncode, 0, same.stderr)
                for name in OUTPUTS:
                    self.assertEqual((new_in / name).read_bytes(), (old_out / name).read_bytes())

    def test_no_openings_is_na_and_historical_self_check_already_refuses(self) -> None:
        project = self.project()
        dimensions = load(project / "dimensions.json")
        dimensions["openings"] = []
        dimensions["origins"] = {k: v for k, v in dimensions["origins"].items()
                                 if not k.startswith("openings[")}
        save(project / "dimensions.json", dimensions)
        massing, registry = load(project / "massing.json"), load(project / "components_registry.json")
        b = self.builder_module
        rows = b.read_world_table(project)
        assembly, thickness = b.build_assembly(dimensions, massing, registry, rows)
        self.assertEqual(assembly["opening_cuts"], [])
        self.assertEqual(assembly["wall_cells"], [])
        self.assertEqual(self.oracle(assembly, massing, dimensions).status, "NOT_APPLICABLE")
        script = b.render_ms(assembly, massing, dimensions, registry, thickness)
        failures = b.self_check(assembly, dimensions, massing, registry, rows, script)
        self.assertTrue(any("leaf opening_cuts" in item for item in failures), failures)
        self.assertTrue(any("leaf wall_cells" in item for item in failures), failures)
        self.assertIn("for host_node in host_nodes", script)
        self.assertNotIn("local host_nodes =", script)
        with self.assertRaisesRegex(b.Refusal, "NOT_APPLICABLE"):
            b.verify_spatial_coverage(assembly, massing, dimensions)
        for old in (True, False):
            for mode in ((), ("--build",)):
                with self.subTest(old=old, mode=mode):
                    self.assert_refused_without_changes(project, self.output_sentinels(project),
                                                        *mode, old=old, contains="leaf opening_cuts")

    def test_review_and_unsupported_geometry_not_promoted_to_pass(self) -> None:
        for label, delta, expected in (("review", 0.1, "REVIEW"),
                                       ("beyond-tolerance", 0.500001, "FAIL"),
                                       ("nonrectangular", None, "FAIL")):
            with self.subTest(case=label):
                project = self.project()
                massing = load(project / "massing.json")
                host = next(row for row in massing["elements"] if row["id"] == "EL-014")
                if delta is None:
                    host["profile_cm"].insert(1, [900.0, 1.0])
                else:
                    host["z_range_cm"][1] += delta
                save(project / "massing.json", massing)
                old_out = self.fresh()
                old = self.run_builder(project, old_out, old=True)
                self.assertEqual(old.returncode, 0, old.stderr)
                candidate = load(old_out / "assembly.json")
                measured = self.oracle(candidate, massing, load(project / "dimensions.json"))
                self.assertEqual(measured.status, expected, measured.findings)
                self.assertEqual(json.loads(old.stdout)["self_check"]["G-82"], "pass")
                for mode in ((), ("--build",), ("--build", "--allow-draft")):
                    with self.subTest(mode=mode):
                        self.assert_refused_without_changes(project, self.output_sentinels(project),
                                                            *mode, contains=f"coverage is {expected}")

    def test_explicit_same_separate_empty_matching_and_conflicting(self) -> None:
        project = self.project(explicit=True)
        same = self.run_builder(project, project, "--build", "--allow-draft")
        self.assertEqual(same.returncode, 0, same.stderr)
        self.assertEqual(load(project / "assembly.json")["wall_technique"], "legacy_cells_v1")
        matching = self.output_sentinels(project, include_walls=True)
        good = self.run_builder(project, matching, "--build", "--allow-draft")
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual((matching / "walls.json").read_bytes(), (project / "walls.json").read_bytes())
        empty = self.fresh()
        self.assert_refused_without_changes(project, empty, "--build", "--allow-draft",
                                            contains="byte-identical")
        conflicting = self.output_sentinels(project, include_walls=True)
        walls = load(conflicting / "walls.json")
        walls["wall_runs"][0]["end_cm"] = [1700.0, 0.0]
        save(conflicting / "walls.json", walls)
        self.assert_refused_without_changes(project, conflicting, "--build", "--allow-draft",
                                            contains="differs")

    def test_explicit_draft_superseded_and_g93_same_and_separate_refuse(self) -> None:
        for issue in ("draft", "superseded", "reversed-block", "missing-origin"):
            for same in (False, True):
                with self.subTest(issue=issue, same=same):
                    project = self.project(explicit=True)
                    walls = load(project / "walls.json")
                    if issue in ("draft", "superseded"):
                        walls["status"] = issue
                    elif issue == "reversed-block":
                        walls["blocks"][0]["z_range_cm"] = [420.0, 0.0]
                    else:
                        walls["origins"].pop("wall_runs[0]")
                    save(project / "walls.json", walls)
                    if same:
                        out = project
                        (out / "assembly.ms").write_bytes(SENTINEL)
                    else:
                        out = self.output_sentinels(project, include_walls=True)
                    self.assert_refused_without_changes(project, out, "--build", "--allow-draft")

    def test_registry_dependency_provenance_controls(self) -> None:
        # Matching output walls exclude a selector-mismatch refusal as a mask.
        for issue in ("clean", "invalid-derived-source", "back-reference-to-walls"):
            with self.subTest(issue=issue):
                project = self.project(explicit=True, registry_source=True)
                registry = load(project / "components_registry.json")
                if issue == "invalid-derived-source":
                    registry["origins"]["components[0].layer"]["derives_from"] = ["NO_SUCH_FIELD"]
                elif issue == "back-reference-to-walls":
                    registry["origin_inputs"] = ["wall_runs[0].thickness_cm"]
                save(project / "components_registry.json", registry)
                out = self.output_sentinels(project, include_walls=True)
                if issue == "clean":
                    result = self.run_builder(project, out, "--build", "--allow-draft")
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                else:
                    self.assert_refused_without_changes(project, out, "--build", "--allow-draft")

    def test_json_number_roundtrip_has_positive_and_negative_controls(self) -> None:
        b = self.builder_module
        for token in ("0.1", "5e-1", "1e-6", "-0.0", "9007199254740991",
                      "9007199254740991.0", "9.007199254740991e15",
                      "-9007199254740991", "-9.007199254740991e15"):
            with self.subTest(accepted=token):
                self.assertIn("number", b.strict_loads('{"number":' + token + '}'))
        for token in ("10000000000000001.9", "0.10000000000000001", "1e-400",
                      "9007199254740992", "9007199254740992.0", "9.007199254740992e15",
                      "10000000000000000", "-9007199254740992.0", "1e999", "1" + "0" * 5000):
            with self.subTest(refused=token[:40]):
                with self.assertRaises(ValueError):
                    b.strict_loads('{"number":' + token + '}')

    def test_json_precision_refusal_preserves_both_routes_and_sentinels(self) -> None:
        # Both builders read dimensions.json, and explicit legacy also reads all
        # declared dependencies. Keep output route bytes matching so this tests
        # precision rejection rather than a route-conflict refusal.
        cases = (
            (False, "dimensions.json", "10000000000000001.9", "loses decimal precision"),
            (False, "massing.json", "10000000000000001", "safe integer bound"),
            (False, "components_registry.json", "1e-400", "loses decimal precision"),
            (False, "assembly.json", "10000000000000001.9", "loses decimal precision"),
            (False, "dimensions.json", "1" + "0" * 5000, "not finite"),
            (True, "dimensions.json", "10000000000000001.9", "loses decimal precision"),
            (True, "massing.json", "10000000000000001", "safe integer bound"),
            (True, "components_registry.json", "1e-400", "loses decimal precision"),
            (True, "walls.json", "10000000000000001.9", "loses decimal precision"),
            (True, "assembly.json", "10000000000000001.9", "loses decimal precision"),
            (True, "dimensions.json", "1" + "0" * 5000, "not finite"),
        )
        for explicit, name, token, diagnostic in cases:
            with self.subTest(explicit=explicit, file=name, token=token[:25]):
                project = self.project(explicit=explicit)
                path = project / name
                original = path.read_text(encoding="utf-8")
                self.assertIn('"linear_cm": 0.5', original)
                path.write_bytes(original.replace('"linear_cm": 0.5',
                                                  '"linear_cm": ' + token, 1).encode("utf-8"))
                # If assembly itself is malformed as a sentinel, require the
                # input path to fail first; the separate output remains valid.
                out = self.fresh()
                if name == "assembly.json":
                    source_assembly = load(EXAMPLES / "assembly.json")
                    if explicit:
                        source_assembly["wall_technique"] = "legacy_cells_v1"
                    save(out / "assembly.json", source_assembly)
                else:
                    shutil.copyfile(project / "assembly.json", out / "assembly.json")
                (out / "assembly.ms").write_bytes(SENTINEL)
                if explicit:
                    shutil.copyfile(project / "walls.json", out / "walls.json")
                self.assert_refused_without_changes(project, out, "--build", "--allow-draft",
                                                    contains=diagnostic)

    def test_safe_integer_boundary_and_oversized_float_tokens_on_both_routes(self) -> None:
        for explicit in (False, True):
            for token in ("9007199254740991", "9007199254740991.0", "9.007199254740991e15"):
                with self.subTest(explicit=explicit, accepted=token):
                    project = self.project(explicit=explicit)
                    path = project / "assembly.json"
                    text = path.read_text(encoding="utf-8")
                    # Previous assembly is only a route declaration: its cell
                    # data are rebuilt, so this test value does not claim a
                    # physically meaningful wall volume.
                    import re
                    text, replacements = re.subn(r'("volume_cm3"\s*:\s*)[\d.]+', r'\g<1>' + token,
                                                  text, count=1)
                    self.assertEqual(replacements, 1)
                    path.write_bytes(text.encode("utf-8"))
                    out = self.output_sentinels(project, include_walls=explicit)
                    result = self.run_builder(project, out, "--build", "--allow-draft")
                    self.assertEqual(result.returncode, 0, result.stderr)
            for token in ("9007199254740992.0", "9.007199254740992e15"):
                with self.subTest(explicit=explicit, refused=token):
                    project = self.project(explicit=explicit)
                    path = project / "dimensions.json"
                    text = path.read_text(encoding="utf-8")
                    self.assertIn('"linear_cm": 0.5', text)
                    path.write_bytes(text.replace('"linear_cm": 0.5',
                                                  '"linear_cm": ' + token, 1).encode("utf-8"))
                    out = self.output_sentinels(project, include_walls=explicit)
                    self.assert_refused_without_changes(project, out, "--build", "--allow-draft",
                                                        contains="safe integer bound")

    def test_equivalent_decimal_spelling_preserves_historical_output(self) -> None:
        for explicit in (False, True):
            with self.subTest(explicit=explicit):
                project = self.project(explicit=explicit)
                out = self.output_sentinels(project, include_walls=explicit)
                original = self.run_builder(project, out, "--build")
                self.assertEqual(original.returncode, 0, original.stderr)
                expected = {name: (out / name).read_bytes() for name in OUTPUTS}
                path = project / "dimensions.json"
                text = path.read_text(encoding="utf-8")
                self.assertIn('"linear_cm": 0.5', text)
                path.write_bytes(text.replace('"linear_cm": 0.5', '"linear_cm": 5e-1', 1)
                                 .encode("utf-8"))
                alternate = self.run_builder(project, out, "--build")
                self.assertEqual(alternate.returncode, 0, alternate.stderr)
                self.assertEqual(expected, {name: (out / name).read_bytes() for name in OUTPUTS})

    def test_unprintable_oracle_diagnostic_is_a_refusal(self) -> None:
        # Exercise both an oracle that returns an enormous integer in a finding
        # and one that throws while constructing a diagnostic.
        from wall_cell_coverage import check_wall_cell_coverage
        import wall_cell_coverage as coverage
        b = self.builder_module
        huge = 10 ** 5000
        try:
            coverage.check_wall_cell_coverage = lambda *_: SimpleNamespace(
                status="FAIL", findings=[{"huge": huge}])
            with self.assertRaisesRegex(b.Refusal, "diagnostic could not be safely formatted"):
                b.verify_spatial_coverage({}, {}, {})
            def explode(*_):
                str(huge)
            coverage.check_wall_cell_coverage = explode
            with self.assertRaisesRegex(b.Refusal, "coverage could not run"):
                b.verify_spatial_coverage({}, {}, {})
        finally:
            coverage.check_wall_cell_coverage = check_wall_cell_coverage


if __name__ == "__main__":
    unittest.main(verbosity=2)
