"""Offline Python model + textual checks, NOT a MAXScript interpreter or live proof."""

from dataclasses import dataclass
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MISSING = object()


class Refusal(Exception):
    pass


@dataclass(frozen=True)
class Expected:
    schema: str = "p3-session-registry-2"
    identity: str = "a" * 64
    binding: str = "b" * 64
    namespace: str = "P3FutureExample"
    nonce: str = "abcDEF0123456789"
    path: str = ""
    filename: str = ""
    time: int = 0
    sub: int = 0
    dirty: bool = False
    units: str = "millimeters"
    scale: float = 1.0


@dataclass
class Scene:
    root: object
    root_handle: int
    root_class: str = "DummyRoot"
    path: str = ""
    filename: str = ""
    time: int = 0
    sub: int = 0
    dirty: bool = False
    selection_count: int = 0
    object_count: int = 0
    units: str = "millimeters"
    scale: float = 1.0
    handle_roundtrip: bool = True


@dataclass
class Lease:
    values: list


@dataclass
class Witness:
    lease: Lease
    values: list
    env: list
    root_record: list
    selection: list
    root: object
    root_handle: int
    root_class: str
    path: str
    filename: str
    time: int
    sub: int
    dirty: bool
    anchor: object = None


@dataclass
class Anchor:
    witness: Witness
    lease: Lease
    values: list
    env: list
    root_record: list
    selection: list
    root: object


@dataclass
class Registry:
    wall: object
    witness: object
    anchor: object
    historical_main03_present: bool = False


@dataclass
class Fixture:
    expected: Expected
    scene: Scene
    registry: Registry
    original: Lease
    original_values: list
    original_witness: Witness
    original_anchor: Anchor
    sentinel: int = 0


def new_fixture():
    expected = Expected()
    root = object()
    scene = Scene(root=root, root_handle=39)
    root_record = [root, scene.root_handle, scene.root_class]
    selected = []
    env = [root_record, "", "", expected.time, selected, expected.sub]
    values = [expected.schema, expected.identity, expected.binding, expected.namespace,
              "ARMED", expected.nonce, env, None, None, expected.dirty]
    lease = Lease(values)
    witness = Witness(lease, values, env, root_record, selected, root,
                      scene.root_handle, scene.root_class, "", "", expected.time,
                      expected.sub, expected.dirty)
    anchor = Anchor(witness, lease, values, env, root_record, selected, root)
    witness.anchor = anchor
    return Fixture(expected, scene, Registry(lease, witness, anchor), lease,
                   values, witness, anchor)


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def guard(f):
    """Mirror the proposed initial-only invariants; no shared runtime import."""
    r, e, s = f.registry, f.expected, f.scene
    require(not r.historical_main03_present, "historical")
    require(r.witness is not MISSING and r.anchor is not MISSING, "holder missing")
    require(type(r.witness) is Witness and type(r.anchor) is Anchor, "holder shape")
    w, a = r.witness, r.anchor
    require(w.anchor is a and a.witness is w, "holder linkage")
    require(r.wall is not MISSING, "registry missing")
    require(type(w.lease) is Lease and a.lease is w.lease and r.wall is w.lease, "lease identity")
    lease, v = w.lease, w.values
    require(type(v) is list and a.values is v and lease.values is v, "values identity")
    require(len(v) == 10, "values shape")
    require(v[0:4] == [e.schema, e.identity, e.binding, e.namespace], "identity")
    require(v[4] == "ARMED" and v[5] == e.nonce and v[7] is None
            and v[8] is None and v[9] is e.dirty, "state")
    env = v[6]
    require(type(env) is list and env is w.env and env is a.env and len(env) == 6, "environment identity")
    rr, selected = env[0], env[4]
    require(type(rr) is list and len(rr) == 3 and rr is w.root_record
            and rr is a.root_record and type(selected) is list
            and selected is w.selection and selected is a.selection, "environment component")
    require(len(selected) == 0 and rr[0] is w.root and a.root is w.root
            and rr[1] == w.root_handle and rr[2] == w.root_class, "root record")
    require(env[1:4] == [e.path, e.filename, e.time] and env[5] == e.sub, "environment content")
    require((w.path, w.filename, w.time, w.sub, w.dirty) ==
            (e.path, e.filename, e.time, e.sub, e.dirty), "witness context")
    require(s.root is w.root and s.root_handle == w.root_handle
            and s.root_class == w.root_class and s.handle_roundtrip, "root")
    require((s.path, s.filename, s.time, s.sub) == (e.path, e.filename, e.time, e.sub), "scene context")
    require(s.object_count == 0 and s.selection_count == 0 and s.dirty is e.dirty, "census")
    require((s.units, s.scale) == (e.units, e.scale), "units")
    return w, a, lease, v, s.root


