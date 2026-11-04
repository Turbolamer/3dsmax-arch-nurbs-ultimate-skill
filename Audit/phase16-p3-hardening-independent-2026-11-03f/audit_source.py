"""Independent d9 emitted-source observations; never executes MAXScript."""

import hashlib
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
MIRROR = HERE / "d9-fixture"
RUNTIME = MIRROR / "scripts/wall_surface_runtime.py"
assert hashlib.sha256(RUNTIME.read_bytes()).hexdigest() == (
    "d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a"
)
sys.path.insert(0, str(MIRROR / "scripts"))
sys.path.insert(0, str(MIRROR / "Audit"))
sys.path.insert(0, str(MIRROR / "Audit/phase16-p3-runtime-hardening-2026-11-03f"))
from wall_surface_runtime import build_plan, generate_script
from test_phase16_p3_runtime import fixture, UNITS, IDENTITY
from test_protection import interpret_status_expression


walls, dims = fixture()
wall = generate_script(build_plan(walls, dims), IDENTITY, "P3RuntimeOffline", UNITS)
precreate = wall[wall.index('stage = "pre-create"'):wall.index('local node = Editable_Mesh()')]
code = re.sub(r'"(?:\\.|[^"\\])*"|--[^\n]*', '', precreate)
node_reader = wall[wall.index('fn p3NodeSnapshot node'):wall.index('fn p3CensusGuard node')]
entry = wall[wall.index('registryWitness = globalVars.get registryKey'):
             wall.index('stage = "unresolved-prior-attempt"')]
state = {"attemptStarted": False, "unresolvedEntry": False, "censusKnown": True,
         "reportErrors": [], "residual": [], "stage": "entry"}
status = interpret_status_expression(wall, state)
checks = {
    "precreate_has_no_unconditional_require_false_or_bare_throw":
        re.search(r'\bp3RequireState\s+false\b|\bthrow\b', code) is None,
    "attempt_and_building_precede_constructor":
        precreate.index('attemptStarted = true') < precreate.index('lease[5] = "BUILDING"'),
    "node_reader_reaches_evaluated_snapshot_after_comment_not_guard":
        'local evaluatedState = p3EvaluatedSnapshot node' in node_reader and
        re.search(r'\bp3RequireState\s+false\b|\bthrow\b',
                  re.sub(r'"(?:\\.|[^"\\])*"|--[^\n]*', '', node_reader)) is None,
    "nonce_and_identity_guards_precede_prior_building_classification":
        entry.index('registry identity mismatch') < entry.index('missing bounded external lease witness') <
        entry.index('if lease[5] == "BUILDING"'),
    "entry_status_for_modeled_early_guard_failure": status == "P3_REFUSED",
    "success_publication_replaces_attempt_evidence_before_commit":
        wall.index('lease[8] = node') < wall.index('lease[5] = "COMMITTED"'),
    "post_failure_poison_occurs_after_census_and_residual_work":
        wall.index('censusCount = objects.count') < wall.index('lease[5] = "POISONED"') and
        wall.index('CONSTRUCTOR_RETURN_NOT_OBSERVED') < wall.index('lease[5] = "POISONED"'),
}
report = {"scope": "static analysis of generated source; modeled status is not MAXScript execution",
          "runtime_sha256": hashlib.sha256(RUNTIME.read_bytes()).hexdigest(),
          "checks": checks, "modeled_early_guard_status": status,
          "model_assumptions": "entry failure before unresolved flag; attempt false; successful bounded census and no diagnostic errors"}
with (HERE / "source-checks.json").open("x", encoding="utf-8") as out:
    json.dump(report, out, indent=2)
    out.write("\n")
print(json.dumps(report, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
