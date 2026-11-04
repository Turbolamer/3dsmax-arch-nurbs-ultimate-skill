# Synthetic poly wall input — offline P2 fixture

`walls.json` is a **hypothetical, test-only input declaration**, not a user
project, generated model, production source, or runtime evidence. It matches
`walls_declaration()` in `Audit/test_phase16_p2_cases.py` for the current
`examples/dimensions.json`: `pavilion-01`, the F-S/F-N/F-W facade endpoints,
and the three design tolerances provide the cross-file test context. The
hypothetical test brief independently supplies the inner-face interpretation,
outward vectors, heights, thickness, IDs, openings, adjacency, epsilons and
topology ceilings; these are synthetic inputs, **not** measurements or inferred
facts about the example's physical building. `source.kind: user_brief`,
`origin: given`, and the timestamp describe that hypothetical test brief only.
Epsilons and topology budgets are not defaults and are not derived from F01.

The `locked` status applies **only to this input document**. The fixture does
not contain a locked poly assembly, `wall_surface.json`, `wall_surface.ms`, a
poly builder, or poly runtime QA. A clean lint of this declaration is not P2
acceptance, a successful build, geometry validation, or evidence from Max.
The input remains dependent on the repository's `examples/` and is not a
standalone pipeline. In particular, do **not** pass this directory directly to
`Audit/test_phase16_p2.py --p2-fixture`: that separate harness explicitly
requires a real locked poly assembly, which does not yet exist.

## Reproduce the input controls

Run the following from the repository root in Bash (including Git Bash on
Windows). It copies `examples/` to an owned temporary directory, replaces the
copied legacy assembly with the existing `draft_assembly()` placeholder, and
checks the tracked `walls.json`. It removes the copied legacy `assembly.ms` to
avoid mistaking it for poly output. `-B` prevents Python bytecode writes. The
temporary directory is cleaned automatically; no existing project file is
modified and Max is not used.

The clean control requires actual `PASS` rows for G-93, G-94 and G-97 with no
overall failures. Its empty draft assembly produces a G-4 warning; G-92 and
G-96 remain SKIP because the assembly/route echo is incomplete. Three negative
controls independently mutate one input each and assert the exact rule and
location. G-97 values are declaration ceilings, not polygon measurements.
The final `--build` check must refuse the draft assembly via G-4 even though
the locked walls themselves pass that status check.

