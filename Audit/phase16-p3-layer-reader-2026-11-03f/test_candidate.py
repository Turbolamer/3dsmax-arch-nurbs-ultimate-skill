"""Static source checks plus an independent Python model, not a Max interpreter.

Run from any directory: python -B <this-file> -v
The model uses synthetic references, not Max instances. No Max API is called.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import re
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("layer_emitter_candidate", HERE / "emitter_fragment.py")
emitter = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(emitter)


# Independently transcribed from the read-only evidence, not extracted from the
# candidate. Dict equality is case-insensitive here as MAXScript Names are.
_LAYER_BOOL = """on Lock current isGIExcluded renderable inheritVisibility primaryVisibility
secondaryVisibility receiveshadows castShadows applyAtmospherics renderOccluded ishidden
isfrozen boxmode backfacecull alledges vertexTicks showTrajectory xray ignoreExtents
showFrozenInGray showVertexColors vertexColorsShaded motionBlurOn""".split()
_GI_BOOL = """isGIExcluded isGIOccluder isGIReceiver isGIDiffuse isGISpecular
GIUseGlobalMeshing GIMeshingEnabled isGIExcludedFromRegather storeIllumToMesh GIByLayer
GIUseAdaptiveSubdivision""".split()


def expected_profiles():
    layer = {name.lower(): "bool" for name in _LAYER_BOOL}
    layer.update({"wirecolor": "color", "name": "string", "visibility": "float",
                  "imagemotionblurmultiplier": "float", "motionblur": "name", "display": "name",
                  "inodegiproperties": "gi", "layerasreftarg": "backing"})
    backing = dict(layer, degrade="bool")
    gi = {name.lower(): "bool" for name in _GI_BOOL}
    gi.update({"nbgirefinesteps": "integer", "nbgirefinestepsdone": "integer",
               "gimeshsize": "float", "giraymult": "float", "giminmeshsize": "float",
               "giinitialmeshsize": "float", "gicontrastthreshold": "float"})
    return layer, backing, gi


LAYER, BACKING, GI = expected_profiles()


def parsed_profile(source, variable):
    match = re.search(r"\blocal\s+" + re.escape(variable) + r"\s*=\s*#\((.*?)\n\)", source, re.S | re.I)
    if not match:
        raise ValueError("profile missing")
    pairs = re.findall(r"#\(\s*#([A-Za-z0-9_]+)\s*,\s*#([A-Za-z0-9_]+)\s*\)", match.group(1))
    result = {name.lower(): kind.lower() for name, kind in pairs}
    if len(pairs) != len(result):
        raise ValueError("duplicate names")
    return result


class Incomplete(Exception):
    pass


class Ref:
    """Synthetic stable identity: handles intentionally may be recycled in tests."""
    def __init__(self, handle, kind):
        self.handle, self.kind, self.alive = handle, kind, True


def values_for(profile, backing):
    values = {}
    for key, kind in profile.items():
        values[key] = {"bool": False, "integer": 0, "float": 1.0, "name": "viewport",
                       "string": "0", "color": (88, 144, 225, 255),
                       "backing": backing, "gi": None}[kind]
    if "inodegiproperties" in values:
        values["inodegiproperties"] = values_for(GI, backing)
    return values


def fixture():
    node, root, backing, manager = (Ref(11, "node"), Ref(12, "root"),
                                    Ref(13, "layer"), Ref(14, "manager"))
    return {"node": node, "expected_node": node, "root": root, "expected_root": root,
            "backing": backing, "expected_backing": backing, "manager": manager,
            "handle_map": {r.handle: r for r in (node, root, backing, manager)},
            "count": 1, "parent": None, "children": 0, "members": [node],
            "scene": [node],
            "outgoing": 0, "deps": [manager, root, node],
            "interface": values_for(LAYER, backing), "target": values_for(BACKING, backing)}


def read_fixture(state):
    """Independent bounded model of intended policy; output never implies PASS."""
    def exact(ref):
        if not isinstance(ref, Ref) or not ref.alive or state["handle_map"].get(ref.handle) is not ref:
            raise Incomplete("reference/handle")
        return (ref, ref.handle, ref.kind)

    def scalar(value, kind):
        if kind == "bool":
            valid = type(value) is bool
        elif kind == "integer":
            valid = type(value) is int
        elif kind == "float":
            valid = type(value) is float and math.isfinite(value) and abs(value) < 1e38
        elif kind in ("name", "string"):
            valid = type(value) is str and (kind != "string" or len(value) <= 4096)
        elif kind == "color":
            valid = (type(value) is tuple and len(value) == 4 and all(
                type(x) in (int, float) and math.isfinite(x) and abs(x) < 1e38 for x in value))
        else:
            valid = False
        if not valid:
            raise Incomplete("type/value")
        return (kind, value)

    def fields(values, profile):
        if type(values) is not dict or set(values) != set(profile):
            raise Incomplete("property enumeration")
        out = []
        for key, kind in profile.items():
            value = values[key]
            if kind == "gi":
                value = fields(value, GI)
            elif kind == "backing":
                if value is not state["expected_backing"]:
                    raise Incomplete("backing changed")
                value = exact(value)
            else:
                value = scalar(value, kind)
            out.append((key, value))
        return tuple(out)

    try:
        node, root, backing, manager = (state[k] for k in ("node", "root", "backing", "manager"))
        if (node is not state["expected_node"] or root is not state["expected_root"] or
                backing is not state["expected_backing"] or len({id(r) for r in (node, root, backing, manager)}) != 4):
            raise Incomplete("witness")
        identities = tuple(exact(r) for r in (node, root, backing, manager))
        if (state["count"] != 1 or len(state["scene"]) != 1 or state["scene"][0] is not node or
                state["parent"] is not None or state["children"] != 0 or
                len(state["members"]) != 1 or state["members"][0] is not node or state["outgoing"] != 0):
            raise Incomplete("membership/hierarchy")
        deps = state["deps"]
        if (len(deps) not in (2, 3) or sum(d is root for d in deps) != 1 or
                sum(d is manager for d in deps) != 1 or sum(d is node for d in deps) > 1 or
                any(d is not root and d is not manager and d is not node for d in deps)):
            raise Incomplete("dependencies")
        result = (identities, (node, node.handle, node.kind), sum(d is node for d in deps),
                  fields(state["interface"], LAYER), fields(state["target"], BACKING))
        return ("INCOMPLETE", "PARTIAL_CAPTURE_ONLY", result)
    except (Incomplete, KeyError, TypeError, ValueError):
        return ("INCOMPLETE", "READ_FAILED")


def compare_model(a, b, handle_map=None):
    if (len(a) != 3 or len(b) != 3 or a[:2] != ("INCOMPLETE", "PARTIAL_CAPTURE_ONLY") or
            b[:2] != ("INCOMPLETE", "PARTIAL_CAPTURE_ONLY")):
        return ("INCOMPLETE", "UNCOMPARABLE")
    # Validate operational handles again; a stale record cannot prove sameness.
    for snapshot in (a, b):
        for ref, handle, kind in snapshot[2][0]:
            if (not ref.alive or ref.handle != handle or ref.kind != kind or
                    (handle_map is not None and handle_map.get(handle) is not ref)):
                return ("INCOMPLETE", "UNCOMPARABLE")
    return ("INCOMPLETE", "OBSERVED_MATCH" if a[2] == b[2] else "OBSERVED_DIFFERENT")


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = emitter.emit_local_helpers()

    def test_profiles_match_independently_transcribed_evidence(self):
        self.assertEqual((len(LAYER), len(BACKING), len(GI)), (33, 34, 18))
        self.assertEqual(parsed_profile(self.source, "p3LayerInterfaceProfile"), LAYER)
        self.assertEqual(parsed_profile(self.source, "p3LayerBackingProfile"), BACKING)
        self.assertEqual(parsed_profile(self.source, "p3LayerGIProfile"), GI)
        self.assertEqual(set(BACKING) - set(LAYER), {"degrade"})

    def test_helper_is_local_and_emitted_in_wrapper_with_fail_closed_stubs(self):
        self.assertIn("fn p3LayerSnapshot ", self.source)
        self.assertIn("fn p3LayerSame ", self.source)
        self.assertNotRegex(self.source, r"(?im)^\s*(?:global|struct)\s")
        wrapper = emitter.emit_example_wrapper()
        self.assertLess(wrapper.index("(\n"), wrapper.index("fn p3LayerSnapshot"))
        self.assertIn('throw "P3_LAYER_INCOMPLETE|example', wrapper)
        self.assertIn('throw "P3_LAYER_INCOMPLETE|layer closure', emitter.INITIAL_CAPTURE)
        self.assertIn('throw "INCOMPLETE_REPLAY|', emitter.REPLAY_OBSERVATION)

    def test_emitter_rejects_file_injection_or_byte_change(self):
        original = Path.read_bytes
        def injected(path):
            raw = original(path)
            return raw + b'\nprint "INJECTED"\n' if path.name == "layer_reader.ms" else raw
        with patch.object(Path, "read_bytes", injected):
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                emitter.emit_local_helpers()
        with self.assertRaises(TypeError):
            emitter.emit_local_helpers("node); delete objects")

    def test_exact_guards_and_no_backing_recursion(self):
        for token in ("getAnimByHandle h", "(getHandleByAnim resolved) == h", "layer = node.layer",
                      "actualBacking = layer.layerAsRefTarg", "actualBacking == expectedBacking and p3LayerTreeEqual actualBackingRef backingRef", "members.count == 1 and members[1] == expectedNode",
                      "sceneNodes.count == 1 and sceneNodes[1] == expectedNode",
                      "rootHits == 1 and managerHits == 1 and nodeHits <= 1",
                      "p3LayerValidatePayload a[4]", "p3LayerValidatePayload b[4]",
                      "names.count == profile.count", "duplicates == 1"):
            self.assertIn(token, self.source)
        block = self.source.split("else if spec[2] == #backing then", 1)[1].split("else detached", 1)[0]
        self.assertIn("p3LayerExactRef value", block)
        self.assertNotIn("p3LayerReadProps value", block)
        self.assertNotIn("getLayerFromName", self.source)
        self.assertNotIn("execute ", self.source)

    def test_candidate_detaches_both_sides_and_validates_before_comparison(self):
        for token in (
            "local interfaceProps = p3LayerReadProps layer p3LayerInterfaceProfile expectedBacking",
            "local backingProps = p3LayerReadProps expectedBacking p3LayerBackingProfile expectedBacking",
            'detached = #("gi", p3LayerReadGI value)',
            "local a = p3LayerReadOnce node expectedNode expectedBacking expectedRoot expectedManager",
            "local b = p3LayerReadOnce node expectedNode expectedBacking expectedRoot expectedManager",
            "p3LayerRequire (p3LayerTreeEqual a b)",
            "p3LayerValidatePropRecords payload[9] p3LayerInterfaceProfile payload[3]",
            "p3LayerValidatePropRecords payload[10] p3LayerBackingProfile payload[3]",
            'if equal then "OBSERVED_MATCH" else "OBSERVED_DIFFERENT"',
        ):
            self.assertIn(token, self.source)
        compare = self.source.split("fn p3LayerSame a b =", 1)[1]
        self.assertLess(compare.index("p3LayerValidatePayload b[4]"), compare.index("p3LayerTreeEqual a[4] b[4]"))
        self.assertIn('"P3_LAYER_COMPARE_1", "INCOMPLETE"', compare)

    def test_repeat_and_detached_snapshots_not_live_aliases(self):
        state = fixture()
        before = read_fixture(state)
        self.assertEqual(before[1], "PARTIAL_CAPTURE_ONLY")
        self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "OBSERVED_MATCH"))
        state["interface"]["lock"] = True
        self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "OBSERVED_DIFFERENT"))
        state["interface"]["lock"] = False
        self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "OBSERVED_MATCH"))

    def test_each_interface_and_backing_field_is_in_payload(self):
        for domain, profile in (("interface", LAYER), ("target", BACKING)):
            for key, kind in profile.items():
                if kind in ("gi", "backing"):
                    continue
                with self.subTest(domain=domain, key=key):
                    state = fixture()
                    baseline = read_fixture(state)
                    current = state[domain][key]
                    alternative = {"bool": not current if kind == "bool" else True,
                                   "float": 2.0, "string": "renamed", "name": "changed",
                                   "color": (1, 2, 3, 4)}[kind]
                    state[domain][key] = alternative
                    self.assertEqual(compare_model(baseline, read_fixture(state)), ("INCOMPLETE", "OBSERVED_DIFFERENT"))

    def test_each_gi_field_and_each_nested_interface(self):
        for domain in ("interface", "target"):
            for key, kind in GI.items():
                with self.subTest(domain=domain, key=key):
                    state = fixture()
                    before = read_fixture(state)
                    gi = state[domain]["inodegiproperties"]
                    gi[key] = (not gi[key]) if kind == "bool" else (2 if kind == "integer" else 2.0)
                    self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "OBSERVED_DIFFERENT"))

    def test_missing_and_unknown_every_profile_including_gi(self):
        for domain in ("interface", "target", "interface_gi", "target_gi"):
            for operation in ("missing", "unknown", "duplicate_case"):
                with self.subTest(domain=domain, operation=operation):
                    state = fixture()
                    container = state[domain.split("_")[0]]
                    if domain.endswith("_gi"):
                        container = container["inodegiproperties"]
                    if operation == "missing":
                        del container[next(iter(container))]
                    elif operation == "unknown":
                        container["futureunknown"] = True
                    else:
                        container[next(iter(container)).upper()] = True
                    self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))

    def test_wrong_types_nan_infinity_and_unknown_nested_value(self):
        cases = [("interface", "visibility", float("nan")), ("target", "visibility", float("inf")),
                 ("target", "degrade", 1), ("interface", "name", object()),
                 ("target", "wirecolor", (1, 2, float("nan"), 4)),
                 ("target", "inodegiproperties", None)]
        for domain, key, value in cases:
            with self.subTest(domain=domain, key=key):
                state = fixture()
                state[domain][key] = value
                self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))
        state = fixture()
        state["target"]["inodegiproperties"]["gimeshsize"] = float("nan")
        self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))

    def test_exact_membership_and_root_manager_dependencies(self):
        state = fixture()
        self.assertEqual(read_fixture(state)[1], "PARTIAL_CAPTURE_ONLY")
        state["deps"] = [state["manager"], state["root"]]
        self.assertEqual(read_fixture(state)[1], "PARTIAL_CAPTURE_ONLY")
        for mutation in (lambda s: s["members"].clear(), lambda s: s["members"].append(Ref(15, "node")),
                         lambda s: s["scene"].append(Ref(18, "node")),
                         lambda s: s.update(scene=[Ref(19, "node")]),
                         lambda s: s["deps"].append(Ref(16, "foreign")),
                         lambda s: s["deps"].remove(s["root"]), lambda s: s.update(parent=Ref(17, "layer")),
                         lambda s: s.update(children=1), lambda s: s.update(outgoing=1)):
            state = fixture()
            mutation(state)
            self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))

    def test_replacement_handle_mismatch_and_current_name_not_authority(self):
        state = fixture()
        before = read_fixture(state)
        state["interface"]["name"] = "renamed"
        self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "OBSERVED_DIFFERENT"))
        state["interface"]["name"] = "0"
        state["backing"] = Ref(state["backing"].handle, "layer")
        self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))
        state = fixture()
        state["handle_map"][state["backing"].handle] = Ref(state["backing"].handle, "layer")
        self.assertEqual(read_fixture(state), ("INCOMPLETE", "READ_FAILED"))
        state = fixture()
        before = read_fixture(state)
        repeat = read_fixture(state)
        state["handle_map"][state["backing"].handle] = Ref(state["backing"].handle, "layer")
        self.assertEqual(compare_model(before, repeat, state["handle_map"]), ("INCOMPLETE", "UNCOMPARABLE"))
        state = fixture()
        before = read_fixture(state)
        state["backing"].alive = False
        self.assertEqual(compare_model(before, read_fixture(state)), ("INCOMPLETE", "UNCOMPARABLE"))

    def test_name_injection_is_detached_data_not_authority_or_code(self):
        state = fixture()
        before = read_fixture(state)
        attack_text = '0"\n)\ndelete objects\n('
        state["interface"]["name"] = attack_text
        after = read_fixture(state)
        self.assertEqual(compare_model(before, after), ("INCOMPLETE", "OBSERVED_DIFFERENT"))
        self.assertIn(("name", ("string", attack_text)), after[2][3])
        self.assertIn('#("string", copy value)', self.source)
        self.assertNotIn("execute ", self.source)

    def test_malformed_or_failed_read_never_equal(self):
        complete = read_fixture(fixture())
        for bad in (("INCOMPLETE", "READ_FAILED"), (), ("PASS", "PARTIAL_CAPTURE_ONLY", None)):
            self.assertEqual(compare_model(complete, bad), ("INCOMPLETE", "UNCOMPARABLE"))


if __name__ == "__main__":
    unittest.main()
