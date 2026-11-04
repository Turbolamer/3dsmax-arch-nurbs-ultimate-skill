"""Offline emitted-source protections; NOT a MAXScript interpreter or Max test.

Positive/negative mutations exercise these source-contract detectors against the
actual generated text. No assertions establish 3ds Max behavior or compile it.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "Audit"))
from wall_surface_runtime import build_plan, generate_arm_script, generate_script
from test_phase16_p3_runtime import fixture, UNITS, IDENTITY


def emit():
    walls, dims = fixture()
    plan = build_plan(walls, dims)
    wall = generate_script(plan, IDENTITY, "P3RuntimeOffline", UNITS)
    arm = generate_arm_script(plan, IDENTITY, "P3RuntimeOffline", UNITS,
                              "FreshExplicitNonce0123456789")
    return wall, arm


def part(source, start, end):
    return source[source.index(start):source.index(end, source.index(start))]


def ordered(source, *parts):
    pos = -1
    for item in parts:
        pos = source.find(item, pos + 1)
        if pos < 0:
            return False
    return True


def cleanup_refuses_deletion(source):
    block = source[source.index('local reportErrors = #()'):]
    return ("getAnimByHandle" not in block and "delete exactNode" not in block
            and "delete candidate" not in block
            and '"RETAINED_NO_CALIBRATED_DEPENDENCY_EXCLUSION"' in block)


def protects_conversion(source):
    body = part(source, 'stage = "convert"', 'stage = "grid-vertices"')
    return (ordered(body, 'local converted = convertTo node Editable_Poly',
                    'append conversionRefs converted',
                    'converted == node', '(getAnimByHandle initialHandle) == node')
            and 'node = getAnimByHandle initialHandle' not in body)


def preevaluation_order(source):
    body = part(source, 'fn p3NodeSnapshot node', 'fn p3CensusGuard node')
    return ordered(body, 'objects.count == 1', 'local shellMod = node.modifiers[1]',
                   'local nodeRef = p3ExactRef node', 'local graphState = p3GraphSnapshot node',
                   'local evaluatedState = p3EvaluatedSnapshot node')


def interpret_status_expression(source, state):
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


class ProtectiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wall, cls.arm = emit()

    def test_preedit_snapshot_is_exact_settled_hash(self):
        saved = Path(__file__).with_name("wall_surface_runtime.pre-edit.py.bin").read_bytes()
        self.assertEqual(hashlib.sha256(saved).hexdigest(),
                         "bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15")

    def test_cleanup_never_promotes_handle_or_deletes_exact_node(self):
        self.assertTrue(cleanup_refuses_deletion(self.wall))
        block = self.wall.index('local reportErrors = #()')
        self.assertFalse(cleanup_refuses_deletion(self.wall[:block] +
                          self.wall[block:].replace('local exactNode = createdRefs[i]',
                          'local exactNode = getAnimByHandle createdHandles[i]', 1)))
        self.assertFalse(cleanup_refuses_deletion(self.wall + '\n delete exactNode\n'))

    def test_conversion_candidate_saved_before_continuity_check(self):
        self.assertTrue(protects_conversion(self.wall))
        mutation = self.wall.replace('append conversionRefs converted', '-- candidate lost', 1)
        self.assertFalse(protects_conversion(mutation))
        mutation = self.wall.replace('converted == node', 'converted != undefined', 1)
        self.assertFalse(protects_conversion(mutation))

    def test_no_candidate_return_and_unknown_census_are_incomplete(self):
        failure = self.wall[self.wall.index('local reportErrors = #()'):]
        for marker in ('CONSTRUCTOR_RETURN_NOT_OBSERVED', 'CONVERSION_RETURN_NOT_OBSERVED',
                       'UNKNOWN_OR_NONEMPTY_POST_FAILURE_CENSUS', 'UNRESOLVED_CREATED_REF',
                       'UNRESOLVED_CONVERSION_CANDIDATE', 'P3_INCOMPLETE_RESIDUAL'):
            self.assertIn(marker, failure)
        self.assertTrue(ordered(failure, 'censusCount = objects.count',
                                'for i = 1 to createdRefs.count'))
        self.assertIn('if attemptStarted or unresolvedEntry or not censusKnown', failure)
        self.assertIn('|original=', failure)
        self.assertIn('|reportErrors=', failure)

    def test_extracted_status_branch_truth_table(self):
        base = dict(attemptStarted=False, unresolvedEntry=False, censusKnown=True,
                    reportErrors=[], residual=[], stage="entry")
        cases = [({}, 'P3_REFUSED'),
                 ({'stage': 'replay-read-only'}, 'P3_INCOMPLETE_REPLAY'),
                 ({'attemptStarted': True}, 'P3_INCOMPLETE_RESIDUAL'),
                 ({'unresolvedEntry': True}, 'P3_INCOMPLETE_RESIDUAL'),
                 ({'censusKnown': False}, 'P3_INCOMPLETE_RESIDUAL'),
                 ({'reportErrors': ['read failed']}, 'P3_INCOMPLETE_RESIDUAL'),
                 ({'residual': ['unknown']}, 'P3_INCOMPLETE_RESIDUAL'),
                 ({'stage': 'replay-read-only', 'reportErrors': ['read failed']},
                  'P3_INCOMPLETE_RESIDUAL')]
        for change, expected in cases:
            with self.subTest(change=change):
                self.assertEqual(interpret_status_expression(self.wall, {**base, **change}), expected)
        mutation = self.wall.replace('attemptStarted or unresolvedEntry',
                                     'attemptStarted and unresolvedEntry', 1)
        self.assertNotEqual(interpret_status_expression(mutation, {**base, 'attemptStarted': True}),
                            'P3_INCOMPLETE_RESIDUAL')

    def test_observed_census_records_exact_objects_for_manual_inspection(self):
        self.assertIn('append observedCensus observed', self.wall)
        self.assertIn('conversionRefs, residual, cleanupOutcomes, observedCensus', self.wall)
        self.assertIn('censusNodes[1] == node', self.wall)
        self.assertIn('censusCount <= 64', self.wall)

    def test_dirty_arm_and_prior_unresolved_refuse_before_building(self):
        body = part(self.wall, 'if lease[5] == "BUILDING"', 'local node = Editable_Mesh()')
        self.assertTrue(ordered(body, 'INCOMPLETE: prior BUILDING/POISONED',
                                'getSaveRequired() == lease[10]',
                                'attemptStarted = true', 'lease[5] = "BUILDING"',
                                'lease[8] = attemptEvidence'))
        self.assertIn('(classOf lease[10]) == BooleanClass', self.wall)

    def test_attempt_refs_captured_before_next_risky_operation(self):
        body = part(self.wall, 'attemptStarted = true', 'stage = "grid-vertices"')
        self.assertTrue(ordered(body, 'lease[8] = attemptEvidence',
                                'constructorStarted = true', 'local node = Editable_Mesh()',
                                'append createdRefs node', 'getHandleByAnim node',
                                'append createdHandles initialHandle', 'conversionStarted = true',
                                'local converted = convertTo', 'append conversionRefs converted'))

    def test_local_nonce_copy_is_rechecked_but_not_called_independent(self):
        self.assertIn('local localNonce = copy lease[6]', self.wall)
        before_build = part(self.wall, 'stage = "pre-create"', 'attemptStarted = true')
        self.assertIn('lease[6] == localNonce', before_build)
        self.assertIn('independent witness still required', before_build)

    def test_replay_is_incomplete_before_node_inspection_or_mutation(self):
        replay = part(self.wall, 'stage = "replay-read-only"', 'stage = "pre-create"')
        self.assertIn('p3RequireState false "INCOMPLETE_REPLAY:', replay)
        for op in ('p3NodeSnapshot ', 'snapshotAsMesh', 'delete ', 'globalVars.set',
                   'setUserProp', 'convertTo ', 'addModifier', 'lease[5] ='):
            self.assertNotIn(op, replay)
        self.assertIn('P3_INCOMPLETE_REPLAY', self.wall)
        self.assertNotIn('P3_NOOP|', self.wall)

    def test_partial_cheap_checks_precede_evaluation_but_are_not_complete(self):
        self.assertTrue(preevaluation_order(self.wall))
        mutation = self.wall.replace('local graphState = p3GraphSnapshot node',
                                     'local graphState = undefined', 1)
        self.assertFalse(preevaluation_order(mutation))
        self.assertIn('this traversal is incomplete and is NOT an evaluation safety', self.wall)
        self.assertIn('Construction must not be run until main resolves', self.wall)

    def test_required_fields_refuse_instead_of_absent_equals_absent(self):
        body = part(self.wall, 'local explicitNames =', 'local userBuffer =')
        self.assertIn('p3RequireState (isProperty node p)', body)
        self.assertNotIn('#("absent")', body)

    def test_mutable_user_buffer_is_copied_before_baseline(self):
        body = part(self.wall, 'local userBuffer = getUserPropBuffer node',
                    'local evaluatedState =')
        self.assertTrue(ordered(body, '(classOf userBuffer) == String',
                                'userBuffer = copy userBuffer', 'local layerState ='))
        self.assertIn('(copy maxFilePath), (copy maxFileName)', self.arm)
        self.assertIn('(copy identity), (copy binding), (copy ownerNamespace)', self.arm)
        self.assertIn('(copy maxFilePath), (copy maxFileName)', self.wall)

    def test_snapshot_disposal_unknown_propagates_into_outer_status(self):
        body = part(self.wall, 'fn p3EvaluatedSnapshot node', 'fn p3NodeSnapshot node')
        self.assertIn('snapshotDisposalState = "DISPOSAL_UNKNOWN"', body)
        self.assertIn('snapshotDisposalError = getCurrentException() as string', body)
        self.assertIn('snapshotDisposalState = "DISPOSAL_CALL_RETURNED_AFTER_READ_FAILURE"', body)
        self.assertIn('SNAPSHOT_DISPOSAL_UNKNOWN', self.wall)
        self.assertIn('|snapshotError=', self.wall)
        self.assertIn('|original=', body)

    def test_arm_cleanup_requires_exact_published_instance_and_reports_failure(self):
        body = self.arm[self.arm.index('local declaredHere = false'):]
        self.assertTrue(ordered(body, 'declaredHere and (globalVars.get registryKey) == witness',
                                'globalVars.remove registryKey',
                                'if globalVars.isGlobal registryKey'))
        for marker in ('RETAINED_UNPROVEN_OR_REPLACED_GLOBAL', 'REMOVAL_OR_READBACK_UNKNOWN',
                       '|cleanupError=', '|original=', '|key='):
            self.assertIn(marker, body)

    def test_runtime_documents_independent_witness_not_self_authentication(self):
        self.assertIn('must compare the independently held struct and detached fields', self.wall)
        self.assertIn('Retain this exact struct AND detached expected fields', self.arm)
        self.assertIn('self-read cannot prove an independently retained witness', self.wall)

    def test_commit_is_construction_marker_not_replay_acceptance(self):
        self.assertIn("Contract's construction-only marker, NOT accepted replay/QA", self.wall)
        self.assertIn('lease[5] = "COMMITTED"', self.wall)
        self.assertIn('P3_CREATED_UNVERIFIED|', self.wall)


if __name__ == '__main__':
    unittest.main(verbosity=2)
