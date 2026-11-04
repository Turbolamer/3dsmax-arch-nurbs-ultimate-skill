#!/usr/bin/env python3
"""Offline-only extraction of canonical preflight bodies and native calibrations.

Writes only to this explicitly owned Audit directory; never contacts 3ds Max.
Run from the repository root with Python -B. Existing unequal files are refused.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(relative: str, value: str) -> None:
    target = HERE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    data = value.encode("utf-8")
    if target.exists():
        if target.read_bytes() != data:
            raise RuntimeError(f"Refusing to overwrite unequal artifact: {target}")
        return
    with target.open("xb") as handle:
        handle.write(data)


def dump(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    sources = [ROOT / "scripts/env_preflight.py", ROOT / "scripts/scene_units.py"]
    before = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sources}
    env = runpy.run_path(str(sources[0]))
    units = runpy.run_path(str(sources[1]))
    specs = env["build_checks"]()
    manifest = []
    kinds = {
        "max_version": "STRICT_READ_ONLY",
        "units": "STRICT_READ_ONLY",
        "nurbset_present": "TRANSIENT_NON_NODE_CONSTRUCTION",
        "loft_not_creatable": "CONDITIONAL_SCENE_MUTATION_IF_BASELINE_CHANGES",
        "sweep_creatable": "TRANSIENT_NON_NODE_CONSTRUCTION",
        "sweep_on_shape": "SCENE_MUTATION",
        "quadpatch_creatable": "SCENE_MUTATION",
        "materials": "TRANSIENT_NON_NODE_CONSTRUCTION_OUT_OF_SCOPE",
    }
    for spec in specs:
        item = {"name": spec.name, "source": spec.source, "severity": spec.severity}
        if spec.source == env["SOURCE_MAXSCRIPT"]:
            relative = f"canonical/{spec.name}.ms"
            write_new(relative, spec.script)
            item.update(
                body=relative,
                sha256=hashlib.sha256(spec.script.encode("utf-8")).hexdigest(),
                classification=kinds[spec.name],
                provenance="Exact CheckSpec.script bytes; emitted, NOT executed in Max",
            )
        else:
            item.update(body=None, classification="TYPED_EVIDENCE_MAIN_ONLY")
        manifest.append(item)

    captures = []
    for filename, args, expected_exit in [
        ("canonical-emit.txt", [], 0),
        ("canonical-emit.json", ["--json"], 0),
        ("canonical-emit-require-complete.json", ["--json", "--require-complete"], 1),
    ]:
        cmd = [sys.executable, "-B", "scripts/env_preflight.py", *args]
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if p.returncode != expected_exit or p.stderr:
            raise RuntimeError(f"Unexpected offline emit outcome: {cmd!r}: {p.returncode}: {p.stderr}")
        if "--json" in args:
            result = json.loads(p.stdout)
            assert result["skip"] == len(specs) == 10
            assert all(row["status"] == "SKIP" for row in result["probes"])
        write_new(filename, p.stdout)
        captures.append({"command": cmd, "exit_code": p.returncode, "stdout": filename, "stderr": ""})

    # This evaluates the main's already captured entry string OFFLINE. It is not
    # another live observation and is not put into a purported current results set.
    entry = json.loads((ROOT / "Audit/_phase16-p3-live-entry-2026-11-02e.json").read_text(encoding="utf-8"))
    entry_string = entry["state"]["result"]
    assert "type=millimeters|scale=1.0" in entry_string
    supplied_reference = "SystemType=millimeters SystemScale=1.0"
    reference_eval = env["check_units"](env["ResultsRunner"]({"units": supplied_reference}))
    assert reference_eval.ok
    c, f = units["unit_factor"]("millimeters", 1.0)
    assert c == 0.1 and f == 10.0

    preamble = units["emit_unit_preamble"]("P16_P3E_modified_native_calibration", "__f_unit")
    guard = '''    local __before_count = objects.count
    local __before_selection = selection.count
    local __before_type = units.SystemType
    local __before_scale = units.SystemScale
    local __before_path = maxFilePath
    local __before_file = maxFileName
    local __before_save = getSaveRequired()
    if __before_count != 0 or __before_selection != 0 do throw "P16P3E_REFUSE: expected empty unselected scene"
    if __before_path != "" or __before_file != "" do throw "P16P3E_REFUSE: expected unnamed scene"
    if __before_type != #millimeters or __before_scale != 1.0 do throw "P16P3E_REFUSE: expected native millimeters scale 1"
'''
    native_readonly = '''(
    -- MODIFIED CALIBRATION, NOT a canonical env_preflight.py body. NOT LIVE-VERIFIED.
    -- No scene/unit/file/selection/dirty-flag writes. Current entry guards only.
''' + guard + preamble + '''
    local __cm_decode = units.decodeValue "1cm"
    local __mm10_decode = units.decodeValue "10mm"
    local __mm1_decode = units.decodeValue "1mm"
    local __ok = (abs (__c_cm - 0.1) <= 0.000001) and (abs (__f_unit - 10.0) <= 0.000001)
    __ok = __ok and (abs (__cm_decode - 10.0) <= 0.000001)
    __ok = __ok and (abs (__mm10_decode - __cm_decode) <= 0.000001)
    __ok = __ok and (abs (__mm1_decode - 1.0) <= 0.000001)
    local __unchanged = (objects.count == __before_count) and (selection.count == __before_selection)
    __unchanged = __unchanged and (units.SystemType == __before_type) and (units.SystemScale == __before_scale)
    __unchanged = __unchanged and (maxFilePath == __before_path) and (maxFileName == __before_file)
    __unchanged = __unchanged and ((getSaveRequired()) == __before_save)
    "MODIFIED_CALIBRATION|native_units_readonly|guard=ok|unitOk=" + (__ok as string) + "|unchanged=" + (__unchanged as string) + "|SystemType=" + (__before_type as string) + " SystemScale=" + (__before_scale as string) + "|c_cm_per_scene=" + (__c_cm as string) + "|f_scene_per_cm=" + (__f_unit as string) + "|decode_1cm=" + (__cm_decode as string) + "|decode_10mm=" + (__mm10_decode as string) + "|decode_1mm=" + (__mm1_decode as string)
)
'''
    write_new("modified/01_native_units_readonly.ms", native_readonly)

    native_box = '''(
    -- MODIFIED CALIBRATION, NOT a canonical env_preflight.py body. NOT LIVE-VERIFIED.
    -- OPTIONAL mutating measurement: one Box, zero modifiers, exact local-ref cleanup.
    -- Names are labels, NEVER lookup/deletion authority. Never clears dirty state.
''' + guard + preamble + '''
    local __node = undefined
    local __probe_threw = false
    local __probe_error = ""
    local __measure_ok = false
    local __mn = undefined
    local __mx = undefined
    local __actual_name = ""
    try
    (
        __node = Box name:"P16P3E_UNIT_6d04f9a2" width:(10.0 * __f_unit) length:(20.0 * __f_unit) height:(30.0 * __f_unit) pos:([100.0,200.0,300.0] * __f_unit) widthsegs:1 lengthsegs:1 heightsegs:1
        __actual_name = __node.name
        __mn = __node.min
        __mx = __node.max
        -- Independent literal native-unit expectation for mm/1, not an echo of f.
        __measure_ok = (distance __mn [950.0,1900.0,3000.0] <= 0.0001)
        __measure_ok = __measure_ok and (distance __mx [1050.0,2100.0,3300.0] <= 0.0001)
        __measure_ok = __measure_ok and (__node.modifiers.count == 0)
    )
    catch (__probe_threw = true; __probe_error = getCurrentException())

    -- CLEANUP FIRST after guarded work; no property formatting may precede it.
    local __cleanup_threw = false
    local __cleanup_error = ""
    if __node != undefined do
    (
        try (if isValidNode __node do delete __node)
        catch (__cleanup_threw = true; __cleanup_error = getCurrentException())
    )
    local __alive = false
    if __node != undefined do
    (
        try (__alive = isValidNode __node) catch (__alive = true)
    )
    local __census_ok = (objects.count == __before_count) and (selection.count == __before_selection)
    local __units_ok = (units.SystemType == __before_type) and (units.SystemScale == __before_scale)
    local __file_ok = (maxFilePath == __before_path) and (maxFileName == __before_file)
    local __save_after = getSaveRequired()
    "MODIFIED_CALIBRATION|native_box_roundtrip|guard=ok|probeThrew=" + (__probe_threw as string) + "|measureOk=" + (__measure_ok as string) + "|cleanupThrew=" + (__cleanup_threw as string) + "|ownedAlive=" + (__alive as string) + "|censusOk=" + (__census_ok as string) + "|unitsOk=" + (__units_ok as string) + "|fileOk=" + (__file_ok as string) + "|saveBefore=" + (__before_save as string) + "|saveAfter=" + (__save_after as string) + "|actualName=" + __actual_name + "|minNative=" + (__mn as string) + "|maxNative=" + (__mx as string) + "|probeError=" + __probe_error + "|cleanupError=" + __cleanup_error
)
'''
    write_new("modified/02_native_box_roundtrip.ms", native_box)
    write_new("results-template.json", dump({spec.name: None for spec in specs}))

    after = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sources}
    assert before == after
    write_new("preparation.json", dump({
        "status": "OFFLINE_PREPARATION_ONLY_NO_MAX_CALLS",
        "source_hashes_before": before,
        "source_hashes_after": after,
        "source_drift": before != after,
        "canonical_checks": manifest,
        "offline_commands": captures,
        "offline_reference_only": {
            "source": "Audit/_phase16-p3-live-entry-2026-11-02e.json",
            "interpretation": "Main's entry supplied by brief; not a new capture, not an overall preflight PASS",
            "units_text_normalization": supplied_reference,
            "canonical_units_evaluator_accepts": reference_eval.ok,
            "c_cm_per_native": c,
            "f_native_per_cm": f,
        },
        "modified_bodies_live_executed": False,
        "strict_readonly_recommended": ["canonical/max_version.ms", "canonical/units.ms", "modified/01_native_units_readonly.ms"],
        "optional_scene_measurement": "modified/02_native_box_roundtrip.ms",
        "class_api_rechecks_recommended": False,
    }))
    print(dump({"status": "OFFLINE_PREPARED_NOT_LIVE_VERIFIED", "source_drift": False, "canonical_bodies": 8, "offline_emit_checks": 10, "offline_emit_skip": 10, "native_factor_reference_only": {"c": c, "f": f}, "manifest": str(HERE / "preparation.json")}))


if __name__ == "__main__":
    main()