def call_guarded(f, *, hashes_match=True, delegate=None, creation=False):
    """Read-only sentinel or modeled create; neither is a MAXScript execution."""
    try:
        require(hashes_match, "hash")
        held = guard(f)
    except (Refusal, AttributeError, TypeError, IndexError):
        return "INCOMPLETE_BEFORE_DELEGATE"
    f.sentinel += 1
    try:
        if delegate is not None:
            delegate(f)
    except Exception:
        return "INCOMPLETE_AFTER_DELEGATE"
    # A real build changes state/census, so re-running the initial guard is invalid.
    w, a, lease, values, root = held
    try:
        require(f.registry.witness is w and f.registry.anchor is a
                and w.anchor is a and a.witness is w, "post holder")
        require(f.registry.wall is lease and w.lease is lease and a.lease is lease
                and w.values is values and a.values is values and lease.values is values, "post lease")
        require(values[0:4] == [f.expected.schema, f.expected.identity,
                                f.expected.binding, f.expected.namespace]
                and values[5] == f.expected.nonce, "post literals")
        require(f.scene.root is root and w.root is root and a.root is root, "post root")
        if creation:
            # Placeholder contract only; the actual state name and node slot
            # remain undecided until the repaired runtime is independently reviewed.
            require(values[4] == "PROVISIONAL_REVIEWED", "post state")
            require(values[7] is not None and f.scene.object_count == 1, "post node/census")
            require(values[9] is f.scene.dirty, "post dirty")
    except (Refusal, AttributeError, TypeError, IndexError):
        return "INCOMPLETE_AFTER_DELEGATE"
    return "UNVERIFIED_NEEDS_INDEPENDENT_POST_INSPECTION"


