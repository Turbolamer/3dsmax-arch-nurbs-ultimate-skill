"""Audit-only syntax smoke and adapter faults. NOT a Max parser or live test."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import unittest


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("p3_measurement_adapter", HERE / "adapter.py")
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)
CAL_SPEC = importlib.util.spec_from_file_location("p3_snapshot_calibration", HERE / "calibration.py")
CAL = importlib.util.module_from_spec(CAL_SPEC)
CAL_SPEC.loader.exec_module(CAL)


def sample(stage="final"):
    mesh = {"coordinate_space": "world", "index_base": 1,
            "vertices": [[0.0, 0.0, 0.0], [100.0, 0.0, 0.0], [100.0, 0.0, 100.0], [0.0, 0.0, 100.0]],
            "faces": [[1, 2, 3, 4]]}
    raw = {"schema_version": "p3-independent-measurement-1", "status": "CAPTURED_NOT_ACCEPTED",
           "stage": stage, "units": {"system_type": "millimeters", "system_scale": 1.0, "scene_units_per_cm": 10.0},
           "target": {"anim_handle": "10", "node_handle": "11", "base_anim_handle": "12", "object_transform": []}}
    if stage == "grid":
        raw["grid"] = deepcopy(mesh)
    else:
        raw["base"] = mesh
        raw["evaluated"] = deepcopy(mesh)
        del raw["evaluated"]["faces"]
        raw["evaluated"]["triangles"] = [[1, 2, 3], [1, 3, 4]]
    return raw


EVIDENCE = {"kind": "synthetic_test", "length_unit": "cm"}


def synthetic_calibration(matrix):
    """Explicitly synthetic nonidentity one-quad, not a produced/live fixture.

    Construct expected positions by the test's own literal matrix multiplication,
    rather than by calling calibration.transform_once or any generator helper.
    """
    points = [[2.0, 0.0, 3.0], [13.0, 0.0, 3.0], [13.0, 0.0, 10.0], [2.0, 0.0, 10.0]]
    world = [[p[0]*matrix[0][j] + p[1]*matrix[1][j] + p[2]*matrix[2][j] + matrix[3][j]
              for j in range(3)] for p in points]
    return {"schema_version": "p3-snapshot-calibration-1", "status": "CAPTURED_NOT_ACCEPTED",
            "index_base": 1, "base_vertices_local": points, "base_faces": [[1, 2, 3, 4]],
            "object_transform": deepcopy(matrix), "base_vertices_world_once": deepcopy(world),
            "snapshot_vertices_world": deepcopy(world), "snapshot_triangles": [[1, 2, 3], [1, 3, 4]],
            "node_bounds_world": [[min(p[j] for p in world) for j in range(3)],
                                  [max(p[j] for p in world) for j in range(3)]],
            "evidence_scope": "synthetic_test"}


TRANSLATED = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [37, -19, 11]]
ROTATED = [[0, 1, 0], [-1, 0, 0], [0, 0, 1], [0, 0, 0]]
ROTATED_TRANSLATED = [[0, 1, 0], [-1, 0, 0], [0, 0, 1], [37, -19, 11]]


def reserved_name_faults(source):
    """Small lexical guard, not a MAXScript parser or full language validator.

    Strip comments/quoted strings, then reject known MAXScript reserved words in
    declared-name or assignment-target slots. Includes mixed-case and `local x=1,
    by=2` faults. Legitimate `for i=1 to 4 by 1 do` must remain permitted.
    """
    token = re.compile(r'--[^\n]*|/\*.*?\*/|@"(?:[^"]|"")*"|"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z_0-9]*|\+=|-=|\*=|/=|==|!=|<=|>=|=', re.S)
    tokens = [match.group().lower() for match in token.finditer(source)
              if not match.group().startswith(("--", "/*", '"', '@"'))]
    reserved = set("about and animate as at attributes by case catch collect continue coordsys do else exit false fn for from function global if in local macroscript mapped max not of off on or parameters persistent plugin rcmenu return rollout set struct then throw to tool true try undo utility when where while with".split())
    declaration = {"local", "global", "persistent", "fn", "function", "for"}
    assignment = {"=", "+=", "-=", "*=", "/="}
    return [(i, value) for i, value in enumerate(tokens) if value in reserved and
            ((i > 0 and tokens[i-1] in declaration) or (i+1 < len(tokens) and tokens[i+1] in assignment))]


class AdapterChecks(unittest.TestCase):
    def test_scale_triangles_and_no_invention(self):
        raw = sample()
        before = deepcopy(raw)
        result = ADAPTER.oracle_capture(raw, EVIDENCE)
        self.assertEqual(result["base"]["vertices_cm"][2], [10.0, 0.0, 10.0])
        self.assertEqual(result["evaluated"]["triangles"], [[1, 2, 3], [1, 3, 4]])
        self.assertNotIn("faces", result["evaluated"])
        self.assertNotIn("grid", result)
        self.assertEqual(raw, before)
        result["evaluated"]["triangles"][0][0] = 99
        self.assertEqual(raw, before)

    def test_normalization_preserves_nonidentity_world_observations(self):
        # Adapter-only format controls, not a physical Shell/produced fixture.
        for matrix in (TRANSLATED, ROTATED, ROTATED_TRANSLATED):
            calibration = synthetic_calibration(matrix)
            raw = sample()
            raw["target"]["object_transform"] = deepcopy(matrix)
            raw["base"]["vertices"] = deepcopy(calibration["base_vertices_world_once"])
            raw["evaluated"]["vertices"] = deepcopy(calibration["snapshot_vertices_world"])
            with self.subTest(matrix=matrix):
                result = ADAPTER.oracle_capture(raw, EVIDENCE)
                expected = [[x/10 for x in p] for p in calibration["snapshot_vertices_world"]]
                self.assertEqual(result["evaluated"]["vertices_cm"], expected)
                self.assertEqual(result["base"]["vertices_cm"], expected)
                self.assertNotIn("faces", result["evaluated"])

    def test_real_grid_input_retained_and_join_bound(self):
        result = ADAPTER.oracle_capture(sample(), EVIDENCE, grid_raw=sample("grid"))
        self.assertEqual(result["grid"]["faces"], [[1, 2, 3, 4]])
        for key in ("anim_handle", "node_handle", "base_anim_handle", "object_transform"):
            grid = sample("grid")
            grid["target"][key] = "changed"
            with self.subTest(key=key), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(sample(), EVIDENCE, grid_raw=grid)

    def test_bad_units_and_indexes_refuse(self):
        for value in (True, 0, -1, float("nan"), float("inf"), "10"):
            raw = sample()
            raw["units"]["scene_units_per_cm"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(raw, EVIDENCE)
        for value in (True, "2", 2.0):
            raw = sample()
            raw["evaluated"]["triangles"][0][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(raw, EVIDENCE)
        raw = sample()
        raw["base"]["index_base"] = True
        with self.assertRaises(ValueError):
            ADAPTER.oracle_capture(raw, EVIDENCE)

    def test_nonfinite_and_missing_evidence_refuse(self):
        raw = sample()
        raw["base"]["vertices"][0][0] = float("nan")
        with self.assertRaises(ValueError):
            ADAPTER.oracle_capture(raw, EVIDENCE)
        for evidence in (None, {}, {"kind": "scene_capture", "length_unit": "mm"}):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(sample(), evidence)
        for field in ("vertices", "triangles"):
            raw = sample()
            del raw["evaluated"][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(raw, EVIDENCE)

    def test_grid_units_and_state_refuse(self):
        for field, value in (("status", "PASS"), ("stage", "final"), ("schema_version", "other")):
            raw = sample("grid")
            raw[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                ADAPTER.oracle_capture(sample(), EVIDENCE, grid_raw=raw)
        grid = sample("grid")
        grid["units"]["system_type"] = "centimeters"
        with self.assertRaises(ValueError):
            ADAPTER.oracle_capture(sample(), EVIDENCE, grid_raw=grid)


class StaticFileChecks(unittest.TestCase):
    def test_integer64_json_suffix_regression(self):
        source = (HERE / "measure.ms").read_text(encoding="utf-8")
        self.assertIn("Integer64: jint value", source)
        self.assertIn("Integer: jint value", source)
        self.assertIn("(jint fileBytes)", source)
        self.assertIn('(jint (3516 as Integer64)) != "3516"', source)
        writer = (HERE / "calibrate_writer.ms").read_text(encoding="utf-8")
        self.assertIn("(integerValue fileBytes)", writer)
        self.assertIn("(integerValue expectedBytes)", writer)
        for module in (source, writer):
            self.assertNotIn("(fileBytes as string)", module)
            self.assertIn('if s.count > 0 and (toLower (substring s s.count 1)) == "l" do s = substring s 1 (s.count - 1)', module)
            self.assertIn('findString "0123456789"', module)
        for raw, expected in (("3516L", 3516), ("-3516L", -3516), ("0L", 0),
                              ("9223372036854775807L", 9223372036854775807),
                              ("-9223372036854775808L", -9223372036854775808)):
            with self.subTest(raw=raw):
                # Mirror only suffix removal to demonstrate JSON grammar and exact
                # decimal preservation, not pretend to run MAXScript interop.
                stripped = raw[:-1] if raw[-1:].lower() == "l" else raw
                self.assertEqual(json.loads('{"bytes":' + stripped + '}')["bytes"], expected)
                with self.assertRaises(json.JSONDecodeError):
                    json.loads('{"bytes":' + raw + '}')

    def test_reserved_variable_names_absent_from_owned_maxscript(self):
        for filename in ("measure.ms", "calibrate_snapshot.ms", "calibrate_writer.ms"):
            with self.subTest(filename=filename):
                self.assertEqual(reserved_name_faults((HERE / filename).read_text(encoding="utf-8")), [])

    def test_reserved_name_guard_fault_controls(self):
        for word in ("by", "on", "off", "to", "from", "at", "By", "ON"):
            for source in ("local " + word + " = 1", "local okay = 1, " + word + "=2", "for " + word + " = 1 to 4 do ()"):
                with self.subTest(word=word, source=source):
                    self.assertTrue(reserved_name_faults(source))
        self.assertEqual(reserved_name_faults('local okay = "local by = 1" -- local on = 2\nfor i=1 to 4 by 1 do (okay += 1)'), [])

    def test_delimiters_only_not_maxscript_parse(self):
        for filename in ("measure.ms", "calibrate_snapshot.ms", "calibrate_writer.ms"):
            with self.subTest(filename=filename):
                self.check_delimiters((HERE / filename).read_text(encoding="utf-8"))

    def check_delimiters(self, source):
        stack = []
        pairs = {")": "(", "]": "[", "}": "{"}
        quoted = comment = escaped = False
        pos = 0
        while pos < len(source):
            char = source[pos]
            pos += 1
            if comment:
                comment = char != "\n"
                continue
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == "-" and pos < len(source) and source[pos] == "-":
                comment = True
            elif char == '"':
                quoted = True
            elif char in "([{":
                stack.append(char)
            elif char in ")]}":
                self.assertTrue(stack, "unmatched closing delimiter")
                self.assertEqual(stack.pop(), pairs[char])
        self.assertFalse(quoted)
        self.assertFalse(stack)

    def test_forbidden_scene_operations_not_present(self):
        lines = (HERE / "measure.ms").read_text(encoding="utf-8").splitlines()
        operational = "\n".join(line for line in lines if not line.lstrip().startswith("--"))
        for forbidden in ("convertTo", "collapseStack", "getNodeByName", "delete n", "delete o", "addModifier", "snapshot n", "formattedPrint"):
            self.assertNotIn(forbidden, operational)
        self.assertIn("FileMode\").CreateNew", operational)
        self.assertIn("delete tmpMesh", operational)

    def test_snapshot_reads_world_without_second_transform(self):
        measure = (HERE / "measure.ms").read_text(encoding="utf-8")
        self.assertIn("in coordsys world (for i = 1 to evaluatedVerts collect (getVert tmpMesh i))", measure)
        self.assertNotIn("(getVert tmpMesh i) *", measure)
        calibration = (HERE / "calibrate_snapshot.ms").read_text(encoding="utf-8")
        self.assertIn("in coordsys world (for i = 1 to 4 collect (getVert meshValue i))", calibration)
        self.assertNotIn("(getVert meshValue i) *", calibration)
        # Explicit local-base transform is legitimate and must remain separate.
        self.assertIn("for p in baseLocal collect (p * n.objectTransform)", measure)

    def test_writer_avoids_marshaled_byte_array_overload_and_flushes_before_hash(self):
        for filename in ("measure.ms", "calibrate_writer.ms"):
            source = (HERE / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn('dotNetObject "System.Text.UTF8Encoding" false', source)
                self.assertIn('dotNetObject "System.IO.StreamWriter" outputStream encoding', source)
                self.assertIn('FileMode").CreateNew', source)
                self.assertIn('FileShare").None', source)
                self.assertIn("encoding.GetByteCount", source)
                self.assertNotIn("encoding.GetBytes", source)
                self.assertNotIn("bytes.Length", source)
                self.assertNotIn("outputStream.Write bytes", source)
                self.assertNotIn("System.BitConverter", source)
                self.assertIn("digest.count != 32", source)
                self.assertIn("for byteValue in digest do", source)
                write = source.index("outputWriter.Write ")
                writer_flush = source.index("outputWriter.Flush()", write)
                file_flush = source.index("outputStream.Flush()", writer_flush)
                rewind = source.index("outputStream.Position = 0", file_flush)
                hashed = source.index("hashProvider.ComputeHash outputStream", rewind)
                close = source.index("outputWriter.Close()", hashed)
                self.assertLess(write, writer_flush)
                self.assertLess(writer_flush, file_flush)
                self.assertLess(file_flush, rewind)
                self.assertLess(rewind, hashed)
                self.assertLess(hashed, close)


class NonidentityCalibrationChecks(unittest.TestCase):
    def test_translated_rotated_and_combined_positive(self):
        for matrix, flags in ((TRANSLATED, (True, False)), (ROTATED, (False, True)), (ROTATED_TRANSLATED, (True, True))):
            raw = synthetic_calibration(matrix)
            before = deepcopy(raw)
            with self.subTest(matrix=matrix):
                result = CAL.assess_snapshot_calibration(raw)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual((result["translation_exercised"], result["rotation_exercised"]), flags)
                self.assertEqual(raw, before)

    def test_original_double_transform_fault_discriminates_each_motion(self):
        for matrix in (TRANSLATED, ROTATED, ROTATED_TRANSLATED):
            raw = synthetic_calibration(matrix)
            raw["snapshot_vertices_world"] = [[p[0]*matrix[0][j] + p[1]*matrix[1][j] + p[2]*matrix[2][j] + matrix[3][j]
                                                for j in range(3)] for p in raw["snapshot_vertices_world"]]
            with self.subTest(matrix=matrix):
                result = CAL.assess_snapshot_calibration(raw)
                self.assertEqual(result["status"], "FAIL")
                self.assertFalse(result["checks"]["SNAPSHOT_ALREADY_WORLD"])
                self.assertFalse(result["checks"]["SNAPSHOT_NOT_DOUBLE_TRANSFORMED"])

    def test_identity_nonrigid_and_unsupported_capture_refuse(self):
        for matrix in ([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]],
                       [[2, 0, 0], [0, 1, 0], [0, 0, 1], [37, -19, 11]],
                       [[-1, 0, 0], [0, 1, 0], [0, 0, 1], [37, -19, 11]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                CAL.assess_snapshot_calibration(synthetic_calibration(matrix))
        for value in (None, {}, {"status": "PASS"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                CAL.assess_snapshot_calibration(value)

    def test_local_snapshot_and_bad_independent_channel_fail(self):
        raw = synthetic_calibration(ROTATED_TRANSLATED)
        raw["snapshot_vertices_world"] = deepcopy(raw["base_vertices_local"])
        self.assertEqual(CAL.assess_snapshot_calibration(raw)["status"], "FAIL")
        raw = synthetic_calibration(TRANSLATED)
        raw["base_vertices_world_once"][0][0] += 1
        self.assertFalse(CAL.assess_snapshot_calibration(raw)["checks"]["BASE_LOCAL_TIMES_MATRIX_ONCE"])
        raw = synthetic_calibration(ROTATED)
        raw["node_bounds_world"][0][0] += 1
        self.assertFalse(CAL.assess_snapshot_calibration(raw)["checks"]["NODE_WORLD_BBOX"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
