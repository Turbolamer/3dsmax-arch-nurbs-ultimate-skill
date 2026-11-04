"""Structural-only checks for the P3.1 layer-reader helper.

This test never invokes Max, MAXScript, fileIn, a bridge, or scene mutation.
It checks conservative source shape and the explicit offline boundary only.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import unittest


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "layer_reader_p31_offline.ms"
README_PATH = HERE / "README_p31_offline.md"
REPORT_PATH = HERE / "REPORT_p31_offline.md"
EVIDENCE_PATH = HERE.parent / "_phase16-p3-layer-readonly-2026-11-03f.json"


def profile_block(source: str, name: str) -> str:
    match = re.search(
        rf"\blocal\s+{re.escape(name)}\s*=\s*#\((.*?)\n\)",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing profile {name}")
    return match.group(1)


def profile_pairs(source: str, name: str) -> list[tuple[str, str]]:
    return re.findall(
        r"#\(\s*#([A-Za-z0-9_]+)\s*,\s*#([A-Za-z0-9_]+)\s*\)",
        profile_block(source, name),
    )


class P31OfflineStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE_PATH.read_text(encoding="utf-8")
        cls.readme = README_PATH.read_text(encoding="utf-8")
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def test_artifacts_are_present_and_python_test_parses(self) -> None:
        self.assertTrue(SOURCE_PATH.is_file())
        self.assertTrue(README_PATH.is_file())
        self.assertTrue(REPORT_PATH.is_file())
        ast.parse(Path(__file__).read_text(encoding="utf-8"))

    def test_observed_profiles_and_backing_only_degrade(self) -> None:
        interface = profile_pairs(self.source, "p31InterfaceProfile")
        backing = profile_pairs(self.source, "p31BackingProfile")
        gi = profile_pairs(self.source, "p31GIProfile")
        self.assertEqual(len(interface), 33)
        self.assertEqual(len(backing), 34)
        self.assertEqual(len(gi), 18)
        self.assertEqual({name for name, _ in backing} - {name for name, _ in interface}, {"degrade"})
        self.assertEqual(len({name.lower() for name, _ in interface}), 33)
        self.assertEqual(len({name.lower() for name, _ in backing}), 34)
        self.assertEqual(len({name.lower() for name, _ in gi}), 18)
        self.assertIn("#(#degrade, #bool)", profile_block(self.source, "p31BackingProfile"))

    def test_profile_names_and_types_match_recorded_enumerations(self) -> None:
        evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
        type_map = {
            "BooleanClass": "bool", "Integer": "integer", "Float": "float",
            "Name": "name", "String": "string", "Color": "color",
            "MixinInterface": "gi", "Base_LayerBase_Layer": "backing",
        }
        cases = (
            ("layer_properties", "p31InterfaceProfile"),
            ("backing_reference_enumeration", "p31BackingProfile"),
            ("gi_properties", "p31GIProfile"),
        )
        for evidence_key, profile_name in cases:
            with self.subTest(profile=profile_name):
                observed = re.findall(
                    r"(?:p|refProp)=([^;|]+);(?:cls|class)=([^;|]+)",
                    evidence[evidence_key]["result"],
                )
                expected = {name.lower(): type_map[kind] for name, kind in observed}
                actual = {name.lower(): kind.lower() for name, kind in profile_pairs(self.source, profile_name)}
                self.assertEqual(len(observed), len(expected))
                self.assertEqual(actual, expected)

    def test_exact_witness_rejects_mixin_before_anim_api(self) -> None:
        block = self.source.split("fn p31ExactWitness witness =", 1)[1].split(")\n\nfn p31FiniteFloat", 1)[0]
        self.assertIn("(classOf value) != MixinInterface", block)
        self.assertLess(block.index("MixinInterface"), block.index("getHandleByAnim"))
        self.assertIn("getAnimByHandle h", block)
        self.assertIn("(getHandleByAnim resolved) == h", block)
        self.assertIn("value != undefined and h != undefined", block)
        self.assertEqual(self.source.count("getHandleByAnim"), 2)
        self.assertEqual(self.source.count("getAnimByHandle"), 1)

    def test_enumeration_guard_rejects_drift_unknowns_and_duplicates(self) -> None:
        block = self.source.split("fn p31CheckProfile target profile =", 1)[1].split("\n\nfn p31ReadGI", 1)[0]
        for token in (
            "local names = getPropNames target",
            "(classOf names) == Array",
            "names.count == profile.count",
            "names.count <= 34",
            "(classOf p) == Name",
            "hits == 1",
            "duplicates == 1",
            "(findItem names spec[1]) != 0",
        ):
            self.assertIn(token, block)
        self.assertIn('if condition != true do throw ("P31_LAYER_INCOMPLETE|" + reason)', self.source)

    def test_layer_as_ref_targ_is_exact_and_not_recursed(self) -> None:
        self.assertIn("local layer = node.layer", self.source)
        self.assertIn("local actualBacking = layer.layerAsRefTarg", self.source)
        self.assertIn("actualBacking != undefined and actualBacking == backing", self.source)
        branch = self.source.split("else if spec[2] == #backing then", 1)[1].split("else detached", 1)[0]
        self.assertIn("p31ExactWitness #(value, backingWitness[2])", branch)
        self.assertNotIn("p31ReadProperties value", branch)
        self.assertIn('detached = #("same_exact_backing")', branch)

    def test_scalar_detachment_is_typed_bounded_and_finite(self) -> None:
        self.assertIn("#bool", self.source)
        self.assertIn("#integer", self.source)
        self.assertIn("#float", self.source)
        self.assertIn("#name", self.source)
        self.assertIn("#string", self.source)
        self.assertIn("#color", self.source)
        self.assertIn("value.count <= 4096", self.source)
        self.assertIn("value == value and abs value < 1.0e38", self.source)
        self.assertIn("p31ColorComponent value.r", self.source)
        self.assertIn("p31ColorComponent value.a", self.source)
        self.assertIn("default: throw \"P31_LAYER_INCOMPLETE|unknown scalar kind\"", self.source)

    def test_nested_gi_is_explicitly_profiled(self) -> None:
        self.assertIn("fn p31ReadGI gi =", self.source)
        self.assertIn("(classOf gi) == MixinInterface", self.source)
        self.assertIn("p31CheckProfile gi p31GIProfile", self.source)
        self.assertIn('if spec[2] == #gi then detached = #("gi", p31ReadGI value)', self.source)
        self.assertIn("local backingState = p31ReadProperties backing p31BackingProfile", self.source)

    def test_each_read_requires_both_property_surfaces_and_hierarchy(self) -> None:
        block = self.source.split("fn p31ReadOnce nodeWitness", 1)[1].split("\n\nfn p31DetachedEqual", 1)[0]
        self.assertIn("p31ExactWitness nodeWitness", block)
        self.assertIn("p31ExactWitness backingWitness", block)
        self.assertIn("p31ReadMembers layer nodeWitness backingWitness memberWitnesses", block)
        self.assertIn("p31ReadDependencies backingWitness rootWitness managerWitness memberWitnesses", block)
        self.assertIn("p31ReadProperties layer p31InterfaceProfile backingWitness", block)
        self.assertIn("p31ReadProperties backing p31BackingProfile backingWitness", block)
        self.assertEqual(block.count("p31RequireNoHierarchy layer"), 2)

    def test_membership_is_witness_bound_and_bounded(self) -> None:
        block = self.source.split("fn p31ReadMembers layer", 1)[1].split("\n\n-- Allowed dependents", 1)[0]
        for token in (
            "memberWitnesses.count >= 1",
            "memberWitnesses.count <= 16",
            "p31ExactWitness witness",
            "isValidNode witness[1]",
            "subjectHits == 1",
            "duplicate member witness",
            "local reported = layer.getNumNodes()",
            "local members = #()",
            "layer.nodes &members",
            "members.count == reported",
            "memberLayer = witness[1].layer",
            "memberBacking = memberLayer.layerAsRefTarg",
            "memberBacking != undefined and memberBacking == backingWitness[1]",
        ):
            self.assertIn(token, block)
        self.assertNotIn("getNodeByName", block)

    def test_hierarchy_and_dependency_guards_fail_closed(self) -> None:
        hierarchy = self.source.split("fn p31RequireNoHierarchy layer =", 1)[1].split("\n\n-- max 16", 1)[0]
        self.assertIn("parent == undefined", hierarchy)
        self.assertIn("childCount == 0", hierarchy)
        deps = self.source.split("fn p31ReadDependencies backingWitness", 1)[1].split("\n\nfn p31ReadOnce", 1)[0]
        for token in (
            "p31ExactWitness rootWitness",
            "p31ExactWitness managerWitness",
            "rootNode == rootWitness[1]",
            "refs.getNumRefs backingWitness[1]",
            "refs.dependents backingWitness[1]",
            "deps.count >= 2",
            "deps.count <= (2 + memberWitnesses.count)",
            "foreign or ambiguous dependent",
            "rootHits == 1 and managerHits == 1",
            "member overlaps dependency witness",
        ):
            self.assertIn(token, deps)
        self.assertIn("fn p31ReadDependencies backingWitness rootWitness managerWitness memberWitnesses", self.source)

    def test_read_is_double_checked_and_always_incomplete(self) -> None:
        block = self.source.split("fn p31ObserveTwice", 1)[1]
        self.assertIn('"P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "READ_FAILED"', block)
        self.assertIn("local a = p31ReadOnce", block)
        self.assertIn("local b = p31ReadOnce", block)
        self.assertIn("p31DetachedEqual a b", block)
        self.assertIn('"PARTIAL_STABLE"', block)
        self.assertIn('"CHANGED_DURING_READ"', block)
        self.assertIn('catch (result = #("P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "READ_FAILED"))', block)
        self.assertNotIn('"PASS"', block)

    def test_no_scene_mutation_or_runtime_integration_tokens(self) -> None:
        forbidden = (
            "fileIn", "execute ", "delete ", "deleteLayer", "newLayer", "LayerManager.new",
            "Box ", "Sphere ", "save", "reset", "clearUndo", "setSaveRequired",
            "getLayerFromName", "getNodeByName", "global ", "::",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, self.source)
        self.assertIn("OFFLINE TEXT ONLY", self.source)

    def test_name_is_state_only_and_gaps_are_recorded(self) -> None:
        self.assertIn("#(#name, #string)", self.source)
        self.assertIn("Names are detached state only", self.readme)
        self.assertIn("same-name replacement", self.readme)
        self.assertRegex(self.report, r"not compiled, parsed, `fileIn`-ed,\s+timed, or executed")
        for gap in (
            "MAXScript validity", "Manager witness", "Hierarchy", "Membership bounds",
            "Dependency graph", "State coverage", "Identity/lifecycle", "Production integration",
            "Replay and construction",
        ):
            self.assertIn(gap, self.readme)


if __name__ == "__main__":
    unittest.main()