class IndependentFaultModel(unittest.TestCase):
    def check_pre_refusal(self, mutate, expected_reason=None):
        f = new_fixture()
        mutate(f)
        before = (f.registry.wall, f.registry.witness, f.registry.anchor, f.scene.object_count)
        before_values = f.original.values
        before_contents = tuple(before_values)
        before_held_contents = tuple(f.original_values)
        before_anchor = dict(vars(f.original_anchor))
        before_witness = dict(vars(f.original_witness))
        before_scene = dict(vars(f.scene))
        before_expected_nonce = f.expected.nonce
        if expected_reason is not None:
            with self.assertRaisesRegex(Refusal, "^" + expected_reason + "$"):
                guard(f)
        self.assertEqual(call_guarded(f), "INCOMPLETE_BEFORE_DELEGATE")
        self.assertEqual(f.sentinel, 0)
        # Injections deliberately change candidate fields *before* the guard.
        # The guard must preserve that exact observed state, not restore it.
        self.assertIs(f.original.values, before_values)
        self.assertEqual(tuple(f.original.values), before_contents)
        self.assertEqual(tuple(f.original_values), before_held_contents)
        self.assertEqual(vars(f.scene), before_scene)
        for key, value in before_anchor.items():
            self.assertIs(getattr(f.original_anchor, key), value)
        for key, value in before_witness.items():
            self.assertIs(getattr(f.original_witness, key), value)
        self.assertEqual(f.expected.nonce, before_expected_nonce)
        self.assertIs(f.original_witness.lease, f.original)
        self.assertIs(f.original_anchor.witness, f.original_witness)
        self.assertIs(f.registry.wall, before[0])
        self.assertIs(f.registry.witness, before[1])
        self.assertIs(f.registry.anchor, before[2])
        self.assertEqual(f.scene.object_count, before[3])

    def test_same_instance_positive_across_separate_model_calls(self):
        f = new_fixture()
        self.assertEqual(call_guarded(f), "UNVERIFIED_NEEDS_INDEPENDENT_POST_INSPECTION")
        self.assertEqual(call_guarded(f), "UNVERIFIED_NEEDS_INDEPENDENT_POST_INSPECTION")
        self.assertIs(f.registry.wall, f.original)
        self.assertEqual(f.sentinel, 2)

    def test_equal_payload_replacement_lease(self):
        self.check_pre_refusal(lambda f: setattr(f.registry, "wall", Lease(list(f.original_values))), "lease identity")

    def test_missing_undefined_wrong_registry_are_distinct(self):
        for value in (MISSING, None, 123):
            with self.subTest(value=value):
                self.check_pre_refusal(lambda f: setattr(f.registry, "wall", value))

    def test_fresh_equal_values_and_environment_arrays(self):
        self.check_pre_refusal(lambda f: setattr(f.original, "values", list(f.original_values)), "values identity")
        self.check_pre_refusal(lambda f: f.original_values.__setitem__(6, list(f.original_values[6])), "environment identity")
        self.check_pre_refusal(lambda f: f.original_values[6].__setitem__(0, list(f.original_values[6][0])), "environment component")
        self.check_pre_refusal(lambda f: f.original_values[6].__setitem__(4, []), "environment component")

    def test_replaced_and_missing_holders(self):
        for slot, replacement in (("witness", MISSING), ("witness", None),
                                  ("witness", object()), ("anchor", MISSING),
                                  ("anchor", None), ("anchor", object())):
            with self.subTest(slot=slot, replacement=replacement):
                self.check_pre_refusal(lambda f: setattr(f.registry, slot, replacement))

    def test_replaced_original_reference_field_in_one_holder(self):
        for slot in ("lease", "values", "env", "root_record", "selection", "root"):
            with self.subTest(slot=slot):
                self.check_pre_refusal(lambda f: setattr(f.original_anchor, slot, object()))

    def test_valid_length_wrong_nonce_and_identity_fields(self):
        replacements = ((0, "p3-session-registry-3"), (1, "c" * 64),
                        (2, "d" * 64), (3, "AnotherNamespace"),
                        (5, "abcDEF012345678X"))
        for index, replacement in replacements:
            with self.subTest(index=index):
                reason = "state" if index == 5 else "identity"
                self.check_pre_refusal(lambda f: f.original_values.__setitem__(index, replacement), reason)

    def test_bad_state_and_nonempty_attempt_slots(self):
        for index, replacement in ((4, "BUILDING"), (4, "POISONED"),
                                   (4, "COMMITTED"), (7, object()),
                                   (8, []), (9, True)):
            with self.subTest(index=index):
                self.check_pre_refusal(lambda f: f.original_values.__setitem__(index, replacement))

    def test_scene_and_unit_context_changes(self):
        for slot, replacement in (("root", object()), ("root_handle", 40),
                                  ("root_class", "Other"), ("handle_roundtrip", False),
                                  ("path", "saved/"), ("filename", "scene.max"),
                                  ("time", 1), ("sub", 1), ("dirty", True),
                                  ("selection_count", 1), ("object_count", 1),
                                  ("units", "centimeters"), ("scale", 2.0)):
            with self.subTest(slot=slot):
                self.check_pre_refusal(lambda f: setattr(f.scene, slot, replacement))

    def test_existing_historical_key_refuses_without_changes(self):
        self.check_pre_refusal(lambda f: setattr(f.registry, "historical_main03_present", True))

    def test_held_hash_mismatch_prevents_delegate(self):
        f = new_fixture()
        self.assertEqual(call_guarded(f, hashes_match=False), "INCOMPLETE_BEFORE_DELEGATE")
        self.assertEqual(f.sentinel, 0)
        self.assertIs(f.registry.wall, f.original)

    def test_delegate_replacement_and_throw_are_incomplete(self):
        f = new_fixture()
        self.assertEqual(call_guarded(f, delegate=lambda x: setattr(x.registry, "wall", Lease(list(x.original_values)))),
                         "INCOMPLETE_AFTER_DELEGATE")
        self.assertEqual(f.sentinel, 1)
        self.assertIs(f.original.values, f.original_values)
        g = new_fixture()
        def fail(_):
            raise RuntimeError("delegate failure")
        self.assertEqual(call_guarded(g, delegate=fail), "INCOMPLETE_AFTER_DELEGATE")

    def test_modeled_provisional_post_transition_and_failures(self):
        def create(x):
            x.original_values[4] = "PROVISIONAL_REVIEWED"
            x.original_values[7] = object()
            x.scene.object_count = 1
        f = new_fixture()
        self.assertEqual(call_guarded(f, delegate=create, creation=True),
                         "UNVERIFIED_NEEDS_INDEPENDENT_POST_INSPECTION")
        for faulty in (lambda x: x.original_values.__setitem__(4, "COMMITTED"),
                       lambda x: setattr(x.scene, "object_count", 2),
                       lambda x: setattr(x.scene, "dirty", True)):
            g = new_fixture()
            def change(x):
                create(x)
                faulty(x)
            self.assertEqual(call_guarded(g, delegate=change, creation=True),
                             "INCOMPLETE_AFTER_DELEGATE")

    def test_complete_coordinated_rewrite_is_outside_model_threat_boundary(self):
        f = new_fixture()
        forged = new_fixture()
        # Preserve all expected literals/root while coherently replacing both
        # in-process holders and the registry: original references are gone.
        fake_values = list(f.original_values)
        forged.original.values = fake_values
        forged.original_witness.lease = forged.original
        forged.original_anchor.lease = forged.original
        forged.original_witness.values = fake_values
        forged.original_anchor.values = fake_values
        for slot in ("env", "root_record", "selection", "root", "root_handle", "root_class", "path", "filename", "time", "sub", "dirty"):
            setattr(forged.original_witness, slot, getattr(f.original_witness, slot))
        for slot in ("env", "root_record", "selection", "root"):
            setattr(forged.original_anchor, slot, getattr(f.original_anchor, slot))
        f.registry = Registry(forged.original, forged.original_witness, forged.original_anchor)
        self.assertEqual(call_guarded(f), "UNVERIFIED_NEEDS_INDEPENDENT_POST_INSPECTION")
        self.assertIsNot(f.registry.wall, f.original)  # documented limitation, NOT safety PASS


