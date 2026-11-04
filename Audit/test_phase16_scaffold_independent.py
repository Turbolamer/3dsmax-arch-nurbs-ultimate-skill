#!/usr/bin/env python3
"""Protective scaffold controls and bounded observations in owned temp dirs.

Fixed cases assert safe behavior using the current descriptor-staging writer.
Sequential project commits remain a limit, never arbitrary-race protection.
Synthetic assembly is only a nonproduction mock.
This is an observation probe, not an acceptance test. No Max or installer runs.
Run from the repository root with: python -B Audit/test_phase16_scaffold_independent.py
"""
import copy
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
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Audit"))
from test_phase16_p2_cases import synthetic_poly_assembly  # noqa: E402

APPROVED = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
PARENT = str(APPROVED) if os.name == "nt" and APPROVED.is_dir() else None
INIT = ROOT / "scripts" / "init_project.py"
VALIDATE = ROOT / "scripts" / "validate_specs.py"
FIXTURE = ROOT / "specs" / "fixtures" / "poly-shell-input" / "walls.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, doc):
    path.write_bytes((json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def tree_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def command(script, *args):
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)],
                          text=True, encoding="utf-8", capture_output=True, check=False)


def seed_dir(parent, initializer):
    seed = parent / "seed"
    shutil.copytree(ROOT / "examples", seed)
    shutil.copyfile(FIXTURE, seed / "walls.json")
    save(seed / "assembly.json", initializer.scaffold_assembly("pavilion-01"))
    return seed


