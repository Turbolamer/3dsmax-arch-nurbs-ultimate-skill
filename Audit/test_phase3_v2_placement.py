#!/usr/bin/env python3
"""Phase 3 Verification Test Suite: S5 place_components.py v2 Placement & Route-Aware S2.

Tests:
1. S5 placement on fixture specs/fixtures/v2-closed-shell-input/ succeeds,
   producing valid assembly.json and assembly.ms.
2. assembly.json structure:
   - echoes wall_technique: "closed_inner_contour_shell_v2"
   - wall_ref: "wall_surface.json"
   - strictly omits wall_cells and opening_cuts (§8 of contract 20)
   - carries 3 placements corresponding to OP-001, OP-002, OP-003
   - clean origins tree
3. Math and transform verification:
   - Door OP-001: W=98 cm, H=209 cm, D=12 cm; pivot at [150, -16, 0]; bounds [101, -22, 0] to [199, -10, 209].
   - Window OP-002: W=178 cm, H=119 cm, D=12 cm; pivot at [410, -16, 90]; bounds [321, -22, 90] to [499, -10, 209].
   - Window OP-003: W=198 cm, H=129 cm, D=12 cm; pivot at [616, 200, 110]; bounds [610, 101, 110] to [622, 299, 239].
4. G-81 zero modifiers:
   - zero addModifier calls in emitted assembly.ms
   - zero modifier properties
   - zero layer mutations (G-79)
5. Emitted MAXScript syntax check, matrix3 formatting, unit scaling, idempotence delete guards:
   - matrix3 [T] [N] [Z] ([pos] * __f_unit)
   - unit preamble: units.SystemScale and __f_unit
   - delete-by-name twice for all prototypes and placements
   - Mechanism A: host wall hiding (host.isHidden = true)
   - census assert (3 placed nodes)
   - fatal crash prevention: zero formattedPrint
6. Negative controls:
   - Refusal if wall_surface.json is missing in v2 route
   - Refusal if opening has invalid/inverted s_range
   - Refusal if opening station exceeds segment bounds
   - Refusal if opening collision / overlap occurs
   - Refusal if clearances exceed rough opening dimensions
   - Refusal if openings[] array is empty
7. Validator integration:
   - validate_specs.py reports 0 FAIL on v2 fixture
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import place_components as s5

FIXTURE_DIR = ROOT / "specs" / "fixtures" / "v2-closed-shell-input"


def compute_world_bounds(
    pivot: list[float],
    size: list[float],
    local_frame: dict,
) -> tuple[list[float], list[float]]:
    """Compute exact 3D AABB for a placement Box from its pivot, size [W, D, H], and local frame."""
    w, d, h = size[0], size[1], size[2]
    t = local_frame["tangent"]
    n = local_frame["outward"]
    u = local_frame["up"]

    corners: list[list[float]] = []
    for x in (-w / 2.0, w / 2.0):
        for y in (-d / 2.0, d / 2.0):
            for z in (0.0, h):
                pt = [
                    pivot[0] + x * t[0] + y * n[0] + z * u[0],
                    pivot[1] + x * t[1] + y * n[1] + z * u[1],
                    pivot[2] + x * t[2] + y * n[2] + z * u[2],
                ]
                corners.append(pt)

    min_b = [min(c[i] for c in corners) for i in range(3)]
    max_b = [max(c[i] for c in corners) for i in range(3)]
    return min_b, max_b


def run_validator(directory: Path, *extra_args: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "validate_specs.py"),
        "--dir",
        str(directory),
        "--json",
        *extra_args,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    report = json.loads(res.stdout) if res.stdout else {}
    return res.returncode, report


class Test1_FixtureGeneration(unittest.TestCase):
    """Test 1: S5 placement on fixture specs/fixtures/v2-closed-shell-input/ succeeds."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t1_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_fixture_build_succeeds(self):
        """place_components.py runs cleanly into output directory."""
        args = ["--in", str(FIXTURE_DIR), "--out", str(self.tmp_dir)]
        exit_code = s5.main(args)
        self.assertEqual(exit_code, 0, "place_components.py exited non-zero on fixture")

        json_path = Path(self.tmp_dir) / "assembly.json"
        ms_path = Path(self.tmp_dir) / "assembly.ms"
        self.assertTrue(json_path.is_file(), "assembly.json was not created")
        self.assertTrue(ms_path.is_file(), "assembly.ms was not created")
        self.assertGreater(json_path.stat().st_size, 0)
        self.assertGreater(ms_path.stat().st_size, 0)

        # Validate that assembly.json is valid strict JSON
        with open(json_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual(doc["spec"], "assembly")
        self.assertEqual(doc["status"], "locked")


class Test2_AssemblyStructure(unittest.TestCase):
    """Test 2: assembly.json structure, route echoing, and exclusivity omissions."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t2_")
        s5.main(["--in", str(FIXTURE_DIR), "--out", str(self.tmp_dir)])
        with open(Path(self.tmp_dir) / "assembly.json", "r", encoding="utf-8") as f:
            self.assembly = json.load(f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_route_and_wall_ref_echo(self):
        """Echoes wall_technique: closed_inner_contour_shell_v2 and wall_ref: wall_surface.json."""
        self.assertEqual(self.assembly["wall_technique"], "closed_inner_contour_shell_v2")
        self.assertEqual(self.assembly["wall_ref"], "wall_surface.json")

    def test_exclusivity_omissions_contract_20_sec8(self):
        """opening_cuts and wall_cells MUST BE OMITTED entirely for v2."""
        self.assertNotIn(
            "opening_cuts",
            self.assembly,
            "Contract 20 §8 violation: opening_cuts must be omitted in v2",
        )
        self.assertNotIn(
            "wall_cells",
            self.assembly,
            "Contract 20 §8 violation: wall_cells must be omitted in v2",
        )

    def test_placements_count_and_ids(self):
        """Carries 3 placements corresponding to OP-001, OP-002, OP-003."""
        placements = self.assembly["placements"]
        self.assertEqual(len(placements), 3)

        op_ids = [p["opening_id"] for p in placements]
        self.assertEqual(op_ids, ["OP-001", "OP-002", "OP-003"])

        plc_ids = [p["id"] for p in placements]
        self.assertEqual(plc_ids, ["PLC-001", "PLC-002", "PLC-003"])

        node_names = [p["node_name"] for p in placements]
        self.assertEqual(node_names, ["PLC_001", "PLC_002", "PLC_003"])

    def test_clean_origins_tree(self):
        """Clean origins tree: origin_inputs and origins entries for v2."""
        self.assertIn("storeys[0].openings", self.assembly["origin_inputs"])
        origins = self.assembly["origins"]
        self.assertIn("wall_technique", origins)
        self.assertIn("wall_ref", origins)
        for i in range(3):
            self.assertIn(f"placements[{i}]", origins)
            self.assertEqual(origins[f"placements[{i}]"]["origin"], "derived")
            self.assertEqual(
                origins[f"placements[{i}]"]["derives_from"],
                ["storeys[0].openings"],
            )


class Test3_MathAndTransformVerification(unittest.TestCase):
    """Test 3: Math and transform verification for Door OP-001, Window OP-002, Window OP-003."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t3_")
        s5.main(["--in", str(FIXTURE_DIR), "--out", str(self.tmp_dir)])
        with open(Path(self.tmp_dir) / "assembly.json", "r", encoding="utf-8") as f:
            self.assembly = json.load(f)
        with open(FIXTURE_DIR / "wall_surface.json", "r", encoding="utf-8") as f:
            self.wall_surface = json.load(f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_door_op001_exact_math_and_bounds(self):
        """Door OP-001: W=98 cm, H=209 cm, D=12 cm; pivot at [150, -16, 0]; bounds [101, -22, 0] to [199, -10, 209]."""
        p = self.assembly["placements"][0]
        self.assertEqual(p["opening_id"], "OP-001")
        self.assertEqual(p["kind"], "door")

        # Size: [W, D, H] = [98, 12, 209]
        self.assertEqual(p["size_cm"], [98.0, 12.0, 209.0])

        # Pivot: [150, -16, 0]
        self.assertEqual(p["position_cm"], [150.0, -16.0, 0.0])

        # Rot Z: 0.0 deg
        self.assertAlmostEqual(p["rot_z_deg"], 0.0, places=4)

        # Bounds: [101, -22, 0] to [199, -10, 209]
        min_b, max_b = compute_world_bounds(p["position_cm"], p["size_cm"], p["local_frame"])
        for i, val in enumerate([101.0, -22.0, 0.0]):
            self.assertAlmostEqual(min_b[i], val, places=3)
        for i, val in enumerate([199.0, -10.0, 209.0]):
            self.assertAlmostEqual(max_b[i], val, places=3)

    def test_window_op002_exact_math_and_bounds(self):
        """Window OP-002: W=178 cm, H=119 cm, D=12 cm; pivot at [410, -16, 90]; bounds [321, -22, 90] to [499, -10, 209]."""
        p = self.assembly["placements"][1]
        self.assertEqual(p["opening_id"], "OP-002")
        self.assertEqual(p["kind"], "window")

        # Size: [W, D, H] = [178, 12, 119]
        self.assertEqual(p["size_cm"], [178.0, 12.0, 119.0])

        # Pivot: [410, -16, 90]
        self.assertEqual(p["position_cm"], [410.0, -16.0, 90.0])

        # Rot Z: 0.0 deg
        self.assertAlmostEqual(p["rot_z_deg"], 0.0, places=4)

        # Bounds: [321, -22, 90] to [499, -10, 209]
        min_b, max_b = compute_world_bounds(p["position_cm"], p["size_cm"], p["local_frame"])
        for i, val in enumerate([321.0, -22.0, 90.0]):
            self.assertAlmostEqual(min_b[i], val, places=3)
        for i, val in enumerate([499.0, -10.0, 209.0]):
            self.assertAlmostEqual(max_b[i], val, places=3)

    def test_window_op003_exact_math_and_bounds(self):
        """Window OP-003: W=198 cm, H=129 cm, D=12 cm; pivot at [616, 200, 110]; bounds [610, 101, 110] to [622, 299, 239]."""
        p = self.assembly["placements"][2]
        self.assertEqual(p["opening_id"], "OP-003")
        self.assertEqual(p["kind"], "window")

        # Size: [W, D, H] = [198, 12, 129]
        self.assertEqual(p["size_cm"], [198.0, 12.0, 129.0])

        # Pivot: [616, 200, 110]
        self.assertEqual(p["position_cm"], [616.0, 200.0, 110.0])

        # Rot Z: 90.0 deg
        self.assertAlmostEqual(p["rot_z_deg"], 90.0, places=4)

        # Bounds: [610, 101, 110] to [622, 299, 239]
        min_b, max_b = compute_world_bounds(p["position_cm"], p["size_cm"], p["local_frame"])
        for i, val in enumerate([610.0, 101.0, 110.0]):
            self.assertAlmostEqual(min_b[i], val, places=3)
        for i, val in enumerate([622.0, 299.0, 239.0]):
            self.assertAlmostEqual(max_b[i], val, places=3)

    def test_recess_and_reveals_consistency(self):
        """Inner reveal (recess) + frame depth + outer reveal = wall thickness (30 cm)."""
        wall_t = float(self.wall_surface["storeys"][0]["wall_thickness_cm"])
        for p in self.assembly["placements"]:
            mp = p["mounting_parameters"]
            recess = mp["recess_cm"]
            depth = mp["frame_depth_cm"]
            outer_reveal = wall_t - recess - depth
            self.assertEqual(recess, 10.0)
            self.assertEqual(depth, 12.0)
            self.assertEqual(outer_reveal, 8.0)
            self.assertAlmostEqual(recess + depth + outer_reveal, wall_t, places=4)


class Test4_ZeroModifiersG81(unittest.TestCase):
    """Test 4: G-81 zero modifiers and safe script generation."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t4_")
        s5.main(["--in", str(FIXTURE_DIR), "--out", str(self.tmp_dir)])
        with open(Path(self.tmp_dir) / "assembly.ms", "r", encoding="utf-8") as f:
            self.ms_script = f.read()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_strict_zero_modifiers(self):
        """Verify emitted assembly.ms has zero addModifier calls."""
        self.assertNotIn("addModifier", self.ms_script)
        self.assertNotIn(".modifiers", self.ms_script)

    def test_zero_layer_mutations_g79(self):
        """Verify emitted assembly.ms has zero layer assignment on nodes."""
        self.assertNotIn("node.layer", self.ms_script)
        self.assertNotIn(".layer =", self.ms_script)

    def test_zero_fatal_tokens(self):
        """Verify no fatal tokens exist: formattedPrint, stopCreating, global fn."""
        self.assertNotIn("formattedPrint", self.ms_script)
        self.assertNotIn("stopCreating", self.ms_script)
        self.assertNotIn("global fn", self.ms_script)


class Test5_MaxscriptFormattingAndGuards(unittest.TestCase):
    """Test 5: Emitted MAXScript syntax check, matrix3 formatting, unit scaling, idempotence delete guards."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t5_")
        s5.main(["--in", str(FIXTURE_DIR), "--out", str(self.tmp_dir)])
        with open(Path(self.tmp_dir) / "assembly.ms", "r", encoding="utf-8") as f:
            self.ms_script = f.read()
        with open(Path(self.tmp_dir) / "assembly.json", "r", encoding="utf-8") as f:
            self.assembly = json.load(f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_unit_scale_preamble(self):
        """Preamble checks units.SystemScale and defines __f_unit."""
        self.assertIn("local __sys_scale = units.SystemScale as float", self.ms_script)
        self.assertIn("local __f_unit = 1.0 / __c_cm", self.ms_script)

    def test_idempotence_double_delete_by_name(self):
        """Deleting a base does not delete its instances: all nodes deleted twice by name."""
        all_nodes = ["PROTO_DOOR_01_1", "PROTO_COMP_WINDOW_2", "PROTO_COMP_WINDOW_3", "PLC_001", "PLC_002", "PLC_003"]
        for nm in all_nodes:
            count = self.ms_script.count(f'local prev_{nm} = getNodeByName "{nm}"')
            self.assertEqual(count, 2, f"Node {nm} was not deleted twice by name")

    def test_matrix3_transform_formatting(self):
        """Transform formatted as matrix3 [T] [N] [Z] ([pos] * __f_unit)."""
        # PLC_001
        self.assertIn(
            "PLC_001.transform = matrix3 [1.0000000, 0.0000000, 0.0000000] [0.0000000, -1.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([150, -16, 0] * __f_unit)",
            self.ms_script,
        )
        # PLC_002
        self.assertIn(
            "PLC_002.transform = matrix3 [1.0000000, 0.0000000, 0.0000000] [0.0000000, -1.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([410, -16, 90] * __f_unit)",
            self.ms_script,
        )
        # PLC_003
        self.assertIn(
            "PLC_003.transform = matrix3 [0.0000000, 1.0000000, 0.0000000] [1.0000000, 0.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([616, 200, 110] * __f_unit)",
            self.ms_script,
        )

    def test_reference_instancing(self):
        """Instances created via copy + baseObject = proto.baseObject."""
        self.assertIn("local PLC_001 = copy PROTO_DOOR_01_1", self.ms_script)
        self.assertIn("PLC_001.baseObject = PROTO_DOOR_01_1.baseObject", self.ms_script)
        self.assertIn("local PLC_002 = copy PROTO_COMP_WINDOW_2", self.ms_script)
        self.assertIn("PLC_002.baseObject = PROTO_COMP_WINDOW_2.baseObject", self.ms_script)
        self.assertIn("local PLC_003 = copy PROTO_COMP_WINDOW_3", self.ms_script)
        self.assertIn("PLC_003.baseObject = PROTO_COMP_WINDOW_3.baseObject", self.ms_script)

    def test_mechanism_a_host_wall_hiding(self):
        """Mechanism A: host wall hiding sets isHidden = true for facade_wall hosts."""
        self.assertIn("host_nd.isHidden = true", self.ms_script)

    def test_census_assertion(self):
        """Census assertion verifies 3 placed nodes."""
        self.assertIn("if placed_found != 3 do (", self.ms_script)


class Test6_NegativeControls(unittest.TestCase):
    """Test 6: Negative controls and refusal validation."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_phase3_t6_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make_input_dir(self) -> Path:
        p = Path(self.tmp_dir) / "input"
        if p.exists():
            shutil.rmtree(p)
        shutil.copytree(FIXTURE_DIR, p)
        return p

    def test_refusal_when_wall_surface_json_missing(self):
        """Refusal if wall_surface.json is missing in v2 route."""
        p = self._make_input_dir()
        (p / "wall_surface.json").unlink()
        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on missing wall_surface.json")

    def test_refusal_on_invalid_or_inverted_s_range(self):
        """Refusal if opening has invalid/inverted s_range (s_min >= s_max or s_min < 0)."""
        # Case A: s_min >= s_max
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"][0]["station_along_segment"]["s_min_cm"] = 250.0
        ws["openings"][0]["station_along_segment"]["s_max_cm"] = 200.0
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)

        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on inverted station range")

        # Case B: s_min < 0
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"][0]["station_along_segment"]["s_min_cm"] = -10.0
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on negative station range")

    def test_refusal_on_station_out_of_bounds(self):
        """Refusal if opening station exceeds segment length."""
        # seg_south length = 600 cm. Set s_max to 650 cm.
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"][1]["station_along_segment"]["s_max_cm"] = 650.0
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)

        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on station out of bounds")

    def test_refusal_on_opening_collision_overlap(self):
        """Refusal if opening collision / overlap occurs on the same segment."""
        # OP-001 is [100, 200] on seg_south. Set OP-002 to [180, 400] on seg_south (overlaps 180 < 200).
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"][1]["station_along_segment"]["s_min_cm"] = 180.0
        ws["openings"][1]["station_along_segment"]["s_max_cm"] = 400.0
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)

        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on opening collision/overlap")

    def test_refusal_on_excessive_clearances(self):
        """Refusal if clearances exceed rough opening dimensions."""
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"][0]["mounting_parameters"]["clearance_sides_cm"] = 55.0  # 2*55 = 110 > 100
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)

        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on excessive clearances")

    def test_refusal_on_empty_openings(self):
        """Refusal if openings[] array is empty."""
        p = self._make_input_dir()
        ws_file = p / "wall_surface.json"
        with open(ws_file, "r", encoding="utf-8") as f:
            ws = json.load(f)
        ws["openings"] = []
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2)

        out = Path(self.tmp_dir) / "out"
        out.mkdir(exist_ok=True)
        ret = s5.main(["--in", str(p), "--out", str(out)])
        self.assertEqual(ret, 1, "Expected refusal on empty openings[]")


class Test7_ValidatorIntegration(unittest.TestCase):
    """Test 7: Spec validator reports 0 FAIL on v2 fixture."""

    def test_validate_specs_zero_failures(self):
        ret, report = run_validator(FIXTURE_DIR)
        self.assertEqual(ret, 0, f"validate_specs.py exited non-zero: {ret}")
        self.assertEqual(report.get("exit_code"), 0)
        findings = report.get("findings", [])
        fails = [f for f in findings if f.get("status") == "FAIL"]
        self.assertEqual(len(fails), 0, f"Validator found FAIL findings: {fails}")


if __name__ == "__main__":
    unittest.main()
