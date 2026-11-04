"""Independent OFFLINE audit checks for the Phase 16 P3 layer-reader candidate.

This file deliberately does not import production runtime code, invoke Max, call
an MCP server, parse MAXScript as Max, or mutate any scene.  The source checks
characterize the two candidate texts; the small Python model is an independent
fail-closed policy model used only for negative controls.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import math
import re
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_DIR = ROOT / "Audit" / "phase16-p3-layer-reader-2026-11-03f"
OLD_MS = CANDIDATE_DIR / "layer_reader.ms"
P31_MS = CANDIDATE_DIR / "layer_reader_p31_offline.ms"
EMITTER = CANDIDATE_DIR / "emitter_fragment.py"
EVIDENCE = ROOT / "Audit" / "_phase16-p3-layer-readonly-2026-11-03f.json"
MEMBERSHIP_PROBE = ROOT / "Audit" / "phase16-p3-main-probes-2026-11-03f" / "layer-membership.ms"


EXPECTED_HASHES = {
    "layer_reader.ms": "0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7",
    "layer_reader_p31_offline.ms": "5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2",
    "emitter_fragment.py": "105cbcba7771175e0291a421dea4f874c66b9f51ddb0db3fd5dba340cb8b16b9",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _profile_block(source: str, name: str) -> str:
    match = re.search(
        rf"\blocal\s+{re.escape(name)}\s*=\s*#\((.*?)\n\)",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing MAXScript profile {name}")
    return match.group(1)


def _profile_pairs(source: str, name: str) -> list[tuple[str, str]]:
    return re.findall(
        r"#\(\s*#([A-Za-z0-9_]+)\s*,\s*#([A-Za-z0-9_]+)\s*\)",
        _profile_block(source, name),
    )


def _maxscript_delimiters_balanced(source: str) -> bool:
    """A lexical delimiter smoke check, not a MAXScript parser."""

    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    stack: list[str] = []
    in_string = False
    escaped = False
    in_comment = False
    index = 0
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if in_comment:
            if char == "\n":
                in_comment = False
            index += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == "-" and next_char == "-":
            in_comment = True
            index += 2
            continue
        if char == '"':
            in_string = True
        elif char in opening:
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
        index += 1
    return not in_string and not stack and not in_comment


@dataclass(eq=False)
class Ref:
    handle: int
    kind: str
    alive: bool = True


class Incomplete(Exception):
    pass


def _observed_profiles() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    type_map = {
        "BooleanClass": "bool",
        "Integer": "integer",
        "Float": "float",
        "Name": "name",
        "String": "string",
        "Color": "color",
        "MixinInterface": "gi",
        "Base_LayerBase_Layer": "backing",
    }
    sources = (
        ("layer_properties", r"p=([^;|]+);cls=([^;|]+)"),
        ("backing_reference_enumeration", r"refProp=([^;|]+);class=([^;|]+)"),
        ("gi_properties", r"p=([^;|]+);cls=([^;|]+)"),
    )
    output: list[dict[str, str]] = []
    for evidence_key, pattern in sources:
        observed = re.findall(pattern, evidence[evidence_key]["result"])
        output.append({name.lower(): type_map[class_name] for name, class_name in observed})
    return output[0], output[1], output[2]


def _model_fixture() -> dict:
    interface, backing, gi = _observed_profiles()
    node = Ref(11, "node")
    root = Ref(12, "root")
    layer = Ref(13, "layer")
    manager = Ref(14, "manager")
    refs = (node, root, layer, manager)

    def value(kind: str, backing_ref: Ref):
        return {
            "bool": False,
            "integer": 0,
            "float": 1.0,
            "name": "viewport",
            "string": "0",
            "color": (88, 144, 225, 255),
            "backing": backing_ref,
            "gi": None,
        }[kind]

    def fields(profile: dict[str, str], backing_ref: Ref) -> dict:
        result = {key: value(kind, backing_ref) for key, kind in profile.items()}
        if "inodegiproperties" in result:
            result["inodegiproperties"] = fields(gi, backing_ref)
        return result

    return {
        "interface_profile": interface,
        "backing_profile": backing,
        "gi_profile": gi,
        "node": node,
        "expected_node": node,
        "root": root,
        "expected_root": root,
        "backing": layer,
        "expected_backing": layer,
        "manager": manager,
        "handle_map": {ref.handle: ref for ref in refs},
        "scene": [node],
        "members": [node],
        "parent": None,
        "children": 0,
        "dependencies": [root, manager, node],
        "interface": fields(interface, layer),
        "backing_state": fields(backing, layer),
    }


def _model_exact(state: dict, ref: Ref) -> tuple[Ref, int, str]:
    if not isinstance(ref, Ref) or not ref.alive or state["handle_map"].get(ref.handle) is not ref:
        raise Incomplete("reference/handle")
    return ref, ref.handle, ref.kind


def _model_scalar(value, kind: str):
    if kind == "bool":
        valid = type(value) is bool
    elif kind == "integer":
        valid = type(value) is int
    elif kind == "float":
        valid = type(value) is float and math.isfinite(value) and abs(value) < 1.0e38
    elif kind in ("name", "string"):
        valid = type(value) is str and (kind != "string" or len(value) <= 4096)
    elif kind == "color":
        valid = (
            type(value) is tuple
            and len(value) == 4
            and all(type(component) in (int, float) and math.isfinite(component) for component in value)
        )
    else:
        valid = False
    if not valid:
        raise Incomplete("type/value")
    if kind == "string":
        return kind, str(value)
    return kind, value


def _model_fields(state: dict, values: dict, profile: dict[str, str], backing: Ref) -> tuple:
    if type(values) is not dict or set(values) != set(profile):
        raise Incomplete("property enumeration")
    result = []
    for key, kind in profile.items():
        current = values[key]
        if kind == "gi":
            current = _model_fields(state, current, state["gi_profile"], backing)
        elif kind == "backing":
            if current is not state["expected_backing"]:
                raise Incomplete("backing changed")
            current = ("same_exact_backing", backing.handle)
        else:
            current = _model_scalar(current, kind)
        result.append((key, current))
    return tuple(result)


def _strict_model_snapshot(state: dict) -> tuple:
    """Independent contract model; it is intentionally stricter than P31."""

    try:
        node = state["node"]
        root = state["root"]
        backing = state["backing"]
        manager = state["manager"]
        if node is not state["expected_node"] or root is not state["expected_root"]:
            raise Incomplete("witness")
        if backing is not state["expected_backing"]:
            raise Incomplete("backing witness")
        if len({id(node), id(root), id(backing), id(manager)}) != 4:
            raise Incomplete("ambiguous witness")
        identities = tuple(_model_exact(state, ref) for ref in (node, root, backing, manager))
        if state["scene"] != [node] or state["members"] != [node]:
            raise Incomplete("scene/membership")
        if state["parent"] is not None or state["children"] != 0:
            raise Incomplete("hierarchy")
        deps = state["dependencies"]
        if len(deps) not in (2, 3):
            raise Incomplete("dependency count")
        if sum(dep is root for dep in deps) != 1 or sum(dep is manager for dep in deps) != 1:
            raise Incomplete("root/manager dependency")
        if sum(dep is node for dep in deps) > 1 or any(
            dep is not root and dep is not manager and dep is not node for dep in deps
        ):
            raise Incomplete("foreign dependency")
        payload = (
            identities,
            _model_fields(state, state["interface"], state["interface_profile"], backing),
            _model_fields(state, state["backing_state"], state["backing_profile"], backing),
        )
        return "INCOMPLETE", "PARTIAL_CAPTURE_ONLY", payload
    except (Incomplete, KeyError, TypeError, ValueError):
        return "INCOMPLETE", "READ_FAILED"


def _strict_model_compare(a: tuple, b: tuple, state: dict) -> tuple:
    if (
        len(a) != 3
        or len(b) != 3
        or a[:2] != ("INCOMPLETE", "PARTIAL_CAPTURE_ONLY")
        or b[:2] != ("INCOMPLETE", "PARTIAL_CAPTURE_ONLY")
    ):
        return "INCOMPLETE", "UNCOMPARABLE"
    for snapshot in (a, b):
        for ref, handle, kind in snapshot[2][0]:
            current = state["handle_map"].get(handle)
            if current is not ref or not ref.alive or ref.handle != handle or ref.kind != kind:
                return "INCOMPLETE", "UNCOMPARABLE"
    return "INCOMPLETE", "OBSERVED_MATCH" if a == b else "OBSERVED_DIFFERENT"


class IndependentLayerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.old = OLD_MS.read_text(encoding="utf-8")
        cls.p31 = P31_MS.read_text(encoding="utf-8")
        cls.emitter = EMITTER.read_text(encoding="utf-8")

    def test_frozen_candidate_hashes_are_reproducible(self) -> None:
        for name, expected in EXPECTED_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(_sha256(CANDIDATE_DIR / name), expected)

    def test_profile_counts_and_types_match_raw_measured_evidence(self) -> None:
        observed = _observed_profiles()
        for source, names in ((self.old, ("p3LayerInterfaceProfile", "p3LayerBackingProfile", "p3LayerGIProfile")),
                              (self.p31, ("p31InterfaceProfile", "p31BackingProfile", "p31GIProfile"))):
            with self.subTest(source=names[0]):
                actual = tuple({key.lower(): kind.lower() for key, kind in _profile_pairs(source, name)} for name in names)
                self.assertEqual(actual, observed)
                self.assertEqual(len(actual[0]), 33)
                self.assertEqual(len(actual[1]), 34)
                self.assertEqual(len(actual[2]), 18)
                self.assertEqual(set(actual[1]) - set(actual[0]), {"degrade"})

    def test_lexical_delimiter_smoke_is_not_a_parse_or_filein_result(self) -> None:
        self.assertTrue(_maxscript_delimiters_balanced(self.old))
        self.assertTrue(_maxscript_delimiters_balanced(self.p31))
        ast.parse(EMITTER.read_text(encoding="utf-8"))

    def test_finding_old_emitter_pins_old_reader_not_p31_reader(self) -> None:
        old_hash = EXPECTED_HASHES["layer_reader.ms"]
        p31_hash = EXPECTED_HASHES["layer_reader_p31_offline.ms"]
        self.assertIn(f'READER_SHA256 = "{old_hash}"', self.emitter)
        self.assertNotIn(p31_hash, self.emitter)

    def test_finding_old_reader_snapshot_keeps_live_reference_objects(self) -> None:
        self.assertIn("#(value, h, classOf value)", self.old)
        self.assertIn("local nodeRef = p3LayerExactRef node", self.old)
        self.assertIn("local rootRef = p3LayerExactRef expectedRoot", self.old)
        self.assertIn("local backingRef = p3LayerExactRef expectedBacking", self.old)
        self.assertIn("local managerRef = p3LayerExactRef expectedManager", self.old)

    def test_finding_old_comparator_cannot_enforce_fresh_snapshot_provenance(self) -> None:
        compare = self.old.split("fn p3LayerSame a b =", 1)[1]
        self.assertIn("p3LayerValidatePayload a[4]", compare)
        self.assertIn("p3LayerValidatePayload b[4]", compare)
        self.assertNotIn("p3LayerReadOnce", compare)
        self.assertNotIn("p3LayerSnapshot", compare)
        self.assertNotIn("expectedBacking", compare)

    def test_finding_manager_witness_is_not_bound_to_actual_layer_manager(self) -> None:
        old_read = self.old.split("fn p3LayerReadOnce", 1)[1].split("fn p3LayerSnapshot", 1)[0]
        p31_read = self.p31.split("fn p31ReadDependencies", 1)[1].split("fn p31ReadOnce", 1)[0]
        self.assertNotRegex(old_read, r"expectedManager\s*==\s*LayerManager")
        self.assertNotRegex(p31_read, r"managerWitness\s*\[1\]\s*==\s*LayerManager")
        self.assertIn("managerHits == 1", old_read)
        self.assertIn("managerHits == 1", p31_read)

    def test_finding_p31_get_num_nodes_is_not_in_measured_membership_control(self) -> None:
        self.assertIn("layer.getNumNodes()", self.p31)
        measured_probe = MEMBERSHIP_PROBE.read_text(encoding="utf-8")
        self.assertNotIn("getNumNodes", measured_probe)
        self.assertNotIn("getNumNodes", EVIDENCE.read_text(encoding="utf-8"))

    def test_finding_p31_has_no_global_scene_census_guard(self) -> None:
        read_once = self.p31.split("fn p31ReadOnce", 1)[1].split("fn p31DetachedEqual", 1)[0]
        self.assertNotIn("objects.count", read_once)
        self.assertNotIn("selection.count", read_once)
        self.assertIn("local members = p31ReadMembers", read_once)

    def test_finding_nested_gi_is_value_profile_only_without_identity_marker(self) -> None:
        old_gi = self.old.split("fn p3LayerReadGI", 1)[1].split("fn p3LayerReadProps", 1)[0]
        p31_gi = self.p31.split("fn p31ReadGI", 1)[1].split("fn p31ReadProperties", 1)[0]
        self.assertNotIn("p3LayerExactRef", old_gi)
        self.assertNotIn("p31ExactWitness", p31_gi)
        self.assertIn("p31CheckProfile gi p31GIProfile", p31_gi)

    def test_finding_reader_does_not_admit_units_selection_or_file_context(self) -> None:
        for source, marker in ((self.old, "fn p3LayerReadOnce"), (self.p31, "fn p31ReadOnce")):
            body = source.split(marker, 1)[1]
            self.assertNotIn("units.", body)
            self.assertNotIn("selection", body)
            self.assertNotIn("maxFilePath", body)
            self.assertNotIn("maxFileName", body)

    def test_candidate_statuses_are_incomplete_only(self) -> None:
        for source in (self.old, self.p31):
            self.assertNotIn('"PASS"', source)
            self.assertIn("INCOMPLETE", source)
        self.assertIn("INCOMPLETE_REPLAY", self.emitter)
        self.assertIn("P3_LAYER_INCOMPLETE", self.emitter)

    def test_original_suite_does_not_kill_in_memory_finite_guard_mutant(self) -> None:
        # Characterization of test strength, not execution of the MAXScript.
        # The candidate file and emitter are NEVER changed on disk. The hash pin
        # is adjusted only in the isolated in-memory module, so this checks the
        # behavior/model assertions rather than the intentional byte lock.
        original_line = 'p3LayerRequire (value == value and abs value < 1.0e38) "nonfinite/out-of-range numeric value"'
        mutant_line = 'p3LayerRequire true "nonfinite/out-of-range numeric value"'
        self.assertEqual(self.old.count(original_line), 1)
        mutant = self.old.replace(original_line, mutant_line).encode("utf-8")
        self.assertNotEqual(hashlib.sha256(mutant).hexdigest(), EXPECTED_HASHES["layer_reader.ms"])

        spec = importlib.util.spec_from_file_location(
            "independent_mutant_suite", CANDIDATE_DIR / "test_candidate.py"
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        module.emitter.READER_SHA256 = hashlib.sha256(mutant).hexdigest()
        original_read_bytes = Path.read_bytes

        def substitute_in_memory(path: Path) -> bytes:
            if path.resolve() == OLD_MS.resolve():
                return mutant
            return original_read_bytes(path)

        with patch.object(Path, "read_bytes", substitute_in_memory):
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.CandidateTests)
            result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertEqual(result.testsRun, 14)
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.skipped, [])
        self.assertEqual(_sha256(OLD_MS), EXPECTED_HASHES["layer_reader.ms"])

    def test_p31_structural_suite_does_not_kill_in_memory_type_guard_mutant(self) -> None:
        # As above, this is an in-memory mutation of source text, NOT execution
        # of the changed MAXScript and NOT an edit of the candidate on disk.
        original_line = 'p31Require (cls == Integer or cls == Float) "unsupported color component"'
        mutant_line = 'p31Require true "unsupported color component"'
        self.assertEqual(self.p31.count(original_line), 1)
        mutant = self.p31.replace(original_line, mutant_line)
        self.assertNotEqual(hashlib.sha256(mutant.encode("utf-8")).hexdigest(), EXPECTED_HASHES["layer_reader_p31_offline.ms"])

        spec = importlib.util.spec_from_file_location(
            "independent_p31_mutant_suite", CANDIDATE_DIR / "test_p31_offline.py"
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        original_read_text = Path.read_text

        def substitute_in_memory(path: Path, *args, **kwargs) -> str:
            if path.resolve() == P31_MS.resolve():
                return mutant
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", substitute_in_memory):
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.P31OfflineStructuralTests)
            result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertEqual(result.testsRun, 14)
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.skipped, [])
        self.assertEqual(_sha256(P31_MS), EXPECTED_HASHES["layer_reader_p31_offline.ms"])

    def test_model_equal_mutate_restore_is_fail_closed_and_detached(self) -> None:
        state = _model_fixture()
        baseline = _strict_model_snapshot(state)
        self.assertEqual(baseline[1], "PARTIAL_CAPTURE_ONLY")

        state["interface"]["name"] = "renamed"
        changed = _strict_model_snapshot(state)
        self.assertEqual(_strict_model_compare(baseline, changed, state), ("INCOMPLETE", "OBSERVED_DIFFERENT"))

        state["interface"]["name"] = "0"
        restored = _strict_model_snapshot(state)
        self.assertEqual(_strict_model_compare(baseline, restored, state), ("INCOMPLETE", "OBSERVED_MATCH"))

    def test_model_rejects_unknown_missing_wrong_nonfinite_and_nested_fields(self) -> None:
        mutations = []

        state = _model_fixture()
        del state["interface"]["name"]
        mutations.append(state)

        state = _model_fixture()
        state["backing_state"]["unexpected"] = True
        mutations.append(state)

        state = _model_fixture()
        state["interface"]["visibility"] = float("nan")
        mutations.append(state)

        state = _model_fixture()
        state["backing_state"]["inodegiproperties"]["gimeshsize"] = float("inf")
        mutations.append(state)

        state = _model_fixture()
        state["interface"]["inodegiproperties"] = None
        mutations.append(state)

        for mutated in mutations:
            with self.subTest(mutation=len(mutations)):
                self.assertEqual(_strict_model_snapshot(mutated), ("INCOMPLETE", "READ_FAILED"))

    def test_model_rejects_stale_replacement_foreign_members_and_dependencies(self) -> None:
        state = _model_fixture()
        replacement = Ref(state["backing"].handle, "layer")
        state["backing"] = replacement
        self.assertEqual(_strict_model_snapshot(state), ("INCOMPLETE", "READ_FAILED"))

        state = _model_fixture()
        state["scene"].append(Ref(15, "foreign-node"))
        self.assertEqual(_strict_model_snapshot(state), ("INCOMPLETE", "READ_FAILED"))

        state = _model_fixture()
        state["members"] = [Ref(16, "foreign-node")]
        self.assertEqual(_strict_model_snapshot(state), ("INCOMPLETE", "READ_FAILED"))

        state = _model_fixture()
        state["dependencies"].append(Ref(17, "foreign-dependent"))
        self.assertEqual(_strict_model_snapshot(state), ("INCOMPLETE", "READ_FAILED"))

        state = _model_fixture()
        state["handle_map"][state["backing"].handle] = Ref(state["backing"].handle, "replacement")
        self.assertEqual(_strict_model_snapshot(state), ("INCOMPLETE", "READ_FAILED"))

        state = _model_fixture()
        before = _strict_model_snapshot(state)
        repeat = _strict_model_snapshot(state)
        state["handle_map"][state["backing"].handle] = Ref(state["backing"].handle, "layer")
        self.assertEqual(_strict_model_compare(before, repeat, state), ("INCOMPLETE", "UNCOMPARABLE"))


if __name__ == "__main__":
    unittest.main()
