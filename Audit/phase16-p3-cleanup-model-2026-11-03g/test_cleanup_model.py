"""Discriminating offline controls for reference_model.py only; no Max calls."""

import unittest

from reference_model import Anchor, Harness, Injection, Ref, Slots, SyntheticScene, Witness, same_refs


def fault(point="probe:before", *, mutate=None, interrupt=False, support=False, scene=None):
    h = Harness(scene, standalone_disposal_supported=support, injections={
        point: Injection("original-fault", mutate=mutate, interrupt=interrupt)
    })
    return h, h.run()


class CleanupModelTests(unittest.TestCase):
    def assert_neighbors(self, harness):
        for node in harness.baseline_nodes:
            self.assertTrue(node.alive)
            self.assertTrue(node.base.alive)
            self.assertTrue(any(other is node for other in harness.scene.nodes))

    def assert_refusal(self, h, result, reason, *, node_alive=True):
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP", result)
        self.assertTrue(any(reason in error for error in result.errors), result.errors)
        self.assertNotIn("delete:before", result.events)
        self.assertNotIn("dispose:before", result.events)
        if node_alive and h.frame.node is not None:
            self.assertTrue(h.frame.node.alive)
        self.assert_neighbors(h)

    def test_safe_node_before_shell_deletes_exact_and_preserves_survivors(self):
        h, result = fault("pre_shell_validate:after")
        self.assertEqual(result.status, "CLEANED", result.errors)
        self.assertFalse(h.frame.node.alive)
        self.assertIsNone(h.frame.shell)
        self.assertTrue(same_refs(result.observed_nodes, h.baseline_nodes))
        self.assertTrue(same_refs(result.observed_non_nodes, h.baseline_non_nodes))
        self.assert_neighbors(h)
        self.assertTrue(h.scene.dirty)  # never cleared as a false cleanliness signal
        self.assertEqual(result.original_error, "original-fault")
        self.assertIn("delete:before", result.events)
        self.assertIn("post:survivors", result.events)

    def test_safe_fully_attached_shell_fixture_delete_and_postcheck(self):
        h, result = fault()
        self.assertEqual(result.status, "CLEANED", result.errors)
        self.assertFalse(h.frame.node.alive)
        self.assertFalse(h.frame.base.alive)
        self.assertFalse(h.frame.shell.alive)
        self.assertIn("post:shell", result.events)
        self.assertIn("post:witness", result.events)
        self.assert_neighbors(h)

    def test_safe_cleanup_also_works_in_synthetic_empty_baseline(self):
        for point in ("pre_shell_validate:after", "probe:before"):
            with self.subTest(point=point):
                h, result = fault(point, scene=SyntheticScene(neighbors=0))
                self.assertEqual(result.status, "CLEANED", result.errors)
                self.assertEqual(result.observed_nodes, ())
                self.assertEqual(result.observed_non_nodes, ())
                self.assertFalse(h.frame.node.alive)

    def test_safe_unattached_shell_is_conditional_and_disposed_first(self):
        h, result = fault("pre_attach_validate:after", support=True)
        self.assertEqual(result.status, "CLEANED", result.errors)
        self.assertLess(result.events.index("dispose:before"), result.events.index("delete:before"))
        self.assertFalse(h.frame.shell.alive)
        self.assertFalse(h.frame.node.alive)
        self.assert_neighbors(h)

    def test_unattached_without_disposal_capability_retains_all(self):
        h, result = fault("pre_attach_validate:after")
        self.assert_refusal(h, result, "SHELL_DISPOSAL_UNSUPPORTED")
        self.assertTrue(h.frame.shell.alive)

    def test_stage_decision_truth_table_does_not_require_shell_before_constructor(self):
        # Expected results are explicit, not computed using the implementation's guard.
        table = (
            ("admission:before", "INCOMPLETE_CLEANUP", "CONTEXT_CHANGED"),
            ("node_construct:before", "INCOMPLETE_CLEANUP", "CONTEXT_CHANGED"),
            ("node_construct:allocated_before_return", "INCOMPLETE_CLEANUP", "NODE_CONSTRUCTION_UNKNOWN"),
            ("node_construct:after", "INCOMPLETE_CLEANUP", "NODE_REF_MISMATCH_OR_INVALID"),
            ("node_witness:after", "INCOMPLETE_CLEANUP", "NODE_REF_MISMATCH_OR_INVALID"),
            ("node_anchor:after", "INCOMPLETE_CLEANUP", "NODE_HANDLE_UNKNOWN"),
            ("node_handle:after", "INCOMPLETE_CLEANUP", "NODE_HANDLE_UNKNOWN"),
            ("node_handle_witness:after", "INCOMPLETE_CLEANUP", "NODE_HANDLE_UNKNOWN"),
            ("node_handle_anchor:after", "INCOMPLETE_CLEANUP", "BASE_REF_MISMATCH_OR_INVALID"),
            ("base_read:after", "INCOMPLETE_CLEANUP", "BASE_REF_MISMATCH_OR_INVALID"),
            ("base_witness:after", "INCOMPLETE_CLEANUP", "BASE_REF_MISMATCH_OR_INVALID"),
            ("base_anchor:after", "CLEANED", None),
            ("base_validate:after", "CLEANED", None),
            ("pre_shell_validate:after", "CLEANED", None),
            ("shell_construct:before", "INCOMPLETE_CLEANUP", "SHELL_CONSTRUCTION_UNKNOWN"),
            ("shell_construct:allocated_before_return", "INCOMPLETE_CLEANUP", "SHELL_CONSTRUCTION_UNKNOWN"),
            ("shell_construct:after", "INCOMPLETE_CLEANUP", "SHELL_REF_MISMATCH_OR_INVALID"),
            ("shell_witness:after", "INCOMPLETE_CLEANUP", "SHELL_REF_MISMATCH_OR_INVALID"),
            ("shell_anchor:after", "INCOMPLETE_CLEANUP", "SHELL_HANDLE_UNKNOWN"),
            ("shell_handle:after", "INCOMPLETE_CLEANUP", "SHELL_HANDLE_UNKNOWN"),
            ("shell_handle_witness:after", "INCOMPLETE_CLEANUP", "SHELL_HANDLE_UNKNOWN"),
            ("shell_handle_anchor:after", "CLEANED", None),
            ("shell_handle_validate:after", "CLEANED", None),
            ("pre_attach_validate:after", "CLEANED", None),
            ("attach:before", "INCOMPLETE_CLEANUP", "ATTACH_OUTCOME_UNKNOWN"),
            ("attach:effect_before_return", "INCOMPLETE_CLEANUP", "ATTACH_OUTCOME_UNKNOWN"),
            ("attach:after", "CLEANED", None),
            ("probe:before", "CLEANED", None),
        )
        for point, status, reason in table:
            with self.subTest(point=point):
                h, result = fault(point, support=True)
                self.assertEqual(result.status, status, result.errors)
                if reason:
                    self.assertTrue(any(reason in e for e in result.errors), result.errors)
                    self.assertNotIn("delete:before", result.events)
                    self.assertNotIn("dispose:before", result.events)
                else:
                    self.assertIn("delete:before", result.events)
                self.assert_neighbors(h)

    def test_constructor_effect_before_return_never_adopts_by_census_or_handle(self):
        for point, ref_name in (("node_construct:allocated_before_return", "node"),
                                ("shell_construct:allocated_before_return", "shell")):
            with self.subTest(point=point):
                h, result = fault(point, support=True)
                self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
                self.assertIsNone(getattr(h.frame, ref_name))
                self.assertNotIn("delete:before", result.events)
                self.assertNotIn("dispose:before", result.events)
                self.assertTrue(any(ref.kind == ref_name and ref.alive
                                    for ref in (*h.scene.nodes, *h.scene.non_nodes)))
                self.assert_neighbors(h)

    def test_partial_attachment_retained_with_and_without_visible_effect(self):
        for point, edge_expected in (("attach:before", False), ("attach:effect_before_return", True)):
            with self.subTest(point=point):
                h, result = fault(point, support=True)
                self.assert_refusal(h, result, "ATTACH_OUTCOME_UNKNOWN")
                self.assertEqual(any(edge == (h.frame.node, "modifier", h.frame.shell)
                                     for edge in h.scene.edges), edge_expected)
                self.assertTrue(h.frame.shell.alive)

    def test_forward_guards_refuse_foreign_graph_or_swapped_ref_before_next_mutation(self):
        def add_edge(h):
            h.scene.edges.append((h.baseline_nodes[0], "foreign-ref", h.frame.node))
        h = Harness(injections={"pre_shell_validate:before": Injection("drift", mutate=add_edge, action_only=True)})
        result = h.run()
        self.assertEqual(result.original_error, "GRAPH_MISMATCH")
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertNotIn("shell_construct:before", result.events)
        self.assertNotIn("delete:before", result.events)
        self.assertTrue(h.frame.node.alive)
        self.assert_neighbors(h)

        def swap_shell(h):
            old = h.frame.shell
            h.frame.shell = Ref("shell", old.handle)
            h.scene.handles[old.handle] = h.frame.shell
        h = Harness(injections={"pre_attach_validate:before": Injection("swap", mutate=swap_shell, action_only=True)})
        result = h.run()
        self.assertEqual(result.original_error, "SHELL_REF_MISMATCH_OR_INVALID")
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertNotIn("attach:before", result.events)
        self.assertNotIn("delete:before", result.events)
        self.assertTrue(h._retained_witness.shell.alive)
        self.assert_neighbors(h)

    def test_swapped_node_reference_same_handle_and_lookup_still_refused(self):
        captured = {}
        def swap(h):
            original = h.frame.node
            impostor = Ref("node", original.handle, base=original.base)
            h.frame.node = impostor
            h.scene.handles[original.handle] = impostor  # a matching lookup is not authority
            captured.update(original=original, impostor=impostor)
        h, result = fault(mutate=swap)
        self.assertEqual(captured["original"].handle, captured["impostor"].handle)
        self.assertIs(h.scene.handles[captured["impostor"].handle], captured["impostor"])
        self.assertIs(h._retained_witness.node, captured["original"])
        self.assertIs(h._retained_anchor.node, captured["original"])
        self.assert_refusal(h, result, "NODE_REF_MISMATCH_OR_INVALID")
        self.assertTrue(captured["original"].alive)
        self.assertTrue(captured["impostor"].alive)

    def test_swapped_shell_reference_same_handle_and_lookup_still_refused(self):
        captured = {}
        def swap(h):
            original = h.frame.shell
            impostor = Ref("shell", original.handle)
            h.frame.shell = impostor
            h.scene.handles[original.handle] = impostor
            captured.update(original=original, impostor=impostor)
        h, result = fault(mutate=swap)
        self.assertIs(h._retained_witness.shell, captured["original"])
        self.assertEqual(captured["original"].handle, captured["impostor"].handle)
        self.assertIs(h.scene.handles[captured["impostor"].handle], captured["impostor"])
        self.assert_refusal(h, result, "SHELL_REF_MISMATCH_OR_INVALID")
        self.assertTrue(captured["original"].alive)

    def test_ref_handle_and_roundtrip_faults_are_distinct(self):
        def missing_node(h): h.frame.node = None
        def missing_shell(h): h.frame.shell = None
        def bad_node(h): h.frame.node_handle += 1
        def bad_shell(h): h.frame.shell_handle += 1
        def unresolved_node(h): del h.scene.handles[h.frame.node_handle]
        def unresolved_shell(h): del h.scene.handles[h.frame.shell_handle]
        def invalid_node(h): h.frame.node.alive = False
        def invalid_shell(h): h.frame.shell.alive = False
        cases = ((missing_node, "NODE_REF_MISMATCH_OR_INVALID", False),
                 (missing_shell, "SHELL_REF_MISMATCH_OR_INVALID", True),
                 (bad_node, "NODE_HANDLE_MISMATCH", True), (bad_shell, "SHELL_HANDLE_MISMATCH", True),
                 (unresolved_node, "NODE_ROUNDTRIP_MISMATCH", True),
                 (unresolved_shell, "SHELL_ROUNDTRIP_MISMATCH", True),
                 (invalid_node, "NODE_REF_MISMATCH_OR_INVALID", False),
                 (invalid_shell, "SHELL_REF_MISMATCH_OR_INVALID", True))
        for mutate, reason, alive in cases:
            with self.subTest(reason=reason, mutate=mutate.__name__):
                h, result = fault(mutate=mutate)
                self.assert_refusal(h, result, reason, node_alive=alive)

    def test_missing_replaced_or_altered_witness_anchor_and_slots_refuse(self):
        def missing_witness(h): h.registry_witness = None
        def wrong_witness_type(h): h.registry_witness = object()
        def replaced_witness(h): h.registry_witness = Witness(**vars(h._retained_witness))
        def missing_anchor(h): h.anchor = None
        def wrong_anchor_type(h): h.anchor = object()
        def replaced_anchor(h): h.anchor = Anchor(**vars(h._retained_anchor))
        def wrong_anchor_witness(h): h.anchor.witness = Witness(**vars(h._retained_witness))
        def wrong_anchor_frame(h): h.anchor.frame = Slots(**vars(h.frame))
        def replaced_frame(h): h.frame = Slots(**vars(h.frame))
        def missing_node_witness(h): h._retained_witness.node = None
        def missing_shell_witness(h): h._retained_witness.shell = None
        def missing_node_handle(h): h.frame.node_handle = None
        def missing_shell_handle(h): h.frame.shell_handle = None
        def missing_base_anchor(h): h.anchor.base = None
        cases = ((missing_witness, "WITNESS_IDENTITY"), (wrong_witness_type, "WITNESS_IDENTITY"),
                 (replaced_witness, "WITNESS_IDENTITY"), (missing_anchor, "WITNESS_IDENTITY"),
                 (wrong_anchor_type, "WITNESS_IDENTITY"), (replaced_anchor, "WITNESS_IDENTITY"),
                 (wrong_anchor_witness, "WITNESS_IDENTITY"), (wrong_anchor_frame, "WITNESS_IDENTITY"),
                 (replaced_frame, "WITNESS_IDENTITY"), (missing_node_witness, "NODE_REF_MISMATCH_OR_INVALID"),
                 (missing_shell_witness, "SHELL_REF_MISMATCH_OR_INVALID"),
                 (missing_node_handle, "NODE_HANDLE_UNKNOWN"), (missing_shell_handle, "SHELL_HANDLE_UNKNOWN"),
                 (missing_base_anchor, "BASE_REF_MISMATCH_OR_INVALID"))
        for mutate, reason in cases:
            with self.subTest(mutate=mutate.__name__):
                h, result = fault(mutate=mutate)
                self.assert_refusal(h, result, reason)

    def test_context_selection_units_and_stage_drift_refuse(self):
        def root(h): h.scene.root = Ref("root")
        def path(h): h.scene.document = ("other", "", 0)
        def time(h): h.scene.document = ("untitled", "", 1)
        def dirty(h): h.scene.dirty = False
        def selection(h): h.scene.selection = [h.baseline_nodes[0]]
        def units(h): h.scene.units = ("centimeters", 0.1, 0.1)  # equal factor, changed pair
        def factor(h): h.scene.units = ("millimeters", 1.0, 1.0)
        def trace(h): h.completed.remove("shell_construct")
        cases = ((root, "CONTEXT_CHANGED"), (path, "CONTEXT_CHANGED"), (time, "CONTEXT_CHANGED"),
                 (dirty, "CONTEXT_CHANGED"), (selection, "SELECTION_CHANGED"), (units, "UNITS_CHANGED"),
                 (factor, "UNITS_CHANGED"), (trace, "TRACE_INVALID"))
        for mutate, reason in cases:
            with self.subTest(mutate=mutate.__name__):
                h, result = fault(mutate=mutate)
                self.assert_refusal(h, result, reason)

    def test_wrong_initial_units_refuse_before_node_constructor(self):
        scene = SyntheticScene()
        scene.units = ("centimeters", 0.1, 0.1)
        h, result = fault(scene=scene)
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertEqual(result.original_error, "ADMISSION_CONTEXT")
        self.assertNotIn("node_construct:before", result.events)
        self.assertTrue(same_refs(scene.nodes, h.baseline_nodes))
        self.assert_neighbors(h)

    def test_census_replacement_with_equal_count_is_not_accepted(self):
        def replace(h):
            old = h.baseline_nodes[0]
            fresh = Ref("node", old.handle, base=old.base)
            h.scene.nodes[h.scene.nodes.index(old)] = fresh
        h, result = fault(mutate=replace)
        self.assertEqual(len(h.scene.nodes), len(h.baseline_nodes) + 1)
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertTrue(any("CENSUS_MISMATCH" in e for e in result.errors))
        self.assertNotIn("delete:before", result.events)
        self.assertTrue(h.frame.node.alive)

    def test_foreign_node_edges_to_owned_node_base_and_shell_refuse(self):
        for target in ("node", "base", "shell"):
            for new_foreign in (False, True):
                with self.subTest(target=target, new_foreign=new_foreign):
                    def inject(h):
                        if new_foreign:
                            foreign = Ref("foreign-node", 900 + len(h.scene.nodes))
                            h.scene.nodes.append(foreign)
                            h.scene.handles[foreign.handle] = foreign
                        else:
                            foreign = h.baseline_nodes[0]
                        h.scene.edges.append((foreign, "foreign-node-ref", getattr(h.frame, target)))
                    h, result = fault(mutate=inject)
                    self.assert_refusal(h, result, "CENSUS_MISMATCH" if new_foreign else "GRAPH_MISMATCH")

    def test_foreign_non_node_edges_and_reverse_edges_refuse(self):
        for target in ("node", "base", "shell"):
            for reverse in (False, True):
                with self.subTest(target=target, reverse=reverse):
                    scene = SyntheticScene()
                    foreign = Ref("foreign-controller")
                    scene.non_nodes.append(foreign)  # already present in pre-attempt census
                    def inject(h):
                        owned = getattr(h.frame, target)
                        edge = (owned, "foreign-ref", foreign) if reverse else (foreign, "foreign-ref", owned)
                        h.scene.edges.append(edge)
                    h, result = fault(scene=scene, mutate=inject)
                    self.assert_refusal(h, result, "GRAPH_MISMATCH")
                    self.assertTrue(foreign.alive)

    def test_unexpected_foreign_non_node_and_new_node_each_refuse(self):
        def extra_non_node(h): h.scene.non_nodes.append(Ref("foreign-controller"))
        def extra_node(h): h.scene._new_node()
        for mutate, reason in ((extra_non_node, "NON_NODE_CENSUS_MISMATCH"), (extra_node, "CENSUS_MISMATCH")):
            with self.subTest(reason=reason):
                h, result = fault(mutate=mutate)
                self.assert_refusal(h, result, reason)

    def test_shared_base_is_never_treated_as_attempt_owned(self):
        def shared(h):
            base = h.baseline_nodes[0].base
            h.frame.node.base = base
            h.frame.base = h._retained_witness.base = h.anchor.base = base
        h, result = fault(mutate=shared)
        self.assert_refusal(h, result, "BASE_SHARED_WITH_BASELINE")

    def test_extra_parent_child_and_base_edges_refuse(self):
        for relation in ("parent", "child", "extra-base", "extra-modifier"):
            with self.subTest(relation=relation):
                def inject(h): h.scene.edges.append((h.frame.node, relation, h.baseline_nodes[0]))
                h, result = fault(mutate=inject)
                self.assert_refusal(h, result, "GRAPH_MISMATCH")

    def test_graph_completeness_unknown_and_unreadable_are_refusals(self):
        def unknown(h): h.scene.graph_complete = None
        def unreadable(h): h.scene.unreadable.add("graph")
        for mutate, reason in ((unknown, "GRAPH_COMPLETENESS_UNKNOWN"), (unreadable, "UNREADABLE_GRAPH")):
            with self.subTest(reason=reason):
                h, result = fault(mutate=mutate)
                self.assert_refusal(h, result, reason)

    def test_each_cleanup_guard_reader_failure_retains(self):
        names = ("witness", "context", "units", "selection", "node_ref", "node_handle", "base_ref",
                 "census", "shell_ref", "shell_handle", "graph")
        for name in names:
            with self.subTest(reader=name):
                def make_unreadable(h): h.scene.unreadable.add(name)
                h, result = fault(mutate=make_unreadable)
                self.assert_refusal(h, result, "UNREADABLE_" + name.upper())

    def test_fault_after_disposal_is_rechecked_before_node_delete(self):
        def unit_drift(h): h.scene.units = ("meters", 1.0, 100.0)
        h = Harness(standalone_disposal_supported=True, injections={
            "pre_attach_validate:after": Injection("original"),
            "dispose:after": Injection("drift", mutate=unit_drift, action_only=True),
        })
        result = h.run()
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertTrue(any("UNITS_CHANGED" in e for e in result.errors))
        self.assertFalse(h.frame.shell.alive)
        self.assertTrue(h.frame.node.alive)
        self.assertNotIn("delete:before", result.events)
        self.assert_neighbors(h)

        # A no-op disposal must reach the complete post-disposal guard; this
        # discriminates an omitted post-disposal validity check.
        scene = SyntheticScene()
        scene.dispose_mode = "noop"
        h, result = fault("pre_attach_validate:after", support=True, scene=scene)
        self.assertIn("dispose_post:before", result.events)
        self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
        self.assertTrue(any("SHELL_DISPOSAL_UNVERIFIED" in e for e in result.errors))
        self.assertNotIn("delete:before", result.events)
        self.assertTrue(h.frame.node.alive)

    def test_disposal_errors_or_noop_retain_node_and_report_effects(self):
        for mode, reason, shell_alive in (("throw_before", "DISPOSAL", True),
                                          ("throw_after", "DISPOSAL", False),
                                          ("noop", "SHELL_DISPOSAL_UNVERIFIED", True)):
            with self.subTest(mode=mode):
                scene = SyntheticScene()
                scene.dispose_mode = mode
                h, result = fault("pre_attach_validate:after", support=True, scene=scene)
                self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
                self.assertTrue(any(reason in e for e in result.errors), result.errors)
                self.assertNotIn("delete:before", result.events)
                self.assertTrue(h.frame.node.alive)
                self.assertEqual(h.frame.shell.alive, shell_alive)
                self.assertEqual(result.original_error, "original-fault")
                self.assert_neighbors(h)

    def test_delete_failure_noop_and_wrong_target_are_not_success(self):
        table = (("throw_before", True, True), ("throw_after", False, True),
                 ("noop", True, True), ("wrong_neighbor", True, False), ("collateral", False, False))
        for mode, owned_alive, neighbor_alive in table:
            with self.subTest(mode=mode):
                scene = SyntheticScene()
                scene.delete_mode = mode
                h, result = fault(scene=scene)
                self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
                self.assertEqual(h.frame.node.alive, owned_alive)
                self.assertEqual(h.baseline_nodes[0].alive, neighbor_alive)
                self.assertEqual(result.original_error, "original-fault")
                self.assertTrue(result.errors)
                self.assertIsNotNone(result.observed_nodes)
                if mode in ("wrong_neighbor", "collateral"):
                    self.assertTrue(any("SURVIVORS_MISMATCH" in e for e in result.errors))

    def test_every_postcheck_reader_error_does_not_hide_other_checks(self):
        for name in ("ref", "shell", "survivors", "non_nodes", "graph", "witness", "context"):
            with self.subTest(reader=name):
                def unreadable(h): h.scene.unreadable.add("post_" + name)
                h, result = fault(mutate=unreadable)
                self.assertEqual(result.status, "INCOMPLETE_CLEANUP")
                self.assertTrue(any("UNREADABLE_POST_" + name.upper() in e for e in result.errors))
                self.assertIn("post:context", result.events)
                self.assertFalse(h.frame.node.alive)
                self.assert_neighbors(h)

    def test_multiple_delete_and_postcheck_errors_preserve_original(self):
        scene = SyntheticScene()
        scene.delete_mode = "throw_before"
        def unreadable(h):
            h.scene.unreadable.update(("post_ref", "post_survivors"))
        h, result = fault(mutate=unreadable, scene=scene)
        self.assertEqual(result.original_error, "original-fault")
        self.assertTrue(any("DELETE:" in e for e in result.errors))
        self.assertTrue(any("UNREADABLE_POST_REF" in e for e in result.errors))
        self.assertTrue(any("UNREADABLE_POST_SURVIVORS" in e for e in result.errors))
        self.assertIn("post:context", result.events)
        self.assertTrue(h.frame.node.alive)

    def test_diagnostic_read_error_makes_cleaned_result_incomplete(self):
        def unreadable(h): h.scene.unreadable.add("diagnostic")
        h, result = fault(mutate=unreadable)
        self.assertEqual(result.status, "INCOMPLETE_DIAGNOSTICS")
        self.assertTrue(any("UNREADABLE_DIAGNOSTIC" in e for e in result.errors))
        self.assertIsNone(result.observed_nodes)
        self.assertFalse(h.frame.node.alive)

    def test_interrupt_at_every_construction_and_witness_boundary_never_cleans(self):
        points = [step + suffix for step in Harness.STEPS for suffix in (":before", ":after")]
        points += ["node_construct:allocated_before_return", "shell_construct:allocated_before_return",
                   "attach:effect_before_return"]
        for point in points:
            with self.subTest(point=point):
                h, result = fault(point, interrupt=True, support=True)
                self.assertEqual(result.status, "INCOMPLETE_INTERRUPTED")
                self.assertEqual(result.events[-1], point)
                self.assertNotIn("cleanup:begin", result.events)
                self.assertNotIn("delete:before", result.events)
                self.assertIsNone(result.observed_nodes)
                self.assert_neighbors(h)
                before = tuple(h.scene.nodes)
                again = h.run()
                self.assertEqual(again.status, "INCOMPLETE_NO_RETRY")
                self.assertTrue(same_refs(before, h.scene.nodes))

    def test_interrupt_during_cleanup_disposal_delete_or_postcheck_never_retries(self):
        cases = (("cleanup:begin", "probe:before", False), ("cleanup:guard_begin", "probe:before", False),
                 ("dispose:before", "pre_attach_validate:after", True),
                 ("dispose:effect_before_return", "pre_attach_validate:after", True),
                 ("dispose_post:before", "pre_attach_validate:after", True),
                 ("delete:before", "probe:before", False), ("delete:effect_before_return", "probe:before", False),
                 ("post:ref", "probe:before", False), ("post:survivors", "probe:before", False),
                 ("read:diagnostic", "probe:before", False))
        for interrupt_point, original_point, support in cases:
            with self.subTest(point=interrupt_point):
                h = Harness(standalone_disposal_supported=support, injections={
                    original_point: Injection("original"),
                    interrupt_point: Injection("interrupted", interrupt=True),
                })
                result = h.run()
                self.assertEqual(result.status, "INCOMPLETE_INTERRUPTED", result)
                self.assertEqual(result.original_error, "original")
                self.assertEqual(result.events[-1], interrupt_point)
                self.assertIsNone(result.observed_nodes)
                self.assertEqual(h.run().status, "INCOMPLETE_NO_RETRY")
                self.assert_neighbors(h)

    def test_no_fault_is_not_a_cleanup_or_acceptance_success(self):
        h = Harness()
        result = h.run()
        self.assertEqual(result.status, "INCOMPLETE_NO_FAULT")
        self.assertTrue(h.frame.node.alive)
        self.assertNotIn("delete:before", result.events)


if __name__ == "__main__":
    unittest.main(verbosity=2)
