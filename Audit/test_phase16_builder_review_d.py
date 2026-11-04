#!/usr/bin/env python3
"""Independent P2/S5 review, including deliberately red unresolved safety gates.

Run: python -B Audit/test_phase16_builder_review_d.py -v
No source/fixture is edited. Every CLI executes frozen production bytes in a
private copy under the approved OpenCode temp directory. Historical comparisons
execute actual git-show 6c0f27b source, never an emulation or checkout.

Three safety tests assert the desired protection, not today's unsafe behavior:
second-file I/O failure, final-check wall substitution, and final-check directory
substitution. If still broken they FAIL (not SKIP/xfail). Other injected probes
calibrate first-file failure, mid-build snapshot checks, pre-existing links and
late hardlink replacement. Injection hooks model a precisely timed adversary or
OS failure; they do not imply a naturally occurring race was observed.
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
EXAMPLES = ROOT / "examples"
WALL_FIXTURE = ROOT / "specs/fixtures/poly-shell-input/walls.json"
SCRIPTS = ("place_components.py", "validate_specs.py", "wall_cell_coverage.py",
           "scene_units.py", "curve_gen.py")
LEGACY = "legacy_cells_v1"
MODES = ((), ("--allow-draft",), ("--build",), ("--build", "--allow-draft"))
OUTPUTS = ("assembly.json", "assembly.ms")
SENTINEL = b"-- INDEPENDENT 02d OUTPUT SENTINEL, MUST SURVIVE REFUSAL\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, doc: dict) -> None:
    path.write_bytes((json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())


def tree(path: Path) -> dict[str, bytes | str]:
    result: dict[str, bytes | str] = {}
    if not path.exists():
        return result
    for item in sorted(path.rglob("*")):
        key = item.relative_to(path).as_posix()
        if item.is_symlink():
            result[key] = "LINK:" + os.readlink(item)
        elif item.is_file():
            result[key] = item.read_bytes()
        elif item.is_dir():
            result[key] = "DIRECTORY"
        else:
            raise AssertionError(f"unexpected entry: {item}")
    return result


def changed(before: dict, after: dict) -> list[str]:
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def fixture_hashes() -> dict[str, str]:
    files = [p for p in EXAMPLES.rglob("*") if p.is_file()] + [WALL_FIXTURE]
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(files)}


# The production module and its helpers are imported ONLY from the disposable
# source snapshot, with cwd outside the repository. No production function is
# replaced except the named timing/error injection hook.
INJECT = r'''
import json, os, pathlib, sys
config = json.loads(sys.argv[1])
sys.path.insert(0, config["source"])
import place_components as b
kind = config["hook"]
project, out = pathlib.Path(config["project"]), pathlib.Path(config["out"])
if kind in ("io-first", "io-second"):
    original_replace = b.os.replace
    bad_name = "assembly.json" if kind == "io-first" else "assembly.ms"
    def replacement(src, dst):
        if pathlib.Path(dst).name == bad_name:
            raise PermissionError("INJECTED 02d replace failure: " + bad_name)
        return original_replace(src, dst)
    b.os.replace = replacement
elif kind == "input-during-render":
    original_render = b.render_ms
    def render(*args, **kwargs):
        result = original_render(*args, **kwargs)
        p = project / "dimensions.json"
        p.write_bytes(p.read_bytes() + b" ")
        return result
    b.render_ms = render
else:
    original_route = b.require_safe_output_route
    calls = 0
    def route(*args, **kwargs):
        global calls
        result = original_route(*args, **kwargs)
        calls += 1
        if calls == 2:
            if kind == "late-wall":
                p = out / "walls.json"
                value = json.loads(p.read_text(encoding="utf-8"))
                value["wall_technique"] = "poly_surface_shell_v1"
                p.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            elif kind == "late-directory":
                out.rename(pathlib.Path(config["parked"]))
                out.symlink_to(pathlib.Path(config["victim"]), target_is_directory=True)
            elif kind == "late-hardlink":
                (out / "assembly.ms").unlink()
                os.link(config["victim"], out / "assembly.ms")
            else:
                raise RuntimeError("unknown injection: " + kind)
            print("INJECTED 02d after final route check: " + kind, file=sys.stderr)
        return result
    b.require_safe_output_route = route
sys.exit(b.main(config["argv"]))
'''


class BuilderReviewD(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/opencode"
        if os.name == "nt" and not approved.is_dir():
            raise RuntimeError(f"approved temporary directory unavailable: {approved}")
        cls.parent = str(approved) if os.name == "nt" else None
        owner = tempfile.TemporaryDirectory(prefix="p16-builder-review-d-source-", dir=cls.parent)
        cls.addClassCleanup(owner.cleanup)
        cls.source = Path(owner.name) / "scripts"
        cls.source.mkdir()
        cls.hashes = {}
        for name in SCRIPTS:
            data = (ROOT / "scripts" / name).read_bytes()
            cls.hashes[name] = sha(data)
            (cls.source / name).write_bytes(data)
        cls.fixtures = fixture_hashes()
        cls.old = Path(owner.name) / "historical"
        cls.old.mkdir()
        cls.old_hashes = {}
        for name in ("place_components.py", "scene_units.py"):
            result = subprocess.run(["git", "show", f"6c0f27b:scripts/{name}"], cwd=ROOT,
                                    capture_output=True, timeout=30, check=True)
            cls.old_hashes[name] = sha(result.stdout)
            (cls.old / name).write_bytes(result.stdout)
        print("REVIEW_D_SOURCE " + json.dumps(cls.hashes, sort_keys=True), file=sys.stderr)
        print("REVIEW_D_HISTORICAL " + json.dumps(cls.old_hashes, sort_keys=True), file=sys.stderr)
        print("REVIEW_D_FIXTURE_MANIFEST " + sha(json.dumps(cls.fixtures, sort_keys=True).encode()),
              file=sys.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        current = {name: sha((ROOT / "scripts" / name).read_bytes()) for name in SCRIPTS}
        drift = [name for name in SCRIPTS if current[name] != cls.hashes[name]]
        print("REVIEW_D_FINAL_SOURCE " + json.dumps(current, sort_keys=True), file=sys.stderr)
        if drift:
            raise AssertionError(f"PRELIMINARY: source changed during frozen run: {drift}")
        if fixture_hashes() != cls.fixtures:
            raise AssertionError("repository fixture drift: no final acceptance")

    def setUp(self) -> None:
        owner = tempfile.TemporaryDirectory(prefix="p16-builder-review-d-case-", dir=self.parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.index = 0

    def fresh(self, label: str = "case") -> Path:
        self.index += 1
        path = self.temp / f"{self.index:03d}-{label}"
        path.mkdir()
        return path

    def project(self, *, explicit: bool = True) -> Path:
        project = self.fresh("input") / "pipeline"
        shutil.copytree(EXAMPLES, project)
        self.assertFalse((project / "walls.json").exists())
        if explicit:
            walls = load(WALL_FIXTURE)
            self.assertTrue(all(v == {"origin": "given"} for v in walls["origins"].values()))
            self.assertEqual(walls["project"], load(project / "dimensions.json")["project"])
            walls["wall_technique"] = LEGACY
            save(project / "walls.json", walls)
            assembly = load(project / "assembly.json")
            assembly["wall_technique"] = LEGACY
            save(project / "assembly.json", assembly)
        return project

    def sentinels(self, project: Path, *, same: bool = False) -> Path:
        out = project if same else self.fresh("output")
        assembly = load(project / "assembly.json")
        # Valid but distinct serialization prevents a no-op from masquerading as
        # the successful control while avoiding a malformed-route masking fault.
        (out / "assembly.json").write_bytes((json.dumps(assembly, separators=(", ", ": ")) + "\n").encode())
        (out / "assembly.ms").write_bytes(SENTINEL)
        if out != project and (project / "walls.json").exists():
            shutil.copyfile(project / "walls.json", out / "walls.json")
        return out

    def command(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", *argv], cwd=self.temp,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"),
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=120, check=False)

    def build(self, project: Path, out: Path, *flags: str, old: bool = False,
              hook: str | None = None, **injection: str) -> subprocess.CompletedProcess[str]:
        argv = ["--in", str(project), "--out", str(out), "--json", *flags]
        if hook:
            config = dict(source=str(self.source), project=str(project), out=str(out),
                          hook=hook, argv=argv, **injection)
            return self.command(["-c", INJECT, json.dumps(config)])
        return self.command([str((self.old if old else self.source) / "place_components.py"), *argv])

    def built(self, result: subprocess.CompletedProcess[str], out: Path) -> dict:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["exit_code"], 0)
        doc = load(out / "assembly.json")
        self.assertEqual((len(doc["placements"]), len(doc["opening_cuts"]), len(doc["wall_cells"])),
                         (136, 16, 52))
        return doc

    def refused(self, project: Path, out: Path, *flags: str, contains: str,
                old: bool = False, hook: str | None = None) -> subprocess.CompletedProcess[str]:
        before_in, before_out = tree(project), tree(out)
        result = self.build(project, out, *flags, old=old, hook=hook)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(contains, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(changed(before_out, tree(out)), "refusal changed output")
        if hook is None:
            self.assertFalse(changed(before_in, tree(project)), "refusal changed input")
        return result

    def oracle(self, project: Path, assembly_path: Path) -> str:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);"
                "from wall_cell_coverage import check_wall_cell_coverage as c;"
                "from pathlib import Path;"
                "p=Path(sys.argv[2]);a=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8'));"
                "m=json.loads((p/'massing.json').read_text(encoding='utf-8'));"
                "d=json.loads((p/'dimensions.json').read_text(encoding='utf-8'));"
                "r=c(a,m,d);print(json.dumps({'status':r.status,'findings':r.findings}))")
        result = self.command(["-c", code, str(self.source), str(project), str(assembly_path)])
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["status"]

    def test_locked_and_nonlocked_explicit_all_flag_modes_same_and_separate(self) -> None:
        for same in (False, True):
            for flags in MODES:
                with self.subTest(same=same, flags=flags, status="locked"):
                    project = self.project()
                    out = self.sentinels(project, same=same)
                    self.assertEqual(self.built(self.build(project, out, *flags), out)["wall_technique"], LEGACY)
                for status in ("draft", "superseded"):
                    with self.subTest(same=same, flags=flags, status=status):
                        project = self.project()
                        walls = load(project / "walls.json")
                        walls["status"] = status
                        save(project / "walls.json", walls)
                        self.refused(project, self.sentinels(project, same=same), *flags,
                                     contains="explicit legacy requires locked")

    def test_single_target_g93_calibrated_and_refusal_preserves_sentinels(self) -> None:
        for same in (False, True):
            with self.subTest(same=same):
                project = self.project()
                args = [str(self.source / "validate_specs.py"), "--dir", str(project),
                        "--json", "--build", "--allow-draft"]
                good = self.command(args)
                good_report = json.loads(good.stdout)
                self.assertEqual(good.returncode, 0, good.stderr)
                self.assertTrue(any(r["rule"] == "G-93" and r["severity"] == "PASS"
                                    for r in good_report["findings"]))
                calibrated = self.sentinels(project)
                self.built(self.build(project, calibrated, "--build", "--allow-draft"), calibrated)
                walls = load(project / "walls.json")
                walls["blocks"][0]["z_range_cm"] = [420.0, 0.0]
                save(project / "walls.json", walls)
                bad = self.command(args)
                report = json.loads(bad.stdout)
                target = [r for r in report["findings"] if r["rule"] == "G-93"]
                self.assertEqual(bad.returncode, 1)
                self.assertTrue(any(r["severity"] == "FAIL" and
                                    "walls.json::blocks[0].z_range_cm" in r["location"] for r in target), target)
                self.assertFalse(any(r["severity"] == "PASS" for r in target), target)
                self.refused(project, self.sentinels(project, same=same), "--build", "--allow-draft",
                             contains="G-93")

    def test_explicit_output_empty_matching_conflicting_and_same_missing_outputs(self) -> None:
        project = self.project()
        good = self.sentinels(project)
        self.built(self.build(project, good, "--build", "--allow-draft"), good)
        self.refused(project, self.fresh("empty"), "--build", "--allow-draft", contains="byte-identical")
        mismatch = self.sentinels(project)
        wall = load(mismatch / "walls.json")
        wall["wall_runs"][0]["end_cm"] = [1700.0, 0.0]
        save(mismatch / "walls.json", wall)
        self.refused(project, mismatch, "--build", "--allow-draft", contains="differs")
        (project / "assembly.json").unlink()
        (project / "assembly.ms").unlink()
        self.built(self.build(project, project, "--build", "--allow-draft"), project)

    def test_semantically_equal_but_different_wall_bytes_are_refused(self) -> None:
        project = self.project()
        out = self.sentinels(project)
        self.built(self.build(project, out), out)
        (out / "walls.json").write_bytes((json.dumps(load(project / "walls.json")) + "\n").encode())
        self.assertEqual(load(project / "walls.json"), load(out / "walls.json"))
        self.assertNotEqual((project / "walls.json").read_bytes(), (out / "walls.json").read_bytes())
        self.refused(project, out, contains="differs")

    def test_mid_build_snapshot_change_is_refused_before_output(self) -> None:
        project = self.project()
        out = self.sentinels(project)
        control = self.sentinels(project)
        self.built(self.build(project, control), control)
        self.refused(project, out, contains="changed during the build", hook="input-during-render")

    def test_actual_historical_no_opening_builder_already_refuses(self) -> None:
        project = self.project(explicit=False)
        dimensions = load(project / "dimensions.json")
        dimensions["openings"] = []
        dimensions["origins"] = {k: v for k, v in dimensions["origins"].items()
                                  if not k.startswith("openings[")}
        save(project / "dimensions.json", dimensions)
        for old in (False, True):
            for flags in ((), ("--build",)):
                with self.subTest(old=old, flags=flags):
                    self.refused(project, self.sentinels(project), *flags, old=old,
                                 contains="leaf opening_cuts")

    def test_actual_historical_near_tolerance_boundary(self) -> None:
        for delta, expected in ((0.0, "PASS"), (0.000001, "REVIEW"),
                                (0.499999, "REVIEW"), (0.5, "REVIEW"), (0.500001, "FAIL")):
            with self.subTest(delta=delta, expected=expected):
                project = self.project(explicit=False)
                massing = load(project / "massing.json")
                next(e for e in massing["elements"] if e["id"] == "EL-014")["z_range_cm"][1] += delta
                save(project / "massing.json", massing)
                out_old = self.fresh("old")
                previous = self.build(project, out_old, old=True)
                self.built(previous, out_old)
                self.assertEqual(json.loads(previous.stdout)["self_check"]["G-82"], "pass")
                self.assertEqual(self.oracle(project, out_old / "assembly.json"), expected)
                for flags in ((), ("--build", "--allow-draft")):
                    out = self.sentinels(project)
                    if expected == "PASS":
                        self.built(self.build(project, out, *flags), out)
                        for name in OUTPUTS:
                            self.assertEqual((out / name).read_bytes(), (out_old / name).read_bytes())
                    else:
                        self.refused(project, out, *flags, contains=f"coverage is {expected}")

    def test_actual_historical_unsupported_nonrectangle_is_new_refusal(self) -> None:
        project = self.project(explicit=False)
        massing = load(project / "massing.json")
        next(e for e in massing["elements"] if e["id"] == "EL-014")["profile_cm"].insert(1, [900.0, 1.0])
        save(project / "massing.json", massing)
        out_old = self.fresh("old")
        self.built(self.build(project, out_old, old=True), out_old)
        self.assertEqual(self.oracle(project, out_old / "assembly.json"), "FAIL")
        self.refused(project, self.sentinels(project), contains="coverage is FAIL")

    def test_first_file_replace_failure_leaves_both_sentinels_and_no_temps(self) -> None:
        project = self.project()
        control = self.sentinels(project)
        self.built(self.build(project, control), control)
        out = self.sentinels(project)
        before = tree(out)
        result = self.build(project, out, hook="io-first")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INJECTED 02d replace failure: assembly.json", result.stderr)
        print("REVIEW_D_IO_FIRST traceback=" + str("Traceback" in result.stderr), file=sys.stderr)
        self.assertFalse(changed(before, tree(out)), "first-file I/O failure changed output or leaked temp")

    def test_safety_second_file_io_failure_must_not_leave_partial_pair(self) -> None:
        project = self.project()
        control = self.sentinels(project)
        self.built(self.build(project, control), control)
        out = self.sentinels(project)
        before = tree(out)
        result = self.build(project, out, hook="io-second")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INJECTED 02d replace failure: assembly.ms", result.stderr)
        after = tree(out)
        self.assertEqual(after["assembly.ms"], SENTINEL)
        self.assertEqual(set(after), set(before), "temporary-file leak")
        self.assertFalse(changed(before, after),
                         "OPEN SAFETY LIMIT: second-file failure leaves mixed output pair; changed="
                         + repr(changed(before, after))
                         + "; JSON equals successful control="
                         + str(after["assembly.json"] == (control / "assembly.json").read_bytes())
                         + "; traceback=" + str("Traceback" in result.stderr))

    def test_existing_directory_symlink_is_rejected_before_writes(self) -> None:
        project = self.project()
        victim = self.sentinels(project)
        link = self.temp / "preexisting-output-link"
        try:
            link.symlink_to(victim, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        before = tree(victim)
        result = self.build(project, link)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe symlink or reparse point", result.stderr)
        self.assertFalse(changed(before, tree(victim)))

    def test_late_leaf_hardlink_is_replaced_without_truncating_external_file(self) -> None:
        project = self.project()
        out = self.sentinels(project)
        victim = self.fresh("victim") / "protected.ms"
        victim.write_bytes(SENTINEL)
        self.built(self.build(project, out, hook="late-hardlink", victim=str(victim)), out)
        self.assertEqual(victim.read_bytes(), SENTINEL)
        self.assertEqual(victim.stat().st_nlink, 1)
        self.assertEqual((out / "assembly.ms").stat().st_nlink, 1)

    def test_safety_final_wall_substitution_must_not_commit_mixed_route(self) -> None:
        project = self.project()
        control = self.sentinels(project)
        self.built(self.build(project, control), control)
        out = self.sentinels(project)
        before = tree(out)
        result = self.build(project, out, hook="late-wall")
        self.assertIn("INJECTED 02d after final route check: late-wall", result.stderr)
        if result.returncode == 0:
            self.assertEqual(load(out / "walls.json")["wall_technique"], "poly_surface_shell_v1")
            self.assertEqual(load(out / "assembly.json")["wall_technique"], LEGACY)
        self.assertNotEqual(result.returncode, 0,
                            "OPEN SAFETY LIMIT: late wall replacement commits legacy assembly beside poly walls")
        self.assertEqual((out / "assembly.json").read_bytes(), before["assembly.json"])
        self.assertEqual((out / "assembly.ms").read_bytes(), before["assembly.ms"])

    def test_safety_final_directory_substitution_must_not_overwrite_victim(self) -> None:
        project = self.project()
        out = self.sentinels(project)
        victim = self.sentinels(project)
        before = tree(victim)
        probe = self.temp / "symlink-capability-control"
        try:
            probe.symlink_to(victim, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        self.assertEqual((probe / "assembly.ms").read_bytes(), SENTINEL)
        probe.unlink()
        parked = self.temp / "parked-original-output"
        result = self.build(project, out, hook="late-directory", victim=str(victim), parked=str(parked))
        self.assertIn("INJECTED 02d after final route check: late-directory", result.stderr)
        self.assertTrue(out.is_symlink())
        self.assertEqual((parked / "assembly.ms").read_bytes(), SENTINEL)
        self.assertFalse(changed(before, tree(victim)),
                         "OPEN SAFETY LIMIT: late parent-directory substitution overwrites victim JSON/MS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
