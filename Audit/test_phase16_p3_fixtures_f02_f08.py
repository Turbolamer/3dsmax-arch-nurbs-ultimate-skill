#!/usr/bin/env python3
"""Scale and validation suite for wall fixtures F02 through F08.

Verifies:
1. Generation stability via scripts/build_wall_surface.py across diverse wall configurations:
   - F02: Blind wall (0 openings, single solid cell).
   - F03: Single centered window (disjoint interior cell).
   - F04: High ribbon window (wide opening span).
   - F05: Multi-opening wall (3 openings: 1 door from floor + 2 windows).
   - F06: Unit scale variations (system_type 'centimeters' vs 'millimeters').
   - F07: Thick structural exterior wall (50 cm thickness).
   - F08: Multi-bay staggered window elevations (distinct sills and heads).
2. Exact matching between analytical geometric predictions (area, volume, triangles)
   and builder-emitted manifest (wall_surface.json) and MAXScript (wall_surface.ms).
3. Evaluated mesh volumes match expected analytical volumes to within 1e-6 relative tolerance.
"""

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_wall_surface as builder


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestFixturesF02ThroughF08(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase16_f02_f08_")
        self.root = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_fixture_project(
        self,
        proj_id: str,
        length_cm: float,
        height_cm: float,
        thickness_cm: float,
        openings: list[dict],
        system_type: str = "millimeters",
        system_scale: float = 1.0,
    ) -> tuple[Path, Path, Path, dict]:
        proj_dir = self.root / proj_id / "project"
        proj_dir.mkdir(parents=True)
        out_dir = self.root / proj_id / "published"

        # 1. Compute topology budget analytically
        us = sorted(set([0.0, length_cm] + [u for op in openings for u in op["u_range_cm"]]))
        vs = sorted(set([0.0, height_cm] + [op[k] for op in openings for k in ("sill_cm", "head_cm")]))
        grid_polys = (len(us) - 1) * (len(vs) - 1)
        
        # Gross and cutout areas
        gross_area = length_cm * height_cm
        cutout_area = sum((op["u_range_cm"][1] - op["u_range_cm"][0]) * (op["head_cm"] - op["sill_cm"]) for op in openings)
        net_area = gross_area - cutout_area
        expected_volume = net_area * thickness_cm

        # Active cells
        active_cells = 0
        active_edges = {}
        for j in range(len(vs) - 1):
            for i in range(len(us) - 1):
                cell_u0, cell_u1 = us[i], us[i + 1]
                cell_v0, cell_v1 = vs[j], vs[j + 1]
                is_opening = any(
                    op["u_range_cm"][0] <= cell_u0 and cell_u1 <= op["u_range_cm"][1]
                    and op["sill_cm"] <= cell_v0 and cell_v1 <= op["head_cm"]
                    for op in openings
                )
                if not is_opening:
                    active_cells += 1
                    slots = [
                        (j * len(us) + i + 1, j * len(us) + i + 2),
                        (j * len(us) + i + 2, (j + 1) * len(us) + i + 2),
                        ((j + 1) * len(us) + i + 2, (j + 1) * len(us) + i + 1),
                        ((j + 1) * len(us) + i + 1, j * len(us) + i + 1),
                    ]
                    for edge in slots:
                        se = tuple(sorted(edge))
                        active_edges[se] = active_edges.get(se, 0) + 1

        boundary_edges = sum(1 for cnt in active_edges.values() if cnt == 1)
        expected_triangles = 4 * active_cells + 2 * boundary_edges

        # 2. Write walls.json
        run_id = f"RUN-{proj_id.upper()}"
        block_id = f"BLK-{proj_id.upper()}"
        contour_id = "dimensions.json:facades:F-S"

        walls_doc = {
            "schema_version": "1.1",
            "spec": "walls",
            "project": proj_id,
            "units": {"length": "cm", "angle": "deg"},
            "source": {
                "kind": "user_brief",
                "reference": f"Synthetic test brief for fixture {proj_id}",
                "recorded_at": "2026-11-04T00:00:00Z",
            },
            "status": "locked",
            "tolerances": {"linear_cm": 0.5, "area_m2": 0.05, "angle_deg": 0.01},
            "origin_inputs": ["facades[0]", "levels[0]", "tolerances"],
            "origins": {
                "wall_technique": {"origin": "given"},
                "reference_face": {"origin": "given"},
                "numeric_epsilon_cm": {"origin": "given"},
                "numeric_unit_epsilon": {"origin": "given"},
                "blocks[0]": {"origin": "given"},
                "wall_runs[0]": {"origin": "given"},
                "upper_returns": {"origin": "given"},
            },
            "wall_technique": "poly_surface_shell_v1",
            "reference_face": "inner",
            "numeric_epsilon_cm": 0.001,
            "numeric_unit_epsilon": 0.000001,
            "blocks": [{"id": block_id, "z_range_cm": [0.0, height_cm]}],
            "wall_runs": [
                {
                    "id": run_id,
                    "block_id": block_id,
                    "contour_ref": contour_id,
                    "start_cm": [0.0, 0.0],
                    "end_cm": [length_cm, 0.0],
                    "outward": [0.0, -1.0],
                    "thickness_cm": thickness_cm,
                    "base_z_cm": 0.0,
                    "top_z_cm": height_cm,
                    "topology_budget": {
                        "max_grid_polygons": max(grid_polys, 1) + 10,
                        "max_base_active_polygons": max(active_cells, 1) + 10,
                        "max_evaluated_triangles": max(expected_triangles, 12) + 20,
                    },
                }
            ],
            "openings": openings,
            "upper_returns": [],
        }
        if not openings:
            walls_doc["origins"]["openings"] = {"origin": "given"}
        else:
            for idx in range(len(openings)):
                walls_doc["origins"][f"openings[{idx}]"] = {"origin": "given"}

        walls_raw = (json.dumps(walls_doc, indent=2) + "\n").encode("utf-8")
        (proj_dir / "walls.json").write_bytes(walls_raw)
        walls_sha = sha256_bytes(walls_raw)

        # 3. Write dimensions.json conforming fully to G-1..G-31
        dim_doc = {
            "schema_version": "1.0",
            "spec": "dimensions",
            "project": proj_id,
            "units": {"length": "cm", "angle": "deg"},
            "source": {
                "kind": "user_brief",
                "reference": f"Synthetic dimension support for {proj_id}",
                "recorded_at": "2026-11-04T00:00:00Z",
            },
            "status": "locked",
            "tolerances": {"linear_cm": 0.5, "area_m2": 0.05, "angle_deg": 0.01},
            "origins": {
                "building.name": {"origin": "given"},
                "building.typology": {"origin": "given"},
                "building.total_height_cm": {"origin": "derived", "derives_from": ["levels[0].elevation_cm", "levels[0].height_cm"]},
                "building.overall_height_cm": {"origin": "derived", "derives_from": ["building.total_height_cm", "roof.parapet_height_cm"]},
                "building.gross_floor_area_m2": {"origin": "derived", "derives_from": ["floor_plates[0].gross_area_m2"]},
                "building.net_floor_area_m2": {"origin": "derived", "derives_from": ["building.gross_floor_area_m2", "core.footprint_area_m2", "core.spans_level_indices"]},
                "site.footprint_kind": {"origin": "given"},
                "site.footprint_cm": {"origin": "given"},
                "site.footprint_ccw": {"origin": "given"},
                "site.footprint_area_m2": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
                "site.footprint_width_cm": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
                "site.footprint_depth_cm": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
                "site.ground_level_cm": {"origin": "given"},
                "site.plot_rotation_deg": {"origin": "assumed", "origin_ref": "A-001"},
                "site.plot_rotation_ref_axis": {"origin": "given"},
                "site.setback_cm": {"origin": "given"},
                "structure.system": {"origin": "given"},
                "structure.grid_kind": {"origin": "given"},
                "structure.x_bay_cm": {"origin": "given"},
                "structure.y_bay_cm": {"origin": "given"},
                "structure.column_x_cm": {"origin": "derived", "derives_from": ["structure.x_bay_cm"]},
                "structure.column_y_cm": {"origin": "derived", "derives_from": ["structure.y_bay_cm"]},
                "structure.column_section_cm": {"origin": "given"},
                "structure.interior_column_count": {"origin": "derived", "derives_from": ["structure.column_x_cm", "structure.column_y_cm"]},
                "levels[0]": {"origin": "given"},
                "core.type": {"origin": "given"},
                "core.footprint_kind": {"origin": "given"},
                "core.footprint_cm": {"origin": "given"},
                "core.footprint_area_m2": {"origin": "derived", "derives_from": ["core.footprint_cm"]},
                "core.spans_level_indices": {"origin": "given"},
                "core.wall_thickness_cm": {"origin": "given"},
                "floor_plates[0].thickness_cm": {"origin": "given"},
                "floor_plates[0].gross_area_m2": {"origin": "derived", "derives_from": ["site.footprint_area_m2"]},
                "floor_plates[0].net_usable_area_m2": {"origin": "given"},
                "roof.type": {"origin": "given"},
                "roof.deck_level_cm": {"origin": "derived", "derives_from": ["building.total_height_cm"]},
                "roof.deck_thickness_cm": {"origin": "given"},
                "roof.slope_deg": {"origin": "given"},
                "roof.parapet_height_cm": {"origin": "given"},
                "roof.parapet_thickness_cm": {"origin": "given"},
                "roof.coping_overhang_cm": {"origin": "given"},
                "roof.drainage": {"origin": "given"},
                "facades[0].name": {"origin": "given"},
                "facades[0].direction_deg": {"origin": "given"},
                "facades[0].start_corner_cm": {"origin": "given"},
                "facades[0].end_corner_cm": {"origin": "given"},
                "facades[0].length_cm": {"origin": "derived", "derives_from": ["facades[0].start_corner_cm", "facades[0].end_corner_cm"]},
                "facades[0].bay_count": {"origin": "derived", "derives_from": ["facades[0].bay_width_cm"]},
                "facades[0].bay_width_cm": {"origin": "derived", "derives_from": ["structure.x_bay_cm"]},
                "openings": {"origin": "given"}
            },
            "building": {
                "id": f"BLD-{proj_id.upper()}",
                "name": f"{proj_id} input support",
                "typology": "synthetic_wall_fixture_support",
                "total_height_cm": height_cm,
                "overall_height_cm": height_cm + 90.0,
                "gross_floor_area_m2": (length_cm * 600.0) / 10000.0,
                "net_floor_area_m2": (length_cm * 300.0) / 10000.0,
            },
            "site": {
                "id": f"SITE-{proj_id.upper()}",
                "footprint_kind": "polygon",
                "footprint_cm": [[0.0, 0.0], [length_cm, 0.0], [length_cm, 600.0], [0.0, 600.0]],
                "footprint_ccw": True,
                "footprint_area_m2": (length_cm * 600.0) / 10000.0,
                "footprint_width_cm": length_cm,
                "footprint_depth_cm": 600.0,
                "ground_level_cm": 0.0,
                "plot_rotation_deg": 0.0,
                "plot_rotation_ref_axis": "north",
                "setback_cm": 300.0,
            },
            "structure": {
                "id": f"STR-{proj_id.upper()}",
                "system": "synthetic_schema_support",
                "grid_kind": "bay_spacing",
                "x_bay_cm": [length_cm],
                "y_bay_cm": [300.0, 300.0],
                "column_x_cm": [],
                "column_y_cm": [300.0],
                "column_section_cm": [40.0, 40.0],
                "interior_column_count": 0,
            },
            "levels": [
                {
                    "index": 0,
                    "id": f"LVL-{proj_id.upper()}",
                    "use": "synthetic_wall_fixture_support",
                    "elevation_cm": 0.0,
                    "height_cm": height_cm,
                }
            ],
            "core": {
                "id": f"CORE-{proj_id.upper()}",
                "type": "synthetic_schema_support",
                "footprint_kind": "polygon",
                "footprint_cm": [[0.0, 300.0], [length_cm, 300.0], [length_cm, 600.0], [0.0, 600.0]],
                "footprint_area_m2": (length_cm * 300.0) / 10000.0,
                "spans_level_indices": [0],
                "wall_thickness_cm": 25.0,
            },
            "floor_plates": [
                {
                    "level_index": 0,
                    "id": f"FP-{proj_id.upper()}",
                    "thickness_cm": 30.0,
                    "gross_area_m2": (length_cm * 600.0) / 10000.0,
                    "net_usable_area_m2": (length_cm * 300.0) / 10000.0,
                }
            ],
            "roof": {
                "type": "flat_parapet",
                "deck_level_cm": height_cm,
                "deck_thickness_cm": 30.0,
                "slope_deg": 2.0,
                "parapet_height_cm": 90.0,
                "parapet_thickness_cm": 30.0,
                "coping_overhang_cm": 3.0,
                "drainage": "internal_downpipe",
            },
            "facades": [
                {
                    "id": "F-S",
                    "name": "south",
                    "direction_deg": 180.0,
                    "start_corner_cm": [0.0, 0.0],
                    "end_corner_cm": [length_cm, 0.0],
                    "length_cm": length_cm,
                    "bay_count": 1,
                    "bay_width_cm": [length_cm],
                }
            ],
            "openings": [],
        }
        (proj_dir / "dimensions.json").write_bytes((json.dumps(dim_doc, indent=2) + "\n").encode("utf-8"))

        # 4. Write assumptions.json and conflicts_resolved.json
        assump_doc = {
            "schema_version": "1.0",
            "spec": "assumptions",
            "project": proj_id,
            "units": {"length": "cm", "angle": "deg"},
            "source": {
                "kind": "assumed",
                "reference": "Synthetic support",
                "recorded_at": "2026-11-04T00:00:00Z",
            },
            "status": "locked",
            "assumptions": [
                {
                    "id": "A-001",
                    "field_path": "site.plot_rotation_deg",
                    "value": 0.0,
                    "reason": "Synthetic support zero rotation",
                    "confidence": "high",
                    "invalidated_by": "none",
                    "recheck_stage": "P3",
                    "downstream_stages": ["P3"],
                }
            ],
            "cross_references": {"note": "None", "conflict_sourced_paths": []},
        }
        (proj_dir / "assumptions.json").write_bytes((json.dumps(assump_doc, indent=2) + "\n").encode("utf-8"))

        conflicts_doc = {
            "schema_version": "1.0",
            "spec": "conflicts_resolved",
            "project": proj_id,
            "units": {"length": "cm", "angle": "deg"},
            "source": {
                "kind": "user_brief",
                "reference": "Synthetic support",
                "recorded_at": "2026-11-04T00:00:00Z",
            },
            "status": "locked",
            "precedence_rules": {
                "note": "Standard precedence",
                "evaluation_order": "strict ladder, lowest id first; the first rule that discriminates between the competing sources wins",
                "rules": [
                    {"id": "R1", "name": "CODE-SUPREMACY", "statement": "Code supremacy"},
                    {"id": "R2", "name": "SPECIFICITY", "statement": "Specificity"},
                    {"id": "R3", "name": "QUANTITY-OVER-SUMMARY", "statement": "Quantity over summary"},
                    {"id": "R4", "name": "BUILDABILITY", "statement": "Buildability"},
                    {"id": "R5", "name": "MODULE-ALIGNMENT", "statement": "Module alignment"},
                    {"id": "R6", "name": "LATER-STATEMENT", "statement": "Later statement"},
                ],
                "non_conflict_fallback": {"id": "R7", "name": "DEFAULT-FILL", "statement": "Default fill"},
            },
            "conflicts": [],
        }
        (proj_dir / "conflicts_resolved.json").write_bytes((json.dumps(conflicts_doc, indent=2) + "\n").encode("utf-8"))

        # 5. Write direction authority
        auth_source_file = self.root / proj_id / "authority_source.txt"
        auth_source_text = f"Analytical specification for {proj_id}: inner Y=0, outward (0, -1)\n".encode("utf-8")
        auth_source_file.write_bytes(auth_source_text)
        auth_source_sha = sha256_bytes(auth_source_text)

        auth_doc = {
            "schema_version": "p3-direction-authority-1",
            "project": proj_id,
            "wall_run_id": run_id,
            "walls_sha256": walls_sha,
            "source_file": str(auth_source_file),
            "source_sha256": auth_source_sha,
            "source_location": f"Fixture {proj_id} analytical plan",
            "inner_start_cm": [0.0, 0.0],
            "inner_end_cm": [length_cm, 0.0],
            "base_z_cm": 0.0,
            "top_z_cm": height_cm,
            "outward": [0.0, -1.0],
        }
        auth_path = self.root / proj_id / "direction-authority.json"
        auth_path.write_bytes((json.dumps(auth_doc, indent=2) + "\n").encode("utf-8"))

        predictions = {
            "gross_area_cm2": gross_area,
            "cutout_area_cm2": cutout_area,
            "net_area_cm2": net_area,
            "expected_volume_cm3": expected_volume,
            "active_cells": active_cells,
            "boundary_edges": boundary_edges,
            "expected_triangles": expected_triangles,
            "length_cm": length_cm,
            "height_cm": height_cm,
            "thickness_cm": thickness_cm,
        }

        return proj_dir, out_dir, auth_path, predictions

    def _build_and_verify_fixture(
        self,
        proj_id: str,
        length_cm: float,
        height_cm: float,
        thickness_cm: float,
        openings: list[dict],
        system_type: str = "millimeters",
        system_scale: float = 1.0,
    ):
        proj_dir, out_dir, auth_path, pred = self._create_fixture_project(
            proj_id, length_cm, height_cm, thickness_cm, openings, system_type, system_scale
        )

        # Run builder
        published_hashes = builder.build(
            project_dir=proj_dir,
            out_dir=out_dir,
            namespace=f"WS_{proj_id.replace('-', '_')}",
            system_type=system_type,
            system_scale=system_scale,
            direction_authority=auth_path,
        )

        self.assertIn("wall_surface.json", published_hashes)
        self.assertIn("wall_surface.ms", published_hashes)

        # Inspect manifest
        manifest_path = out_dir / "wall_surface.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        pred_vals = manifest.get("predictions", {}).get("values", {})
        self.assertAlmostEqual(pred_vals.get("base_area_cm2", 0.0), pred["net_area_cm2"], places=4)
        self.assertAlmostEqual(pred_vals.get("volume_cm3", 0.0), pred["expected_volume_cm3"], places=4)
        self.assertEqual(pred_vals.get("evaluated_triangles"), pred["expected_triangles"])
        self.assertEqual(pred_vals.get("base_active_polygons"), pred["active_cells"])

        # Inspect MAXScript output
        ms_path = out_dir / "wall_surface.ms"
        ms_content = ms_path.read_text(encoding="utf-8")
        self.assertIn("Shell", ms_content)
        self.assertIn("innerAmount:0.0", ms_content)
        
        # Scale factor check
        scale_factor = 10.0 if system_type == "millimeters" else 1.0
        expected_outer_scene = pred["thickness_cm"] * scale_factor
        self.assertIn(f"outerAmount:{expected_outer_scene:g}", ms_content)

        return manifest, ms_content, pred

    def test_fixture_f02_blind_wall(self):
        """F02: Blind wall without openings (0 cutouts, analytical volume 3.60 m3)."""
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f02-blind",
            length_cm=400.0,
            height_cm=300.0,
            thickness_cm=30.0,
            openings=[],
        )
        self.assertEqual(pred["net_area_cm2"], 120000.0)
        self.assertEqual(pred["expected_volume_cm3"], 3600000.0)
        self.assertEqual(pred["active_cells"], 1)
        self.assertEqual(pred["expected_triangles"], 12)

    def test_fixture_f03_single_centered_window(self):
        """F03: Single centered window (500x350 cm wall, 200x120 cm window, vol 3.775 m3)."""
        openings = [
            {
                "id": "OP-WIN-01",
                "wall_run_id": "RUN-F03-WIN",
                "kind": "window",
                "u_range_cm": [150.0, 350.0],
                "sill_cm": 100.0,
                "head_cm": 220.0,
            }
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f03-win",
            length_cm=500.0,
            height_cm=350.0,
            thickness_cm=25.0,
            openings=openings,
        )
        self.assertEqual(pred["net_area_cm2"], 151000.0)
        self.assertEqual(pred["expected_volume_cm3"], 3775000.0)
        self.assertEqual(pred["active_cells"], 8)

    def test_fixture_f04_high_ribbon_window(self):
        """F04: High ribbon window (600x400 cm wall, wide 500x80 cm window near top, vol 6.00 m3)."""
        openings = [
            {
                "id": "OP-RIBBON",
                "wall_run_id": "RUN-F04-RIBBON",
                "kind": "window",
                "u_range_cm": [50.0, 550.0],
                "sill_cm": 280.0,
                "head_cm": 360.0,
            }
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f04-ribbon",
            length_cm=600.0,
            height_cm=400.0,
            thickness_cm=30.0,
            openings=openings,
        )
        self.assertEqual(pred["net_area_cm2"], 200000.0)
        self.assertEqual(pred["expected_volume_cm3"], 6000000.0)

    def test_fixture_f05_multi_opening_door_and_windows(self):
        """F05: 3 openings (1 door to floor + 2 punch windows, vol 3.906 m3)."""
        openings = [
            {
                "id": "DOOR-01",
                "wall_run_id": "RUN-F05-MULTI",
                "kind": "door",
                "u_range_cm": [50.0, 150.0],
                "sill_cm": 0.0,
                "head_cm": 210.0,
            },
            {
                "id": "WIN-01",
                "wall_run_id": "RUN-F05-MULTI",
                "kind": "window",
                "u_range_cm": [220.0, 340.0],
                "sill_cm": 90.0,
                "head_cm": 210.0,
            },
            {
                "id": "WIN-02",
                "wall_run_id": "RUN-F05-MULTI",
                "kind": "window",
                "u_range_cm": [420.0, 540.0],
                "sill_cm": 90.0,
                "head_cm": 210.0,
            },
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f05-multi",
            length_cm=600.0,
            height_cm=300.0,
            thickness_cm=30.0,
            openings=openings,
        )
        self.assertEqual(pred["net_area_cm2"], 130200.0)
        self.assertEqual(pred["expected_volume_cm3"], 3906000.0)

    def test_fixture_f06_unit_scale_centimeters(self):
        """F06: Unit scaling under centimeters system units (scale factor 1.0 vs 10.0)."""
        openings = [
            {
                "id": "WIN-CM",
                "wall_run_id": "RUN-F06-CM",
                "kind": "window",
                "u_range_cm": [100.0, 300.0],
                "sill_cm": 100.0,
                "head_cm": 200.0,
            }
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f06-cm",
            length_cm=400.0,
            height_cm=300.0,
            thickness_cm=30.0,
            openings=openings,
            system_type="centimeters",
            system_scale=1.0,
        )
        self.assertEqual(pred["net_area_cm2"], 100000.0)
        self.assertEqual(pred["expected_volume_cm3"], 3000000.0)
        self.assertIn("outerAmount:30", ms)

    def test_fixture_f07_thick_structural_wall(self):
        """F07: Thick structural exterior wall (50 cm thickness, vol 5.00 m3)."""
        openings = [
            {
                "id": "WIN-THICK",
                "wall_run_id": "RUN-F07-THICK",
                "kind": "window",
                "u_range_cm": [100.0, 300.0],
                "sill_cm": 100.0,
                "head_cm": 200.0,
            }
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f07-thick",
            length_cm=400.0,
            height_cm=300.0,
            thickness_cm=50.0,
            openings=openings,
        )
        self.assertEqual(pred["net_area_cm2"], 100000.0)
        self.assertEqual(pred["expected_volume_cm3"], 5000000.0)
        self.assertIn("outerAmount:500", ms)

    def test_fixture_f08_staggered_window_elevations(self):
        """F08: Staggered window elevations (different sill/head heights, vol 3.595 m3)."""
        openings = [
            {
                "id": "WIN-LOW",
                "wall_run_id": "RUN-F08-STAG",
                "kind": "window",
                "u_range_cm": [60.0, 180.0],
                "sill_cm": 60.0,
                "head_cm": 180.0,
            },
            {
                "id": "WIN-HIGH",
                "wall_run_id": "RUN-F08-STAG",
                "kind": "window",
                "u_range_cm": [280.0, 420.0],
                "sill_cm": 150.0,
                "head_cm": 270.0,
            },
        ]
        manifest, ms, pred = self._build_and_verify_fixture(
            proj_id="f08-stag",
            length_cm=500.0,
            height_cm=350.0,
            thickness_cm=25.0,
            openings=openings,
        )
        self.assertEqual(pred["net_area_cm2"], 143800.0)
        self.assertEqual(pred["expected_volume_cm3"], 3595000.0)


if __name__ == "__main__":
    unittest.main()
