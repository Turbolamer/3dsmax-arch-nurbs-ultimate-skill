"""Create a byte-verified, isolated copy of the requested d9 offline test setup.

The hardening test was edited concurrently. Reverse only those edits to recover
the earlier *exact* test bytes, verify the author's recorded SHA-256, then run
the untouched bytes in a private mirror. A hash mismatch aborts before writing.
"""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MIRROR = HERE / "d9-fixture"
HARDENING = ROOT / "Audit/phase16-p3-runtime-hardening-2026-11-03f"
EXPECTED_RUNTIME = "d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a"
EXPECTED_OLD_TEST = "36885bad3d566065c8471a4cf8c7dcc6c452de9676e58c03e6cb4f776b83b327"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def cut(data, start, end):
    if data.count(start) != 1 or data.count(end) != 1:
        raise ValueError("cannot uniquely locate edit")
    begin = data.index(start)
    finish = data.index(end, begin)
    return data[:begin] + data[finish:]


runtime = (HARDENING / "wall_surface_runtime.pre-precreate-gate.py.bin").read_bytes()
current_test = (HARDENING / "test_protection.py").read_bytes()
if digest(runtime) != EXPECTED_RUNTIME:
    raise SystemExit("snapshot changed; refuse reconstruction")
test = current_test.decode("utf-8")
test = cut(test, "def precreate_guard(source):\n", "def interpret_status_expression(source, state):\n")
old_interpreter = '''def interpret_status_expression(source, state):
    """Interpret the emitted status selection's small boolean subset only.

    This exercises branches extracted from source, not MAXScript evaluation.
    Unknown grammar/operators refuse rather than being guessed.
    """
    line = next(line.strip() for line in source.splitlines() if line.strip().startswith('local status = if '))
    match = re.fullmatch(r'local status = if (.*?) then "([^"]+)" else if (.*?) then "([^"]+)" else "([^"]+)"', line)
    if not match:
        raise ValueError("unsupported emitted status syntax")

    def read(node):
        if isinstance(node, ast.Name):
            return state[node.id]
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Attribute) and node.attr == 'count':
            return len(read(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not read(node.operand)
        if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.Or, ast.And)):
            values = [bool(read(value)) for value in node.values]
            return any(values) if isinstance(node.op, ast.Or) else all(values)
        if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
            left, right = read(node.left), read(node.comparators[0])
            if isinstance(node.ops[0], ast.Gt):
                return left > right
            if isinstance(node.ops[0], ast.Eq):
                return left == right
        raise ValueError("unsupported emitted predicate")

    def predicate(expr):
        return bool(read(ast.parse(expr, mode='eval').body))

    return match[2] if predicate(match[1]) else match[4] if predicate(match[3]) else match[5]


'''
start = "def interpret_status_expression(source, state):\n"
end = "class ProtectiveSourceTests(unittest.TestCase):\n"
if test.count(start) != 1 or test.count(end) != 1:
    raise SystemExit("interpreter not uniquely located")
begin, finish = test.index(start), test.index(end)
test = test[:begin] + old_interpreter + test[finish:]
test = cut(test, "    def test_pre_gate_snapshot_is_exact_previous_runtime_hash(self):\n",
           "    def test_cleanup_never_promotes_handle_or_deletes_exact_node(self):\n")
case = "                 ({'stage': 'precreate-safety-refusal'}, 'P3_INCOMPLETE_PRECREATE'),\n"
if test.count(case) != 1:
    raise SystemExit("new case not uniquely located")
test = test.replace(case, "", 1)
test = cut(test, "    def test_temporary_precreate_guard_precedes_every_scene_or_lease_mutation(self):\n",
           "    def test_attempt_refs_captured_before_next_risky_operation(self):\n")
test_bytes = test.encode("utf-8")
if digest(test_bytes) != EXPECTED_OLD_TEST:
    raise SystemExit("old test reconstruction hash mismatch: " + digest(test_bytes))

files = {
    "scripts/wall_surface_runtime.py": runtime,
    "scripts/scene_units.py": (ROOT / "scripts/scene_units.py").read_bytes(),
    "Audit/test_phase16_p3_runtime.py": (ROOT / "Audit/test_phase16_p3_runtime.py").read_bytes(),
    "Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py": test_bytes,
    "Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-edit.py.bin":
        (HARDENING / "wall_surface_runtime.pre-edit.py.bin").read_bytes(),
}
for name, data in files.items():
    target = MIRROR / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as out:
        out.write(data)
manifest = {name: digest(data) for name, data in files.items()}
with (HERE / "d9-fixture-manifest.json").open("x", encoding="utf-8") as out:
    json.dump(manifest, out, indent=2)
    out.write("\n")
print(json.dumps(manifest, indent=2))
