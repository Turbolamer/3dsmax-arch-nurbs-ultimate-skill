#!/usr/bin/env python3
"""Independent adversarial tests for the actual P3 public emitter, stdlib only.

Run: python -B Audit/test_phase16_p3_independent.py --fixture PATH -v
PATH contains walls.json; --authority can explicitly locate its operational record.
If omitted, discover a unique analytical F01 input/authority under Audit. Missing
production modules/fixtures are NOT RUN (exit 2), never skips or synthetic output.
All commands execute frozen copies of actual scripts in private temporary dirs.
No Max, installs, git writes, production repair, or preexisting fixture edits.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("build_wall_surface.py", "wall_surface_inputs.py",
            "wall_surface_runtime.py", "wall_surface_publish.py")
PAIR = ("wall_surface.json", "wall_surface.ms")
FIXTURE = None
AUTHORITY = None
SOURCE_MANIFEST = {}
FIXTURE_MANIFEST = {}
CASE_EVENTS = []
SENTINEL = b"INDEPENDENT P3 PRIVATE VICTIM: MUST NOT BE WRITTEN OR REMOVED\n"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, doc):
    path.write_bytes((json.dumps(doc, ensure_ascii=False, sort_keys=True,
                                indent=2, allow_nan=False) + "\n").encode("utf-8"))


def snapshot(path):
    """Bytes and directory/link presence; never follow symlink directory trees."""
    if not path.exists() and not path.is_symlink():
        return {}
    if path.is_file():
        return {".": path.read_bytes()}
    result = {}
    for base, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            p = Path(base) / name
            key = p.relative_to(path).as_posix()
            if p.is_symlink():
                result[key] = "LINK:" + os.readlink(p)
            elif p.is_dir():
                result[key] = "DIRECTORY"
            else:
                result[key] = p.read_bytes()
    return result


def hashed_files(paths):
    return {str(p): digest(p.read_bytes()) for p in sorted(set(paths)) if p.is_file()}


def authority_source(record_path, doc):
    value = Path(doc["source_file"])
    return value if value.is_absolute() else record_path.parent / value


def fixture_source(record_path, doc):
    """Read root-CWD-relative F01 seed, then rebind only the private copy.

    This only finds the original analytical source to copy/rebind explicitly in
    test-private requests. Original record bytes remain hashed and unchanged.
    """
    path = authority_source(record_path, doc)
    if not path.is_file() and doc["source_file"] == "Audit/AGENT_PLAN_poly_surface_shell.md":
        path = ROOT / doc["source_file"]
    if not path.is_file():
        raise RuntimeError("NOT RUN: authentic authority source unavailable: " + str(path))
    return path


def discover(fixture, authority):
    """Discover INPUTS only, never use a fabricated/produced assembly as a seed."""
    if fixture:
        directory = Path(fixture).resolve()
        if directory.is_file():
            directory = directory.parent
        candidates = [directory]
    else:
        candidates = []
        for path in (ROOT / "Audit").rglob("walls.json"):
            try:
                walls = read_json(path)
                runs = walls.get("wall_runs", [])
                if (len(runs) == 1 and runs[0].get("start_cm") == [0, 0]
                        and runs[0].get("end_cm") == [400, 0]
                        and runs[0].get("top_z_cm") == 300):
                    candidates.append(path.parent)
            except (OSError, ValueError, TypeError):
                continue
    if len(candidates) != 1:
        raise RuntimeError("NOT RUN: need a unique real F01 input directory; "
                           f"found {len(candidates)}; pass --fixture PATH")
    directory = candidates[0]
    if not (directory / "walls.json").is_file():
        raise RuntimeError("NOT RUN: walls.json missing from " + str(directory))
    if authority:
        records = [Path(authority).resolve()]
    else:
        records = []
        # Operational record may be immediately beside, not inside, the pipeline.
        paths = set(directory.glob("*.json")) | set(directory.parent.glob("*.json"))
        for path in sorted(paths):
            try:
                if read_json(path).get("schema_version") == "p3-direction-authority-1":
                    records.append(path)
            except (OSError, ValueError, TypeError, AttributeError):
                continue
    if len(records) != 1 or not records[0].is_file():
        raise RuntimeError("NOT RUN: need a unique p3-direction-authority-1 record; "
                           "pass --authority PATH")
    return directory, records[0]


def load_frozen(source, name):
    # Actual module bytes, not hand-built stand-ins. Imports resolve in frozen tree.
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location("independent_" + name, source / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IndependentEmitter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/opencode"
        if os.name == "nt" and not approved.is_dir():
            raise RuntimeError("approved temporary directory unavailable: " + str(approved))
        cls.temp_parent = str(approved) if os.name == "nt" else None
        owner = tempfile.TemporaryDirectory(prefix="p16-p3-independent-source-", dir=cls.temp_parent)
        cls.addClassCleanup(owner.cleanup)
        cls.source = Path(owner.name) / "scripts"
        cls.source.mkdir()
        for p in (ROOT / "scripts").glob("*.py"):
            (cls.source / p.name).write_bytes(p.read_bytes())
        audit = Path(owner.name) / "Audit"
        audit.mkdir()
        contract = ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"
        (audit / contract.name).write_bytes(contract.read_bytes())
        cls.runtime = load_frozen(cls.source, "wall_surface_runtime")
        cls.publisher = load_frozen(cls.source, "wall_surface_publish")

    def setUp(self):
        owner = tempfile.TemporaryDirectory(prefix="p16-p3-independent-case-", dir=self.temp_parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.serial = 0

    def fresh(self, label):
        self.serial += 1
        p = self.temp / (str(self.serial).zfill(3) + "-" + label)
        p.mkdir()
        return p

    def project(self):
        home = self.fresh("request")
        project = home / "pipeline"
        shutil.copytree(FIXTURE, project)
        record = deepcopy(read_json(AUTHORITY))
        # Read the authentic analytical source, then use the SAME bytes privately.
        source = fixture_source(AUTHORITY, record).resolve()
        raw = source.read_bytes()
        self.assertEqual(digest(raw), record["source_sha256"], "fixture source lock is stale")
        (home / "analytical-plan.md").write_bytes(raw)
        # Absolute private source makes CLI cwd immaterial. The real F01 seed is
        # explicitly root-CWD-relative under the revised coordinator contract.
        record["source_file"] = str(home / "analytical-plan.md")
        record["source_sha256"] = digest(raw)
        auth = home / "direction-authority.json"
        write_json(auth, record)
        self.refresh_authority(project, auth)
        return project, auth

    def refresh_authority(self, project, auth, geometry=False):
        record = read_json(auth)
        walls = read_json(project / "walls.json")
        record["walls_sha256"] = digest((project / "walls.json").read_bytes())
        if geometry:
            run = walls["wall_runs"][0]
            for field in ("outward", "base_z_cm", "top_z_cm"):
                record[field] = run[field]
            record["inner_start_cm"] = run["start_cm"]
            record["inner_end_cm"] = run["end_cm"]
        write_json(auth, record)

    def cli(self, project, auth, out=None, namespace="IndependentP3", unit="millimeters",
            scale="1", extra=(), injection=None):
        if out is None:
            out = self.fresh("output-parent") / "run"
        argv = ["--in", str(project), "--out", str(out), "--namespace", namespace,
                "--system-type", unit, "--system-scale", scale,
                "--direction-authority", str(auth), *extra]
        command = [sys.executable, "-B", str(self.source / "build_wall_surface.py"), *argv]
        if injection:
            command = [sys.executable, "-B", "-c", injection, str(self.source),
                       str(project), str(auth), *argv]
        result = subprocess.run(command, cwd=self.temp, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=60,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                         PYTHONIOENCODING="utf-8"))
        return result, out

    def success(self, project, auth, **kwargs):
        before = snapshot(project)
        result, out = self.cli(project, auth, **kwargs)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(set(p.name for p in out.iterdir()), set(PAIR))
        self.assertEqual(snapshot(project), before, "successful emitter altered inputs")
        manifest = read_json(out / PAIR[0])
        self.assertEqual(manifest.get("schema_version"), "p3-wall-surface-1")
        self.assertEqual(manifest.get("spec"), "wall_surface")
        self.assertEqual(manifest.get("status"), "produced_offline_unverified")
        self.assertNotIn("Traceback", result.stderr)
        CASE_EVENTS.append("PASS positive actual public emission")
        return out, manifest

    def refusal(self, project, auth, label, **kwargs):
        before = snapshot(project)
        out = kwargs.get("out")
        old = snapshot(out) if out else {}
        result, out = self.cli(project, auth, **kwargs)
        self.assertNotEqual(result.returncode, 0, label + ": accepted\n" + result.stdout)
        self.assertNotIn("Traceback", result.stderr, label + ": unhandled error\n" + result.stderr)
        self.assertEqual(snapshot(out), old, label + ": changed output bytes")
        self.assertEqual(snapshot(project), before, label + ": changed input bytes")
        CASE_EVENTS.append("PASS refusal " + label)
        return result

    def calibrated(self):
        project, auth = self.project()
        self.success(project, auth)
        return project, auth

    def mutate_walls(self, project, auth, mutation):
        path = project / "walls.json"
        value = read_json(path)
        mutation(value)
        write_json(path, value)
        self.refresh_authority(project, auth)

    def test_01_real_f01_source_and_deterministic_actual_output(self):
        project, auth = self.project()
        walls = read_json(project / "walls.json")
        run = walls["wall_runs"][0]
        # Source truth is read directly, NOT inferred from vector or manifest.
        text = authority_source(auth, read_json(auth)).read_text(encoding="utf-8-sig")
        self.assertIn("### G.1", text)
        self.assertIn("Y = 0", text)
        self.assertIn("(0,−1,0)", text)
        self.assertIn("50…150", text)
        self.assertIn("230…330", text)
        self.assertEqual((run["start_cm"], run["end_cm"], run["base_z_cm"],
                          run["top_z_cm"], run["outward"], run["thickness_cm"]),
                         ([0, 0], [400, 0], 0, 300, [0, -1], 30))
        self.assertEqual(sorted((tuple(o["u_range_cm"]), o["sill_cm"], o["head_cm"])
                                for o in walls["openings"]),
                         [((50, 150), 0, 210), ((230, 330), 90, 210)])
        first, manifest = self.success(project, auth)
        second, _ = self.success(project, auth)
        self.assertEqual(snapshot(first), snapshot(second), "same-input publication is not deterministic")
        predictions = manifest["predictions"]["values"]
        # Constants independently recomputed from actual analytical F01, not a
        # manufactured produced fixture or a second copy of builder logic.
        for key, expected in {"grid_vertices": 24, "grid_edges": 38, "grid_polygons": 15,
                              "removed_grid_polygons": 3, "base_active_polygons": 12,
                              "base_active_edges": 36, "base_boundary_edges": 24,
                              "base_area_cm2": 87000, "evaluated_polygons": 48,
                              "evaluated_triangles": 96, "volume_cm3": 2610000}.items():
            self.assertEqual(predictions[key], expected, key + ": wrong source-derived prediction")
        self.assertEqual(predictions["bounds_cm"], [[0, -30, 0], [400, 0, 300]])
        self.assertEqual(manifest["direction_evidence"]["geometric_outward"], [0, -1])
        raw = (first / PAIR[1]).read_bytes()
        # Independent hash search allows nested manifest layout without inventing
        # an undocumented key. An actual script digest must be retained as data.
        def leaves(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from leaves(child)
            elif isinstance(value, list):
                for child in value:
                    yield from leaves(child)
            else:
                yield value
        self.assertIn(digest(raw), set(x for x in leaves(manifest) if isinstance(x, str)))
        script = raw.decode("utf-8-sig")
        self.assertNotRegex(script, r"(?im)^\s*(?:resetMaxFile|max\s+reset)\b")
        self.assertNotRegex(script, r"(?i)delete\s+objects\b|delete\s+\$\*|select\s+\$\*")

    def test_02_numeric_raw_json_refusals_have_clean_control(self):
        project, auth = self.calibrated()
        original = (project / "walls.json").read_bytes()
        cases = {
            "boolean": b"true", "numeric-string": b'"30"', "NaN": b"NaN",
            "infinity": b"Infinity", "overflow": b"1e9999", "underflow": b"1e-9999",
            "lossy-integer": b"9007199254740993",
            "rounded-decimal": b"30.00000000000000000000000000000000001",
        }
        for label, token in cases.items():
            with self.subTest(label=label):
                mutated, count = re.subn(rb'("thickness_cm"\s*:\s*)[^,}\s]+',
                                         lambda m: m[1] + token, original, count=1)
                self.assertEqual(count, 1)
                (project / "walls.json").write_bytes(mutated)
                record = read_json(auth)
                record["walls_sha256"] = digest(mutated)
                write_json(auth, record)
                self.refusal(project, auth, label)
        (project / "walls.json").write_bytes(original)
        self.refresh_authority(project, auth)
        self.success(project, auth)

    def test_03_closed_schema_duplicates_and_status_route_refusals(self):
        mutations = {
            "unknown-top": lambda d: d.update(unowned_unknown=1),
            "unknown-run": lambda d: d["wall_runs"][0].update(direction_authority="APPROVED"),
            "unknown-block": lambda d: d["blocks"][0].update(implementation_class="Box"),
            "unknown-opening": lambda d: d["openings"][0].update(implementation_class="Boolean"),
            "unknown-budget": lambda d: d["wall_runs"][0]["topology_budget"].update(max_nodes=1),
            "draft": lambda d: d.update(status="draft"),
            "superseded": lambda d: d.update(status="superseded"),
            "legacy-route": lambda d: d.update(wall_technique="legacy_cells_v1"),
            "outer-reference": lambda d: d.update(reference_face="outer"),
        }
        project, auth = self.calibrated()
        original = (project / "walls.json").read_bytes()
        for label, mutation in mutations.items():
            with self.subTest(label=label):
                (project / "walls.json").write_bytes(original)
                self.mutate_walls(project, auth, mutation)
                self.refusal(project, auth, label)
        for label, raw in (("duplicate", b'{"status":"locked",' + original.lstrip()[1:]),
                           ("deep-json", b'{"x":' + b'['*140 + b'0' + b']'*140 + b'}')):
            with self.subTest(label=label):
                (project / "walls.json").write_bytes(raw)
                record = read_json(auth)
                record["walls_sha256"] = digest(raw)
                write_json(auth, record)
                self.refusal(project, auth, label)

    def test_04_authority_closed_binding_source_hash_missing_and_flip(self):
        project, auth = self.calibrated()
        original = auth.read_bytes()
        changes = {
            "project": ("project", "wrong-project"), "run": ("wall_run_id", "wrong-run"),
            "walls-hash": ("walls_sha256", "0"*64), "source-hash": ("source_sha256", "0"*64),
            "missing-source": ("source_file", "missing-source.md"),
            "source-traversal": ("source_file", "../outside-source.md"),
            "source-ADS": ("source_file", "analytical-plan.md:private"),
            "start": ("inner_start_cm", [1, 0]), "end": ("inner_end_cm", [399, 0]),
            "base": ("base_z_cm", 1), "top": ("top_z_cm", 301),
            "physical-flip": ("outward", [0, 1]), "boolean-outward": ("outward", [False, -1]),
            "unknown-authority-field": ("approved", True),
        }
        for label, (key, value) in changes.items():
            with self.subTest(label=label):
                record = json.loads(original)
                record[key] = value
                write_json(auth, record)
                self.refusal(project, auth, label)
        auth.write_bytes(original)
        source = authority_source(auth, read_json(auth))
        source.write_bytes(source.read_bytes() + b"\nSOURCE DRIFT\n")
        self.refusal(project, auth, "actual-source-drift")

    def test_05_wall_flip_refuses_against_unchanged_physical_authority(self):
        project, auth = self.calibrated()
        self.mutate_walls(project, auth, lambda d: d["wall_runs"][0].update(outward=[0, 1]))
        self.refusal(project, auth, "wall-normal-flip-vs-authority")

    def test_06_provenance_missing_unknown_and_derived_without_oracle(self):
        project, auth = self.calibrated()
        original = (project / "walls.json").read_bytes()
        cases = {
            "missing-origins": lambda d: d.pop("origins"),
            "unknown-origin": lambda d: d["origins"].update({"wall_runs[0]": {"origin": "maybe"}}),
            "missing-ledger": lambda d: d["origins"].update({"wall_runs[0]": {
                "origin": "assumed", "origin_ref": "A-999"}}),
            "derived-no-oracle": lambda d: d["origins"].update({"wall_runs[0]": {
                "origin": "derived", "derives_from": ["dimensions.json:facades[0]"]}}),
        }
        for label, mutation in cases.items():
            with self.subTest(label=label):
                (project / "walls.json").write_bytes(original)
                self.mutate_walls(project, auth, mutation)
                self.refusal(project, auth, label)
        (project / "walls.json").write_bytes(original)
        self.refresh_authority(project, auth)
        dims = read_json(project / "dimensions.json")
        fid = read_json(project / "walls.json")["wall_runs"][0]["contour_ref"].split(":")[-1]
        index = next(i for i, item in enumerate(dims["facades"]) if item["id"] == fid)
        # Do not let duplicate collapsed/leaf annotations mask this formula fault.
        prefix = f"facades[{index}]."
        dims["origins"] = {k: v for k, v in dims["origins"].items() if not k.startswith(prefix)}
        dims["origins"][f"facades[{index}]"] = {
            "origin": "derived", "derives_from": ["building.name"]}
        write_json(project / "dimensions.json", dims)
        self.refusal(project, auth, "reached-upstream-unknown-or-unrelated-formula")

    def test_07_known_formula_bad_arithmetic_and_dependency_refuse(self):
        project, auth = self.calibrated()
        path = project / "dimensions.json"
        original = read_json(path)
        self.assertIn("site", original, "required known-formula case needs site input")
        self.assertIn("footprint_cm", original["site"], "required source polygon unavailable")
        for label, dependencies in (("bad-arithmetic", ["site.footprint_cm"]),
                                    ("bad-dependency", ["building.name"])):
            with self.subTest(label=label):
                dims = deepcopy(original)
                polygon = dims["site"]["footprint_cm"]
                area = abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in
                               zip(polygon, polygon[1:]+polygon[:1]))) / 20000
                dims["site"]["footprint_area_m2"] = area + (10 if label == "bad-arithmetic" else 0)
                dims["origins"]["site.footprint_area_m2"] = {
                    "origin": "derived", "derives_from": dependencies}
                write_json(path, dims)
                self.refusal(project, auth, label)

    def test_08_larger_real_fixture_whole_request_refuses(self):
        project, auth = self.calibrated()
        raw = (ROOT / "specs/fixtures/poly-shell-input/walls.json").read_bytes()
        self.assertGreater(len(json.loads(raw)["wall_runs"]), 1)
        (project / "walls.json").write_bytes(raw)
        self.refresh_authority(project, auth)
        self.refusal(project, auth, "complete-larger-real-request-no-subset")
        # Also a same-project, otherwise identical second block/run/return cannot
        # silently become a partial single-run publication.
        for label in ("second-block", "second-run", "upper-return"):
            project, auth = self.calibrated()
            walls = read_json(project / "walls.json")
            if label == "second-block":
                value = deepcopy(walls["blocks"][0]); value["id"] += "EXTRA"
                walls["blocks"].append(value)
                walls["origins"]["blocks[1]"] = {"origin": "given"}
            elif label == "second-run":
                value = deepcopy(walls["wall_runs"][0]); value["id"] += "EXTRA"
                walls["wall_runs"].append(value)
                walls["origins"]["wall_runs[1]"] = {"origin": "given"}
            else:
                value = deepcopy(walls["wall_runs"][0]); value["id"] += "RETURN"
                value["adjacent_run_ids"] = [walls["wall_runs"][0]["id"]]
                walls["upper_returns"].append(value)
                walls["origins"]["upper_returns[0]"] = {"origin": "given"}
            write_json(project / "walls.json", walls)
            self.refresh_authority(project, auth)
            self.refusal(project, auth, label)

    def test_09_all_declared_topology_budgets_are_enforced(self):
        project, auth = self.calibrated()
        original = (project / "walls.json").read_bytes()
        for key, value in (("max_grid_polygons", 14), ("max_base_active_polygons", 11),
                           ("max_evaluated_triangles", 95)):
            with self.subTest(budget=key):
                (project / "walls.json").write_bytes(original)
                self.mutate_walls(project, auth, lambda d: d["wall_runs"][0]["topology_budget"].update({key: value}))
                self.refusal(project, auth, key)

    def test_10_cli_namespace_units_scale_injection_and_no_overrides(self):
        project, auth = self.calibrated()
        for token in ("", "a"*41, "1StartsWithDigit", "has space", "NonASCIIя",
                      'x\";delete objects;--', "x\nresetMaxFile #noPrompt", "x-1", "x."):
            with self.subTest(namespace=token):
                self.refusal(project, auth, "namespace:" + repr(token), namespace=token)
        for unit in ("mm", "Millimeters", "centimeters;delete objects", "", "unknown"):
            with self.subTest(unit=unit):
                self.refusal(project, auth, "unit:" + repr(unit), unit=unit)
        for scale in ("0", "-1", "nan", "inf", "True", "1e9999", "1e-9999", "1;delete objects"):
            with self.subTest(scale=scale):
                self.refusal(project, auth, "scale:" + scale, scale=scale)
        for flags in (("--force",), ("--allow-draft",), ("--bogus",),
                      ("--namespace", "ChangedDuplicate"), ("--system-type", "centimeters")):
            with self.subTest(flags=flags):
                self.refusal(project, auth, "override:" + repr(flags), extra=flags)

    def test_11_public_output_existing_pair_private_victim_unchanged(self):
        project, auth = self.calibrated()
        for label, occupied in (("empty", False), ("private-victim", True)):
            out = self.fresh(label)
            if occupied:
                for name in (*PAIR, "foreign.bin"):
                    (out / name).write_bytes(SENTINEL + name.encode())
            self.refusal(project, auth, "existing:" + label, out=out)
        produced, _ = self.success(project, auth)
        self.refusal(project, auth, "repeated-publication-to-actual-run", out=produced)
        self.refusal(project, auth, "input-directory-is-output", out=project)

    def test_12_runtime_direct_clean_float32_near_stations_and_operation_caps(self):
        project, _ = self.project()
        walls, dims = read_json(project / "walls.json"), read_json(project / "dimensions.json")
        unit = {"system_type": "millimeters", "system_scale": 1.0,
                "cm_per_unit": 0.1, "units_per_cm": 10.0}
        control = self.runtime.build_plan(deepcopy(walls), deepcopy(dims))
        self.runtime.generate_script(control, "a"*64, "IndependentP3", unit)
        cases = {}
        near = deepcopy(walls)
        near["openings"][1]["sill_cm"] = 90.00001  # DISTINCT from 90, not a snapping request.
        # Make two distinct close v stations; existing door has sill=0 so change
        # its head as well rather than rely on a currently absent 90 station.
        near["openings"][0]["head_cm"] = 90
        cases["distinct-near-stations"] = near
        huge = deepcopy(walls)
        huge["wall_runs"][0].update(base_z_cm=100000000.125, top_z_cm=100000300.125)
        huge["blocks"][0]["z_range_cm"] = [100000000.125, 100000300.125]
        cases["Float32-large-world"] = huge
        large = deepcopy(walls)
        run = large["wall_runs"][0]
        run["topology_budget"] = {"max_grid_polygons": 1000000,
                                  "max_base_active_polygons": 1000000,
                                  "max_evaluated_triangles": 1000000}
        large["openings"] = [{"id": "Operation"+str(i), "wall_run_id": run["id"],
                              "kind": "window", "u_range_cm": [10+50*i, 30+50*i],
                              "sill_cm": 90, "head_cm": 210} for i in range(7)]
        cases["operational-cap-not-input-budget"] = large
        grid = deepcopy(large)
        grid["openings"] = grid["openings"][:6]
        # 6 openings are permitted, but 13 u cells * 3 v cells = 39 exceeds
        # the independent 32-grid-polygon cap even with huge declared budgets.
        cases["operational-grid-cap-within-opening-cap"] = grid
        for label, changed in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(Exception, msg=label + " must refuse"):
                    plan = self.runtime.build_plan(changed, deepcopy(dims))
                    self.runtime.generate_script(plan, "a"*64, "IndependentP3", unit)
                CASE_EVENTS.append("PASS runtime refusal " + label)
        # Native-coordinate overflow is configuration-dependent: use public CLI,
        # not a synthetic manifest or guessed runtime call signature.
        project, auth = self.calibrated()
        self.refusal(project, auth, "native-Float32-overflow", scale=str(2.0**-120))

    def test_13_publisher_real_no_replace_late_collision_and_private_bytes(self):
        pub = self.publisher
        raw = {PAIR[0]: b'{"actual":"publisher-control"}\n', PAIR[1]: b"-- actual bytes\n"}
        parent = self.fresh("publisher")
        good = parent / "clean"
        hashes = pub.publish_new_directory(good, raw)
        self.assertEqual(hashes, {k: digest(v) for k, v in raw.items()})
        self.assertEqual({k: (good/k).read_bytes() for k in raw}, raw)
        old = snapshot(good)
        with self.assertRaises(Exception):
            pub.publish_new_directory(good, raw)
        self.assertEqual(snapshot(good), old)
        out = parent / "late-victim"
        real_rename = pub.os.rename
        invoked = []
        def collision(src, dst):
            invoked.append(True)
            Path(dst).mkdir()
            (Path(dst) / "private.bin").write_bytes(SENTINEL)
            return real_rename(src, dst)
        with mock.patch.object(pub.os, "rename", side_effect=collision):
            with self.assertRaises(Exception):
                pub.publish_new_directory(out, raw)
        self.assertEqual(len(invoked), 1, "did not reach real no-replace commit")
        self.assertEqual(snapshot(out), {"private.bin": SENTINEL})
        self.assertFalse(list(parent.glob(".wall-surface-stage-*")), "owned staging leaked on recoverable collision")
        CASE_EVENTS.append("PASS publisher real late-collision no-clobber")

    def test_14_publisher_second_write_failure_has_no_partial_pair(self):
        pub = self.publisher
        parent = self.fresh("publisher-io")
        out = parent / "new-run"
        raw = {PAIR[0]: b"{}\n", PAIR[1]: b"-- safety control\n"}
        # Calibrate actual helper first, then only inject the precise file error.
        pub.publish_new_directory(parent / "control", raw)
        original = pub._open_binary
        calls = []
        def fail_second(path, mode):
            if Path(path).name == PAIR[1] and mode == "xb":
                calls.append(True)
                raise PermissionError("INDEPENDENT injected second-file write failure")
            return original(path, mode)
        with mock.patch.object(pub, "_open_binary", side_effect=fail_second):
            with self.assertRaises(Exception):
                pub.publish_new_directory(out, raw)
        self.assertEqual(calls, [True])
        self.assertFalse(out.exists(), "partial pair was published")
        self.assertFalse(list(parent.glob(".wall-surface-stage-*")), "owned staging not recovered")
        CASE_EVENTS.append("PASS publisher second-file I/O atomic visibility")

    def test_15_publisher_private_stage_substitution_is_retained_not_deleted(self):
        pub = self.publisher
        parent = self.fresh("publisher-private-substitution")
        out = parent / "new-run"
        raw = {PAIR[0]: b"{}\n", PAIR[1]: b"-- safety control\n"}
        pub.publish_new_directory(parent / "control", raw)
        original = pub._verify_pair
        observed = []
        parked = parent / "owned-parked.ms"
        def substitute(stage, *args, **kwargs):
            (stage / PAIR[1]).rename(parked)
            (stage / PAIR[1]).write_bytes(SENTINEL)
            observed.append(stage)
            return original(stage, *args, **kwargs)
        with mock.patch.object(pub, "_verify_pair", side_effect=substitute):
            with self.assertRaises(Exception) as caught:
                pub.publish_new_directory(out, raw)
        self.assertEqual(len(observed), 1)
        self.assertFalse(out.exists())
        self.assertEqual((observed[0] / PAIR[1]).read_bytes(), SENTINEL,
                         "cleanup deleted/substituted private victim")
        self.assertEqual(parked.read_bytes(), raw[PAIR[1]])
        self.assertIsNotNone(getattr(caught.exception, "evidence_path", None),
                             "unrecovered identity uncertainty omitted recovery path")
        CASE_EVENTS.append("PASS publisher substituted private victim retained with evidence")

    def test_16_real_render_then_observed_input_or_authority_source_drift_refuses(self):
        injection = r'''
import pathlib, sys
sys.path.insert(0, sys.argv[1])
import build_wall_surface as b
import wall_surface_runtime as runtime
real = runtime.generate_script
project, auth = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
which = sys.argv[4]
def changed(*args, **kwargs):
    result = real(*args, **kwargs)
    if which == "dimensions":
        target = project / "dimensions.json"
    else:
        target = auth.parent / "analytical-plan.md"
    target.write_bytes(target.read_bytes() + b"\nINDEPENDENT OBSERVED SOURCE DRIFT\n")
    print("INDEPENDENT_DRIFT_INJECTED:" + which, file=sys.stderr)
    return result
runtime.generate_script = changed
sys.exit(b.main(sys.argv[5:]))
'''
        for which in ("dimensions", "physical-source"):
            with self.subTest(source=which):
                project, auth = self.calibrated()
                target = project / "dimensions.json" if which == "dimensions" else auth.parent / "analytical-plan.md"
                old = target.read_bytes()
                out = self.fresh("drift-output-parent") / "run"
                argv = ["--in", str(project), "--out", str(out), "--namespace", "IndependentP3",
                        "--system-type", "millimeters", "--system-scale", "1",
                        "--direction-authority", str(auth)]
                result = subprocess.run([sys.executable, "-B", "-c", injection, str(self.source),
                                         str(project), str(auth), which, *argv],
                                        cwd=self.temp, capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=60,
                                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
                self.assertIn("INDEPENDENT_DRIFT_INJECTED:"+which, result.stderr,
                              "did not reach actual successful render before drift")
                self.assertNotEqual(result.returncode, 0, "observed drift was published")
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(out.exists(), "observed drift left an output pair")
                self.assertEqual(target.read_bytes(), old + b"\nINDEPENDENT OBSERVED SOURCE DRIFT\n",
                                 "builder overwrote the changed original source")
                CASE_EVENTS.append("PASS after-real-render observed drift " + which)

    def test_17_raw_consumed_upstream_and_authority_size_limits(self):
        project, auth = self.calibrated()
        dims_path = project / "dimensions.json"
        original = dims_path.read_bytes()
        duplicate = b'{"project":"wrong-first-value",' + original.lstrip()[1:]
        for label, raw in (("used-upstream-duplicate", duplicate),
                           ("used-upstream-oversized", original + b" "*(2*1024*1024))):
            with self.subTest(label=label):
                dims_path.write_bytes(raw)
                self.refusal(project, auth, label)
        dims_path.write_bytes(original)
        self.success(project, auth)
        original_auth = auth.read_bytes()
        auth.write_bytes(b'{"project":"wrong-first-value",' + original_auth.lstrip()[1:])
        self.refusal(project, auth, "duplicate-authority")
        auth.write_bytes(original_auth + b" "*(2*1024*1024))
        self.refusal(project, auth, "oversized-authority")

    def test_18_output_parent_alias_and_hardlinked_input_preserve_private_victims(self):
        project, auth = self.calibrated()
        for spelling in ("CON", "Ambiguous.", "Ambiguous ", "file:stream"):
            with self.subTest(alias=spelling):
                parent = self.fresh("path-parent")
                self.refusal(project, auth, "output-alias:"+spelling, out=parent / spelling)
        victim = self.fresh("private-hardlink-victim") / "original.json"
        target = project / "dimensions.json"
        raw = target.read_bytes()
        victim.write_bytes(raw)
        target.unlink()
        os.link(victim, target)
        self.assertEqual(os.stat(victim).st_nlink, 2, "hardlink injection not established")
        self.refusal(project, auth, "hardlinked-consumed-input")
        self.assertEqual(victim.read_bytes(), raw, "private hardlink victim changed")

    def test_19_oversized_actual_source_and_actual_script_pair_are_refused(self):
        project, auth = self.calibrated()
        record = read_json(auth)
        source = authority_source(auth, record)
        original = source.read_bytes()
        raw = original + b" "*(16*1024*1024)
        source.write_bytes(raw)
        record["source_sha256"] = digest(raw)
        write_json(auth, record)
        self.refusal(project, auth, "actual-source-size-ceiling")
        project, auth = self.calibrated()
        injection = r'''
import sys
sys.path.insert(0, sys.argv[1])
import build_wall_surface as b
import wall_surface_runtime as runtime
real = runtime.generate_script
def enlarged(*args, **kwargs):
    result = real(*args, **kwargs)
    print("INDEPENDENT_ACTUAL_SCRIPT_ENLARGED", file=sys.stderr)
    return result + "--" + "x"*(2*1024*1024) + "\n"
runtime.generate_script = enlarged
sys.exit(b.main(sys.argv[4:]))
'''
        result = self.refusal(project, auth, "actual-script-pair-size-ceiling", injection=injection)
        self.assertIn("INDEPENDENT_ACTUAL_SCRIPT_ENLARGED", result.stderr,
                      "did not reach actual production script before size mutation")

    def test_20_explicit_arm_separation_binding_and_invalid_nonce_refusals(self):
        project, auth = self.calibrated()
        out, manifest = self.success(project, auth)
        walls, dims = read_json(project / "walls.json"), read_json(project / "dimensions.json")
        plan = self.runtime.build_plan(walls, dims)
        units = {"system_type": "millimeters", "system_scale": 1.0,
                 "cm_per_unit": 0.1, "units_per_cm": 10.0}
        script = (out / PAIR[1]).read_text(encoding="utf-8")
        # These are source-emission assertions ONLY, not Max lease semantics.
        # Main must execute missing/replaced/poisoned registry controls live.
        self.assertIn("missing explicit armed session registry", script)
        self.assertNotIn("globalVars.set registryKey", script,
                         "geometry artifact must not implicitly publish/re-arm a registry")
        arm = self.runtime.generate_arm_script(plan, manifest["identity"], "IndependentP3",
                                               units, "IndependentNonce_0123456789")
        self.assertIn('objects.count != 0', arm)
        self.assertIn('selection.count != 0', arm)
        self.assertIn('globalVars.isGlobal registryKey', arm)
        self.assertIn('globalVars.set registryKey witness', arm)
        self.assertIn(manifest["identity"], arm)
        self.assertIn('"ARMED"', arm)
        self.assertNotRegex(arm, r"(?im)^\s*(?:delete|resetMaxFile|box|mesh|polyop\.createVert)\b")
        for variable in ("registryKey", "artifactBinding"):
            expression = re.search(r"(?m)^    local " + variable + r" = (.+)$", script)
            self.assertIsNotNone(expression)
            self.assertIn(expression.group(1), arm, "arm/geometry identity literal mismatch")
        for nonce in ("", "short", "x"*129, 'bad\";delete objects;--', "x"*16+"\n", "я"*16):
            with self.subTest(nonce=nonce):
                with self.assertRaises(ValueError):
                    self.runtime.generate_arm_script(plan, manifest["identity"], "IndependentP3", units, nonce)
        CASE_EVENTS.append("PASS emitted explicit-arm separation/binding/nonces (NOT live)")

    def test_21_two_individually_small_artifacts_still_enforce_pair_two_mib(self):
        project, auth = self.calibrated()
        injection = r'''
import pathlib, sys
sys.path.insert(0, sys.argv[1])
import build_wall_surface as b
import wall_surface_runtime as runtime
real = runtime.generate_script
def enlarged(*args, **kwargs):
    result = real(*args, **kwargs)
    record = args[3] if len(args)>3 else kwargs['expected_units']
    print("INDEPENDENT_REAL_SCRIPT_UNDER_2M", file=sys.stderr)
    return result + "--" + "x"*(1400*1024) + "\n"
runtime.generate_script = enlarged
sys.exit(b.main(sys.argv[4:]))
'''
        record = read_json(auth)
        # Valid bounded source_location as data, not executable code. Manifest
        # retains authority as data; script stays individually below 2 MiB.
        record["source_location"] = "G.1 actual analytical source; " + "s"*(800*1024)
        write_json(auth, record)
        self.assertLess(auth.stat().st_size, 2*1024*1024)
        result = self.refusal(project, auth, "pair-total-not-per-file-ceiling", injection=injection)
        self.assertIn("INDEPENDENT_REAL_SCRIPT_UNDER_2M", result.stderr)
        self.assertIn("artifact pair exceeds 2 MiB", result.stderr)

    def test_22_publisher_direct_total_two_mib_contract(self):
        pub = self.publisher
        parent = self.fresh("publisher-pair-limit")
        small = {PAIR[0]: b"{}\n", PAIR[1]: b"-- real publisher control\n"}
        pub.publish_new_directory(parent / "control", small)
        large = {PAIR[0]: b"j"*(1100*1024), PAIR[1]: b"m"*(1100*1024)}
        self.assertTrue(all(len(v) < 2*1024*1024 for v in large.values()))
        out = parent / "too-large-pair"
        with self.assertRaises(Exception, msg="publisher must enforce contract pair <=2 MiB"):
            pub.publish_new_directory(out, large)
        self.assertFalse(out.exists(), "publisher published an over-limit pair")


def main():
    global FIXTURE, AUTHORITY, SOURCE_MANIFEST, FIXTURE_MANIFEST
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture")
    parser.add_argument("--authority")
    opts, remaining = parser.parse_known_args()
    missing = [name for name in REQUIRED if not (ROOT / "scripts" / name).is_file()]
    if missing:
        print("NOT RUN: missing production modules: " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        FIXTURE, AUTHORITY = discover(opts.fixture, opts.authority)
        record = read_json(AUTHORITY)
        actual_source = fixture_source(AUTHORITY, record).resolve()
        SOURCE_MANIFEST = hashed_files([*(ROOT / "scripts").glob("*.py"),
                                       ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"])
        FIXTURE_MANIFEST = hashed_files([*FIXTURE.rglob("*"), AUTHORITY, actual_source,
                                       ROOT / "specs/fixtures/poly-shell-input/walls.json"])
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("INDEPENDENT_P3_SOURCE " + json.dumps(SOURCE_MANIFEST, sort_keys=True), file=sys.stderr)
    print("INDEPENDENT_P3_FIXTURES " + json.dumps(FIXTURE_MANIFEST, sort_keys=True), file=sys.stderr)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IndependentEmitter)
    if remaining and any(x not in ("-v", "-q") for x in remaining):
        parser.error("only -v/-q unittest options are supported")
    result = unittest.TextTestRunner(verbosity=2 if "-v" in remaining else 1).run(suite)
    source_after = hashed_files([*(ROOT / "scripts").glob("*.py"),
                                 ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"])
    fixture_after = hashed_files(Path(p) for p in FIXTURE_MANIFEST)
    drift = [p for p in set(SOURCE_MANIFEST) | set(source_after)
             if SOURCE_MANIFEST.get(p) != source_after.get(p)]
    drift += [p for p in FIXTURE_MANIFEST if FIXTURE_MANIFEST[p] != fixture_after.get(p)]
    print("INDEPENDENT_P3_FINAL_SOURCE " + json.dumps(source_after, sort_keys=True), file=sys.stderr)
    print("INDEPENDENT_P3_FINAL_FIXTURES " + json.dumps(fixture_after, sort_keys=True), file=sys.stderr)
    print("INDEPENDENT_P3_EVENTS " + json.dumps(CASE_EVENTS), file=sys.stderr)
    print("INDEPENDENT_P3_DRIFT " + json.dumps(drift), file=sys.stderr)
    print("INDEPENDENT_P3_RESULT " + json.dumps({
        "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skips": len(result.skipped), "events": len(CASE_EVENTS), "drift": drift}), file=sys.stderr)
    if drift or result.skipped or not result.wasSuccessful():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
