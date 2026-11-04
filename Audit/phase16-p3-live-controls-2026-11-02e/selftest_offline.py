#!/usr/bin/env python3
"""Offline adapter tests only. Synthetic admissions are NEVER passed to prepare()."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

from prepare_controls import (ADAPTER, EDITS, HERE, ROOT, digest, make_bind, make_edit,
                              make_restore, once, variant, instrument_capture, fresh_harness)
from check_winding_capture import parse_capture

sys.path.insert(0, str(ROOT / "scripts"))
from wall_surface_runtime import build_plan, generate_script

FIXTURE = ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e" / "project"
SOURCE_PATHS = [ROOT / "scripts" / "wall_surface_runtime.py", FIXTURE / "walls.json", FIXTURE / "dimensions.json"]
BEFORE = {str(p): digest(p.read_bytes()) for p in SOURCE_PATHS}


class OfflineAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        walls = json.loads((FIXTURE / "walls.json").read_text())
        dimensions = json.loads((FIXTURE / "dimensions.json").read_text())
        cls.plan = build_plan(walls, dimensions)
        cls.identity = "a" * 64
        cls.namespace = "OfflineAdapterOnly"
        cls.manifest = {"identity": cls.identity, "owner": {"namespace": cls.namespace}}
        cls.original = generate_script(cls.plan, cls.identity, cls.namespace,
                 {"system_type": "millimeters", "system_scale": 1., "cm_per_unit": .1, "units_per_cm": 10.})
        cls.cfg = {"identity": cls.identity, "namespace": cls.namespace, "registry": "__P3W_adapter_test",
                   "control_key": "__P3Audit_adapter_test", "node_handle": 123,
                   "node_name": cls.namespace + "__wall", "artifact_path": "D:/not_executed/wall_surface.ms"}

    def test_real_generator_source_adapters_all_six(self):
        for i, kind in enumerate(("unit_cm_1", "unit_cm_0p1_equal_factor", "corrupt_factor",
                                  "exact_name_collision", "api_create_failure", "reverse_winding")):
            with self.subTest(kind=kind):
                altered, meta = variant(self.original, self.manifest, "Offline_N" + str(i), kind)
                self.assertNotEqual(digest(altered.encode()), digest(self.original.encode()))
                self.assertIn(meta["identity"], altered)
                self.assertIn(meta["registry"], altered)
                self.assertNotIn('local artifactIdentity = "' + self.identity + '"', altered)
                self.assertIn("NEGATIVE TEST ONLY", altered)
                self.assertNotIn("units.SystemType =", altered)
                self.assertNotIn("units.SystemScale =", altered)
                if kind == "reverse_winding":
                    captured = instrument_capture(altered)
                    self.assertIn('auditCapture "grid" node', captured)
                    self.assertIn('auditCapture "base" node', captured)
                    self.assertIn('auditCapture "evaluated" node', captured)
                harness = fresh_harness(HERE / "NOT_EXECUTED.ms", meta, "__OfflineForeignKey")
                self.assertIn("MAIN", harness)
                self.assertNotIn("delete objects", harness)

    def test_all_edit_scripts_have_explicit_separate_restoration(self):
        restored = make_restore(self.cfg)
        for kind in EDITS:
            script = make_edit(self.cfg, kind)
            self.assertIn("REFUSAL_VERIFIED_EDIT_LEFT_IN_PLACE", script)
            self.assertIn("requireRefusal result", script)
            self.assertNotIn("fn restoreOwnSynthetic", script)
            self.assertIn('"' + kind + '": (', restored)
        self.assertIn("intervening edit: restore forbidden", restored)
        self.assertIn("never clear dirty flag", restored)

    def test_binding_never_adopts_by_name(self):
        script = make_bind(self.cfg)
        self.assertIn("actual committed production registry", script)
        self.assertNotIn("getNodeByName", script)

    def test_template_drift_refuses_before_output(self):
        with self.assertRaises(ValueError):
            once("a a", "a", "b")
        altered = self.original.replace("local id = polyop.createVert node point", "changed anchor")
        with self.assertRaises(ValueError):
            variant(altered, self.manifest, "Offline_N7", "api_create_failure")

    def test_current_public_cm_0p1_restriction_is_not_a_live_guard_pass(self):
        with self.assertRaisesRegex(ValueError, "Float32"):
            generate_script(self.plan, self.identity, self.namespace,
                {"system_type": "centimeters", "system_scale": .1, "cm_per_unit": .1, "units_per_cm": 10.})

    def test_capture_parser_requires_all_actual_arrays(self):
        with self.assertRaises(ValueError):
            parse_capture("P3_CONTROL_CAPTURE|stage=grid|vertices=24|faces=15|triangles=0\n")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OfflineAdapterTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    after = {str(p): digest(p.read_bytes()) for p in SOURCE_PATHS}
    print(json.dumps({"scope": "OFFLINE_ADAPTER_ONLY_NO_MAX_OR_POSITIVE_ADMISSION",
                      "adapter": ADAPTER, "before": BEFORE, "after": after,
                      "drift": BEFORE != after}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() and BEFORE == after else 1)
