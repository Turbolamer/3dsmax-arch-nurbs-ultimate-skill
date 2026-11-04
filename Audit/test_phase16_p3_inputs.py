#!/usr/bin/env python3
"""Offline P3.1 input adapter tests; no generated assembly/poly evidence.

Only disposable inputs are authored. The existing example contour's collapsed
derived declaration has no accepted formula oracle, so the positive explicitly
declares its test contour given in a new temporary brief, never edits the seed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import validate_specs as validator
from scripts import wall_surface_inputs as inputs
from test_phase16_p2_isolated import draft_assembly, walls_declaration, write_json

EXAMPLES = ROOT / "examples"
PROTECTED = [ROOT / "scripts" / name for name in
             ("validate_specs.py", "place_components.py", "init_project.py", "wall_cell_coverage.py")]
PROTECTED += [path for path in EXAMPLES.rglob("*") if path.is_file()]
F01 = ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e" / "project"
PROTECTED += [path for path in F01.glob("*.json")]
HASHES = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in PROTECTED}


def tearDownModule():
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in PROTECTED}
    changed = [str(path.relative_to(ROOT)) for path in PROTECTED if after[path] != HASHES[path]]
    print("ACCEPTED_SOURCE_AND_SEED_DRIFT " + repr(changed), flush=True)
    if changed:
        raise AssertionError("accepted source/seed changed during input adapter tests")


class AdapterTests(unittest.TestCase):
    def setUp(self):
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        owner = tempfile.TemporaryDirectory(prefix="p3-input-tests-", dir=parent)
        self.addCleanup(owner.cleanup)
        self.root = Path(owner.name) / "project"
        self.root.mkdir()
        self.docs = {path.stem: validator.strict_json_loads(path.read_text(encoding="utf-8"))
                     for path in EXAMPLES.glob("*.json")
                     if path.stem in inputs.INPUT_NAMES and path.stem != "assembly"}
        dim = self.docs["dimensions"]
        dim["origins"]["facades[0]"] = {"origin": "given"}
        dim["source"]["reference"] += "; disposable P3 test brief explicitly gives F-S contour"
        walls = walls_declaration(dim)
        walls["blocks"] = walls["blocks"][:1]
        walls["wall_runs"] = walls["wall_runs"][:1]
        walls["upper_returns"] = []
        walls["origin_inputs"] = ["facades[0]"]
        walls["origins"] = {path: {"origin": "given"} for path in
                            ("wall_technique", "reference_face", "numeric_epsilon_cm",
                             "numeric_unit_epsilon", "blocks[0]", "wall_runs[0]",
                             "openings[0]", "openings[1]", "upper_returns")}
        # Shared exact v stations keep the bounded grid to 24 vertices/15 quads.
        walls["openings"][1]["sill_cm"] = walls["openings"][0]["sill_cm"]
        walls["openings"][1]["head_cm"] = walls["openings"][0]["head_cm"]
        self.docs["walls"] = walls
        self.flush()

    def flush(self):
        for name, doc in self.docs.items():
            write_json(self.root / (name + ".json"), doc)

    def load(self, **kwargs):
        parameters = {"namespace": "InputTest", "system_type": "millimeters", "system_scale": 1}
        parameters.update(kwargs)
        return inputs.load_inputs(self.root, **parameters)

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def refusal(self, text=""):
        before = self.snapshot()
        with self.assertRaises(inputs.InputRefusal) as caught:
            self.load()
        if text:
            self.assertIn(text, str(caught.exception))
        self.assertEqual(before, self.snapshot(), "refusal must not write source or outputs")
        return str(caught.exception)

    def test_positive_snapshots_units_and_shared_exact_stations(self):
        before = self.snapshot()
        result = self.load()
        self.assertEqual(result["length_cm"], 1800)
        self.assertEqual(result["geometric_outward"], [0.0, -1.0])
        self.assertEqual(result["expected_units"]["scene_units_per_cm"], 10)
        self.assertEqual(result["v_stations_cm"], [0.0, 90.0, 270.0, 420.0])
        self.assertEqual(len(result["u_stations_cm"]) * len(result["v_stations_cm"]), 24)
        self.assertEqual(result["input_snapshots"], before)
        for name, raw in before.items():
            self.assertEqual(result["input_hashes"][name], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["input_sources"]["walls"], str(self.root / "walls.json"))
        self.assertIsNone(inputs.verify_inputs_unchanged(result))
        self.assertIsNone(result["verify_inputs_unchanged"]())
        self.assertEqual(before, self.snapshot())

    def test_authentic_f01_positive_no_downstream_outputs_invented(self):
        project = self.root / "authentic-f01-copy"
        shutil.copytree(F01, project)
        before = {path.name: path.read_bytes() for path in project.glob("*.json")}
        result = inputs.load_inputs(project, namespace="F01", system_type="millimeters", system_scale=1)
        self.assertEqual(result["u_stations_cm"], [0, 50, 150, 230, 330, 400])
        self.assertEqual(result["v_stations_cm"], [0, 90, 210, 300])
        self.assertEqual(result["input_snapshots"], before)
        self.assertEqual(set(before), {"walls.json", "dimensions.json", "assumptions.json", "conflicts_resolved.json"})
        self.assertEqual(len(result["allowed_skips"]), 23)
        excluded = [f for f in result["validation_findings"] if f["severity"] == "FAIL"]
        self.assertEqual({f["location"] for f in excluded},
                         {"massing.json", "nurbs.json", "facade_grids.json", "components_registry.json"})
        self.assertTrue(all(f["rule"] == "G-1" for f in excluded))
        self.assertEqual(before, {path.name: path.read_bytes() for path in project.glob("*.json")})

    def test_authentic_f01_missing_inventory_not_waived_when_reached(self):
        project = self.root / "authentic-f01-copy"
        shutil.copytree(F01, project)
        walls = validator.strict_json_loads((project / "walls.json").read_text(encoding="utf-8"))
        walls["origin_inputs"].append("sections[0].points_cm")
        write_json(project / "walls.json", walls)
        with self.assertRaisesRegex(inputs.InputRefusal, "origin_inputs"):
            inputs.load_inputs(project, namespace="F01", system_type="millimeters", system_scale=1)

    def test_private_snapshot_not_second_original_parse(self):
        original = validator.load_session
        def instrument(paths, root, report, *args, **kwargs):
            self.assertNotEqual(root, self.root)
            self.assertTrue(all(path.parent == root for path in paths))
            self.assertEqual((root / "walls.json").read_bytes(), (self.root / "walls.json").read_bytes())
            # Mutation after snapshot must not become a second parsed source.
            (self.root / "walls.json").write_bytes(b'{"bad":true}\n')
            return original(paths, root, report, *args, **kwargs)
        with patch.object(validator, "load_session", side_effect=instrument):
            with self.assertRaisesRegex(inputs.InputRefusal, "input changed since snapshot"):
                self.load()

    def test_publication_drift_hash_and_membership(self):
        result = self.load()
        path = self.root / "dimensions.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(inputs.InputRefusal, "input changed"):
            result["verify_inputs_unchanged"]()
        self.flush()
        result = self.load()
        write_json(self.root / "assembly.json", draft_assembly(self.docs["walls"]))
        with self.assertRaisesRegex(inputs.InputRefusal, "membership/path changed"):
            inputs.verify_inputs_unchanged(result)

    def test_duplicate_json_tokens_each_consumed_kind(self):
        for name in ("walls", "dimensions", "assumptions", "nurbs"):
            with self.subTest(name=name):
                self.load()  # individually calibrated positive
                path = self.root / (name + ".json")
                raw = path.read_bytes()
                path.write_bytes(raw.replace(b'"project":', b'"project":"duplicate", "project":', 1))
                self.refusal("duplicate JSON object key")
                path.write_bytes(raw)

    def test_json_loss_overflow_underflow_and_deep_nesting(self):
        path = self.root / "walls.json"
        raw = path.read_bytes()
        for token in (b"NaN", b"Infinity", b"1e999", b"1e-999", b"9007199254740992",
                      b"10000000000000001.9", b"[" * 129 + b"0" + b"]" * 129):
            with self.subTest(token=token[:25]):
                self.load()
                path.write_bytes(raw.replace(b'"numeric_epsilon_cm": 0.001', b'"numeric_epsilon_cm": ' + token))
                self.refusal("strict input parse/hygiene")
                path.write_bytes(raw)

    def test_json_hygiene(self):
        path = self.root / "walls.json"
        raw = path.read_bytes()
        for changed in (b"\xef\xbb\xbf" + raw, raw.replace(b"\n", b"\r\n"), raw[:-1], raw + b"\n"):
            with self.subTest(prefix=changed[:10]):
                self.load()
                path.write_bytes(changed)
                self.refusal("strict input parse/hygiene")
                path.write_bytes(raw)

    def test_draft_and_superseded_sources(self):
        for name in ("walls", "dimensions", "assumptions", "massing"):
            for status in ("draft", "superseded"):
                with self.subTest(name=name, status=status):
                    self.load()
                    self.docs[name]["status"] = status
                    self.flush()
                    self.refusal("must be locked")
                    self.docs[name]["status"] = "locked"
                    self.flush()

    def test_selector_and_outer_reference(self):
        for field, value in (("wall_technique", "legacy_cells_v1"),
                             ("wall_technique", "POLY_surface_shell_v1"),
                             ("reference_face", "outer")):
            with self.subTest(field=field, value=value):
                self.load()
                old = self.docs["walls"][field]
                self.docs["walls"][field] = value
                self.flush()
                self.refusal("required" if field == "wall_technique" else "inner-reference")
                self.docs["walls"][field] = old
                self.flush()

    def test_closed_wall_objects_unknown_fields(self):
        wall = self.docs["walls"]
        for target in (wall, wall["source"], wall["blocks"][0], wall["wall_runs"][0],
                       wall["wall_runs"][0]["topology_budget"], wall["openings"][0],
                       wall["origins"]["wall_runs[0]"]):
            with self.subTest(keys=list(target)):
                self.load()
                target["unlisted"] = 1
                self.flush()
                self.refusal("input validator refused")
                del target["unlisted"]
                self.flush()

    def test_one_run_one_block_no_partial_project(self):
        wall = self.docs["walls"]
        for table in ("blocks", "wall_runs"):
            with self.subTest(table=table):
                self.load()
                second = copy.deepcopy(wall[table][0])
                second["id"] += "-SECOND"
                wall[table].append(second)
                wall["origins"][table + "[1]"] = {"origin": "given"}
                self.flush()
                self.refusal("exactly one block")
                wall[table].pop()
                wall["origins"].pop(table + "[1]")
                self.flush()

    def test_opening_bounds_touching_overlap_and_bad_link(self):
        wall = self.docs["walls"]
        original = copy.deepcopy(wall["openings"])
        changes = [(0, "u_range_cm", [0, 315]), (0, "u_range_cm", [135, 1800]),
                   (0, "head_cm", 420), (0, "sill_cm", -1),
                   (1, "u_range_cm", [315, 500]), (1, "u_range_cm", [314, 500]),
                   (0, "wall_run_id", "MISSING")]
        for index, field, value in changes:
            with self.subTest(index=index, field=field, value=value):
                self.load()
                wall["openings"][index][field] = value
                self.flush()
                self.refusal()
                wall["openings"] = copy.deepcopy(original)
                self.flush()

    def test_required_block_link_and_return_refused(self):
        self.load()
        wall = self.docs["walls"]
        wall["wall_runs"][0]["block_id"] = "MISSING"
        self.flush()
        self.refusal("block_id")
        wall["wall_runs"][0]["block_id"] = wall["blocks"][0]["id"]
        self.flush()
        self.load()
        return_run = copy.deepcopy(wall["wall_runs"][0])
        return_run["id"] = "RETURN"
        return_run["adjacent_run_ids"] = [wall["wall_runs"][0]["id"], "MISSING"]
        wall["upper_returns"] = [return_run]
        wall["origins"].pop("upper_returns")
        wall["origins"]["upper_returns[0]"] = {"origin": "given"}
        self.flush()
        self.refusal()

    def test_precision_thickness_and_planning_count_ceilings(self):
        self.load()
        wall = self.docs["walls"]
        wall["wall_runs"][0]["thickness_cm"] = 0.0001
        self.flush()
        self.refusal("thickness is below")
        wall["wall_runs"][0]["thickness_cm"] = 30
        original = copy.deepcopy(wall["openings"])
        for i in range(2, 7):
            op = copy.deepcopy(original[0])
            op["id"] = "EXTRA-" + str(i)
            op["u_range_cm"] = [800 + i * 100, 850 + i * 100]
            wall["openings"].append(op)
            wall["origins"][f"openings[{i}]"] = {"origin": "given"}
        self.flush()
        self.refusal("at most 6 openings")

    def test_used_upstream_malformed_g1_not_inventory_waived(self):
        self.load()
        self.docs["walls"]["origin_inputs"].append("sections[0].points_cm")
        self.docs["nurbs"].pop("sections")
        self.flush()
        detail = self.refusal("input validator refused")
        self.assertIn("G-1 nurbs.json", detail)

    def test_distinct_near_u_v_stations_refuse_without_snap(self):
        wall = self.docs["walls"]
        for field, value in (("u_range_cm", [315.0005, 775]), ("sill_cm", 90.0005)):
            with self.subTest(field=field):
                self.load()
                op = wall["openings"][1]
                original = copy.deepcopy(op[field])
                op[field] = value
                self.flush()
                self.refusal("closer than numeric_epsilon_cm")
                op[field] = original
                self.flush()

    def test_no_openings_are_supported_as_input(self):
        wall = self.docs["walls"]
        wall["openings"] = []
        wall["origins"].pop("openings[0]")
        wall["origins"].pop("openings[1]")
        wall["origins"]["openings"] = {"origin": "given"}
        self.flush()
        result = self.load()
        self.assertEqual(result["openings"], [])
        self.assertEqual(result["u_stations_cm"], [0, 1800])

    def test_contour_selector_strict(self):
        run = self.docs["walls"]["wall_runs"][0]
        for selector in ("dimensions:facades:F-S", "dimensions.json:facades:F-S ",
                         "massing.json:elements:WALL-01", "dimensions.json:facades:MISSING"):
            with self.subTest(selector=selector):
                self.load()
                run["contour_ref"] = selector
                self.flush()
                self.refusal("contour_ref")
                run["contour_ref"] = "dimensions.json:facades:F-S"
                self.flush()

    def test_provenance_missing_unrelated_and_cycles(self):
        wall = self.docs["walls"]
        self.load()
        del wall["origins"]["openings[0]"]
        self.flush()
        self.refusal("origins")
        wall["origins"]["openings[0]"] = {"origin": "given"}
        wall["origin_inputs"] = ["NO_SUCH_FIELD"]
        self.flush()
        self.refusal("origin_inputs")
        wall["origin_inputs"] = ["facades[0]"]
        self.flush()
        self.load()
        dim = self.docs["dimensions"]
        dim["origins"]["facades[0]"] = {"origin": "derived", "derives_from": ["facades[0]"]}
        self.flush()
        self.refusal("cyclic transitive provenance")

    def test_ledger_value_and_transitive_cross_reference_failure(self):
        self.load()
        item = self.docs["assumptions"]["assumptions"][0]
        item["value"] += 1
        self.flush()
        self.refusal("G-12")
        item["value"] -= 1
        self.flush()
        self.load()
        self.docs["assumptions"]["cross_references"]["conflict_sourced_paths"][0]["conflict_ref"] = "C-999"
        self.flush()
        self.refusal("G-31")

    def test_unknown_required_wall_and_upstream_formula_refused(self):
        self.load()
        dim = self.docs["dimensions"]
        dim["origins"]["facades[0]"] = {"origin": "derived", "derives_from": ["site.footprint_cm"]}
        self.flush()
        self.refusal("required derived formula unavailable")
        dim["origins"]["facades[0]"] = {"origin": "given"}
        self.flush()
        self.load()
        wall = self.docs["walls"]
        wall["origins"]["wall_runs[0]"] = {"origin": "derived", "derives_from": ["facades[0]"]}
        self.flush()
        self.refusal()

    def test_known_required_formula_positive_and_wrong_recompute(self):
        self.docs["walls"]["origin_inputs"].append("building.total_height_cm")
        self.flush()
        self.load()
        self.docs["dimensions"]["building"]["total_height_cm"] += 10
        self.flush()
        self.refusal("G-32")

    def test_future_outputs_not_required_contradictory_assembly_refused(self):
        self.load()
        assembly = validator.strict_json_loads((EXAMPLES / "assembly.json").read_text(encoding="utf-8"))
        write_json(self.root / "assembly.json", assembly)  # authentic legacy output is contradictory
        self.refusal("input validator refused")

    def test_empty_draft_assembly_accepted_not_output_proof(self):
        self.load()
        write_json(self.root / "assembly.json", draft_assembly(self.docs["walls"]))
        result = self.load()
        self.assertTrue(any(f["rule"] == "G-92" for f in result["allowed_skips"]))

    def test_namespace_units_and_equal_factor_pair_kept_explicit(self):
        for kwargs in ({"namespace": "9bad"}, {"namespace": "A;delete"},
                       {"namespace": "Русский"}, {"namespace": "A" * 41},
                       {"system_type": "#millimeters"}, {"system_type": " millimeters"},
                       {"system_scale": True}, {"system_scale": 0},
                       {"system_scale": float("inf")}, {"system_scale": 1e308}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(inputs.InputRefusal):
                    self.load(**kwargs)
        a = self.load()
        b = self.load(system_type="centimeters", system_scale=0.1)
        self.assertEqual(a["expected_units"]["scene_units_per_cm"], b["expected_units"]["scene_units_per_cm"])
        self.assertNotEqual(a["expected_units"], b["expected_units"])

    def test_bounded_json_sizes(self):
        path = self.root / "walls.json"
        raw = path.read_bytes()
        path.write_bytes(b" " * (inputs.MAX_JSON_BYTES + 1))
        self.refusal("exceeds 2 MiB")
        path.write_bytes(raw)
        self.load()
        with patch.object(inputs, "MAX_SOURCE_BYTES", 1):
            self.refusal("exceeds 16 MiB")

    def test_duplicate_parent_pipeline_input_refused(self):
        self.load()
        (self.root / "pipeline").mkdir()
        (self.root / "pipeline" / "walls.json").write_bytes((self.root / "walls.json").read_bytes())
        self.refusal("ambiguous duplicate walls.json")

    def test_numeric_max_precision_refusal(self):
        self.load()
        # No token precision failure here: unit scaling alone exceeds Float32.
        with self.assertRaisesRegex(inputs.InputRefusal, "Float32"):
            self.load(system_scale=1e-39)

    def test_unapproved_required_skip_refused(self):
        self.load()
        original = validator.run_checks
        def inject(session, report):
            original(session, report)
            report.skip("G-86", "dimensions.json", "required analytical target unavailable")
        with patch.object(validator, "run_checks", side_effect=inject):
            self.refusal("unverified input gate: G-86")

    def test_validator_globals_restored(self):
        original = validator.session_build_gate, validator.session_allow_draft
        self.load()
        self.assertEqual(original, (validator.session_build_gate, validator.session_allow_draft))
        self.docs["walls"]["openings"][0]["head_cm"] = 900
        self.flush()
        self.refusal()
        self.assertEqual(original, (validator.session_build_gate, validator.session_allow_draft))


class ProjectArtifactPresenceTests(unittest.TestCase):
    """Real F01 copies, actual public builder, never execute artifact MAXScript."""

    def setUp(self):
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        owner = tempfile.TemporaryDirectory(prefix="p3-artifact-refusal-", dir=parent)
        self.addCleanup(owner.cleanup)
        self.root = Path(owner.name)
        self.project = self.root / "project"
        shutil.copytree(F01, self.project)
        self.authority = self.root / "direction-authority.json"
        self.authority.write_bytes((F01.parent / "direction-authority.json").read_bytes())
        (self.root / "foreign-sentinel.bin").write_bytes(b"FOREIGN\x00preserve\xff")
        self.payloads = {
            "wall_surface.json": b'{"schema_version":"bogus","project":"FOREIGN","route":"legacy_cells_v1"}\n',
            "wall_surface.ms": b"-- Contradictory sentinel ONLY; NEVER EXECUTE\nresetMaxFile #noPrompt\n",
        }

    def capture(self):
        result = {}
        for path in sorted(self.root.rglob("*")):
            key = path.relative_to(self.root).as_posix()
            if path.is_symlink():
                result[key] = ("link", os.readlink(path))
            elif path.is_dir():
                result[key] = ("directory",)
            else:
                result[key] = ("file", path.read_bytes())
        return result

    def load(self, project=None):
        return inputs.load_inputs(project or self.project, namespace="ArtifactTest",
                                  system_type="millimeters", system_scale=1)

    def build(self, out):
        from scripts import build_wall_surface as builder
        return builder.build(self.project, out, "ArtifactTest", "millimeters", 1,
                             self.authority)

    def test_clean_actual_public_build_to_disjoint_run_still_succeeds(self):
        original = self.capture()
        result = self.load()
        self.assertEqual(len(result["project_artifact_presence"]), 4)
        self.assertFalse(any(result["project_artifact_presence"].values()))
        out = self.root / "separate-new-run"
        hashes = self.build(out)
        self.assertEqual(set(hashes), set(inputs.PROJECT_ARTIFACT_NAMES))
        for name, digest in hashes.items():
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)
        self.assertIsNone(inputs.verify_inputs_unchanged(result))
        after = self.capture()
        self.assertEqual(original, {key: value for key, value in after.items()
                                    if key != out.name and not key.startswith(out.name + "/")})

    def test_existing_json_ms_each_or_pair_refuse_before_private_staging(self):
        for names in (("wall_surface.json",), ("wall_surface.ms",), inputs.PROJECT_ARTIFACT_NAMES):
            with self.subTest(names=names):
                self.load()  # clean admission before each isolated injection
                for name in names:
                    (self.project / name).write_bytes(self.payloads[name])
                before = self.capture()
                with patch.object(inputs.tempfile, "TemporaryDirectory") as stage:
                    with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
                        self.load()
                    stage.assert_not_called()
                self.assertEqual(before, self.capture())
                for name in names:
                    (self.project / name).unlink()  # only this test's exact injections

    def test_existing_actual_public_builder_refuses_before_output_staging(self):
        from scripts import wall_surface_publish as publisher
        for names in (("wall_surface.json",), ("wall_surface.ms",), inputs.PROJECT_ARTIFACT_NAMES):
            with self.subTest(names=names):
                self.load()
                for name in names:
                    (self.project / name).write_bytes(self.payloads[name])
                out = self.root / "refused-new-run"
                before = self.capture()
                with patch.object(publisher, "publish_new_directory") as publish:
                    with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
                        self.build(out)
                    publish.assert_not_called()
                self.assertFalse(out.exists())
                self.assertEqual(before, self.capture())
                for name in names:
                    (self.project / name).unlink()

    def test_parent_pipeline_boundary_files_dirs_and_links_refuse(self):
        pipeline = self.project / "pipeline"
        pipeline.mkdir()
        for selected in (self.project, pipeline):
            for directory in (self.project, pipeline):
                for name in inputs.PROJECT_ARTIFACT_NAMES:
                    for kind in ("file", "directory", "link", "dangling-link"):
                        with self.subTest(selected=selected.name, directory=directory.name,
                                          name=name, kind=kind):
                            self.load(selected)
                            path = directory / name
                            if kind == "file":
                                path.write_bytes(self.payloads[name])
                            elif kind == "directory":
                                path.mkdir()
                                (path / "foreign-child").write_bytes(b"do not erase")
                            else:
                                target = self.root / ("foreign-sentinel.bin" if kind == "link" else "missing-target")
                                path.symlink_to(target)
                            before = self.capture()
                            with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
                                self.load(selected)
                            self.assertEqual(before, self.capture())
                            if kind == "directory":
                                (path / "foreign-child").unlink()
                                path.rmdir()
                            else:
                                path.unlink()

    def test_late_presence_and_observed_removal_preserve_all_old_bytes(self):
        for names in (("wall_surface.json",), ("wall_surface.ms",), inputs.PROJECT_ARTIFACT_NAMES):
            with self.subTest(names=names):
                result = self.load()
                old = self.capture()
                self.assertFalse(any(result["project_artifact_presence"].values()))
                for name in names:
                    (self.project / name).write_bytes(self.payloads[name])
                before = self.capture()
                with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
                    inputs.verify_inputs_unchanged(result)
                self.assertEqual(before, self.capture())
                for name in names:
                    (self.project / name).unlink()
                # Complete add/remove between observations is outside this model.
                self.assertIsNone(inputs.verify_inputs_unchanged(result))
                self.assertEqual(old, self.capture())

    def test_late_new_pipeline_artifact_is_not_missing_from_presence_snapshot(self):
        result = self.load()
        pipeline = self.project / "pipeline"
        path = pipeline / "wall_surface.ms"
        self.assertIn(str(path), result["project_artifact_presence"])
        self.assertFalse(result["project_artifact_presence"][str(path)])
        pipeline.mkdir()
        path.symlink_to(self.root / "missing-target")
        before = self.capture()
        with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
            result["verify_inputs_unchanged"]()
        self.assertEqual(before, self.capture())

    def test_late_actual_public_builder_mutation_refuses_before_publisher(self):
        from scripts import build_wall_surface as builder, wall_surface_publish as publisher
        for names in (("wall_surface.json",), ("wall_surface.ms",), inputs.PROJECT_ARTIFACT_NAMES):
            with self.subTest(names=names):
                self.load()
                before = self.capture()
                original = builder.make_artifacts
                def inject(**kwargs):
                    artifacts = original(**kwargs)
                    for name in names:
                        (self.project / name).write_bytes(self.payloads[name])
                    return artifacts
                out = self.root / "late-refused-run"
                with patch.object(builder, "make_artifacts", side_effect=inject):
                    with patch.object(publisher, "publish_new_directory") as publish:
                        with self.assertRaisesRegex(inputs.InputRefusal, "existing project wall artifact"):
                            self.build(out)
                        publish.assert_not_called()
                self.assertFalse(out.exists())
                after = self.capture()
                for name in names:
                    self.assertEqual(after.pop("project/" + name), ("file", self.payloads[name]))
                self.assertEqual(before, after)
                for name in names:
                    (self.project / name).unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
