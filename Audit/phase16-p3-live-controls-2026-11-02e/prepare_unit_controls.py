#!/usr/bin/env python3
"""CURRENT SCOPE: offline three bounded pre-registry unit controls, no Max calls.

Actual F01 input plan -> actual frozen runtime generator. No arm, positive replay
admission or publication-pair claim. All writes stay in a new owned audit child.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import struct
import sys

from prepare_controls import HERE, ROOT, digest, encode, ms_string, once, strict_json


def harness(script: Path, registry: str, expected_reason: str, label: str):
    return f'''-- MAIN ONLY; audit unit refusal, NO ARM and NO unit/scene/global setters.
(
    local artifactPath = {ms_string(str(script))}
    local registryKey = {ms_string(registry)} as name
    if globalVars.isGlobal registryKey do throw "UNIT_CONTROL_ABORT|fresh namespace already present"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "UNIT_CONTROL_ABORT|actual mm/1 required; NEVER change scene units"
    if objects.count > 64 do throw "UNIT_CONTROL_ABORT|bounded census exceeded"
    local beforeNodes = for n in objects collect #(n, getHandleByAnim n)
    local beforeSelection = selection as array
    local beforeType = units.SystemType
    local beforeScale = units.SystemScale
    local beforeDirty = getSaveRequired()
    local beforePath = maxFilePath
    local beforeFile = maxFileName
    local beforeTime = currentTime
    local beforeSubobject = subObjectLevel
    local threw = false
    local reason = ""
    try (fileIn artifactPath quiet:true) catch (threw = true; reason = getCurrentException() as string)
    print ("UNIT_CONTROL_RAW|case={label}|threw=" + (threw as string) + "|reason=" + reason)
    if not threw do throw "UNIT_CONTROL_FAIL|expected actual runtime exception"
    -- Runtime prints P3_REFUSED|stage=entry but bare-throws original P3_REFUSE.
    -- Main MUST separately verify printed entry-stage marker in raw wire stdout.
    if (findString reason {ms_string(expected_reason)}) == undefined do throw "UNIT_CONTROL_FAIL|wrong refusal reason; NOT target unit guard"
    if (findString reason "P3_REFUSE|") == undefined do throw "UNIT_CONTROL_FAIL|not actual runtime refusal"
    if globalVars.isGlobal registryKey do throw "UNIT_CONTROL_FAIL|registry declared/published before refusal"
    local afterNodes = for n in objects collect #(n, getHandleByAnim n)
    if afterNodes.count != beforeNodes.count do throw "UNIT_CONTROL_FAIL|scene census mutation"
    for i = 1 to beforeNodes.count do
        (if beforeNodes[i][1] != afterNodes[i][1] or beforeNodes[i][2] != afterNodes[i][2] do throw "UNIT_CONTROL_FAIL|exact node identity changed")
    local afterSelection = selection as array
    if beforeSelection.count != afterSelection.count do throw "UNIT_CONTROL_FAIL|selection mutation"
    for i = 1 to beforeSelection.count do
        (if beforeSelection[i] != afterSelection[i] do throw "UNIT_CONTROL_FAIL|selection identity changed")
    if units.SystemType != beforeType or units.SystemScale != beforeScale or getSaveRequired() != beforeDirty or maxFilePath != beforePath or maxFileName != beforeFile or currentTime != beforeTime or subObjectLevel != beforeSubobject do throw "UNIT_CONTROL_FAIL|units or protected context changed"
    print "UNIT_CONTROL_TARGET_REFUSAL_UNCHANGED|case={label}|arm=NOT_USED|live_geometry=NOT_TESTED|main_verify_printed_stage_entry=true"
)
'''


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    try:
        out = Path(a.out).absolute()
        if out.exists() or out.parent.resolve() != HERE:
            raise ValueError("output must be a NEW direct child of this owned audit folder")
        paths = [ROOT / "scripts" / "wall_surface_runtime.py", ROOT / "scripts" / "scene_units.py",
                 ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e" / "project" / "walls.json",
                 ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e" / "project" / "dimensions.json"]
        before = {str(path): digest(path.read_bytes()) for path in paths}
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("p3_units_actual_runtime", paths[0])
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        plan = runtime.build_plan(strict_json(paths[2].read_bytes()), strict_json(paths[3].read_bytes()))
        mm1 = {"system_type": "millimeters", "system_scale": 1., "cm_per_unit": .1, "units_per_cm": 10.}
        cm1 = {"system_type": "centimeters", "system_scale": 1., "cm_per_unit": 1., "units_per_cm": 1.}
        cm01 = {"system_type": "centimeters", "system_scale": .1, "cm_per_unit": .1, "units_per_cm": 10.}
        refusal = ""
        try:
            runtime.generate_script(plan, "1" * 64, "P3UnitOfflineCm01", cm01)
        except ValueError as exc:
            refusal = str(exc)
        if "Float32" not in refusal:
            raise ValueError("cm/0.1 current offline refusal changed; require fresh explicit policy decision")
        files = {}
        cases = []
        for suffix, kind, expected in (("Cm1", "expected_cm1", cm1),
                                       ("TypeOnly", "NEGATIVE_MUTATED_type_only_same_factor", mm1),
                                       ("Factor", "NEGATIVE_MUTATED_stored_factor", mm1)):
            namespace = "P3Unit02e_" + digest(str(out).encode())[:6] + "_" + suffix
            identity = digest(encode({"scope": "AUDIT_UNIT_ONLY_NOT_PRODUCTION_PAIR", "sources": before,
                                      "namespace": namespace, "kind": kind}))
            text = runtime.generate_script(plan, identity, namespace, expected)
            # Establish the actual current order before emitting any executable file.
            entry = '        -- Must precede even replay inspection, registry writes, or constructors.\n        unitsGuard()'
            guard_pos = text.index(entry)
            registry_pos = text.index('        require (globalVars.isGlobal registryKey)')
            if guard_pos >= registry_pos or text.index('        require (lease[5] == "ARMED"') <= registry_pos:
                raise ValueError("current runtime no longer units-before-registry/arm")
            if suffix == "TypeOnly":
                # Intentionally inconsistent pair: KEEP actual factor constants and
                # expected scale 1, change only expected TYPE. It demonstrates type
                # discrimination despite equal embedded factors, NOT legit cm/.1.
                text = once(text, "require (actualType == #millimeters)",
                            "require (actualType == #centimeters)")
            elif suffix == "Factor":
                text = once(text, "require (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0)",
                            "require (cmPerUnit == 0.1d0 and unitsPerCm == 11.0d0)")
            text = ("-- " + kind + ": AUDIT ONLY; NO ARM; not an accepted production artifact pair.\n" + text)
            registry = "__P3W_" + digest((namespace + ":" + identity).encode())
            if f'local registryKey = "{registry}" as name' not in text:
                raise ValueError("runtime registry identity adapter changed")
            reason = "computed unit factor mismatch" if suffix == "Factor" else "SystemType mismatch"
            name = kind + ".ms"
            main_name = "MAIN_" + suffix + ".ms"
            files[name] = text.encode()
            files[main_name] = harness(out / name, registry, reason, kind).encode()
            cases.append({"kind": kind, "namespace": namespace, "identity": identity,
                          "registry": registry, "runtime_script": name, "main_path": main_name,
                          "runtime_script_sha256": digest(files[name]), "arm": "NOT_USED",
                          "expected_target_reason": reason, "artifact_pair_acceptance": False})
        after = {str(path): digest(path.read_bytes()) for path in paths}
        if after != before:
            raise ValueError("runtime/fixture drift during generation")
        record = {"status": "PREPARED_OFFLINE_NO_MAX_EXECUTION", "sources": before,
                  "cases": cases, "actual_scene_precondition": "millimeters/1; never change units",
                  "cm_0p1_offline_refusal": refusal, "cm_0p1_float32": struct.unpack("<f", struct.pack("<f", .1))[0],
                  "exact_equal_factor_legitimate_pair_current_mm1": "UNAVAILABLE for cm/.1 under exact-Float32-scale public policy",
                  "type_only_control_scope": "NEGATIVE MUTATED source: #centimeters only; retains mm/1 expected scale/factors; NOT legitimate cm/.1",
                  "replay": "INCOMPLETE_REPLAY in current runtime; no replay or geometry acceptance implied",
                  "files": {name: digest(raw) for name, raw in files.items()}}
        files["unit-control-index.json"] = encode(record)
        out.mkdir()
        for name, raw in files.items():
            with (out / name).open("xb") as stream:
                stream.write(raw)
        print(json.dumps({"status": record["status"], "out": str(out), "sources_unchanged": True,
                          "main_paths": [str(out / c["main_path"]) for c in cases]}, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("NOT PREPARED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