def main():
    global INIT, VALIDATE
    source_files = [ROOT / "scripts" / name for name in
                    ("init_project.py", "validate_specs.py", "curve_gen.py", "wall_cell_coverage.py")]
    snapshots = {path: path.read_bytes() for path in source_files}
    fixture_paths = [FIXTURE, *(p for p in (ROOT / "examples").rglob("*") if p.is_file())]
    fixture_snapshots = {path: path.read_bytes() for path in fixture_paths}
    ast.parse(snapshots[VALIDATE].decode("utf-8"))
    print("SNAPSHOT_HASHES", json.dumps({p.name: hashlib.sha256(data).hexdigest()
                                         for p, data in snapshots.items()}))
    with tempfile.TemporaryDirectory(prefix="phase16-scaffold-review-", dir=PARENT) as owned:
        root = Path(owned)
        frozen = root / "frozen-scripts"
        frozen.mkdir()
        for path, content in snapshots.items():
            (frozen / path.name).write_bytes(content)
        INIT = frozen / "init_project.py"
        VALIDATE = frozen / "validate_specs.py"
        spec = importlib.util.spec_from_file_location("frozen_scaffold_independent", INIT)
        init = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(init)
        seed = seed_dir(root, init)
        dimensions = load(seed / "dimensions.json")
        dimensions["source"]["reference"] = "PRIVATE_SYNTHETIC_TEST_SOURCE_LINE_719"
        save(seed / "dimensions.json", dimensions)
        seed_control = command(VALIDATE, "--dir", seed, "--json")
        seed_control_report = json.loads(seed_control.stdout)
        assert seed_control.returncode == 0, seed_control_report["summary"]

        def make(name, source=seed):
            return command(INIT, "--project", name, "--dir", root, "--from", source)

        good = make("control")
        assert good.returncode == 0, good.stderr
        out = root / "control" / "specs" / "pipeline"
        output_dimensions = load(out / "dimensions.json")
        result = command(VALIDATE, "--dir", out, "--json")
        report = json.loads(result.stdout)
        print("SEED_SOURCE", json.dumps({
            "scaffold_exit": good.returncode,
            "input_reference": dimensions["source"]["reference"],
            "output_reference": output_dimensions["source"]["reference"],
            "input_kind": dimensions["source"]["kind"],
            "output_kind": output_dimensions["source"]["kind"],
            "input_lint_exit": seed_control.returncode,
            "lint_exit": result.returncode,
            "walls_g93": [(x["severity"], x["detail"]) for x in report["findings"]
                          if x["rule"] == "G-93" and x["location"] == "walls.json"],
        }))
        assert dimensions["source"] == output_dimensions["source"]

        # The following is intentionally a configuration-only mock. No wall
        # builder exists, and the apparent locked status must not be interpreted
        # as an emitted artifact or a measurement.
        mock_seed = root / "mock-seed"
        shutil.copytree(seed, mock_seed)
        mock = synthetic_poly_assembly(load(ROOT / "examples" / "assembly.json"))
        assert mock["status"] == "locked" and "synthetic" in mock["source"]["reference"]
        save(mock_seed / "assembly.json", mock)
        mock_result = make("mock-copy", mock_seed)
        mock_out = root / "mock-copy" / "specs" / "pipeline"
        mock_lint = command(VALIDATE, "--dir", mock_out, "--json")
        mock_report = json.loads(mock_lint.stdout)
        print("MOCK_LOCKED_ECHO", json.dumps({
            "seed_exit": mock_result.returncode,
            "assembly_status": load(mock_out / "assembly.json")["status"],
            "assembly_source": load(mock_out / "assembly.json")["source"]["reference"],
            "manifest_copied": (mock_out / "wall_surface.json").exists(),
            "lint_exit": mock_lint.returncode,
            "gates": [(x["rule"], x["severity"], x["detail"]) for x in mock_report["findings"]
                      if x["rule"] in ("G-92", "G-95", "G-96", "G-98", "G-99", "G-100")],
        }))
        assert mock_result.returncode == 0 and not (mock_out / "wall_surface.json").exists()
        # poly_fixture() checks the shape/status and lint only. Call just this
        # fixture guard with the frozen validator, never a live/acceptance gate.
        import test_phase16_p2 as main_harness
        prior_option = main_harness.OPTIONS.p2_fixture
        prior_scripts = main_harness.SCRIPTS
        fixture_case = main_harness.OfflineCase("runTest")
        fixture_case.setUp()
        try:
            main_harness.OPTIONS.p2_fixture = mock_out
            main_harness.SCRIPTS = frozen
            try:
                passed_path = fixture_case.poly_fixture()
            except AssertionError as exc:
                print("MAIN_FIXTURE_GUARD", json.dumps({"mock_accepted": False, "reason": str(exc)}))
            else:
                print("MAIN_FIXTURE_GUARD", json.dumps({
                    "mock_accepted": passed_path.is_dir(),
                    "mock_labeled_synthetic": "synthetic" in load(passed_path / "assembly.json")["source"]["reference"],
                    "wall_manifest_exists": (passed_path / "wall_surface.json").exists(),
                    "note": "configuration-only mock, never evidence of a production assembly",
                }))
        finally:
            main_harness.OPTIONS.p2_fixture = prior_option
            main_harness.SCRIPTS = prior_scripts
            fixture_case.doCleanups()

        # Exercise the same ten opening injections as the cases harness. The
        # first/second array element distinctions match its registry exactly.
        opening_cases = [
            ("unknown_run", 0, "wall_run_id", "RUN-099"),
            ("unknown_kind", 0, "kind", "entrance"),
            ("negative_u", 0, "u_range_cm", [-1.0, 315.0]),
            ("reversed_u", 0, "u_range_cm", [315.0, 135.0]),
            ("zero_width", 0, "u_range_cm", [135.0, 135.0]),
            ("past_end", 1, "u_range_cm", [575.0, 1801.0]),
            ("negative_sill", 0, "sill_cm", -1.0),
            ("head_at_sill", 0, "head_cm", 90.0),
            ("head_above_wall", 0, "head_cm", 421.0),
            ("overlap_u", 1, "u_range_cm", [300.0, 400.0]),
        ]
        original_walls = load(seed / "walls.json")
        for name, index, key, value in opening_cases:
            mutated = copy.deepcopy(original_walls)
            mutated["openings"][index][key] = value
            save(seed / "walls.json", mutated)
            checked = command(VALIDATE, "--dir", seed, "--json")
            checked_report = json.loads(checked.stdout)
            print("OPENING", name, "exit=", checked.returncode,
                  "g93_g94=", [(x["rule"], x["severity"], x["location"]) for x in checked_report["findings"]
                               if x["rule"] in ("G-93", "G-94") and x["severity"] != "SKIP"])
        save(seed / "walls.json", original_walls)

        mismatch = copy.deepcopy(load(seed / "walls.json"))
        mismatch["project"] = "different-source-project"
        save(seed / "walls.json", mismatch)
        input_check = command(VALIDATE, "--dir", seed, "--json")
        input_report = json.loads(input_check.stdout)
        mismatch_result = make("mixed-input")
        mixed_pipeline = root / "mixed-input" / "specs" / "pipeline"
        print("PROJECT_MIX", json.dumps({
            "input_lint_exit": input_check.returncode,
            "input_fails": [(x["rule"], x["location"], x["detail"]) for x in input_report["findings"]
                            if x["severity"] == "FAIL"],
            "seed_exit": mismatch_result.returncode,
            "destination_exists": mixed_pipeline.exists(),
            "seed_error": mismatch_result.stderr.strip(),
        }))
        assert input_check.returncode != 0 and mismatch_result.returncode != 0
        assert not (root / "mixed-input").exists()

        legacy = command(INIT, "--project", "route-switch", "--dir", root,
                         "--from", ROOT / "examples")
        assert legacy.returncode == 0, legacy.stderr
        old_pipeline = root / "route-switch" / "specs" / "pipeline"
        assert "wall_technique" not in load(old_pipeline / "assembly.json")
        existing_script = old_pipeline / "assembly.ms"
        shutil.copyfile(ROOT / "examples" / "assembly.ms", existing_script)
        script_hash = hashlib.sha256(existing_script.read_bytes()).hexdigest()
        before_switch = tree_bytes(root / "route-switch")
        switch = command(INIT, "--project", "route-switch", "--dir", root, "--force")
        assert switch.returncode != 0 and tree_bytes(root / "route-switch") == before_switch
        print("FORCED_ROUTE_SWITCH", json.dumps({
            "exit": switch.returncode,
            "wall_file_exists": (old_pipeline / "walls.json").exists(),
            "assembly_status": load(old_pipeline / "assembly.json")["status"],
            "old_legacy_script_survives": existing_script.is_file() and hashlib.sha256(existing_script.read_bytes()).hexdigest() == script_hash,
            "legacy_script_sha256": script_hash,
            "error": switch.stderr.strip(),
        }))
        assert existing_script.is_file() and hashlib.sha256(existing_script.read_bytes()).hexdigest() == script_hash

        authored = command(INIT, "--project", "authored-walls", "--dir", root)
        assert authored.returncode == 0, authored.stderr
        authored_path = root / "authored-walls" / "specs" / "pipeline" / "walls.json"
        authored_walls = load(FIXTURE)
        authored_walls["project"] = "authored-walls"
        authored_walls["source"]["reference"] = "USER-AUTHORED SENTINEL - DO NOT DESTROY"
        save(authored_path, authored_walls)
        before_hash = hashlib.sha256(authored_path.read_bytes()).hexdigest()
        before_authored = tree_bytes(root / "authored-walls")
        redo = command(INIT, "--project", "authored-walls", "--dir", root, "--force")
        print("AUTHORED_FORCE", json.dumps({
            "exit": redo.returncode,
            "original_sha256": before_hash,
            "new_status": load(authored_path)["status"],
            "new_wall_runs": len(load(authored_path)["wall_runs"]),
            "sentinel_survives": "USER-AUTHORED SENTINEL" in authored_path.read_text(encoding="utf-8"),
        }))
        assert redo.returncode != 0 and tree_bytes(root / "authored-walls") == before_authored

        # A single controlled substitution during the first stage's fsync.
        # This checks the actual writer's post-stage inspection, not an obsolete
        # Path.write_text hook and not arbitrary hostile scheduling protection.
        sentinel = root / "hardlink-sentinel"
        sentinel.write_bytes(b"KEEP THIS SENTINEL\n")
        guarded_target = root / "link-guard" / "specs" / "pipeline" / "dimensions.json"
        guarded_target.parent.mkdir(parents=True)
        os.link(sentinel, guarded_target)
        guarded = command(INIT, "--project", "link-guard", "--dir", root)
        assert guarded.returncode == 2 and sentinel.read_bytes() == b"KEEP THIS SENTINEL\n"
        race_target = root / "link-race" / "specs" / "pipeline" / "dimensions.json"
        original_fsync = init.os.fsync
        substitutions = []

        def substitute(descriptor):
            original_fsync(descriptor)
            assert not substitutions, "more than the first staged file was reached"
            os.link(sentinel, race_target)
            substitutions.append(str(race_target))

        race_error = io.StringIO()
        with patch.object(init.os, "fsync", substitute), redirect_stdout(io.StringIO()), redirect_stderr(race_error):
            race_status = init.main(["--project", "link-race", "--dir", str(root)])
        print("HARDLINK_RACE", json.dumps({
            "preexisting_guard_exit": guarded.returncode,
            "preexisting_guard_reason": guarded.stderr.strip(),
            "after_preflight_substitution_exit": race_status,
            "injected_substitutions": len(substitutions),
            "sentinel_overwritten": sentinel.read_bytes() != b"KEEP THIS SENTINEL\n",
            "scope": "one fsync-boundary substitution, not arbitrary-race safety",
        }))
        assert len(substitutions) == 1 and race_status == 2
        assert sentinel.read_bytes() == b"KEEP THIS SENTINEL\n"
        assert race_target.read_bytes() == sentinel.read_bytes()
        assert "not a safe regular output file" in race_error.getvalue()
        assert not list((root / "link-race").rglob("*.tmp"))

        # Inject a partial descriptor write on an existing project's SECOND file.
        # First file commits, failed file keeps its old bytes, later files stay
        # old. This intentionally proves per-file preservation, not rollback.
        project_name = "io-failure"
        created = command(INIT, "--project", project_name, "--dir", root)
        assert created.returncode == 0, created.stderr
        partial = root / project_name
        earlier = partial / "specs" / "pipeline" / "dimensions.json"
        target = partial / "specs" / "pipeline" / "assumptions.json"
        earlier.write_bytes(b"FIRST OLD RECORDED FILE\n")
        target.write_bytes(b"SECOND OLD RECORDED FILE\n")
        before_partial = tree_bytes(partial)
        original_fdopen = init.os.fdopen
        opened = []
        injected = []

        class PartialFailure:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                self.stream.__enter__()
                return self
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
            def write(self, content):
                self.stream.write(content[:17])
                self.stream.flush()
                injected.append(17)
                raise OSError(28, "injected descriptor failure after partial stage", str(target))

        def fail_second(descriptor, *args, **kwargs):
            stream = original_fdopen(descriptor, *args, **kwargs)
            opened.append(descriptor)
            return PartialFailure(stream) if len(opened) == 2 else stream

        stderr = io.StringIO()
        with patch.object(init.os, "fdopen", fail_second), redirect_stdout(io.StringIO()), redirect_stderr(stderr):
            first = init.main(["--project", project_name, "--dir", str(root), "--force"])
        after_partial = tree_bytes(partial)
        print("PARTIAL_WRITE", json.dumps({
            "initial_exit": first,
            "initial_error": stderr.getvalue().strip(),
            "manifest_exists": (partial / "project.json").exists(),
            "descriptor_injections": len(injected),
            "failed_file_preserved": target.read_bytes() == before_partial["specs/pipeline/assumptions.json"],
            "earlier_file_committed": earlier.read_bytes() != before_partial["specs/pipeline/dimensions.json"],
        }))
        assert first == 2 and len(opened) == 2 and injected == [17]
        assert target.read_bytes() == before_partial["specs/pipeline/assumptions.json"]
        assert earlier.read_bytes() != before_partial["specs/pipeline/dimensions.json"]
        assert load(earlier)["status"] == "draft"
        assert {k: v for k, v in before_partial.items() if k != "specs/pipeline/dimensions.json"} == \
               {k: v for k, v in after_partial.items() if k != "specs/pipeline/dimensions.json"}
        assert "preserve and inspect" in stderr.getvalue().lower()
        assert "not committed" in stderr.getvalue().lower()
        assert "prior completed replacements" in stderr.getvalue().lower()
        assert "not a whole-project transaction" in stderr.getvalue().lower()
        assert "re-run with --force to continue" not in stderr.getvalue().lower()
        assert not list(partial.rglob("*.tmp"))
        drift = [str(p.relative_to(ROOT)) for p, data in {**snapshots, **fixture_snapshots}.items()
                 if not p.is_file() or p.read_bytes() != data]
        print("SOURCE_DRIFT", json.dumps(drift))
        assert not drift, "source/fixture changed; repeat after edits stop"


if __name__ == "__main__":
    main()
