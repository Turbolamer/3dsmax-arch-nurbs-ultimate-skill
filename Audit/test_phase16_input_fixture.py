#!/usr/bin/env python3
"""Run the original wall-input mutation cases without inventing a poly output.

The input is explicitly synthetic.  Its temporary assembly is an empty draft,
not a produced or locked assembly.  Max and runtime QA are not exercised.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Audit"))
import test_phase16_p2 as acceptance  # noqa: E402
from test_phase16_p2_cases import draft_assembly, write_json  # noqa: E402

FIXTURE = ROOT / "specs/fixtures/poly-shell-input/walls.json"
VALIDATOR = ROOT / "scripts/validate_specs.py"


class LockedInputOnly(acceptance.PolyAcceptance):
    __unittest_skip__ = False

    def poly_fixture(self) -> Path:
        self.fixture_calls = getattr(self, "fixture_calls", 0) + 1
        pipeline = self.clone(acceptance.FIXTURES["examples"])
        assembly = acceptance.load(pipeline / "assembly.json")
        write_json(pipeline / "assembly.json", draft_assembly(assembly))
        (pipeline / "assembly.ms").unlink(missing_ok=True)
        shutil.copyfile(FIXTURE, pipeline / "walls.json")
        self.assertFalse((pipeline / "wall_surface.json").exists())
        self.assertFalse((pipeline / "wall_surface.ms").exists())
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, acceptance.diagnostic(report))
        for rule in ("G-93", "G-94", "G-97"):
            self.assertTrue(self.rows(report, rule, "PASS"), rule)
            self.assertFalse(self.rows(report, rule, "FAIL"), rule)
        return pipeline


if __name__ == "__main__":
    parent = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
    if os.name == "nt" and parent.is_dir():
        tempfile.tempdir = str(parent)
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (FIXTURE, VALIDATOR)}
    test = LockedInputOnly("test_locked_wall_negative_mutations")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
    after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before}
    if before != after:
        print("INCOMPLETE: fixture or validator changed during run", file=sys.stderr)
        sys.exit(1)
    if not result.wasSuccessful() or result.skipped or getattr(test, "fixture_calls", 0) != 13:
        print("INCOMPLETE: not all 13 input-only subtests ran without skips", file=sys.stderr)
        sys.exit(1)
    print("13 input-only cases, no skips; assembly was a synthetic draft, not poly output.")
