#!/usr/bin/env python3
"""One-shot offline unit-main-03 preparation. Writes only NEW sibling files."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys

OUT = Path(__file__).resolve().parent
AUDIT_OWNER = OUT.parent
ROOT = OUT.parents[2]
FINAL_RUNTIME_SHA = "bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15"
sys.path.insert(0, str(AUDIT_OWNER))
from prepare_controls import digest, encode, ms_string, once, strict_json


def wrapper(script, registry, expected_reason, label):
    # Return diagnostic string on both success and failure. Printing followed by
    # throw loses diagnostic output on this bridge; no test verdict from print.
    return f'''-- MAIN ONLY: bounded pre-registry unit refusal; no ARM, setters or scene edits.
(
    local p3ucResult = "UNIT_CONTROL_ERROR|no_result"
    try
    (
        local p3ucPath = {ms_string(str(script))}
        local p3ucKey = {ms_string(registry)} as name
        if globalVars.isGlobal p3ucKey then p3ucResult = "UNIT_CONTROL_ABORT|fresh_registry_already_exists"
        else if units.SystemType != #millimeters or units.SystemScale != 1.0 then p3ucResult = "UNIT_CONTROL_ABORT|actual_mm_1_required_NEVER_change_units"
        else if objects.count > 64 then p3ucResult = "UNIT_CONTROL_ABORT|scene_census_ceiling"
        else
        (
            local p3ucNodes = for n in objects collect #(n, getHandleByAnim n)
            local p3ucSelection = selection as array
            local p3ucType = units.SystemType
            local p3ucScale = units.SystemScale
            local p3ucDirty = getSaveRequired()
            local p3ucFile = maxFileName
            local p3ucDir = maxFilePath
            local p3ucTime = currentTime
            local p3ucSubobject = subObjectLevel
            local p3ucThrew = false
            local p3ucReason = ""
            try (fileIn p3ucPath quiet:true) catch
                (p3ucThrew = true; p3ucReason = getCurrentException() as string)
            local p3ucAfterNodes = for n in objects collect #(n, getHandleByAnim n)
            local p3ucAfterSelection = selection as array
            local p3ucNodesEqual = p3ucNodes.count == p3ucAfterNodes.count
            if p3ucNodesEqual do for i = 1 to p3ucNodes.count do
                (if p3ucNodes[i][1] != p3ucAfterNodes[i][1] or p3ucNodes[i][2] != p3ucAfterNodes[i][2] do p3ucNodesEqual = false)
            local p3ucSelectionEqual = p3ucSelection.count == p3ucAfterSelection.count
            if p3ucSelectionEqual do for i = 1 to p3ucSelection.count do
                (if p3ucSelection[i] != p3ucAfterSelection[i] do p3ucSelectionEqual = false)
            local p3ucContextEqual = units.SystemType == p3ucType and units.SystemScale == p3ucScale and
                getSaveRequired() == p3ucDirty and maxFilePath == p3ucDir and maxFileName == p3ucFile and
                currentTime == p3ucTime and subObjectLevel == p3ucSubobject
            local p3ucRegistryAbsent = not globalVars.isGlobal p3ucKey
            local p3ucReasonMatches = (findString p3ucReason {ms_string(expected_reason)}) != undefined and
                ((findString p3ucReason "P3_REFUSE|") != undefined or (findString p3ucReason "P3_REFUSED|") != undefined)
            local p3ucProtectedEqual = p3ucNodesEqual and p3ucSelectionEqual and p3ucContextEqual and p3ucRegistryAbsent
            local p3ucStatus = if p3ucThrew and p3ucReasonMatches and p3ucProtectedEqual then
                "UNIT_CONTROL_TARGET_REFUSAL_UNCHANGED" else "UNIT_CONTROL_FAIL"
            local p3ucBriefReason = if p3ucReason.count > 900 then (substring p3ucReason 1 900) else p3ucReason
            p3ucResult = p3ucStatus + "|case={label}|threw=" + (p3ucThrew as string) +
                "|targetReason=" + (p3ucReasonMatches as string) + "|nodesExact=" + (p3ucNodesEqual as string) +
                "|selectionExact=" + (p3ucSelectionEqual as string) + "|contextEqual=" + (p3ucContextEqual as string) +
                "|registryAbsent=" + (p3ucRegistryAbsent as string) + "|units=" + ((units.SystemType) as string) +
                "/" + ((units.SystemScale) as string) + "|nodes=" + ((objects.count) as string) +
                "|dirty=" + ((getSaveRequired()) as string) + "|arm=NOT_USED|reason=" + p3ucBriefReason
        )
    )
    catch
    (
        local p3ucUnexpected = getCurrentException() as string
        if p3ucUnexpected.count > 900 do p3ucUnexpected = substring p3ucUnexpected 1 900
        p3ucResult = "UNIT_CONTROL_ERROR|case={label}|reason=" + p3ucUnexpected
    )
    p3ucResult
)
'''


def main():
    fixture = ROOT / "Audit" / "phase16-p3-f01-input-2026-11-02e" / "project"
    paths = [ROOT / "scripts" / "wall_surface_runtime.py", ROOT / "scripts" / "scene_units.py",
             fixture / "walls.json", fixture / "dimensions.json"]
    before = {str(p): digest(p.read_bytes()) for p in paths}
    if before[str(paths[0])] != FINAL_RUNTIME_SHA:
        raise ValueError("runtime differs from main's explicit final SHA; refuse regeneration")
    prior = [p for name in ("unit-main-01", "unit-main-02") for p in (AUDIT_OWNER / name).rglob("*") if p.is_file()]
    old_before = {str(p): digest(p.read_bytes()) for p in sorted(prior)}
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("p3_unit_main03_final_runtime", paths[0])
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    plan = runtime.build_plan(strict_json(paths[2].read_bytes()), strict_json(paths[3].read_bytes()))
    mm1 = {"system_type": "millimeters", "system_scale": 1., "cm_per_unit": .1, "units_per_cm": 10.}
    cm1 = {"system_type": "centimeters", "system_scale": 1., "cm_per_unit": 1., "units_per_cm": 1.}
    files, cases = {}, []
    for suffix, kind, expected in (("Cm1", "expected_cm1", cm1),
                                   ("TypeOnly", "NEGATIVE_MUTATED_type_only_same_factor", mm1),
                                   ("Factor", "NEGATIVE_MUTATED_stored_factor", mm1)):
        ns = "P3Unit03_" + suffix
        identity = digest(encode({"scope": "MAIN03_UNIT_ONLY_NOT_ACCEPTED_PRODUCTION_PAIR",
                                  "sources": before, "namespace": ns, "kind": kind}))
        text = runtime.generate_script(plan, identity, ns, expected)
        if "fn freeze " in text or len(re.findall(r"\bfn p3[A-Za-z]+\b", text)) != 13:
            raise ValueError("not the main-approved 13-prefixed-helper runtime")
        entry = text.index('        p3UnitsGuard()\n        p3RequireState (maxFilePath')
        registry_read = text.index('        p3RequireState (globalVars.isGlobal registryKey)')
        arm_read = text.index('        p3RequireState (lease[5] == "ARMED"')
        if not entry < registry_read < arm_read:
            raise ValueError("unit-before-registry/arm ordering not established")
        if suffix == "TypeOnly":
            text = once(text, "p3RequireState (actualType == #millimeters)",
                        "p3RequireState (actualType == #centimeters)")
        elif suffix == "Factor":
            text = once(text, "p3RequireState (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0)",
                        "p3RequireState (cmPerUnit == 0.1d0 and unitsPerCm == 11.0d0)")
        text = "-- " + kind + ": AUDIT UNIT ONLY; fresh test identity; NOT accepted production pair.\n" + text
        key = "__P3W_" + digest((ns + ":" + identity).encode())
        if f'local registryKey = "{key}" as name' not in text:
            raise ValueError("actual registry adapter mismatch")
        reason = "computed unit factor mismatch" if suffix == "Factor" else "SystemType mismatch"
        name, main_name = kind + ".ms", "MAIN_" + suffix + ".ms"
        files[name] = text.encode()
        files[main_name] = wrapper(OUT / name, key, reason, kind).encode()
        cases.append({"case": kind, "namespace": ns, "identity": identity, "registry": key,
                      "runtime_script": name, "main_path": main_name, "target_reason": reason,
                      "runtime_sha256": digest(files[name]), "wrapper_sha256": digest(files[main_name]),
                      "arm": "NOT_USED", "production_acceptance": False})
    cm01_refusal = ""
    try:
        runtime.generate_script(plan, "1" * 64, "P3Unit03OfflineCm01",
                 {"system_type": "centimeters", "system_scale": .1, "cm_per_unit": .1, "units_per_cm": 10.})
    except ValueError as exc:
        cm01_refusal = str(exc)
    if "Float32" not in cm01_refusal:
        raise ValueError("cm/.1 offline policy changed; no silent equal-factor inference")
    after = {str(p): digest(p.read_bytes()) for p in paths}
    old_after = {str(p): digest(p.read_bytes()) for p in sorted(prior)}
    if before != after or old_before != old_after:
        raise ValueError("source or preserved old-output drift")
    index = {"status": "PREPARED_OFFLINE_NOT_EXECUTED", "runtime_final_sha256": FINAL_RUNTIME_SHA,
             "sources_before": before, "sources_after": after, "sources_unchanged": True,
             "preserved_old_files_before": old_before, "preserved_old_files_after": old_after,
             "old_files_unchanged": True, "cases": cases, "cm_0p1_offline_refusal": cm01_refusal,
             "type_only_scope": "NEGATIVE MUTATED expected TYPE only; keeps mm/1 expected scale/factors; NOT legitimate cm/.1",
             "actual_precondition": "millimeters/1; do not change scene units",
             "replay": "INCOMPLETE_REPLAY; not tested or accepted here",
             "files": {name: digest(raw) for name, raw in files.items()}}
    files["unit-control-index.json"] = encode(index)
    for name in files:
        if (OUT / name).exists():
            raise ValueError("refuse overwrite: " + name)
    for name, raw in files.items():
        with (OUT / name).open("xb") as stream:
            stream.write(raw)
    print(json.dumps({"status": index["status"], "runtime_sha256": FINAL_RUNTIME_SHA,
                      "sources_unchanged": True, "old_files_unchanged": True,
                      "main_paths": [str(OUT / c["main_path"]) for c in cases]}, indent=2))


if __name__ == "__main__":
    main()