class CandidateSourceShape(unittest.TestCase):
    def test_templates_stop_before_any_filein(self):
        for name, target in (("02-arm-witness.ms", "fileIn armPath quiet:true"),
                             ("03-held-guarded-call.ms", "fileIn scriptPath quiet:true"),
                             ("04-outer-dispatch.ms", "fileIn wrapperPath quiet:true")):
            with self.subTest(file=name):
                source = (HERE / name).read_text(encoding="utf-8")
                self.assertLess(source.index('throw "P16_TEMPLATE_DISABLED'), source.index(target))
                self.assertEqual(source.count(target), 1)
                self.assertNotIn("globalVars.remove", source)
                self.assertNotIn("delete ", source.lower())

    def test_pair_hashes_then_guard_then_only_delegate(self):
        source = (HERE / "03-held-guarded-call.ms").read_text(encoding="utf-8")
        digest_manifest = source.index("(p16Digest hasher manifestRead)")
        digest_script = source.index("(p16Digest hasher scriptRead)")
        guard_call = source.index("retained = p16PreGuard")
        delegate = source.index("result = fileIn scriptPath quiet:true")
        self.assertLess(digest_manifest, guard_call)
        self.assertLess(digest_script, guard_call)
        self.assertLess(guard_call, delegate)
        self.assertLess(delegate, source.index("if delegated do", delegate))
        self.assertIn("anchor.leaseRef != lease", source)
        self.assertIn("anchor.valuesRef != vals", source)
        self.assertIn("vals[6] != nonce", source)
        self.assertIn("vals[6] != expectedNonce", source)
        self.assertIn("vals[5] != expectedProvisionalState", source)
        self.assertIn('expectedProvisionalState == "COMMITTED"', source)
        self.assertIn("postObjects[1] != postNode", source)

    def test_arm_uses_filein_return_not_registry_as_original(self):
        source = (HERE / "02-arm-witness.ms").read_text(encoding="utf-8")
        arm = source.index("heldLease = fileIn armPath quiet:true")
        capture = source.index("heldValues = heldLease.values")
        publication = source.index("globalVars.set witnessKey heldWitness")
        self.assertLess(arm, capture)
        self.assertLess(capture, publication)
        self.assertNotIn("heldLease = globalVars.get", source)
        self.assertNotIn("heldValues = globalVars.get", source)
        self.assertIn("heldWitness.anchorRef = heldAnchor", source)
        self.assertIn("globalVars.set anchorKey heldAnchor", source)

    def test_inline_dispatch_hashes_and_holds_before_wrapper(self):
        source = (HERE / "04-outer-dispatch.ms").read_text(encoding="utf-8")
        self.assertLess(source.index("wrapperRead = dotNetObject"), source.index("hasher.ComputeHash wrapperRead"))
        self.assertLess(source.index("actual != expectedHash"), source.index("result = fileIn wrapperPath quiet:true"))
        self.assertLess(source.index("result = fileIn wrapperPath quiet:true"), source.index("wrapperRead.Close()"))

    def test_candidate_order_check_discriminates_broken_fixture(self):
        def correct_order(text):
            return text.index("HASH_PAIR") < text.index("GUARD") < text.index("DELEGATE")
        self.assertTrue(correct_order("HASH_PAIR|GUARD|DELEGATE"))
        self.assertFalse(correct_order("GUARD|HASH_PAIR|DELEGATE"))


if __name__ == "__main__":
    unittest.main()