```bash
python -B - <<'PY'
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root / "Audit"))
from test_phase16_p2_cases import draft_assembly, walls_declaration

fixture = root / "specs/fixtures/poly-shell-input/walls.json"
validator = root / "scripts/validate_specs.py"
load = lambda p: json.loads(p.read_text(encoding="utf-8"))
save = lambda p, d: p.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))
approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
temp_parent = str(approved) if os.name == "nt" and approved.is_dir() else None

with tempfile.TemporaryDirectory(prefix="poly-shell-input-", dir=temp_parent) as tmp:
    pipeline = Path(tmp) / "pipeline"
    shutil.copytree(root / "examples", pipeline)
    (pipeline / "assembly.ms").unlink(missing_ok=True)
    dimensions = load(pipeline / "dimensions.json")
    assembly = draft_assembly(load(pipeline / "assembly.json"))
    save(pipeline / "assembly.json", assembly)
    original = load(fixture)
    assert original == walls_declaration(dimensions), "fixture drifted from test generator"
    assert assembly["status"] == "draft"
    assert not (pipeline / "wall_surface.json").exists()
    assert not (pipeline / "wall_surface.ms").exists()

    def validate(label, walls, expected_failure=None, location="", allowed_failures=()):
        save(pipeline / "walls.json", walls)
        result = subprocess.run(
            [sys.executable, "-B", str(validator), "--dir", str(pipeline), "--json"],
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        report = json.loads(result.stdout)
        rows = report["findings"]
        failures = [row for row in rows if row["severity"] == "FAIL"]
        assert result.returncode == report["exit_code"], (label, result.stderr, report)
        if expected_failure is None:
            assert result.returncode == 0 and not failures, (label, failures)
            for rule in ("G-93", "G-94", "G-97"):
                assert any(r["rule"] == rule and r["severity"] == "PASS" for r in rows), (label, rule)
            for rule in ("G-95", "G-98", "G-99", "G-100"):
                assert any(r["rule"] == rule and r["severity"] == "SKIP" for r in rows), (label, rule)
                assert not any(r["rule"] == rule and r["severity"] == "PASS" for r in rows), (label, rule)
            for rule in ("G-92", "G-96"):
                assert any(r["rule"] == rule and r["severity"] == "SKIP" for r in rows), (label, rule)
                assert not any(r["rule"] == rule and r["severity"] == "PASS" for r in rows), (label, rule)
            assert any(r["rule"] == "G-4" and r["severity"] == "WARN" and r["location"] == "assembly.json" for r in rows)
            print(label, "G-93/G-94/G-97 PASS; runtime gates SKIP")
        else:
            assert result.returncode == 1, (label, failures)
            assert any(r["rule"] == expected_failure and location in r["location"] for r in failures), (label, failures)
            assert not any(r["rule"] == expected_failure and r["severity"] == "PASS" for r in rows), (label, rows)
            assert all(r["rule"] in (expected_failure, *allowed_failures) for r in failures), (label, failures)
            print(label, expected_failure, "FAIL as expected")

    validate("locked-input positive", original)
    mutations = (
        ("nonpositive_thickness", "G-93", "wall_runs[0].thickness_cm", (), lambda w: w["wall_runs"][0].__setitem__("thickness_cm", 0)),
        ("negative_topology_budget", "G-97", "wall_runs[0].topology_budget.max_grid_polygons", (), lambda w: w["wall_runs"][0]["topology_budget"].__setitem__("max_grid_polygons", -1)),
        ("overlapping_openings", "G-94", "openings[1]", (), lambda w: w["openings"][1].__setitem__("u_range_cm", list(w["openings"][0]["u_range_cm"]))),
    )
    for name, rule, location, allowed, mutate in mutations:
        bad = copy.deepcopy(original)
        mutate(bad)
        validate(name, bad, rule, location, allowed)

    save(pipeline / "walls.json", original)
    result = subprocess.run(
        [sys.executable, "-B", str(validator), "--dir", str(pipeline), "--json", "--build"],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    report = json.loads(result.stdout)
    assert result.returncode == report["exit_code"] == 1
    for severity, location in (("FAIL", "assembly.json"), ("PASS", "walls.json")):
        assert any(r["rule"] == "G-4" and r["severity"] == severity and r["location"] == location
                   for r in report["findings"]), (severity, location, report["summary"])
    print("build gate: locked walls accepted as input, draft assembly refused")
PY
```

To run the **original** acceptance method for the same 13 input mutations,
without creating or claiming a locked assembly, use this adapter. It replaces
only `poly_fixture()` with a temporary `examples/` copy containing this input
and `draft_assembly()`. It deliberately does not run assembly, manifest or
runtime-acceptance methods; the assertion on 13 fixture calls and zero skips
prevents a partial mutation run from looking successful.

```bash
python -B - <<'PY'
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root / "Audit"))
import test_phase16_p2 as acceptance
from test_phase16_p2_cases import draft_assembly, write_json

approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
if os.name == "nt" and approved.is_dir():
    tempfile.tempdir = str(approved)
fixture = root / "specs/fixtures/poly-shell-input/walls.json"

class LockedInputOnly(acceptance.PolyAcceptance):
    __unittest_skip__ = False

    def poly_fixture(self):
        self.fixture_calls = getattr(self, "fixture_calls", 0) + 1
        pipeline = self.clone(acceptance.FIXTURES["examples"])
        assembly = acceptance.load(pipeline / "assembly.json")
        write_json(pipeline / "assembly.json", draft_assembly(assembly))
        (pipeline / "assembly.ms").unlink(missing_ok=True)
        shutil.copyfile(fixture, pipeline / "walls.json")
        self.assertFalse((pipeline / "wall_surface.json").exists())
        self.assertFalse((pipeline / "wall_surface.ms").exists())
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, acceptance.diagnostic(report))
        for rule in ("G-93", "G-94", "G-97"):
            self.assertTrue(self.rows(report, rule, "PASS"), rule)
            self.assertFalse(self.rows(report, rule, "FAIL"), rule)
        return pipeline

test = LockedInputOnly("test_locked_wall_negative_mutations")
result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
assert result.wasSuccessful() and not result.skipped and test.fixture_calls == 13, (result, getattr(test, "fixture_calls", 0))
print("Original acceptance method: 13 locked-input subtests, draft assembly; no skips")
PY
```

These are narrow, offline controls, not an exhaustive validator audit. Other
acceptance tests, provenance controls, future builder integration and live QA
remain separate.
