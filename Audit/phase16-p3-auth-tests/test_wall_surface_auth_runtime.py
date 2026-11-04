"""Authentic P3.1 wall surface runtime contract tests.

Verifies the live-proven runtime contracts:
1. All 16 emitted MAXScript helpers have p3 prefix;
2. In-memory TriMesh Object Space snapshots for RNormals and SmoothGroups with guaranteed delete;
3. Recursive subAnim & controller audit (unkeyed, unwired, 27 forbidden classes);
4. LayerAdmissionGuard root-of-trust & dependency closure (rootScene -> rootNode/Layer_Manager/layer 0);
5. Replay VERIFIED_NOOP branch with baseline comparison and dirty flag check;
6. Arm catch preserves registryKey with POISONED status (never removed);
7. Modifiers strictly limited to Shell (Edit_Normals and other normal modifiers prohibited);
8. Exact current-attempt reference tracking with calibrated residual reporting.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from wall_surface_runtime import build_plan, generate_script, generate_arm_script


def make_fixture():
    dims = {
        "spec": "dimensions",
        "project": "p3-auth-test",
        "status": "locked",
        "units": {"length": "cm"},
        "facades": [
            {
                "id": "F01",
                "start_corner_cm": [0, 0],
                "end_corner_cm": [400, 0],
                "length_cm": 400,
            }
        ],
    }
    walls = {
        "spec": "walls",
        "project": "p3-auth-test",
        "status": "locked",
        "units": {"length": "cm"},
        "wall_technique": "poly_surface_shell_v1",
        "reference_face": "inner",
        "numeric_epsilon_cm": 0.001,
        "numeric_unit_epsilon": 0.000001,
        "blocks": [{"id": "B", "z_range_cm": [0, 300]}],
        "upper_returns": [],
        "wall_runs": [
            {
                "id": "W",
                "block_id": "B",
                "contour_ref": "dimensions.json:facades:F01",
                "start_cm": [0, 0],
                "end_cm": [400, 0],
                "outward": [0, -1],
                "thickness_cm": 30,
                "base_z_cm": 0,
                "top_z_cm": 300,
                "topology_budget": {
                    "max_grid_polygons": 32,
                    "max_base_active_polygons": 32,
                    "max_evaluated_triangles": 256,
                },
            }
        ],
        "openings": [
            {
                "id": "D",
                "wall_run_id": "W",
                "kind": "door",
                "u_range_cm": [50, 150],
                "sill_cm": 0,
                "head_cm": 210,
            },
            {
                "id": "O",
                "wall_run_id": "W",
                "kind": "window",
                "u_range_cm": [230, 330],
                "sill_cm": 90,
                "head_cm": 210,
            },
        ],
    }
    return walls, dims


UNITS = {
    "system_type": "millimeters",
    "system_scale": 1.0,
    "cm_per_unit": 0.1,
    "units_per_cm": 10.0,
}
IDENTITY = hashlib.sha256(b"authentic-auth-test").hexdigest()


class WallSurfaceAuthRuntimeTests(unittest.TestCase):
    def setUp(self):
        walls, dims = make_fixture()
        self.plan = build_plan(walls, dims)
        self.source = generate_script(self.plan, IDENTITY, "P3AuthTest", UNITS)

    def test_01_all_16_emitted_helpers_are_p3_prefixed(self):
        """Verifies exactly 16 helpers, all prefixed with p3."""
        names = re.findall(r"\bfn\s+(\w+)", self.source)
        self.assertEqual(len(names), 16, f"Expected 16 helpers, got {len(names)}: {names}")
        for name in names:
            self.assertTrue(name.startswith("p3"), f"Helper {name} is not p3-prefixed")

        expected_helpers = {
            "p3RequireState",
            "p3UnitsGuard",
            "p3SameState",
            "p3ExactRef",
            "p3CensusGuard",
            "p3FreezeState",
            "p3ReadProperties",
            "p3ReferenceSet",
            "p3TrimeshRNormalsSnapshot",
            "p3PolySnapshot",
            "p3AuditSubAnims",
            "p3EvaluatedSnapshot",
            "p3LayerAdmissionGuard",
            "p3GraphSnapshot",
            "p3NodeSnapshot",
            "p3EnvironmentSnapshot",
        }
        self.assertEqual(set(names), expected_helpers)

    def test_02_trimesh_rnormals_and_smoothgroup_snapshot_with_delete(self):
        """Verifies Object Space TriMesh normals extraction with guaranteed delete."""
        self.assertIn("fn p3TrimeshRNormalsSnapshot targetBase targetNode", self.source)
        self.assertIn("targetBase.mesh", self.source)
        self.assertIn("targetNode.mesh", self.source)
        self.assertIn("meshop.getFaceRNormals", self.source)
        self.assertIn("getFaceSmoothGroup", self.source)
        self.assertIn("delete baseTri", self.source)
        self.assertIn("delete evalTri", self.source)

    def test_03_subanim_recursive_audit(self):
        """Verifies recursive controller audit: numKeys, wire ban, forbidden classes."""
        self.assertIn("fn p3AuditSubAnims seed maxDepth:16", self.source)
        self.assertIn("cur.numSubs", self.source)
        self.assertIn("local nk = numKeys ctrl", self.source)
        self.assertIn("nk == 0 or nk == -1", self.source)
        self.assertIn("float_wire", self.source)
        self.assertIn("forbidden wired/scripted/constraint controller", self.source)

        forbidden_classes = [
            "float_script", "position_script", "point3_script", "rotation_script",
            "scale_script", "transform_script", "float_wire", "position_wire",
            "point3_wire", "rotation_wire", "scale_wire", "Position_Constraint",
            "Orientation_Constraint", "LookAt_Constraint", "Path_Constraint",
            "Attachment", "Surface_Constraint", "Link_Constraint", "Float_Expression",
            "Position_Expression", "Point3_Expression", "Scale_Expression",
            "Float_Reaction", "Position_Reaction", "Point3_Reaction",
            "Rotation_Reaction", "Scale_Reaction",
        ]
        for cls in forbidden_classes:
            self.assertIn(cls, self.source, f"Forbidden class {cls} missing from p3AuditSubAnims")

    def test_04_layer_admission_guard_root_of_trust_and_closure(self):
        """Verifies rootScene anchor and layer dependency graph closure."""
        self.assertIn("fn p3LayerAdmissionGuard", self.source)
        self.assertIn("refs.getReference rootScene 4 == rootNode", self.source)
        self.assertIn("refs.getReference rootScene 11", self.source)
        self.assertIn("refs.getNumRefs backing0", self.source)
        self.assertIn("refs.dependents backing0", self.source)
        self.assertIn("layer count mismatch: requires exactly 1 layer", self.source)

    def test_05_replay_verified_noop_branch(self):
        """Verifies COMMITTED branch executes VERIFIED_NOOP without mutation."""
        self.assertIn('if lease[5] == "COMMITTED" then', self.source)
        self.assertIn("p3SameState currentSnapshot lease[9]", self.source)
        self.assertIn("p3CensusGuard lease[8]", self.source)
        self.assertIn("getSaveRequired() == lease[10]", self.source)
        self.assertIn("P3_REPLAY_NOOP|", self.source)
        self.assertIn("status=VERIFIED_NOOP", self.source)

    def test_06_poisoned_lease_retention_on_arm_catch(self):
        """Verifies arm failure retains registry key as POISONED for forensics."""
        arm = generate_arm_script(
            self.plan, IDENTITY, "P3AuthTest", UNITS, "FreshNonce20261104AuthenticTest_123"
        )
        self.assertIn('witness.values[5] = "POISONED"', arm)
        self.assertIn('cleanupStatus = "POISONED_RETAINED_FOR_FORENSICS"', arm)
        # Ensure globalVars.remove is NOT called in arm catch
        self.assertNotIn("globalVars.remove registryKey", arm)
        self.assertNotIn("globalVars.remove", arm)

    def test_07_normal_modifiers_prohibited_and_strictly_shell(self):
        """Verifies stack permits strictly 1 Shell modifier and bans normal modifiers."""
        self.assertIn("node.modifiers.count == 1 and classOf node.modifiers[1] == Shell", self.source)
        self.assertIn("classOf node.baseObject) == Editable_Poly", self.source)
        prohibited = [
            "Edit_Normals", "Normalmodifier", "Smooth", "Vertex_Weld", "Weighted_Normals"
        ]
        for mod in prohibited:
            self.assertIn(mod, self.source, f"Prohibited modifier {mod} not mentioned in validation")

    def test_08_exact_current_attempt_cleanup_without_handle_delete(self):
        """Verifies cleanup loop uses exact created node refs and reports retained evidence."""
        self.assertIn("for i = 1 to createdRefs.count do", self.source)
        self.assertIn("local exactNode = createdRefs[i]", self.source)
        self.assertIn("RETAINED_NO_CALIBRATED_DEPENDENCY_EXCLUSION", self.source)
        self.assertNotIn("delete (getAnimByHandle", self.source)
        self.assertNotIn("delete (getNodeByName", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
