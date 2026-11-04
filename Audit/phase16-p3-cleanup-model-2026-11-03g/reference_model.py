"""OFFLINE thought experiment; not a 3ds Max API or production runtime.

All objects, handles, graphs, faults and cleanup effects below are synthetic.
The graph certificate and both disposal capabilities are assumptions of this
small closed-world model, NOT claims about Max. See REPORT.md before use.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Optional


class InjectedError(Exception):
    pass


class Interrupted(BaseException):
    """Represents a timeout/crash/lost return; never enter/resume cleanup."""


class Refusal(Exception):
    pass


@dataclass(eq=False)
class Ref:
    kind: str
    handle: Optional[int] = None
    alive: bool = True
    base: Optional["Ref"] = None


@dataclass
class Slots:
    node: Optional[Ref] = None
    base: Optional[Ref] = None
    shell: Optional[Ref] = None
    node_handle: Optional[int] = None
    shell_handle: Optional[int] = None


@dataclass(eq=False)
class Witness(Slots):
    pass


@dataclass(eq=False)
class Anchor(Slots):
    witness: Optional[Witness] = None
    frame: Optional[Slots] = None


@dataclass
class Injection:
    message: str
    mutate: Optional[Callable] = None
    interrupt: bool = False
    action_only: bool = False


@dataclass
class Result:
    status: str
    original_error: str
    errors: tuple
    attempted: tuple
    completed: tuple
    events: tuple
    observed_nodes: Optional[tuple]
    observed_non_nodes: Optional[tuple]


def same_refs(left, right):
    """Multiset identity comparison; no equality, names or handles as keys."""
    left, right = list(left), list(right)
    if len(left) != len(right):
        return False
    unmatched = right[:]
    for value in left:
        index = next((i for i, other in enumerate(unmatched) if value is other), None)
        if index is None:
            return False
        unmatched.pop(index)
    return not unmatched


def same_edges(left, right):
    # Ref is explicitly identity-equal/hashable; multiplicity matters.
    return Counter(left) == Counter(right)


def same_values(left, right):
    return len(left) == len(right) and all(
        type(a) is type(b) and a == b for a, b in zip(left, right)
    )


class SyntheticScene:
    """A fully enumerated finite fixture, not a model of all Max dependencies."""

    def __init__(self, neighbors=1):
        self.nodes = []
        self.non_nodes = []
        self.edges = []  # (dependent, relation, dependency), both directions checked
        self.handles = {}
        self.root = Ref("root")
        self.document = ("untitled", "", 0)  # example path, file, time
        self.units = ("millimeters", 1.0, 0.1)  # type, scale, factor separately
        self.selection = []
        self.dirty = False
        self.graph_complete = True  # synthetic oracle premise, not discovery
        self.unreadable = set()
        self.delete_mode = "normal"
        self.dispose_mode = "normal"
        self.next_handle = 100
        for _ in range(neighbors):
            self._new_node()

    def _number(self):
        self.next_handle += 1
        return self.next_handle

    def _new_node(self):
        base = Ref("base")
        node = Ref("node", self._number(), base=base)
        self.nodes.append(node)
        self.non_nodes.append(base)
        self.handles[node.handle] = node
        self.edges.append((node, "base", base))
        return node

    def new_node(self, hit):
        node = self._new_node()
        self.dirty = True
        hit("node_construct:allocated_before_return")
        return node

    def new_shell(self, hit):
        shell = Ref("shell", self._number())
        self.non_nodes.append(shell)
        self.handles[shell.handle] = shell
        self.dirty = True
        hit("shell_construct:allocated_before_return")
        return shell

    def attach(self, node, shell, hit):
        self.edges.append((node, "modifier", shell))
        self.dirty = True
        hit("attach:effect_before_return")

    def _invalidate(self, ref):
        ref.alive = False
        if ref.handle is not None and self.handles.get(ref.handle) is ref:
            del self.handles[ref.handle]
        self.edges = [edge for edge in self.edges if edge[0] is not ref and edge[2] is not ref]

    def dispose_unattached_shell(self, shell, hit):
        # A fabricated non-node disposal primitive; no Max counterpart asserted.
        if self.dispose_mode == "throw_before":
            raise InjectedError("dispose threw before effect")
        if self.dispose_mode != "noop":
            self._invalidate(shell)
        hit("dispose:effect_before_return")
        if self.dispose_mode == "throw_after":
            raise InjectedError("dispose threw after effect")

    def delete_exact_node(self, node, shell, hit):
        # A fabricated primitive which, only in this fixture, invalidates the
        # attached Shell and the unique base together with the supplied node.
        if self.delete_mode == "throw_before":
            raise InjectedError("delete threw before effect")
        if self.delete_mode == "wrong_neighbor":
            neighbor = next(n for n in self.nodes if n is not node)
            self.nodes.remove(neighbor)
            self._invalidate(neighbor.base)
            self._invalidate(neighbor)
        elif self.delete_mode != "noop":
            if self.delete_mode == "collateral":
                neighbor = next(n for n in self.nodes if n is not node)
                self.nodes.remove(neighbor)
                self._invalidate(neighbor.base)
                self._invalidate(neighbor)
            self.nodes.remove(node)
            if shell is not None:
                self._invalidate(shell)
            self._invalidate(node.base)
            self._invalidate(node)
        hit("delete:effect_before_return")
        if self.delete_mode == "throw_after":
            raise InjectedError("delete threw after effect")


class Harness:
    """Single-use trusted sequential fixture; no post-interruption recovery."""

    STEPS = (
        "admission", "node_construct", "node_witness", "node_anchor", "node_ref_validate",
        "node_handle", "node_handle_witness", "node_handle_anchor", "node_handle_validate",
        "base_read", "base_witness", "base_anchor", "base_validate", "pre_shell_validate",
        "shell_construct", "shell_witness", "shell_anchor", "shell_ref_validate",
        "shell_handle", "shell_handle_witness", "shell_handle_anchor", "shell_handle_validate", "pre_attach_validate",
        "attach", "probe",
    )

    def __init__(self, scene=None, *, standalone_disposal_supported=False, injections=None,
                 expected_units=("millimeters", 1.0, 0.1), expected_document=("untitled", "", 0),
                 expected_initial_dirty=False):
        self.scene = scene if scene is not None else SyntheticScene()
        self.frame = Slots()
        witness = Witness()
        anchor = Anchor(witness=witness, frame=self.frame)
        self.registry_witness = witness
        self.anchor = anchor
        # Separately retained original instances: never obtained from registry.
        self._retained_frame = self.frame
        self._retained_witness = witness
        self._retained_anchor = anchor
        self.baseline_nodes = tuple(self.scene.nodes)
        self.baseline_non_nodes = tuple(ref for ref in self.scene.non_nodes if ref.alive)
        self.baseline_edges = tuple(self.scene.edges)
        self.baseline_selection = tuple(self.scene.selection)
        self.expected_root = self.scene.root
        self.expected_document = tuple(expected_document)
        self.expected_units = tuple(expected_units)
        self.expected_initial_dirty = expected_initial_dirty
        self.standalone_disposal_supported = standalone_disposal_supported
        self.injections = dict(injections or {})
        self.attempted = []
        self.completed = []
        self.events = []
        self.cleanup_errors = []
        self.used = False

    def hit(self, point):
        self.events.append(point)
        injection = self.injections.pop(point, None)
        if injection is not None:
            if injection.mutate is not None:
                injection.mutate(self)
            if injection.interrupt:
                raise Interrupted(injection.message)
            if not injection.action_only:
                raise InjectedError(injection.message)

    def step(self, name, operation):
        self.attempted.append(name)
        self.hit(name + ":before")
        operation()
        self.completed.append(name)
        self.hit(name + ":after")

    def observe(self, name):
        self.hit("read:" + name)
        if name in self.scene.unreadable:
            raise Refusal("UNREADABLE_" + name.upper())

    @staticmethod
    def require(condition, reason):
        if not condition:
            raise Refusal(reason)

    def _handle(self, ref, frame_value, witness_value, anchor_value, label):
        self.observe(label + "_handle")
        values = (frame_value, witness_value, anchor_value, ref.handle)
        self.require(all(type(v) is int and v > 0 for v in values), label.upper() + "_HANDLE_UNKNOWN")
        self.require(all(v == values[0] for v in values), label.upper() + "_HANDLE_MISMATCH")
        # The lookup is ONLY an identity cross-check; never assign it to a slot.
        self.require(self.scene.handles.get(values[0]) is ref, label.upper() + "_ROUNDTRIP_MISMATCH")

    def _identity(self, label):
        self.require(self.frame is self._retained_frame and self.anchor is self._retained_anchor and
                     self.registry_witness is self._retained_witness and
                     self.anchor.frame is self.frame and self.anchor.witness is self._retained_witness,
                     "WITNESS_IDENTITY")
        value = getattr(self.frame, label)
        self.require(value is not None and value is getattr(self._retained_witness, label) and
                     value is getattr(self._retained_anchor, label) and value.kind == label and value.alive,
                     label.upper() + "_REF_MISMATCH_OR_INVALID")
        return value

    def _validate_handle(self, label):
        ref = self._identity(label)
        attr = label + "_handle"
        self._handle(ref, getattr(self.frame, attr), getattr(self._retained_witness, attr),
                     getattr(self._retained_anchor, attr), label)

    def _validate_base(self):
        node = self._identity("node")
        base = self._identity("base")
        self.require(base is node.base and not any(base is ref for ref in self.baseline_non_nodes),
                     "BASE_SHARED_WITH_BASELINE")

    def admit(self):
        self.observe("admission")
        self.require(self.frame is self._retained_frame and self.anchor is self._retained_anchor and
                     self.registry_witness is self._retained_witness and
                     self.anchor.frame is self.frame and self.anchor.witness is self._retained_witness,
                     "ADMISSION_WITNESS")
        self.require(self.scene.root is self.expected_root and
                     same_values(self.scene.document, self.expected_document) and
                     same_values(self.scene.units, self.expected_units) and
                     same_refs(self.scene.selection, self.baseline_selection) and
                     type(self.scene.dirty) is bool and self.scene.dirty is self.expected_initial_dirty,
                     "ADMISSION_CONTEXT")
        self.require(self.scene.graph_complete is True and
                     same_refs(self.scene.nodes, self.baseline_nodes) and
                     same_refs((ref for ref in self.scene.non_nodes if ref.alive), self.baseline_non_nodes) and
                     same_edges(self.scene.edges, self.baseline_edges), "ADMISSION_SCENE")

    def guard(self, *, disposed=False, before_mutation=False):
        self.hit("guard:begin")
        self.require(self.attempted == list(self.STEPS[:len(self.attempted)]) and
                     self.completed == self.attempted[:len(self.completed)] and
                     0 <= len(self.attempted) - len(self.completed) <= 1, "TRACE_INVALID")
        self.observe("witness")
        self.require(self.frame is self._retained_frame and self.anchor is self._retained_anchor and
                     self.registry_witness is self._retained_witness and
                     self.anchor.witness is self._retained_witness and
                     self.anchor.frame is self._retained_frame, "WITNESS_IDENTITY")
        self.observe("context")
        self.require(self.scene.root is self.expected_root and
                     same_values(self.scene.document, self.expected_document) and
                     self.scene.dirty is True, "CONTEXT_CHANGED")
        self.observe("units")
        self.require(same_values(self.scene.units, self.expected_units), "UNITS_CHANGED")
        self.observe("selection")
        self.require(same_refs(self.scene.selection, self.baseline_selection), "SELECTION_CHANGED")
        self.require("node_construct" in self.completed, "NODE_CONSTRUCTION_UNKNOWN")
        self.observe("node_ref")
        n, w, a = self.frame.node, self._retained_witness, self._retained_anchor
        self.require(n is not None and n is w.node and n is a.node and n.kind == "node" and n.alive,
                     "NODE_REF_MISMATCH_OR_INVALID")
        self._handle(n, self.frame.node_handle, w.node_handle, a.node_handle, "node")
        self.observe("base_ref")
        self.require(self.frame.base is not None and self.frame.base is w.base and
                     self.frame.base is a.base and self.frame.base is n.base and
                     self.frame.base.kind == "base" and self.frame.base.alive, "BASE_REF_MISMATCH_OR_INVALID")
        self.require(not any(self.frame.base is ref for ref in self.baseline_non_nodes), "BASE_SHARED_WITH_BASELINE")
        self.observe("census")
        self.require(same_refs(self.scene.nodes, (*self.baseline_nodes, n)), "CENSUS_MISMATCH")
        self.require(all(ref.alive for ref in self.baseline_nodes), "SURVIVOR_INVALID")

        shell_attempted = "shell_construct" in self.attempted
        shell = self.frame.shell
        attached = False
        if not shell_attempted:
            self.require(shell is None and w.shell is None and a.shell is None, "UNEXPECTED_SHELL_REF")
        else:
            self.require("shell_construct" in self.completed, "SHELL_CONSTRUCTION_UNKNOWN")
            self.observe("shell_ref")
            self.require(shell is not None and shell is w.shell and shell is a.shell and
                         shell.kind == "shell", "SHELL_REF_MISMATCH_OR_INVALID")
            if disposed:
                values = (self.frame.shell_handle, w.shell_handle, a.shell_handle, shell.handle)
                self.require(all(type(v) is int and v > 0 and v == values[0] for v in values) and
                             not shell.alive and self.scene.handles.get(values[0]) is None,
                             "SHELL_DISPOSAL_UNVERIFIED")
            else:
                self.require(shell.alive, "SHELL_REF_MISMATCH_OR_INVALID")
                self._handle(shell, self.frame.shell_handle, w.shell_handle, a.shell_handle, "shell")
            if "attach" in self.attempted:
                self.require("attach" in self.completed, "ATTACH_OUTCOME_UNKNOWN")
                attached = True
            self.require(not (disposed and attached), "DISPOSED_ATTACHED_SHELL")

        self.observe("graph")
        self.require(self.scene.graph_complete is True, "GRAPH_COMPLETENESS_UNKNOWN")
        self.require(all(ref.alive for ref in self.baseline_non_nodes), "NON_NODE_SURVIVOR_INVALID")
        expected_non_nodes = list(self.baseline_non_nodes) + [self.frame.base]
        if shell_attempted and not disposed:
            expected_non_nodes.append(shell)
        self.require(same_refs((ref for ref in self.scene.non_nodes if ref.alive), expected_non_nodes),
                     "NON_NODE_CENSUS_MISMATCH")
        expected_edges = list(self.baseline_edges) + [(n, "base", self.frame.base)]
        if attached:
            expected_edges.append((n, "modifier", shell))
        self.require(same_edges(self.scene.edges, expected_edges), "GRAPH_MISMATCH")
        if shell_attempted and not attached and not disposed and not before_mutation:
            self.require(self.standalone_disposal_supported is True, "SHELL_DISPOSAL_UNSUPPORTED")
        return n, shell, attached

    def postcheck(self, node, shell):
        # Independent read-only checks continue after ordinary read errors. A
        # timeout/interruption stops immediately; no post-interruption reads.
        def check(name, predicate, reason):
            try:
                self.hit("post:" + name)
                self.observe("post_" + name)
                self.require(predicate(), reason)
            except Exception as exc:
                self.cleanup_errors.append("POST_" + name.upper() + ": " + str(exc))

        check("ref", lambda: not node.alive and self.scene.handles.get(self.frame.node_handle) is None and
              not self.frame.base.alive, "NODE_REMOVAL_UNVERIFIED")
        if shell is not None:
            check("shell", lambda: not shell.alive and self.scene.handles.get(self.frame.shell_handle) is None,
                  "SHELL_DISPOSAL_UNVERIFIED")
        check("survivors", lambda: same_refs(self.scene.nodes, self.baseline_nodes) and
              all(ref.alive for ref in self.baseline_nodes), "SURVIVORS_MISMATCH")
        check("non_nodes", lambda: same_refs((ref for ref in self.scene.non_nodes if ref.alive),
                                             self.baseline_non_nodes), "NON_NODE_SURVIVORS_MISMATCH")
        check("graph", lambda: self.scene.graph_complete is True and
              same_edges(self.scene.edges, self.baseline_edges), "POST_GRAPH_MISMATCH")
        check("witness", lambda: self.frame is self._retained_frame and self.anchor is self._retained_anchor and
              self.registry_witness is self._retained_witness and self.anchor.frame is self.frame and
              self.anchor.witness is self._retained_witness and self.frame.node is self._retained_witness.node and
              self.frame.node is self.anchor.node and self.frame.base is self._retained_witness.base and
              self.frame.base is self.anchor.base and self.frame.shell is self._retained_witness.shell and
              self.frame.shell is self.anchor.shell and
              self.frame.node_handle == self._retained_witness.node_handle == self.anchor.node_handle and
              self.frame.shell_handle == self._retained_witness.shell_handle == self.anchor.shell_handle,
              "POST_WITNESS_MISMATCH")
        check("context", lambda: self.scene.root is self.expected_root and
              same_values(self.scene.document, self.expected_document) and
              same_values(self.scene.units, self.expected_units) and
              same_refs(self.scene.selection, self.baseline_selection) and
              self.scene.dirty is True, "POST_CONTEXT_MISMATCH")

    def cleanup(self):
        self.hit("cleanup:begin")
        # Distinct marker: a generic guard marker may also be reached by the
        # pre-attachment safety checks during the forward path.
        self.hit("cleanup:guard_begin")
        node, shell, attached = self.guard()
        if shell is not None and not attached:
            try:
                self.hit("dispose:before")
                self.scene.dispose_unattached_shell(shell, self.hit)
                self.hit("dispose:after")
            except Exception as exc:
                self.cleanup_errors.append("DISPOSAL: " + str(exc))
                return
            self.hit("dispose_post:before")
            # Recheck *all* guards, including proof of synthetic disposal, before
            # a subsequent node deletion. No retry on a thrown/unknown result.
            self.guard(disposed=True)
            self.hit("dispose_post:after")
        else:
            # Recheck immediately before any deletion, not just on entering catch.
            self.guard()
        try:
            self.hit("delete:before")
            self.scene.delete_exact_node(node, shell if attached else None, self.hit)
            self.hit("delete:after")
        except Exception as exc:
            self.cleanup_errors.append("DELETE: " + str(exc))
        # A thrown delete is still INCOMPLETE even if all reads look clean.
        self.postcheck(node, shell)

    def finish(self, status, original_error, errors):
        errors = list(errors)
        observed_nodes = observed_non_nodes = None
        if status != "INCOMPLETE_INTERRUPTED" and status != "INCOMPLETE_NO_RETRY":
            try:
                self.observe("diagnostic")
                observed_nodes = tuple(self.scene.nodes)
                observed_non_nodes = tuple(ref for ref in self.scene.non_nodes if ref.alive)
            except Interrupted as exc:
                status = "INCOMPLETE_INTERRUPTED"
                errors.append("DIAGNOSTIC_INTERRUPTED: " + str(exc))
            except Exception as exc:
                errors.append("DIAGNOSTIC: " + str(exc))
                if status == "CLEANED":
                    status = "INCOMPLETE_DIAGNOSTICS"
        return Result(status, original_error, tuple(errors), tuple(self.attempted),
                      tuple(self.completed), tuple(self.events), observed_nodes, observed_non_nodes)

    def run(self):
        if self.used:
            return self.finish("INCOMPLETE_NO_RETRY", "attempt is single-use", ())
        self.used = True
        w, a, f = self._retained_witness, self._retained_anchor, self.frame
        try:
            self.step("admission", self.admit)
            # Constructor return goes directly to the owning frame. The next
            # two steps mirror that exact reference; every gap is faultable.
            self.step("node_construct", lambda: setattr(f, "node", self.scene.new_node(self.hit)))
            self.step("node_witness", lambda: setattr(w, "node", f.node))
            self.step("node_anchor", lambda: setattr(a, "node", f.node))
            self.step("node_ref_validate", lambda: self._identity("node"))
            self.step("node_handle", lambda: setattr(f, "node_handle", f.node.handle))
            self.step("node_handle_witness", lambda: setattr(w, "node_handle", f.node_handle))
            self.step("node_handle_anchor", lambda: setattr(a, "node_handle", f.node_handle))
            self.step("node_handle_validate", lambda: self._validate_handle("node"))
            self.step("base_read", lambda: setattr(f, "base", f.node.base))
            self.step("base_witness", lambda: setattr(w, "base", f.base))
            self.step("base_anchor", lambda: setattr(a, "base", f.base))
            self.step("base_validate", self._validate_base)
            self.step("pre_shell_validate", lambda: self.guard(before_mutation=True))
            self.step("shell_construct", lambda: setattr(f, "shell", self.scene.new_shell(self.hit)))
            self.step("shell_witness", lambda: setattr(w, "shell", f.shell))
            self.step("shell_anchor", lambda: setattr(a, "shell", f.shell))
            self.step("shell_ref_validate", lambda: self._identity("shell"))
            self.step("shell_handle", lambda: setattr(f, "shell_handle", f.shell.handle))
            self.step("shell_handle_witness", lambda: setattr(w, "shell_handle", f.shell_handle))
            self.step("shell_handle_anchor", lambda: setattr(a, "shell_handle", f.shell_handle))
            self.step("shell_handle_validate", lambda: self._validate_handle("shell"))
            self.step("pre_attach_validate", lambda: self.guard(before_mutation=True))
            self.step("attach", lambda: self.scene.attach(f.node, f.shell, self.hit))
            # Marker only: never evaluate geometry or call external APIs.
            self.step("probe", lambda: None)
        except Interrupted as exc:
            return self.finish("INCOMPLETE_INTERRUPTED", str(exc), ())
        except Exception as exc:
            original_error = str(exc)
            try:
                self.cleanup()
                status = "INCOMPLETE_CLEANUP" if self.cleanup_errors else "CLEANED"
            except Interrupted as interrupted:
                status = "INCOMPLETE_INTERRUPTED"
                self.cleanup_errors.append("CLEANUP_INTERRUPTED: " + str(interrupted))
            except Exception as cleanup_error:
                status = "INCOMPLETE_CLEANUP"
                self.cleanup_errors.append("CLEANUP: " + str(cleanup_error))
            return self.finish(status, original_error, self.cleanup_errors)
        return self.finish("INCOMPLETE_NO_FAULT", "no failure was injected", ())
