"""Top-level discovered authentic runtime contract test suite for recorder.py."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

AUDIT = Path(__file__).resolve().parent
sys.path.insert(0, str(AUDIT / "phase16-p3-auth-tests"))
from test_wall_surface_auth_runtime import WallSurfaceAuthRuntimeTests

if __name__ == "__main__":
    unittest.main(verbosity=2)
