#!/usr/bin/env python3
"""Temp-only coordinator boundary tests; fake-runtime tests are NOT Max evidence."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_wall_surface as builder


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def walls() -> dict:
    """Minimal isolated coordinator data, not a validated produced-poly fixture."""
    return {
        "schema_version": "1.1", "spec": "walls", "project": "builder-test",
        "status": "locked", "wall_technique": "poly_surface_shell_v1",
        "reference_face": "inner", "numeric_unit_epsilon": 0.000001,
        "numeric_epsilon_cm": 0.001,
        "blocks": [{"id": "B1", "z_range_cm": [0, 300]}],
        "wall_runs": [{"id": "W1", "block_id": "B1", "start_cm": [0, 0],
                       "end_cm": [500, 0], "outward": [0, -1], "base_z_cm": 0,
                       "top_z_cm": 300, "thickness_cm": 30,
                       "contour_ref": "dimensions.json:facades:F1",
                       "topology_budget": {"max_grid_polygons": 15,
                                           "max_base_active_polygons": 12,
                                           "max_evaluated_triangles": 96}}],
        "openings": [], "upper_returns": [],
    }


def authority(wall_hash: str = "1" * 64, source_hash: str = "2" * 64) -> dict:
    return {
        "schema_version": "p3-direction-authority-1", "project": "builder-test",
        "wall_run_id": "W1", "walls_sha256": wall_hash,
        "source_file": "analytical-plan.txt", "source_sha256": source_hash,
        "source_location": "Analytical test plan: inner Y=0; outward -Y",
        "inner_start_cm": [0, 0], "inner_end_cm": [500, 0],
        "base_z_cm": 0, "top_z_cm": 300, "outward": [0, -1],
    }


class TempCase(unittest.TestCase):
    def setUp(self) -> None:
        approved = Path("C:/Users/Turbolamer/AppData/Local/Temp/opencode")
        self.temporary = tempfile.TemporaryDirectory(
            prefix="p3-builder-test-", dir=str(approved) if approved.is_dir() else None)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).absolute()

    def write_authority(self, record: dict | None = None, source: bytes = b"Inner Y=0; outward -Y\n") -> Path:
        (self.root / "analytical-plan.txt").write_bytes(source)
        record = copy.deepcopy(record if record is not None else authority())
        record["source_sha256"] = digest(source)
        record["source_file"] = str(self.root / "analytical-plan.txt")
        path = self.root / "direction-authority.json"
        path.write_bytes(builder.canonical_json(record))
        return path


class AuthorityTests(TempCase):
    def test_positive_closed_record_and_exact_scalar_values(self) -> None:
        record = authority()
        before = copy.deepcopy(record)
        self.assertEqual(builder.check_authority(record, walls(), "1" * 64), before)
        self.assertEqual(record, before)

    def test_each_missing_key_and_unknown_key_refused(self) -> None:
        for key in builder.AUTHORITY_KEYS:
            with self.subTest(key=key):
                record = authority()
                del record[key]
                with self.assertRaises(builder.BuildRefusal):
                    builder.check_authority(record, walls(), "1" * 64)
        record = authority()
        record["approved"] = True
        with self.assertRaises(builder.BuildRefusal):
            builder.check_authority(record, walls(), "1" * 64)

    def test_bad_root_and_schema_refused(self) -> None:
        for record in (None, [], "text", {**authority(), "schema_version": "1.1"}):
            with self.subTest(record=record), self.assertRaises(builder.BuildRefusal):
                builder.check_authority(record, walls(), "1" * 64)

    def test_finite_numeric_closed_record(self) -> None:
        for key in ("inner_start_cm", "inner_end_cm", "outward", "base_z_cm", "top_z_cm"):
            for value in (True, "0", None, float("nan"), float("inf"), float("-inf"), 10 ** 400):
                with self.subTest(key=key, value=str(value)[:50]):
                    record = authority()
                    record[key] = [value, 0] if key in ("inner_start_cm", "inner_end_cm", "outward") else value
                    with self.assertRaises(builder.BuildRefusal):
                        builder.check_authority(record, walls(), "1" * 64)

    def test_exact_pair_shapes(self) -> None:
        for key in ("inner_start_cm", "inner_end_cm", "outward"):
            for value in ([], [1], [0, 0, 0], {"x": 0, "y": 0}, (0, 0)):
                with self.subTest(key=key, value=value), self.assertRaises(builder.BuildRefusal):
                    builder.check_authority({**authority(), key: value}, walls(), "1" * 64)

    def test_each_source_wall_value_compared_independently(self) -> None:
        changes = {"project": "other", "wall_run_id": "W2", "walls_sha256": "3" * 64,
                   "inner_start_cm": [1, 0], "inner_end_cm": [501, 0],
                   "outward": [0, 1], "base_z_cm": 1, "top_z_cm": 301}
        for key, value in changes.items():
            with self.subTest(key=key), self.assertRaises(builder.BuildRefusal):
                builder.check_authority({**authority(), key: value}, walls(), "1" * 64)
        for key, value in (("start_cm", [1, 0]), ("end_cm", [501, 0]),
                           ("outward", [0, 1]), ("base_z_cm", 1), ("top_z_cm", 301)):
            changed = walls()
            changed["wall_runs"][0][key] = value
            with self.subTest(wall_key=key), self.assertRaises(builder.BuildRefusal):
                builder.check_authority(authority(), changed, "1" * 64)

    def test_nonunique_run_and_inverted_z_refused(self) -> None:
        for run_list in ([], [walls()["wall_runs"][0]] * 2, [None]):
            changed = walls()
            changed["wall_runs"] = run_list
            with self.assertRaises(builder.BuildRefusal):
                builder.check_authority(authority(), changed, "1" * 64)
        changed, record = walls(), authority()
        changed["wall_runs"][0]["top_z_cm"] = record["top_z_cm"] = 0
        with self.assertRaises(builder.BuildRefusal):
            builder.check_authority(record, changed, "1" * 64)

    def test_ambiguous_strings_and_noncanonical_hashes(self) -> None:
        for key in ("project", "wall_run_id", "source_file", "source_location"):
            for value in ("", " trailing ", "x\ny", None, True):
                with self.subTest(key=key, value=value), self.assertRaises(builder.BuildRefusal):
                    builder.check_authority({**authority(), key: value}, walls(), "1" * 64)
        for key in ("walls_sha256", "source_sha256"):
            for value in ("A" * 64, "a" * 63, "a" * 65, "g" * 64, "1" * 64 + "\n"):
                with self.subTest(key=key, value=value), self.assertRaises(builder.BuildRefusal):
                    builder.check_authority({**authority(), key: value}, walls(), "1" * 64)

    def test_source_hash_is_exact_raw_bytes_not_json_or_text_reencoding(self) -> None:
        raw = b"\xef\xbb\xbfInner Y=0; outward -Y\r\n  authored  \r\n"
        path = self.write_authority(source=raw)
        record, hashes = builder.load_authority(path, walls(), "1" * 64)
        source = str(self.root / "analytical-plan.txt")
        self.assertEqual(hashes[source], digest(raw))
        self.assertEqual(record["source_sha256"], digest(raw))
        self.assertEqual(hashes[str(path)], digest(path.read_bytes()))
        self.assertNotEqual(hashes[source], digest(raw.replace(b"\r\n", b"\n")))
        (self.root / "analytical-plan.txt").write_bytes(raw.replace(b"\r\n", b"\n"))
        with self.assertRaisesRegex(builder.BuildRefusal, "source_sha256"):
            builder.load_authority(path, walls(), "1" * 64)

    def test_source_text_is_never_executed(self) -> None:
        marker = self.root / "must-not-exist"
        payload = ("__import__('pathlib').Path(" + repr(str(marker)) + ").write_text('EXECUTED')").encode()
        path = self.write_authority(source=payload)
        builder.load_authority(path, walls(), "1" * 64)
        self.assertFalse(marker.exists())

    def test_strict_authority_parser_numeric_and_duplicate_controls(self) -> None:
        path = self.write_authority()
        positive = path.read_bytes()
        bad_payloads = [b'{' + positive[1:].replace(b'"project":', b'"project":"discard", "project":', 1),
                        positive.replace(b'"base_z_cm":0', b'"base_z_cm":NaN'),
                        positive.replace(b'"base_z_cm":0', b'"base_z_cm":1e999'),
                        positive.replace(b'"base_z_cm":0', b'"base_z_cm":1e-999'),
                        positive.replace(b'"base_z_cm":0', b'"base_z_cm":10000000000000001.9'),
                        b"\xef\xbb\xbf" + positive, b"[" * 129 + b"0" + b"]" * 129]
        for raw in bad_payloads:
            with self.subTest(raw=raw[:70]), self.assertRaises(builder.BuildRefusal):
                path.write_bytes(raw)
                builder.load_authority(path, walls(), "1" * 64)
        path.write_bytes(positive)
        builder.load_authority(path, walls(), "1" * 64)

    def test_missing_source_and_source_traversal_refused(self) -> None:
        path = self.write_authority()
        for value in ("missing.txt", "../analytical-plan.txt", "./analytical-plan.txt",
                      "analytical-plan.txt ", "C:relative.txt", "//server/share.txt", "NUL.txt"):
            changed = json.loads(path.read_bytes())
            changed["source_file"] = value
            path.write_bytes(builder.canonical_json(changed))
            with self.subTest(value=value), self.assertRaises(builder.BuildRefusal):
                builder.load_authority(path, walls(), "1" * 64)

    def test_relative_source_uses_only_process_cwd_no_authority_directory_fallback(self) -> None:
        source = self.root / "analytical-plan.txt"
        source.write_bytes(b"outside -Y\n")
        nested = self.root / "records"
        nested.mkdir()
        record = authority(source_hash=digest(source.read_bytes()))
        path = nested / "authority.json"
        path.write_bytes(builder.canonical_json(record))
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            _, hashes = builder.load_authority(path, walls(), "1" * 64)
            self.assertIn(str(source), hashes)
            os.chdir(nested)
            with self.assertRaisesRegex(builder.BuildRefusal, "does not exist"):
                builder.load_authority(path, walls(), "1" * 64)
        finally:
            os.chdir(previous)


class BoundaryTests(TempCase):
    def test_namespace_strict_ascii(self) -> None:
        for value in ("A", "A_0", "z" * 40):
            self.assertEqual(builder.validate_namespace(value), value)
        for value in ("", "1A", "_A", "A-B", "A B", "A\n", "А", "a" * 41, "a;delete objects"):
            with self.subTest(value=value), self.assertRaises(builder.BuildRefusal):
                builder.validate_namespace(value)

    def test_units_exact_type_scale_and_equal_factor_pairs(self) -> None:
        mm = builder.expected_units("millimeters", "1")
        cm = builder.expected_units("centimeters", "0.1")
        self.assertEqual(mm["units_per_cm"], cm["units_per_cm"])
        self.assertNotEqual(mm, cm)
        self.assertEqual(mm["cm_per_unit"], 0.1)
        for unit in ("MM", "Millimeters", "#millimeters", " millimeters", "millimeters ", "cm", "watts"):
            with self.subTest(unit=unit), self.assertRaises(builder.BuildRefusal):
                builder.expected_units(unit, "1")
        for scale in ("0", "-1", "NaN", "Infinity", "1e999", "1e-999", "+1", "01", " 1", "1 ",
                      "1;resetMaxFile()", "1.00000000000000001", True, None, 0, float("inf"), 10 ** 400):
            with self.subTest(scale=str(scale)[:50]), self.assertRaises(builder.BuildRefusal):
                builder.expected_units("millimeters", scale)

    def test_unknown_flags_abbreviations_duplicate_flags_no_force_or_draft(self) -> None:
        base = ["--in", "input", "--out", "output", "--namespace", "A",
                "--system-type", "millimeters", "--system-scale", "1", "--direction-authority", "a.json"]
        self.assertEqual(builder.parser().parse_args(base).namespace, "A")
        variants = [base + ["--force"], base + ["--allow-draft"], base + ["--draft"],
                    base + ["--namespace", "B"], base + ["--system-scale", "2"],
                    ["--direc" if value == "--direction-authority" else value for value in base]]
        for arguments in variants:
            with self.subTest(arguments=arguments), mock.patch("sys.stderr", new=io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    builder.parser().parse_args(arguments)
                self.assertEqual(raised.exception.code, 2)

    def test_output_exists_and_all_input_overlap_directions_refuse(self) -> None:
        project = self.root / "project"
        project.mkdir()
        existing = self.root / "existing"
        existing.mkdir()
        marker = existing / "sentinel"
        marker.write_bytes(b"preserve")
        for out in (existing, project / "run", project):
            with self.subTest(out=out), self.assertRaises(builder.BuildRefusal):
                builder.check_output_boundary(out, project)
        out = self.root / "new-run"
        self.assertEqual(builder.check_output_boundary(out, project), out)
        with self.assertRaises(builder.BuildRefusal):
            builder.check_output_boundary(out, project, [str(out / "source.json")])
        self.assertEqual(marker.read_bytes(), b"preserve")
        self.assertFalse(out.exists())

    def test_ambiguous_path_spellings_refuse(self) -> None:
        for suffix in ("x/../out", "./out", "out.", "out ", "foo:bar", "CON", "LPT1.txt"):
            with self.subTest(suffix=suffix), self.assertRaises(builder.BuildRefusal):
                builder.safe_path(str(self.root) + "/" + suffix, "test output", exists=False)

    def test_symlink_ancestor_and_hardlink_source_refuse_where_available(self) -> None:
        actual = self.root / "actual"
        actual.mkdir()
        link = self.root / "linked"
        try:
            link.symlink_to(actual, target_is_directory=True)
        except OSError:
            # Calibrated mocked reparse control below remains mandatory on hosts
            # without symlink creation permission; no symlink support is claimed.
            link = None
        if link is not None:
            with self.assertRaisesRegex(builder.BuildRefusal, "links/junctions"):
                builder.safe_path(link / "out", "test output", exists=False)
        source = self.root / "one.txt"
        source.write_bytes(b"raw")
        twin = self.root / "two.txt"
        try:
            os.link(source, twin)
        except OSError:
            return
        with self.assertRaisesRegex(builder.BuildRefusal, "hard-linked"):
            builder.safe_path(source, "source")

    def test_reparse_control_discriminates_regular_ancestor(self) -> None:
        actual = self.root / "ordinary"
        actual.mkdir()
        output = actual / "out"
        self.assertEqual(builder.safe_path(output, "output", exists=False), output)
        original = Path.lstat

        def reparse(path: Path):
            result = original(path)
            if path == actual:
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result

        with mock.patch.object(Path, "lstat", reparse):
            with self.assertRaisesRegex(builder.BuildRefusal, "reparse"):
                builder.safe_path(output, "output", exists=False)

    def test_observed_hash_drift_refuses_without_writing(self) -> None:
        source = self.root / "source.txt"
        source.write_bytes(b"raw\r\n")
        hashes = {str(source): digest(source.read_bytes())}
        builder.verify_hashes(hashes)
        source.write_bytes(b"raw\n")
        with self.assertRaisesRegex(builder.BuildRefusal, "drift"):
            builder.verify_hashes(hashes)
        self.assertEqual(source.read_bytes(), b"raw\n")

    def test_snapshot_binds_exact_raw_bytes_and_parsed_document(self) -> None:
        document = walls()
        wall_raw = json.dumps(document, indent=2).encode() + b"\n"
        dim_raw = b'{"project":"builder-test"}\n'
        wall_path = self.root / "walls.json"
        dimension_path = self.root / "dimensions.json"
        wall_path.write_bytes(wall_raw)
        dimension_path.write_bytes(dim_raw)
        snapshot = {"walls": document, "dimensions": {"project": "builder-test"},
                    "input_hashes": {"walls.json": digest(wall_raw), "dimensions.json": digest(dim_raw)},
                    "input_snapshots": {"walls.json": wall_raw, "dimensions.json": dim_raw},
                    "input_sources": {"walls": str(wall_path), "dimensions": str(dimension_path)}}
        hashes = builder.snapshot_hashes(snapshot)
        self.assertEqual(hashes[str(wall_path)], digest(wall_raw))
        self.assertNotEqual(hashes[str(wall_path)], digest(builder.canonical_json(document)))
        for mutation in ("bytes", "doc", "hash", "membership"):
            changed = copy.deepcopy(snapshot)
            if mutation == "bytes":
                changed["input_snapshots"]["walls.json"] += b" "
            elif mutation == "doc":
                changed["walls"]["project"] = "changed"
            elif mutation == "hash":
                changed["input_hashes"]["walls.json"] = "0" * 64
            else:
                changed["input_sources"].pop("walls")
            with self.subTest(mutation=mutation), self.assertRaises(builder.BuildRefusal):
                builder.snapshot_hashes(changed)

    def test_input_path_preflight_refuses_reparse_before_snapshot(self) -> None:
        project = self.root / "project"
        project.mkdir()
        source = project / "walls.json"
        source.write_bytes(b"{}\n")
        adapter = SimpleNamespace(INPUT_NAMES=frozenset({"walls"}))
        builder.check_input_paths(project, adapter)
        original = Path.lstat

        def reparse(path):
            result = original(path)
            if path == source:
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result

        with mock.patch.object(Path, "lstat", reparse):
            with self.assertRaisesRegex(builder.BuildRefusal, "reparse"):
                builder.check_input_paths(project, adapter)


class ArtifactTests(TempCase):
    @staticmethod
    def fake_runtime() -> SimpleNamespace:
        def generate_script(plan, identity, namespace, expected_units):
            # Test seam only: not executable modeling code or a produced fixture.
            return "-- NONEXECUTABLE COORDINATOR TEST SEAM\n-- identity=" + identity + "\n-- config=" + json.dumps(
                [namespace, expected_units], sort_keys=True) + "\n"
        return SimpleNamespace(generate_script=generate_script)

    def options(self) -> dict:
        return {"walls": walls(), "plan": {"predictions": {"grid_vertices": 4, "grid_polygons": 1}},
                "authority": authority(), "input_hashes": {"/source/walls.json": "1" * 64},
                "generator_hashes": {"/code/runtime.py": "3" * 64}, "namespace": "CoordinatorTest",
                "units": builder.expected_units("millimeters", "1"), "runtime": self.fake_runtime()}

    def test_deterministic_manifest_script_hash_identity_not_circular(self) -> None:
        options = self.options()
        first = builder.make_artifacts(**options)
        second = builder.make_artifacts(**options)
        self.assertEqual(first, second)
        manifest = json.loads(first["wall_surface.json"])
        self.assertEqual(set(first), {"wall_surface.json", "wall_surface.ms"})
        self.assertEqual(manifest["script"]["sha256"], digest(first["wall_surface.ms"]))
        self.assertIn(manifest["identity"].encode(), first["wall_surface.ms"])
        self.assertNotIn(digest(first["wall_surface.json"]).encode(), first["wall_surface.ms"])
        self.assertEqual(manifest["owner"]["id"], manifest["identity"])
        self.assertEqual(manifest["status"], "produced_offline_unverified")
        self.assertEqual(manifest["predictions"]["status"], "offline_predictions_not_live_measurements")
        self.assertEqual(manifest["declared_budgets"]["W1"], walls()["wall_runs"][0]["topology_budget"])
        self.assertNotIn("assembly", manifest)
        self.assertFalse(manifest["direction_evidence"]["automated_semantic_source_proof"])
        self.assertEqual(manifest["acceptance"]["live_execution"], "NOT_RUN")

    def test_identity_changes_for_each_configuration_and_source_hash(self) -> None:
        base = self.options()
        original = json.loads(builder.make_artifacts(**base)["wall_surface.json"])["identity"]
        for key, value in (("input_hashes", {"/source/walls.json": "4" * 64}),
                           ("generator_hashes", {"/code/runtime.py": "4" * 64}),
                           ("namespace", "Different"),
                           ("units", builder.expected_units("centimeters", "0.1")),
                           ("authority", {**authority(), "source_location": "another locator"})):
            changed = {**base, key: value}
            manifest = json.loads(builder.make_artifacts(**changed)["wall_surface.json"])
            with self.subTest(key=key):
                self.assertNotEqual(manifest["identity"], original)

    def test_geometric_normal_is_not_skew_declared_vector(self) -> None:
        options = self.options()
        options["walls"]["wall_runs"][0]["outward"] = [0.0000001, -1]
        manifest = json.loads(builder.make_artifacts(**options)["wall_surface.json"])
        self.assertEqual(manifest["direction_evidence"]["declared_outward"], [0.0000001, -1])
        self.assertEqual(manifest["direction_evidence"]["geometric_outward"], [0.0, -1.0])

    def test_incomplete_metadata_nonfinite_prediction_and_script_without_identity_refuse(self) -> None:
        for plan in ({}, {"predictions": {}}, {"predictions": {"a": float("nan")}},
                     {"predictions": {"a": 1}, "node_names": ["foreign"]}):
            with self.subTest(plan=plan), self.assertRaises(builder.BuildRefusal):
                builder.make_artifacts(**{**self.options(), "plan": plan})
        runtime = SimpleNamespace(generate_script=lambda *args: "-- missing identity\n")
        with self.assertRaises(builder.BuildRefusal):
            builder.make_artifacts(**{**self.options(), "runtime": runtime})

    def test_pair_two_mib_limit_stricter_than_publication_helper(self) -> None:
        runtime = SimpleNamespace(generate_script=lambda plan, identity, *args:
                                  "-- " + identity + "\n" + " " * builder.MAX_ARTIFACT_BYTES + "\n")
        with self.assertRaisesRegex(builder.BuildRefusal, "artifact pair exceeds 2 MiB"):
            builder.make_artifacts(**{**self.options(), "runtime": runtime})

    def test_existing_output_refused_before_any_dependency_load(self) -> None:
        project = self.root / "project"
        output = self.root / "output"
        project.mkdir()
        output.mkdir()
        sentinel = output / "sentinel"
        sentinel.write_bytes(b"preserve")
        with mock.patch.object(builder, "_module", side_effect=AssertionError("must not import")):
            with self.assertRaises(builder.BuildRefusal):
                builder.build(project, output, "A", "millimeters", "1", self.root / "authority.json")
        self.assertEqual(sentinel.read_bytes(), b"preserve")

    def test_coordinator_fake_seams_validate_drift_then_publish_order(self) -> None:
        project = self.root / "project"
        project.mkdir()
        wall_raw = builder.canonical_json(walls())
        dim_raw = b'{"project":"builder-test"}\n'
        (project / "walls.json").write_bytes(wall_raw)
        (project / "dimensions.json").write_bytes(dim_raw)
        record_path = self.write_authority(authority(digest(wall_raw)))
        snapshot = {"walls": walls(), "dimensions": {"project": "builder-test"},
                    "input_hashes": {"walls.json": digest(wall_raw), "dimensions.json": digest(dim_raw)},
                    "input_sources": {"walls": str(project / "walls.json"), "dimensions": str(project / "dimensions.json")},
                    "input_snapshots": {"walls.json": wall_raw, "dimensions.json": dim_raw}}
        events = []

        def load_inputs(path, **kwargs):
            self.assertEqual(kwargs, {"namespace": "A", "system_type": "millimeters", "system_scale": 1.0})
            events.append("load")
            return snapshot

        def verify(inputs):
            events.append("verify")

        def publish(path, artifacts):
            self.assertEqual(events, ["load", "plan", "verify"])
            events.append("publish-fake-seam")
            path.mkdir()
            for name, raw in artifacts.items():
                (path / name).write_bytes(raw)
            return {name: digest(raw) for name, raw in artifacts.items()}

        def plan(*args):
            events.append("plan")
            return {"predictions": {"grid_vertices": 4, "grid_polygons": 1}}

        modules = {"wall_surface_inputs": SimpleNamespace(load_inputs=load_inputs, verify_inputs_unchanged=verify),
                   "wall_surface_runtime": SimpleNamespace(build_plan=plan, **vars(self.fake_runtime())),
                   "wall_surface_publish": SimpleNamespace(publish_new_directory=publish)}
        output = self.root / "output"
        with mock.patch.object(builder, "_module", side_effect=modules.__getitem__):
            hashes = builder.build(project, output, "A", "millimeters", "1", record_path)
        self.assertEqual(set(hashes), {"wall_surface.json", "wall_surface.ms"})
        manifest = json.loads((output / "wall_surface.json").read_bytes())
        self.assertIn(str(record_path), manifest["input_hashes"])
        self.assertIn(str(self.root / "analytical-plan.txt"), manifest["input_hashes"])
        self.assertIn(str(ROOT / "scripts" / "build_wall_surface.py"), manifest["generator_hashes"])
        self.assertIn(str(builder.CONTRACT_PATH), manifest["generator_hashes"])
        self.assertEqual(events[-1], "publish-fake-seam")

    def test_late_source_drift_and_adapter_false_refuse_before_publication(self) -> None:
        for change in ("source", "adapter"):
            with self.subTest(change=change):
                area = self.root / change
                area.mkdir()
                project = area / "project"
                project.mkdir()
                document = walls()
                wall_raw, dim_raw = builder.canonical_json(document), b'{"project":"builder-test"}\n'
                (project / "walls.json").write_bytes(wall_raw)
                (project / "dimensions.json").write_bytes(dim_raw)
                source = area / "analytical-plan.txt"
                source.write_bytes(b"inner Y=0; outside -Y\n")
                record = authority(digest(wall_raw), digest(source.read_bytes()))
                record["source_file"] = str(source)
                record_path = area / "authority.json"
                record_path.write_bytes(builder.canonical_json(record))
                snapshot = {"walls": document, "dimensions": {"project": "builder-test"},
                            "input_hashes": {"walls.json": digest(wall_raw), "dimensions.json": digest(dim_raw)},
                            "input_sources": {"walls": str(project / "walls.json"), "dimensions": str(project / "dimensions.json")},
                            "input_snapshots": {"walls.json": wall_raw, "dimensions.json": dim_raw}}

                def plan(*args):
                    if change == "source":
                        source.write_bytes(b"outside +Y\n")
                    return {"predictions": {"grid_vertices": 4}}

                publisher = mock.Mock()
                modules = {
                    "wall_surface_inputs": SimpleNamespace(load_inputs=lambda *a, **k: snapshot,
                        verify_inputs_unchanged=lambda *a: False if change == "adapter" else None),
                    "wall_surface_runtime": SimpleNamespace(build_plan=plan, **vars(self.fake_runtime())),
                    "wall_surface_publish": publisher,
                }
                with mock.patch.object(builder, "_module", side_effect=modules.__getitem__):
                    with self.assertRaisesRegex(builder.BuildRefusal, "drift"):
                        builder.build(project, area / "out", "A", "millimeters", "1", record_path)
                publisher.publish_new_directory.assert_not_called()
                self.assertFalse((area / "out").exists())

    def test_generator_contract_hash_drift_discriminated_on_temp_source(self) -> None:
        helper = self.root / "generator.py"
        helper.write_bytes(b"# source version one\n")
        lock = {str(helper): digest(helper.read_bytes())}
        builder.verify_hashes(lock)
        helper.write_bytes(b"# source version two\n")
        with self.assertRaisesRegex(builder.BuildRefusal, "input/code drift"):
            builder.verify_hashes(lock)

    def test_actual_runtime_artifact_integration_pure_not_full_fixture(self) -> None:
        import wall_surface_runtime as runtime
        document = walls()
        document["units"] = {"length": "cm", "angle": "deg"}
        dimensions = {"spec": "dimensions", "status": "locked", "project": "builder-test",
                      "units": {"length": "cm", "angle": "deg"},
                      "facades": [{"id": "F1", "start_corner_cm": [0, 0],
                                   "end_corner_cm": [500, 0], "length_cm": 500}]}
        plan = runtime.build_plan(document, dimensions)
        options = self.options()
        options.update(walls=document, plan=plan, runtime=runtime)
        artifacts = builder.make_artifacts(**options)
        self.assertEqual(artifacts, builder.make_artifacts(**options))
        manifest = json.loads(artifacts["wall_surface.json"])
        script = artifacts["wall_surface.ms"].decode()
        self.assertEqual(manifest["subset"], plan["subset"])
        self.assertEqual(manifest["node_names"], ["CoordinatorTest__wall"])
        self.assertIn('"CoordinatorTest__wall"', script)
        self.assertIn(manifest["identity"], script)
        self.assertEqual(manifest["script"]["sha256"], digest(artifacts["wall_surface.ms"]))
        self.assertNotIn("@@", script)
        if os.name == "nt":
            import wall_surface_publish as publisher
            output = self.root / "actual-published-pair"
            expected = {name: digest(raw) for name, raw in artifacts.items()}
            self.assertEqual(publisher.publish_new_directory(output, artifacts), expected)
            self.assertEqual({path.name: digest(path.read_bytes()) for path in output.iterdir()}, expected)
            with self.assertRaises(publisher.PublicationError):
                publisher.publish_new_directory(output, artifacts)
            self.assertEqual({path.name: digest(path.read_bytes()) for path in output.iterdir()}, expected)

    def test_authentic_f01_snapshot_emit_publish_deterministic_new_dirs_only(self) -> None:
        self.assertEqual(os.name, "nt", "This integration requires the real Windows no-replace publisher")
        source = ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e"
        self.assertTrue((source / "project" / "walls.json").is_file(), "authentic F01 input required")
        source_files = [*sorted((source / "project").glob("*.json")), source / "direction-authority.json",
                        ROOT / "Audit" / "AGENT_PLAN_poly_surface_shell.md"]
        before = {str(path): digest(path.read_bytes()) for path in source_files}
        project = self.root / "authentic-project"
        shutil.copytree(source / "project", project)
        authority_path = self.root / "authentic-authority.json"
        shutil.copyfile(source / "direction-authority.json", authority_path)
        previous = Path.cwd()
        try:
            os.chdir(ROOT)  # explicit documented source_file CWD convention
            first = self.root / "authentic-run-one"
            second = self.root / "authentic-run-two"
            hashes = builder.build(project, first, "F01BuilderTest", "millimeters", "1", authority_path)
            self.assertEqual(hashes, builder.build(project, second, "F01BuilderTest", "millimeters", "1", authority_path))
            with self.assertRaisesRegex(builder.BuildRefusal, "must not exist"):
                builder.build(project, first, "F01BuilderTest", "millimeters", "1", authority_path)
            self.assertEqual({path.name: digest(path.read_bytes()) for path in first.iterdir()}, hashes)
            manifest = json.loads((first / "wall_surface.json").read_bytes())
            predictions = manifest["predictions"]["values"]
            for key, expected in (("grid_vertices", 24), ("grid_polygons", 15),
                                  ("base_active_polygons", 12), ("evaluated_triangles", 96),
                                  ("base_area_cm2", 87000), ("volume_cm3", 2610000)):
                self.assertEqual(predictions[key], expected)
            self.assertEqual(manifest["direction_evidence"]["source_file_token"], "Audit/AGENT_PLAN_poly_surface_shell.md")
            self.assertEqual(manifest["direction_evidence"]["resolved_source_file"],
                             str(ROOT / "Audit" / "AGENT_PLAN_poly_surface_shell.md"))
            self.assertEqual(manifest["status"], "produced_offline_unverified")
            self.assertGreaterEqual(len(manifest["generator_hashes"]), 8)
            cli_output = self.root / "authentic-cli-run"
            process = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "build_wall_surface.py"),
                "--in", str(project), "--out", str(cli_output), "--namespace", "F01BuilderTest",
                "--system-type", "millimeters", "--system-scale", "1",
                "--direction-authority", str(authority_path)], cwd=ROOT, capture_output=True, text=True,
                timeout=30)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("produced_offline_unverified", process.stdout)
            self.assertEqual({path.name: digest(path.read_bytes()) for path in cli_output.iterdir()}, hashes)
        finally:
            os.chdir(previous)
        self.assertEqual({str(path): digest(path.read_bytes()) for path in source_files}, before)


if __name__ == "__main__":
    unittest.main()
