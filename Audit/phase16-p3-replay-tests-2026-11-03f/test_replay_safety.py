"""OFFLINE, source-structural safety checks; never run or connect to 3ds Max.

Synthetic fragments below calibrate the detector, not MAXScript or scene behavior.
ActualRuntimeTests reads the real Python emitter and inspects its emitted text in
memory. A green source check is necessary at most, never a live replay proof.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "scripts" / "wall_surface_runtime.py"
TRACKED = (RUNTIME, ROOT / "scripts" / "scene_units.py", Path(__file__).resolve())


def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in TRACKED}


BEFORE = hashes()
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("p3_replay_test_runtime", RUNTIME)
runtime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runtime)
if hashes() != BEFORE:
    raise RuntimeError("source/test drift while importing: discard this run")


@dataclass(frozen=True)
class Tok:
    text: str
    kind: str
    line: int
    start: int
    end: int

    @property
    def key(self):
        return self.text.lower()


TOKEN = re.compile(
    r'(?P<space>\s+)|(?P<comment>--[^\r\n]*|/\*[\s\S]*?\*/)|'
    r'(?P<string>@?"(?:\\.|[^"\\])*")|(?P<symbol>\#[A-Za-z_][A-Za-z_0-9]*)|'
    r'(?P<ident>[A-Za-z_][A-Za-z_0-9]*)|(?P<number>\d+(?:\.\d+)?)|'
    r'(?P<op>==|!=|<=|>=|.)', re.DOTALL
)


def lex(source):
    """Ignore comments; retain string tokens so diagnostics cannot act as code."""
    result = []
    line = 1
    for match in TOKEN.finditer(source):
        text = match.group()
        if match.lastgroup not in ("space", "comment"):
            result.append(Tok(text, match.lastgroup, line, match.start(), match.end()))
        line += text.count("\n")
    return result


def matching_paren(tokens, start):
    if tokens[start].text != "(":
        raise ValueError("expected opening parenthesis")
    depth = 0
    for i in range(start, len(tokens)):
        if tokens[i].kind == "string":
            continue
        if tokens[i].text == "(":
            depth += 1
        elif tokens[i].text == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced parentheses: structural assessment incomplete")


def functions(tokens):
    """Find ordinary parenthesized local fn bodies, not a MAXScript parser."""
    found = {}
    for i, token in enumerate(tokens):
        if token.kind != "ident" or token.key != "fn":
            continue
        if i + 1 >= len(tokens) or tokens[i + 1].kind != "ident":
            raise ValueError("unsupported fn declaration")
        name = tokens[i + 1].key
        j = i + 2
        while j < len(tokens) and tokens[j].text != "=":
            j += 1
        if j + 1 >= len(tokens) or tokens[j + 1].text != "(":
            raise ValueError("unsupported non-parenthesized fn body: " + name)
        end = matching_paren(tokens, j + 1)
        if name in found:
            raise ValueError("duplicate local fn name: " + name)
        found[name] = tokens[j + 2:end]
    return found


def calls(body, names):
    return {t.key for t in body if t.kind == "ident" and t.key in names}


def closure(fns, root):
    seen = set()
    todo = [root]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        todo.extend(calls(fns[name], fns) - seen)
    return seen


def code_keys(body):
    return [t.key for t in body if t.kind != "string"]


def snapshot_root(fns):
    candidates = [name for name in fns if name.endswith("nodesnapshot")]
    if len(candidates) != 1:
        raise ValueError("cannot identify one nodeSnapshot root; review refactor")
    return candidates[0]


def property_binding(body, i):
    """Common `local x = object.property` / `getProperty ... #property` forms."""
    # Stop at a preceding statement terminator. Bound the search so an unrelated
    # earlier assignment cannot give the accessor an invented target variable.
    for j in range(i - 1, max(-1, i - 16), -1):
        if body[j].text == ";":
            break
        if body[j].text == "=" and j > 0 and body[j - 1].kind == "ident":
            return body[j - 1].key
        if body[i].line - body[j].line > 2:
            break
    return None


def direct_call_with(body, callees, target):
    """Recognize a direct first argument, optionally wrapped in parentheses."""
    for i, token in enumerate(body):
        if token.kind != "ident" or token.key not in callees:
            continue
        j = i + 1
        while j < len(body) and body[j].text == "(":
            j += 1
        if j < len(body) and body[j].key == target:
            return True
    return False


def inline_accessor_call(body, callees, accessor):
    """Recognize direct `reader (getProperty x #field)` / `reader x.field`."""
    for i, token in enumerate(body):
        if token.kind == "ident" and token.key in callees:
            for candidate in body[i + 1:i + 8]:
                if candidate.line - token.line > 2 or candidate.text in (";", ","):
                    break
                if candidate.kind in ("ident", "symbol") and candidate.key.lstrip("#") == accessor:
                    return True
    return False


def accessors(body, field):
    for i, token in enumerate(body):
        if token.kind in ("ident", "symbol") and token.key.lstrip("#") == field:
            # Bare words do not prove a property access; comments/strings are
            # already excluded. Allow .field and getProperty ... #field.
            dot = i > 0 and body[i - 1].text == "."
            prop = token.kind == "symbol" and any(
                t.key == "getproperty" for t in body[max(0, i - 5):i]
            )
            if dot or prop:
                yield i, property_binding(body, i)


def enum_functions(fns, reachable):
    # This deliberately recognizes a small, reviewable idiom, not every valid
    # implementation. A different implementation needs test review, not a waiver.
    return {name for name in reachable if {"getpropnames", "getproperty"} <= set(code_keys(fns[name]))}


def field_read(fns, reachable, enum_names, field):
    for name in reachable:
        body = fns[name]
        for _, binding in accessors(body, field):
            if binding and direct_call_with(body, enum_names, binding):
                return True
            if binding and direct_call_with(body, {"getpropnames"}, binding) and direct_call_with(body, {"getproperty"}, binding):
                return True
            if inline_accessor_call(body, enum_names, field):
                return True
    return False


def field_requires_value(fns, reachable, field):
    """Recognize a guard for an accessor binding, not merely an empty result."""
    for name in reachable:
        body = fns[name]
        for index, binding in accessors(body, field):
            if not binding:
                continue
            for i in range(index + 1, len(body) - 1):
                token = body[i]
                if token.kind != "ident" or "require" not in token.key or body[i + 1].text != "(":
                    continue
                end = matching_paren(body, i + 1)
                condition = code_keys(body[i + 2:end])
                if (binding in condition and "!=" in condition and "undefined" in condition
                        and not obviously_bypassed(condition)):
                    return True
    return False


def backing_identity(fns, reachable):
    """Necessary pattern only: backing reference passed to handle round-trip reader."""
    identity_fns = {n for n in reachable
                    if {"gethandlebyanim", "getanimbyhandle", "=="} <= set(code_keys(fns[n]))}
    for name in reachable:
        body = fns[name]
        for _, binding in accessors(body, "layerasreftarg"):
            if binding and direct_call_with(body, identity_fns, binding):
                return True
            if inline_accessor_call(body, identity_fns, "layerasreftarg"):
                return True
    return False


def name_fallback_in_layer_reader(fns, reachable):
    """Conservatively flag name lookups on the node-snapshot call path.

    This is a review trigger, not a claim that all name lookups are authoritative.
    A demonstrably non-authoritative diagnostic can justify adapting this check.
    """
    return any("getlayerfromname" in code_keys(fns[name]) for name in reachable)


def obviously_bypassed(guard):
    """Reject the obvious `... or true` tautology, not all logical disguises."""
    return any(guard[i:i + 2] == ["or", "true"] for i in range(len(guard) - 1))


def guarded_enumerator(fns, enum_names):
    for name in enum_names:
        body = fns[name]
        # Enumeration must be bounded and non-undefined. A swallowed read error
        # is not a comparable value. No catch is OK: a direct read may throw out.
        bounded = False
        for i, token in enumerate(body):
            if token.kind == "ident" and "require" in token.key and i + 1 < len(body) and body[i + 1].text == "(":
                end = matching_paren(body, i + 1)
                condition = code_keys(body[i + 2:end])
                bounded |= ("undefined" in condition and any(k in condition for k in ("<", "<="))
                            and not obviously_bypassed(condition))
        catches_safe = True
        for i, token in enumerate(body):
            if token.key == "catch" and i + 1 < len(body) and body[i + 1].text == "(":
                end = matching_paren(body, i + 1)
                if "throw" not in code_keys(body[i + 2:end]):
                    catches_safe = False
        if bounded and catches_safe:
            return True
    return False


def layer_findings(source):
    fns = functions(lex(source))
    root = snapshot_root(fns)
    reachable = closure(fns, root)
    enumerators = enum_functions(fns, reachable)
    guarded = {name for name in enumerators if guarded_enumerator(fns, {name})}
    return {
        "backing_enumerated": field_read(fns, reachable, enumerators, "layerasreftarg"),
        "gi_enumerated": field_read(fns, reachable, enumerators, "inodegiproperties"),
        "backing_identity": backing_identity(fns, reachable),
        "no_name_fallback": not name_fallback_in_layer_reader(fns, reachable),
        "backing_guarded": field_read(fns, reachable, guarded, "layerasreftarg"),
        "gi_guarded": field_read(fns, reachable, guarded, "inodegiproperties"),
        "backing_nonmissing": field_requires_value(fns, reachable, "layerasreftarg"),
        "gi_nonmissing": field_requires_value(fns, reachable, "inodegiproperties"),
    }


def replay_branch(source):
    tokens = lex(source)
    for i, token in enumerate(tokens):
        if token.kind != "string" or token.text.strip('"').lower() != "committed":
            continue
        for j in range(i + 1, min(i + 5, len(tokens) - 1)):
            if tokens[j].key == "then" and tokens[j + 1].text == "(":
                end = matching_paren(tokens, j + 1)
                return tokens[j + 2:end]
    raise ValueError("cannot locate parenthesized COMMITTED branch; review refactor")


def replay_barrier(source):
    """Recognize a direct, unconditional INCOMPLETE_REPLAY refusal in the branch."""
    body = replay_branch(source)
    depth = 0
    for i, token in enumerate(body):
        if token.kind != "string":
            if token.text == "(":
                depth += 1
            elif token.text == ")":
                depth -= 1
        if depth != 0 or token.kind != "ident":
            continue
        prefix = [t.key for t in body[:i] if t.line == token.line]
        previous = body[i - 1].key if i else None
        if previous in ("then", "do", "else") or any(t in prefix for t in ("if", "then", "do", "else")):
            continue
        rest = body[i + 1:i + 3]
        requirement = "require" in token.key and len(rest) == 2 and rest[0].key == "false"
        throw = token.key == "throw" and len(rest) >= 1
        reason = rest[1] if requirement else rest[0] if throw else None
        if reason and reason.kind == "string" and "INCOMPLETE_REPLAY" in reason.text:
            prior = code_keys(body[:i])
            if "return" in prior or "exit" in prior:
                return False
            return True
    return False


def obvious_replay_writes(source):
    """Detect direct writes/evaluation, not side effects hidden in helper calls."""
    body = replay_branch(source)
    keys = code_keys(body)
    forbidden = {"delete", "setuserprop", "setuserpropbuffer", "addmodifier",
                 "convertto", "update", "snapshotasmesh", "setproperty", "addnode"}
    hits = sorted(forbidden.intersection(keys))
    for i, key in enumerate(keys):
        if key == "globalvars" and keys[i + 1:i + 2] == ["."] and keys[i + 2:i + 3] in (["set"], ["remove"]):
            hits.append("globalvars." + keys[i + 2])
        if key in ("node", "shellmod", "baseref", "rootnode") and keys[i + 1:i + 2] == ["."] and keys[i + 3:i + 4] == ["="]:
            hits.append(key + " property assignment")
        if key == "lease" and keys[i + 1:i + 2] == ["["]:
            end = i + 2
            while end < len(keys) and keys[end] != "]":
                end += 1
            if end + 1 < len(keys) and keys[end + 1] == "=":
                hits.append("lease[] assignment")
    return hits


def guard_spans(source):
    """Extract require conditions and their exact text spans; not an evaluator."""
    tokens = lex(source)
    guards = []
    for i, token in enumerate(tokens):
        if token.kind != "ident" or "require" not in token.key:
            continue
        if i + 1 < len(tokens) and tokens[i + 1].text == "(":
            end = matching_paren(tokens, i + 1)
            guards.append((code_keys(tokens[i + 2:end]), tokens[i + 1].start, tokens[end].end))
    return guards


def unsupported_findings(source):
    guards = [tokens for tokens, _, _ in guard_spans(source)]

    def contains(*items):
        return any(not obviously_bypassed(guard) and all(item in guard for item in items) for guard in guards)

    return {
        "material": contains("material", "==", "undefined"),
        "hierarchy": contains("parent", "children", "count", "rootnode", "==", "0"),
        "custom_attributes": contains("custattributes", "count", "==", "0"),
        "unknown_controller": contains("finditem", "classof", "target", "prs", ">", "0"),
        "controller_keys": contains("keycount", "==", "0", "-", "1"),
    }


# These are intentionally tiny, invented lexical inputs, never execution evidence.
# They calibrate what the source detector can see; they are not a proposed runtime.
DETECTOR_CONTROL = '''
( 
 fn p3RequireState condition reason = (if not condition do throw reason)
 fn p3ReadProperties target = (
   local names = getPropNames target
   p3RequireState (names != undefined and names.count <= 512) "bounded"
   for p in names collect (try (getProperty target p) catch (throw))
 )
 fn p3ExactRef value = (
   local h = getHandleByAnim value
   p3RequireState ((getAnimByHandle h) == value) "roundtrip"
   #(value,h)
 )
 fn p3LayerSnapshot lyr = (
   local backing = lyr.layerAsRefTarg
   local gi = lyr.INodeGIProperties
   p3RequireState (backing != undefined) "backing unavailable"
   p3RequireState (gi != undefined) "GI unavailable"
   #(p3ExactRef backing, p3ReadProperties lyr, p3ReadProperties backing, p3ReadProperties gi)
 )
 fn p3NodeSnapshot node = (p3LayerSnapshot node.layer)
)
'''

REPLAY_CONTROL = '''
(if lease == "COMMITTED" then (
   p3RequireState (same baseline snapshot) "changed"
   p3RequireState false "INCOMPLETE_REPLAY: still unproven"
))
'''


class DetectorControls(unittest.TestCase):
    def test_layer_detector_clean_lexical_control(self):
        self.assertEqual(layer_findings(DETECTOR_CONTROL), {
            "backing_enumerated": True, "gi_enumerated": True,
            "backing_identity": True, "no_name_fallback": True,
            "backing_guarded": True, "gi_guarded": True,
            "backing_nonmissing": True, "gi_nonmissing": True,
        })

    def test_separate_backing_gi_and_identity_mutations_are_detected(self):
        cases = (
            ("p3ReadProperties backing", "backing", "backing_enumerated"),
            ("p3ReadProperties gi", "gi", "gi_enumerated"),
            ("p3ExactRef backing", "backing", "backing_identity"),
        )
        for old, replacement, expected in cases:
            with self.subTest(target=expected):
                self.assertEqual(DETECTOR_CONTROL.count(old), 1)
                observed = layer_findings(DETECTOR_CONTROL.replace(old, replacement, 1))
                self.assertFalse(observed[expected], observed)
                affected = {"backing_enumerated": "backing_guarded", "gi_enumerated": "gi_guarded"}.get(expected)
                if affected:
                    self.assertFalse(observed[affected], observed)
                for other, value in observed.items():
                    if other not in (expected, affected):
                        self.assertTrue(value, (expected, other, observed))

    def test_string_comment_and_unreachable_decoys_do_not_repair_missing_reader(self):
        base = DETECTOR_CONTROL.replace("p3ReadProperties backing", "backing", 1)
        decoys = '''\n-- p3ReadProperties backing\n"p3ReadProperties backing"\n'''
        self.assertFalse(layer_findings(base + decoys)["backing_enumerated"])
        unreachable = base + '''\nfn notCalled x = (local other = x.layerAsRefTarg; p3ReadProperties other)\n'''
        self.assertFalse(layer_findings(unreachable)["backing_enumerated"])

    def test_name_lookup_and_swallowed_enumeration_errors_flagged(self):
        lookup = DETECTOR_CONTROL.replace("local backing = lyr.layerAsRefTarg", 
            'local backing = lyr.layerAsRefTarg; local byName = LayerManager.getLayerFromName lyr.name')
        self.assertFalse(layer_findings(lookup)["no_name_fallback"])
        swallowed = DETECTOR_CONTROL.replace("catch (throw)", 'catch (print "ignored")')
        for key in ("backing_guarded", "gi_guarded"):
            self.assertFalse(layer_findings(swallowed)[key])
        bypass = DETECTOR_CONTROL.replace("names.count <= 512", "names.count <= 512 or true")
        for key in ("backing_guarded", "gi_guarded"):
            self.assertFalse(layer_findings(bypass)[key])
        for variable, key in (("backing", "backing_nonmissing"), ("gi", "gi_nonmissing")):
            missing_guard = DETECTOR_CONTROL.replace(f"({variable} != undefined)", "true")
            self.assertFalse(layer_findings(missing_guard)[key])
        separate = DETECTOR_CONTROL.replace("p3ReadProperties backing", "p3Unsafe backing")
        separate += "\nfn p3Unsafe target = (local n = getPropNames target; getProperty target n[1])\n"
        separate_findings = layer_findings(separate)
        self.assertTrue(separate_findings["backing_enumerated"] and separate_findings["gi_guarded"])
        self.assertFalse(separate_findings["backing_guarded"], separate_findings)
        helper = DETECTOR_CONTROL.replace("local backing = lyr.layerAsRefTarg",
            "local backing = lyr.layerAsRefTarg; local byName = p3Lookup lyr")
        helper += '\nfn p3Lookup lyr = (LayerManager.getLayerFromName lyr.name)\n'
        self.assertFalse(layer_findings(helper)["no_name_fallback"])
        no_compare = DETECTOR_CONTROL.replace('(getAnimByHandle h) == value', '(getAnimByHandle h) != value')
        self.assertFalse(layer_findings(no_compare)["backing_identity"])

    def test_barrier_detector_rejects_absent_decoy_or_conditional_barriers(self):
        self.assertTrue(replay_barrier(REPLAY_CONTROL))
        barrier = 'p3RequireState false "INCOMPLETE_REPLAY: still unproven"'
        for replacement in ('print "INCOMPLETE_REPLAY: still unproven"',
                            'if false do ' + barrier,
                            'if false do\n   ' + barrier,
                            '-- ' + barrier,
                            'return true\n   ' + barrier):
            with self.subTest(replacement=replacement):
                self.assertFalse(replay_barrier(REPLAY_CONTROL.replace(barrier, replacement)))

    def test_barrier_detector_ignores_comments_and_outside_branch(self):
        base = REPLAY_CONTROL.replace('p3RequireState false "INCOMPLETE_REPLAY: still unproven"', 'print "not proof"')
        other = base + '\n-- p3RequireState false "INCOMPLETE_REPLAY: decoy"\np3RequireState false "INCOMPLETE_REPLAY: outside"'
        self.assertFalse(replay_barrier(other))

    def test_direct_replay_mutation_detector_has_negative_controls(self):
        self.assertEqual(obvious_replay_writes(REPLAY_CONTROL), [])
        for operation in ('lease[5] = "COMMITTED"', 'setUserProp node tag value',
                          'delete node', 'globalVars.set key val', 'globalVars.remove key',
                          'node.renderable = true', 'setProperty node #renderable true',
                          'snapshotAsMesh node'):
            with self.subTest(operation=operation):
                mutated = REPLAY_CONTROL.replace('p3RequireState false', operation + '\n   p3RequireState false')
                self.assertTrue(obvious_replay_writes(mutated), operation)


def emit_actual():
    """Small synthetic INPUT only; source is emitted in memory, never fileIn-ed."""
    dims = {"spec": "dimensions", "status": "locked", "units": {"length": "cm"},
            "project": "offline-only", "facades": [{"id": "F", "start_corner_cm": [0, 0],
            "end_corner_cm": [400, 0], "length_cm": 400}]}
    walls = {"spec": "walls", "status": "locked", "units": {"length": "cm"},
             "project": "offline-only", "wall_technique": "poly_surface_shell_v1",
             "reference_face": "inner", "numeric_epsilon_cm": 0.001,
             "numeric_unit_epsilon": 0.000001, "blocks": [{"id": "B", "z_range_cm": [0, 300]}],
             "upper_returns": [], "openings": [], "wall_runs": [{"id": "W", "block_id": "B",
             "contour_ref": "dimensions.json:facades:F", "start_cm": [0, 0], "end_cm": [400, 0],
             "outward": [0, -1], "base_z_cm": 0, "top_z_cm": 300, "thickness_cm": 30,
             "topology_budget": {"max_grid_polygons": 32, "max_base_active_polygons": 32,
                                 "max_evaluated_triangles": 256}}]}
    units = {"system_type": "millimeters", "system_scale": 1.0,
             "cm_per_unit": 0.1, "units_per_cm": 10.0}
    return runtime.generate_script(runtime.build_plan(walls, dims),
        hashlib.sha256(b"offline-source-control-only").hexdigest(), "OfflineReplayControl", units)


class ActualRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = emit_actual()
        cls.layer = layer_findings(cls.source)
        print("\nOFFLINE emitted-source SHA-256:", hashlib.sha256(cls.source.encode()).hexdigest(), flush=True)

    def test_layer_backing_and_gi_are_each_enumerated(self):
        for key, field in (("backing_enumerated", "layerAsRefTarg"),
                           ("gi_enumerated", "INodeGIProperties")):
            with self.subTest(target=key):
                self.assertTrue(self.layer[key],
                    f"{key}: no recognized reachable enumeration in actual emitted source; "
                    "either missing or structural idiom needs review (not live proof)")
                # Once implemented, mutate the actual emitted text in memory,
                # not only the synthetic positive. A diagnostic mention cannot
                # replace the actual property accessor.
                mutated = re.sub(r"\b" + field + r"\b", "P3UnknownLayerField", self.source, flags=re.I)
                changed = layer_findings(mutated)
                self.assertFalse(changed[key], changed)
                other = "gi_enumerated" if key == "backing_enumerated" else "backing_enumerated"
                self.assertTrue(changed[other], (key, changed))

    def test_layer_backing_identity_uses_exact_roundtrip_not_only_name(self):
        self.assertTrue(self.layer["backing_identity"],
            "no recognized backing-reference handle round-trip on node snapshot path")
        self.assertTrue(self.layer["no_name_fallback"],
            "name lookup in the layer accessor requires manual non-authority review")
        mutated = re.sub(r"\bgetAnimByHandle\b", "P3MissingHandleLookup", self.source, flags=re.I)
        changed = layer_findings(mutated)
        self.assertFalse(changed["backing_identity"], changed)
        self.assertTrue(changed["backing_enumerated"] and changed["gi_enumerated"], changed)

    def test_layer_enumeration_refuses_unreadable_or_unbounded_values(self):
        # Generic guarded enumeration elsewhere is insufficient: each target must
        # reach a recognized bounded/non-undefined/error-propagating reader.
        for key in ("backing_guarded", "gi_guarded", "backing_nonmissing", "gi_nonmissing"):
            with self.subTest(target=key):
                self.assertTrue(self.layer[key],
                    f"{key}: target does not reach recognized bounded/error-propagating reader")

    def test_incomplete_replay_remains_unconditionally_blocked(self):
        self.assertTrue(replay_barrier(self.source), "no direct INCOMPLETE_REPLAY barrier found")
        branch = replay_branch(self.source)
        self.assertFalse(any(t.kind == "string" and "P3_NOOP|" in t.text for t in branch),
                         "a NOOP marker must not coexist with the incomplete barrier")

    def test_existing_unsupported_state_guards_and_targeted_mutation(self):
        observed = unsupported_findings(self.source)
        self.assertTrue(all(observed.values()), observed)
        # Mutate the recognized actual condition for each category in isolation;
        # an unrelated remaining guard cannot mask a missing intended one.
        predicates = {
            "material": ("material", "==", "undefined"),
            "hierarchy": ("parent", "children", "count", "rootnode", "==", "0"),
            "custom_attributes": ("custattributes", "count", "==", "0"),
            "unknown_controller": ("finditem", "classof", "target", "prs", ">", "0"),
            "controller_keys": ("keycount", "==", "0", "-", "1"),
        }
        spans = guard_spans(self.source)
        for key, terms in predicates.items():
            with self.subTest(guard=key):
                matching = [(a, b) for tokens, a, b in spans if all(t in tokens for t in terms)]
                self.assertEqual(len(matching), 1, f"ambiguous {key} mutation target; review")
                a, b = matching[0]
                mutated = unsupported_findings(self.source[:a] + "true" + self.source[b:])
                self.assertFalse(mutated[key], mutated)
                self.assertTrue(all(v for k, v in mutated.items() if k != key), mutated)
                bypass = unsupported_findings(self.source[:b-1] + " or true" + self.source[b-1:])
                self.assertFalse(bypass[key], bypass)
                self.assertTrue(all(v for k, v in bypass.items() if k != key), bypass)

    def test_actual_barrier_mutation_cannot_be_masked_by_diagnostic(self):
        pattern = r'p3RequireState\s+false\s+"INCOMPLETE_REPLAY[^"\n]*"'
        matches = list(re.finditer(pattern, self.source))
        self.assertEqual(len(matches), 1, "barrier shape changed: review mutation and live proof state")
        mutated = self.source[:matches[0].start()] + 'print "INCOMPLETE_REPLAY diagnostic only"' + self.source[matches[0].end():]
        self.assertFalse(replay_barrier(mutated), "a diagnostic must not replace refusal")

    def test_replay_branch_contains_no_direct_write_or_mesh_evaluation(self):
        self.assertEqual(obvious_replay_writes(self.source), [])
        pattern = r'p3RequireState\s+false\s+"INCOMPLETE_REPLAY[^"\n]*"'
        match = re.search(pattern, self.source)
        self.assertIsNotNone(match)
        mutated = self.source[:match.start()] + 'lease[5] = "COMMITTED"\n   ' + self.source[match.start():]
        self.assertIn("lease[] assignment", obvious_replay_writes(mutated))


def setUpModule():
    print("\nOFFLINE input SHA-256 (before):", BEFORE, flush=True)


def tearDownModule():
    after = hashes()
    print("\nOFFLINE input SHA-256 (after):", after, flush=True)
    if after != BEFORE:
        raise AssertionError("source/test drift during run: discard all test conclusions")


if __name__ == "__main__":
    unittest.main(verbosity=2)
