#!/usr/bin/env python3
"""Prepare audit-only MAIN-EXECUTED controls; never import/call a Max bridge.

All writes are beneath this new audit directory. Production inputs and emitted
artifact bytes are read only. A positive admission record is an explicit main
attestation, not a verifier of bridge evidence; raw evidence still needs review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ADAPTER = "p3-live-controls-template-2026-11-02e-1"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def ms_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise ValueError("runtime adapter anchor changed/not unique: " + before[:100])
    return text.replace(before, after, 1)


def strict_json(raw: bytes):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError("duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def read_pair(path: Path):
    manifest_raw = (path / "wall_surface.json").read_bytes()
    script_raw = (path / "wall_surface.ms").read_bytes()
    if len(manifest_raw) + len(script_raw) > 2 * 1024 * 1024:
        raise ValueError("artifact pair exceeds initial admission")
    manifest = strict_json(manifest_raw)
    if (manifest.get("schema_version") != "p3-wall-surface-1"
            or manifest.get("status") != "produced_offline_unverified"
            or manifest.get("script", {}).get("sha256") != digest(script_raw)):
        raise ValueError("not a hash-consistent actual P3 artifact pair")
    identity = manifest.get("identity")
    namespace = manifest.get("owner", {}).get("namespace")
    if not isinstance(identity, str) or re.fullmatch("[0-9a-f]{64}", identity) is None:
        raise ValueError("bad actual identity")
    if not isinstance(namespace, str) or re.fullmatch("[A-Za-z][A-Za-z0-9_]{0,39}", namespace) is None:
        raise ValueError("bad actual namespace")
    names = manifest.get("node_names")
    if names != [namespace + "__wall"]:
        raise ValueError("unsupported runtime node naming adapter")
    text = script_raw.decode("utf-8")
    for anchor in (f'local artifactIdentity = "{identity}"',
                   f'local ownerNamespace = "{namespace}"',
                   f'local wallName = "{names[0]}"'):
        if text.count(anchor) != 1:
            raise ValueError("actual script/manifest identity disagrees")
    registry = "__P3W_" + digest((namespace + ":" + identity).encode())
    if text.count(f'local registryKey = "{registry}" as name') != 1:
        raise ValueError("unsupported registry adapter")
    return manifest, manifest_raw, script_raw, text, registry


def check_positive(path: Path, manifest: dict, mr: bytes, sr: bytes):
    record = strict_json(path.read_bytes())
    if (record.get("schema_version") != "p3-main-positive-admission-1"
            or record.get("script_sha256") != digest(sr)
            or record.get("manifest_sha256") != digest(mr)
            or record.get("created") is not True
            or record.get("independent_geometry_accepted") is not True
            or record.get("same_synthetic_node_owned_by_main") is not True
            or record.get("no_live_interleaving") is not True
            or record.get("replay_results") != ["P3_NOOP"] * 3
            or not isinstance(record.get("evidence_paths"), list)
            or not record["evidence_paths"]
            or any(not isinstance(p, str) or not p.strip() for p in record["evidence_paths"])
            or type(record.get("node_handle")) is not int or record["node_handle"] <= 0):
        raise ValueError("main positive actual-build + geometry + three replay admission absent/inconsistent")
    if record.get("actual_units") != manifest.get("expected_units"):
        raise ValueError("positive record actual units disagree with emitted expected units")
    if manifest.get("expected_units") != {"system_type": "millimeters", "system_scale": 1.0,
                                          "cm_per_unit": 0.1, "units_per_cm": 10.0}:
        raise ValueError("this adapter is explicitly current mm/1 only; no live unit change")
    return record


# Local functions live inside each emitted fileIn block, never in raw MCP code.
# Independent target-state witnesses are intentionally broader than the one edit.
# Reader failure aborts; no automatic restore is performed on an assertion error.
HELPERS = r'''
    fn demand condition reason = (if not condition do throw ("CONTROL_ABORT|" + reason))
    fn same a b =
    (
        if classOf a != classOf b then false
        else if classOf a == Array then
            (if a.count != b.count then false else
                (local ok = true; for i = 1 to a.count while ok do ok = same a[i] b[i]; ok))
        else a == b
    )
    fn frozen value depth:0 =
    (
        demand (depth < 32) "witness nesting ceiling"
        case (classOf value) of
        (
            Array: (demand (value.count <= 2048) "witness array ceiling"; for v in value collect frozen v depth:(depth+1))
            Matrix3: #(frozen value.row1, frozen value.row2, frozen value.row3, frozen value.row4)
            Point2: #("point2", value.x, value.y)
            Point3: #("point3", value.x, value.y, value.z)
            Point4: #("point4", value.x, value.y, value.z, value.w)
            Quat: #("quat", value.x, value.y, value.z, value.w)
            Color: #("color", value.r, value.g, value.b, value.a)
            BitArray: #("bits", value.count, value as array)
            String: copy value
            default: value
        )
    )
    fn props target =
    (
        local keys = getPropNames target
        demand (keys.count <= 512) "witness property ceiling"
        for p in keys collect #(p, frozen (getProperty target p))
    )
    fn measured node =
    (
        demand (isValidNode node) "exact node invalid"
        local base = node.baseObject
        demand (classOf base == Editable_Poly) "unsupported witness base"
        local nv = polyop.getNumVerts base
        local nf = polyop.getNumFaces base
        demand (nv <= 64 and nf <= 32 and node.modifiers.count <= 2) "witness geometry ceiling"
        local dv = polyop.getDeadVerts base
        local df = polyop.getDeadFaces base
        local geom = #(for i = 1 to nv collect (if dv[i] then #("dead") else frozen (polyop.getVert base i)),
            for i = 1 to nf collect (if df[i] then #("dead") else frozen (polyop.getFaceVerts base i)))
        local mesh = snapshotAsMesh node
        demand (getNumVerts mesh <= 128 and getNumFaces mesh <= 256) "witness evaluated ceiling"
        local eval = #(for i = 1 to getNumVerts mesh collect frozen (getVert mesh i),
            for i = 1 to getNumFaces mesh collect frozen (getFace mesh i))
        local mods = for m in node.modifiers collect #(m, getHandleByAnim m, m.enabled,
            m.enabledInViews, m.enabledInRenders, props m)
        local controller = getPropertyController node #transform
        #(node, getHandleByAnim node, base, getHandleByAnim base, node.name,
            frozen node.transform, frozen node.objectTransform, frozen node.objectOffsetPos,
            frozen node.objectOffsetRot, frozen node.objectOffsetScale, controller,
            node.material, node.layer, props node.layer, node.isHidden, node.isFrozen,
            node.renderable, node.visibility, node.parent, for n in node.children collect n,
            getUserPropBuffer node, mods, geom, eval)
    )
    fn sceneContext =
        #(for n in objects collect n, selection as array, units.SystemType, units.SystemScale,
          maxFilePath, maxFileName, currentTime as integer, subObjectLevel, getSaveRequired())
    fn sentinelSnapshot node =
    (
        if node == undefined then undefined
        else
        (
            demand (isValidNode node) "exact sentinel invalid"
            if classOf node.baseObject == Editable_Poly then measured node
            else #(node, getHandleByAnim node, node.baseObject, frozen node.transform,
                node.name, node.material, node.layer, node.parent, for n in node.children collect n,
                node.isHidden, node.renderable, getUserPropBuffer node, props node, props node.baseObject)
        )
    )
    fn registryState key = #(globalVars.isGlobal key,
        if globalVars.isGlobal key then frozen (globalVars.get key) else undefined)
    fn callArtifact path =
    (
        local threw = false
        local reason = ""
        try (fileIn path quiet:true) catch (threw = true; reason = getCurrentException() as string)
        #(threw, reason)
    )
    fn requireRefusal result =
    (
        demand result[1] "artifact did not throw; a printed REFUSE is insufficient"
        demand ((findString result[2] "P3_REFUSED|") != undefined or
            (findString result[2] "P3_INCOMPLETE_RESIDUAL|") != undefined) "not an actual runtime refusal"
    )
'''


def wrapper(body: str) -> str:
    return "-- AUDIT ONLY. MAIN fileIn; no execution is claimed by generation.\n(\n" + HELPERS + body + "\n)\n"


def header(cfg: dict) -> str:
    return (f'    local controlKey = {ms_string(cfg["control_key"])} as name\n'
            f'    local registryKey = {ms_string(cfg["registry"])} as name\n'
            f'    local artifactPath = {ms_string(cfg["artifact_path"])}\n'
            '    demand (globalVars.isGlobal controlKey) "main bind.ms not run"\n'
            '    local witness = globalVars.get controlKey\n'
            '    demand (classOf witness == Array and witness.count == 9) "control witness malformed"\n'
            '    demand (witness[8] == "READY") "previous control pending; inspect and explicit restore first"\n'
            '    local node = witness[1]\n'
            '    demand (isValidNode node and (getAnimByHandle witness[2]) == node) "exact synthetic identity lost"\n'
            '    demand (globalVars.isGlobal registryKey and (globalVars.get registryKey) == witness[3]) "production registry lost/substituted"\n'
            '    demand (same witness[4] (registryState registryKey)) "production registry baseline changed"\n'
            '    demand (same witness[5] (measured node)) "not exact bound clean synthetic baseline"\n'
            '    demand (same witness[6] (sceneContext())) "scene context changed since binding/restoration"\n')


EDITS = {
    "transform": ("local saved = copy node.transform", "node.pos += [1,0,0]", "node.transform = saved"),
    "geometry": ("local saved = copy (polyop.getVert node.baseObject 1)",
                 "polyop.setVert node.baseObject 1 (saved + [1,0,0]); update node",
                 "polyop.setVert node.baseObject 1 saved; update node"),
    "material": ("local saved = node.material", "node.material = Standard()", "node.material = saved"),
    "stackparams": ("local saved = node.modifiers[1].outerAmount",
                    "node.modifiers[1].outerAmount = saved + 1.0; update node",
                    "node.modifiers[1].outerAmount = saved; update node"),
    "enabledstate": ("local saved = node.modifiers[1].enabled",
                     "node.modifiers[1].enabled = not saved; update node",
                     "node.modifiers[1].enabled = saved; update node"),
    "enabledviews": ("local saved = node.modifiers[1].enabledInViews",
                     "node.modifiers[1].enabledInViews = not saved; update node",
                     "node.modifiers[1].enabledInViews = saved; update node"),
    "enabledrenders": ("local saved = node.modifiers[1].enabledInRenders",
                       "node.modifiers[1].enabledInRenders = not saved; update node",
                       "node.modifiers[1].enabledInRenders = saved; update node"),
    # This edits the layer property on the target, not shared layer settings.
    # Main must create the exact empty test layer and pass its exact reference;
    # the harness neither creates nor deletes layers.
    "layer": ("local saved = node.layer\n"
              "    local layerKey = (witness[9] + \"_layer\") as name\n"
              "    demand (globalVars.isGlobal layerKey) \"main exact empty test-layer reference absent\"\n"
              "    local testLayer = globalVars.get layerKey\n"
              "    demand (testLayer != undefined and testLayer != saved) \"invalid test-layer reference\"\n"
              "    demand ((for n in objects where n.layer == testLayer collect n).count == 0) \"test layer not empty\"",
              "testLayer.addNode node", "saved.addNode node"),
    "visibility": ("local saved = node.isHidden", "node.isHidden = not saved", "node.isHidden = saved"),
    "renderability": ("local saved = node.renderable", "node.renderable = not saved", "node.renderable = saved"),
    "userprops": ("local saved = getUserPropBuffer node",
                  'setUserProp node "P3AuditSyntheticEdit" "changed_by_main_test"', "setUserPropBuffer node saved"),
    "parent": ("local saved = #(node.parent, copy node.transform)\n"
               "    helper = Point name:(witness[9] + \"_parent\")\n"
               "    helperHandle = getHandleByAnim helper",
               "node.parent = helper",
               "node.parent = saved[1]; node.transform = saved[2]\n"
               "        demand (isValidNode helper and (getAnimByHandle helperHandle) == helper and helper.children.count == 0) \"parent control helper not exact/empty\"\n"
               "        delete helper"),
    "duplicate_tag_copy": ("local saved = undefined\n"
                           "    helper = copy node\n"
                           "    helperHandle = getHandleByAnim helper\n"
                           "    helper.name = witness[9] + \"_copied_tag\"\n"
                           "    setUserPropBuffer helper (getUserPropBuffer node)", "helper.pos += [10,0,0]",
                           "demand (isValidNode helper and (getAnimByHandle helperHandle) == helper) \"copy exact identity lost\"\n"
                           "        delete helper"),
    "related_prefix": ("local saved = undefined\n"
                       "    helper = Box name:(witness[9] + \"__wall_related_foreign\") width:1 length:1 height:1\n"
                       "    helperHandle = getHandleByAnim helper", "helper.pos = [21,22,23]",
                       "demand (isValidNode helper and (getAnimByHandle helperHandle) == helper) \"prefix sentinel exact identity lost\"\n"
                       "        delete helper"),
    "registry_loss": ("local saved = globalVars.get registryKey",
                      "globalVars.set registryKey undefined", "globalVars.set registryKey saved"),
    "registry_removed": ("local saved = globalVars.get registryKey",
                         "globalVars.remove registryKey", "globalVars.set registryKey saved"),
}


def make_edit(cfg: dict, case: str) -> str:
    save, mutate, restore = EDITS[case]
    # A separate explicit restore call is required: tests never repair a replay.
    # The closure retains EXACT saved values and helper refs; no name adoption.
    body = header(cfg) + f'''
    local caseId = {ms_string(case)}
    local helper = undefined
    local helperHandle = undefined
    -- Save and mutate are MAIN'S synthetic control, not production behavior.
    {save}
    {mutate}
    local editedNode = measured node
    local editedRegistry = registryState registryKey
    local editedContext = sceneContext()
    demand (not (same editedNode witness[5]) or not (same editedRegistry witness[4]) or
        not (same editedContext witness[6])) "synthetic edit did not discriminate"
    -- Retain exact saved data, never an uncalibrated closure or name lookup.
    witness[7] = #(caseId, saved, helper, helperHandle, editedNode, editedRegistry, editedContext, sentinelSnapshot helper)
    witness[8] = "EDIT_PENDING"
'''
    if case in ("parent", "duplicate_tag_copy", "related_prefix"):
        body += "    local helperBefore = sentinelSnapshot helper\n"
    body += '''    local result = callArtifact artifactPath
    print ("CONTROL_RAW|case=" + caseId + "|threw=" + (result[1] as string) + "|reason=" + result[2])
    requireRefusal result
    demand (same editedNode (measured node)) "artifact changed/deleted the edited target"
    demand (same editedRegistry (registryState registryKey)) "artifact changed/adopted registry during refusal"
    demand (same editedContext (sceneContext())) "artifact changed scene/units/census/dirty state during refusal"
'''
    if case in ("parent", "duplicate_tag_copy", "related_prefix"):
        body += '    demand (same helperBefore (sentinelSnapshot helper)) "artifact changed/deleted foreign control sentinel"\n'
    body += '''    witness[8] = "REFUSAL_VERIFIED_EDIT_LEFT_IN_PLACE"
    print ("CONTROL_REFUSAL_PRESERVED|case=" + caseId + "|restore=NOT_RUN")
'''
    return wrapper(body)


def make_bind(cfg: dict) -> str:
    return wrapper(f'''
    local registryKey = {ms_string(cfg["registry"])} as name
    local controlKey = {ms_string(cfg["control_key"])} as name
    demand (not globalVars.isGlobal controlKey) "audit key already exists; refuse overwrite"
    demand (globalVars.isGlobal registryKey) "no actual committed production registry"
    local registry = globalVars.get registryKey
    demand (classOf registry == Array and registry.count == 8) "unsupported actual registry"
    demand (registry[1] == "p3-session-registry-1" and registry[2] == {ms_string(cfg["identity"])} and
        registry[4] == {ms_string(cfg["namespace"])}) "actual registry identity disagrees"
    local node = registry[5]
    demand (isValidNode node and (getHandleByAnim node) == {cfg["node_handle"]}) "not main admitted exact synthetic node"
    demand (objects.count == 1 and selection.count == 0 and node.name == {ms_string(cfg["node_name"])}) "not isolated admitted node"
    demand (units.SystemType == #millimeters and units.SystemScale == 1.0) "actual mm/1 required; never set units"
    local baseline = measured node
    demand (same baseline (measured node)) "independent witness unstable"
    local witness = #(node, getHandleByAnim node, registry, registryState registryKey,
        baseline, sceneContext(), undefined, "READY", {ms_string(cfg["namespace"])})
    globalVars.set controlKey witness
    print ("CONTROL_BOUND|handle=" + ((getHandleByAnim node) as string) + "|assumed_prior_positive_and_three_replays=true")
''')


def make_restore(cfg: dict) -> str:
    branches = "\n".join(f'        {ms_string(case)}: (\n            {restore}\n        )'
                           for case, (_, _, restore) in EDITS.items())
    return wrapper(f'''
    -- EXPLICIT MAIN ACTION ONLY for its admitted synthetic test node. Never user edits.
    local controlKey = {ms_string(cfg["control_key"])} as name
    local registryKey = {ms_string(cfg["registry"])} as name
    demand (globalVars.isGlobal controlKey) "no bound audit witness"
    local witness = globalVars.get controlKey
    demand (witness[8] == "REFUSAL_VERIFIED_EDIT_LEFT_IN_PLACE") "refusal preservation not verified; inspect manually, do not auto-restore"
    local node = witness[1]
    demand (isValidNode node and (getAnimByHandle witness[2]) == node) "not exact synthetic target"
    local pending = witness[7]
    demand (same pending[5] (measured node) and same pending[6] (registryState registryKey) and
        same pending[7] (sceneContext())) "intervening edit: restore forbidden"
    local saved = pending[2]
    local helper = pending[3]
    local helperHandle = pending[4]
    demand (same pending[8] (sentinelSnapshot helper)) "intervening helper/sentinel edit: restore forbidden"
    case pending[1] of
    (
{branches}
        default: (throw "CONTROL_ABORT|unknown synthetic restore case")
    )
    demand (same witness[5] (measured node)) "exact target baseline not restored; stop"
    demand (same witness[4] (registryState registryKey)) "exact registry baseline not restored; stop"
    demand (same witness[6] (sceneContext())) "exact scene context not restored; stop (never clear dirty flag)"
    witness[7] = undefined
    witness[8] = "READY"
    print ("CONTROL_OWN_SYNTHETIC_RESTORED|case=" + pending[1] + "|production_restore=false")
''')


def make_clean(cfg: dict) -> str:
    return wrapper(header(cfg) + '''
    local before = measured node
    local contextBefore = sceneContext()
    local rs = registryState registryKey
    local result = callArtifact artifactPath
    print ("CONTROL_CLEAN_RAW|threw=" + (result[1] as string) + "|reason=" + result[2])
    demand (not result[1]) "clean replay after audit binding/restoration refused"
    demand (same before (measured node) and same contextBefore (sceneContext()) and
        same rs (registryState registryKey)) "clean replay mutated state"
    print "CONTROL_CLEAN_UNCHANGED|main_must_confirm_actual_P3_NOOP_marker=true"
''')


def variant(original: str, manifest: dict, namespace: str, kind: str):
    """Alter a PRIVATE TEST byte stream, never a production artifact/pair.

    This intentionally bypasses public publication only for fault injection. The
    original manifest is not copied/rehash-laundered into an accepted new pair.
    """
    old_ns = manifest["owner"]["namespace"]
    old_id = manifest["identity"]
    old_key = "__P3W_" + digest((old_ns + ":" + old_id).encode())
    new_id = digest((ADAPTER + ":" + digest(original.encode()) + ":" + namespace + ":" + kind).encode())
    new_key = "__P3W_" + digest((namespace + ":" + new_id).encode())
    binding_match = re.search(r'local artifactBinding = "([0-9a-f]{64})"', original)
    if binding_match is None:
        raise ValueError("artifactBinding anchor missing")
    new_binding = digest((new_id + ":AUDIT_ONLY_ALTERED_" + kind).encode())
    text = once(original, f'local artifactIdentity = "{old_id}"', f'local artifactIdentity = "{new_id}"')
    text = once(text, f'local ownerNamespace = "{old_ns}"', f'local ownerNamespace = "{namespace}"')
    text = once(text, f'local wallName = "{old_ns}__wall"', f'local wallName = "{namespace}__wall"')
    text = once(text, f'local registryKey = "{old_key}" as name', f'local registryKey = "{new_key}" as name')
    text = once(text, binding_match.group(0), f'local artifactBinding = "{new_binding}"')
    text = "-- NEGATIVE TEST ONLY: altered generated bytes/identity; NOT A PRODUCTION ARTIFACT.\n" + text
    if kind == "unit_cm_1":
        text = once(text, "require (actualType == #millimeters)", "require (actualType == #centimeters)")
        text = once(text, "local cmPerUnit = 0.1d0 * actualScale", "local cmPerUnit = 1.0d0 * actualScale")
        text = once(text, "require (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0)",
                    "require (cmPerUnit == 1.0d0 and unitsPerCm == 1.0d0)")
    elif kind == "unit_cm_0p1_equal_factor":
        # Deliberately uses exact Double .1 in an altered guard. Public generation
        # may refuse .1 because SystemScale is Float32; neither is a live unit edit.
        text = once(text, "require (actualType == #millimeters)", "require (actualType == #centimeters)")
        text = once(text, "require (actualScale == 1.0d0)", "require (actualScale == 0.1d0)")
        text = once(text, "local cmPerUnit = 0.1d0 * actualScale", "local cmPerUnit = 1.0d0 * actualScale")
    elif kind == "corrupt_factor":
        text = once(text, "require (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0)",
                    "require (cmPerUnit == 0.1d0 and unitsPerCm == 11.0d0)")
    elif kind == "api_create_failure":
        # Call the real creation API with an invalid point AFTER three real API
        # calls succeed. The artifact catch must clean only the captured wall ref.
        text = once(text, "local id = polyop.createVert node point",
                    'local apiPoint = if vertexIds.count == 3 then "AUDIT_INVALID_POINT" else point\n'
                    '                local id = polyop.createVert node apiPoint')
        # A sentinel appears after admission so exact-reference catch cleanup can
        # be tested in a scope that otherwise intentionally requires empty census.
        text = once(text, 'stage = "grid-vertices"',
                    'stage = "grid-vertices"\n'
                    f'            local auditForeign = Box name:"{namespace}__wall_foreign" width:1 length:1 height:1\n'
                    '            globalVars.set ("@@AUDIT_FOREIGN_KEY@@" as name) #(auditForeign, getHandleByAnim auditForeign,\n'
                    '                auditForeign.name, copy auditForeign.transform, auditForeign.width, auditForeign.length, auditForeign.height, getUserPropBuffer auditForeign)')
    elif kind == "reverse_winding":
        text = once(text, "local actualLoop = for index in cellSlots[slot] collect vertexIds[index]",
                    "local actualLoop = for index in cellSlots[slot] collect vertexIds[index]\n"
                    "                actualLoop = for k = actualLoop.count to 1 by -1 collect actualLoop[k]")
    elif kind != "exact_name_collision":
        raise ValueError("unknown negative variant: " + kind)
    return text, {"identity": new_id, "namespace": namespace, "registry": new_key,
                  "binding": new_binding, "kind": kind}


CAPTURE = r'''
    fn auditPointText p = ("[" + (p.x as string) + "," + (p.y as string) + "," + (p.z as string) + "]")
    fn auditLoopText ids =
    (
        local out = "["
        for k = 1 to ids.count do (if k > 1 do out += ","; out += ids[k] as string)
        out + "]"
    )
    fn auditCapture stage node =
    (
        local base = node.baseObject
        local vertices = for i = 1 to polyop.getNumVerts base collect polyop.getVert base i
        local dead = polyop.getDeadFaces base
        local loops = for i = 1 to polyop.getNumFaces base where not dead[i] collect polyop.getFaceVerts base i
        local triangles = #()
        if stage == "evaluated" do
        (
            local msh = snapshotAsMesh node
            vertices = for i = 1 to getNumVerts msh collect getVert msh i
            triangles = for i = 1 to getNumFaces msh collect getFace msh i
            loops = #()
            -- Snapshot is non-scene geometry. Do not create a temporary node.
        )
        require (vertices.count <= 128 and loops.count <= 32 and triangles.count <= 96) "audit capture ceiling"
        print ("P3_CONTROL_CAPTURE|stage=" + stage + "|vertices=" + (vertices.count as string) + "|faces=" + (loops.count as string) + "|triangles=" + (triangles.count as string))
        for i = 1 to vertices.count do print ("P3_CONTROL_VERTEX|" + stage + "|" + (i as string) + "|" + (auditPointText vertices[i]))
        for i = 1 to loops.count do print ("P3_CONTROL_FACE|" + stage + "|" + (i as string) + "|" + (auditLoopText loops[i]))
        for i = 1 to triangles.count do print ("P3_CONTROL_TRIANGLE|" + stage + "|" + (i as string) + "|" + (auditPointText triangles[i]))
    )
'''


def instrument_capture(text: str) -> str:
    text = once(text, "    fn unitsGuard =", CAPTURE + "\n    fn unitsGuard =")
    text = once(text, '            stage = "opening-delete-once"',
                '            auditCapture "grid" node\n            stage = "opening-delete-once"')
    text = once(text, '            stage = "one-shell"',
                '            auditCapture "base" node\n            stage = "one-shell"')
    text = once(text, "            setUserProp node tagKey tagValue",
                '            auditCapture "evaluated" node\n            setUserProp node tagKey tagValue')
    return text


def fresh_harness(path: Path, meta: dict, foreign_key: str | None = None) -> str:
    case = meta["kind"]
    body = f'''
    -- Run ONLY after exact teardown of the positive wall; no reset and no unit edit.
    local registryKey = {ms_string(meta["registry"])} as name
    local artifactPath = {ms_string(str(path))}
    local foreignKey = {ms_string(foreign_key or "")} as name
    demand (not globalVars.isGlobal registryKey) "fresh negative namespace already spent"
    demand (not globalVars.isGlobal foreignKey) "foreign-control witness key already exists; never overwrite"
    demand (objects.count == 0 and selection.count == 0 and maxFilePath == "" and maxFileName == "") "fresh synthetic context absent"
    demand (units.SystemType == #millimeters and units.SystemScale == 1.0) "current mm/1 required; never set units"
'''
    if case == "exact_name_collision":
        body += f'''    local foreign = Box name:{ms_string(meta["namespace"] + "__wall")} width:1 length:1 height:1
    local foreignHandle = getHandleByAnim foreign
    local foreignState = #(foreign, foreignHandle, foreign.name, frozen foreign.transform, foreign.width, foreign.length, foreign.height, getUserPropBuffer foreign)
    globalVars.set foreignKey #(foreign, foreignHandle, foreignState)
'''
    body += "    local before = sceneContext()\n    local rs = registryState registryKey\n    local result = callArtifact artifactPath\n"
    if case == "reverse_winding":
        body += '''    print ("CONTROL_WINDING_RAW|threw=" + (result[1] as string) + "|reason=" + result[2])
    demand (not result[1]) "reversed full runtime failed: not a winding measurement control"
    demand (globalVars.isGlobal registryKey) "no reversed runtime commit; incomplete"
    local reg = globalVars.get registryKey
    demand (classOf reg == Array and reg.count == 8 and isValidNode reg[5]) "invalid reversed exact node"
    print ("CONTROL_WINDING_CREATED|handle=" + ((getHandleByAnim reg[5]) as string) + "|independent_measurement=REQUIRED|cleanup=MAIN_EXACT_REF_ONLY")
'''
    elif case == "api_create_failure":
        body += f'''    print ("CONTROL_API_RAW|threw=" + (result[1] as string) + "|reason=" + result[2])
    requireRefusal result
    demand ((findString result[2] "stage=grid-vertices") != undefined) "failure not at injected real API creation stage"
    demand (globalVars.isGlobal foreignKey) "post-admission sentinel not reached"
    local foreignWitness = globalVars.get foreignKey
    local foreign = foreignWitness[1]
    demand (isValidNode foreign and objects.count == 1 and (for n in objects collect n)[1] == foreign) "exact created wall cleanup failed or foreign sentinel deleted"
    demand ((getAnimByHandle foreignWitness[2]) == foreign and same (frozen foreignWitness)
        (frozen #(foreign, getHandleByAnim foreign, foreign.name, copy foreign.transform, foreign.width, foreign.length, foreign.height, getUserPropBuffer foreign))) "foreign sentinel changed"
    demand (same rs (registryState registryKey)) "failed attempt published/changed registry"
    demand (units.SystemType == before[3] and units.SystemScale == before[4]) "failed attempt changed units"
    print ("CONTROL_API_FAILURE_EXACT_CLEANUP|remaining=one_exact_foreign_sentinel|teardown=MAIN_EXACT_REF_ONLY")
'''
    else:
        body += '''    print ("CONTROL_FRESH_RAW|threw=" + (result[1] as string) + "|reason=" + result[2])
    requireRefusal result
    demand (same before (sceneContext())) "fresh refusal mutated scene/context/census"
    demand (same rs (registryState registryKey)) "fresh refusal mutated/published registry"
'''
        if case == "exact_name_collision":
            body += '''    demand (isValidNode foreign and same foreignState #(foreign, getHandleByAnim foreign, foreign.name, frozen foreign.transform, foreign.width, foreign.length, foreign.height, getUserPropBuffer foreign)) "same-exact-name foreign sentinel changed"
    print ("CONTROL_EXACT_COLLISION_PRESERVED|teardown=MAIN_EXACT_REF_ONLY")
'''
        else:
            body += '    print "CONTROL_UNIT_OR_FACTOR_REFUSAL_BEFORE_MUTATION|units_unchanged=true"\n'
    return wrapper(body)


def prepare(args) -> dict:
    artifact = Path(args.artifact).resolve()
    m, mr, sr, original, registry = read_pair(artifact)
    positive = check_positive(Path(args.positive), m, mr, sr)
    out = Path(args.out).absolute()
    if out.exists() or out.parent.resolve() != HERE:
        raise ValueError("--out must be a NEW direct child of this owned audit directory")
    token = args.token
    if re.fullmatch("[A-Za-z][A-Za-z0-9_]{0,19}", token) is None:
        raise ValueError("token must be fresh ASCII namespace token <=20 chars")
    config = {"adapter": ADAPTER, "namespace": m["owner"]["namespace"],
              "identity": m["identity"], "registry": registry, "node_name": m["node_names"][0],
              "artifact_path": str(artifact / "wall_surface.ms"), "script_sha256": digest(sr),
              "manifest_sha256": digest(mr), "node_handle": positive["node_handle"],
              "control_key": "__P3Audit_" + token, "positive_record_sha256": digest(Path(args.positive).read_bytes())}
    files = {"bind.ms": make_bind(config).encode(), "restore_own_synthetic.ms": make_restore(config).encode(),
             "clean_noop_after_bind_or_restore.ms": make_clean(config).encode()}
    for case in EDITS:
        files["edit_" + case + ".ms"] = make_edit(config, case).encode()
    variants = []
    kinds = ["unit_cm_1", "unit_cm_0p1_equal_factor", "corrupt_factor", "exact_name_collision", "api_create_failure", "reverse_winding"]
    for index, kind in enumerate(kinds):
        ns = f"{token}_N{index}"
        altered, meta = variant(original, m, ns, kind)
        foreign_key = "__P3AuditForeign_" + token + "_N" + str(index)
        if kind == "api_create_failure":
            altered = altered.replace("@@AUDIT_FOREIGN_KEY@@", foreign_key)
        if kind == "reverse_winding":
            altered = instrument_capture(altered)
        name = "NEGATIVE_ONLY_" + kind + ".ms"
        files[name] = altered.encode()
        files["fresh_" + kind + ".ms"] = fresh_harness(out / name, meta, foreign_key).encode()
        variants.append({**meta, "script": name, "sha256": digest(files[name]),
                         "original_sha256": digest(sr), "not_production": True,
                         "foreign_key": foreign_key,
                         "declared_source_authority": "UNCHANGED; do not flip authority to match bad geometry"})
    authority = m.get("direction_authority")
    if not isinstance(authority, dict) or authority.get("outward") != [0.0, -1.0]:
        raise ValueError("initial F01 source-authority -Y only")
    wrong_authority = dict(authority)
    wrong_authority["outward"] = [0.0, 1.0]
    files["NEGATIVE_ONLY_wrong_authority.json"] = encode(wrong_authority)
    config["variants"] = variants
    config["status"] = "PREPARED_OFFLINE_NOT_EXECUTED"
    config["files"] = {name: digest(raw) for name, raw in sorted(files.items())}
    files["control-index.json"] = encode(config)
    # No output until every version-specific adapter/anchor has succeeded.
    out.mkdir()
    for name, raw in files.items():
        with (out / name).open("xb") as stream:
            stream.write(raw)
    return {"status": "PREPARED_OFFLINE_NOT_EXECUTED", "out": str(out), "files": len(files)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact", required=True, help="actual emitted pair directory, read-only")
    p.add_argument("--positive", required=True, help="main-authored positive actual build/3 replay admission JSON")
    p.add_argument("--out", required=True, help="new direct child of this audit folder")
    p.add_argument("--token", required=True, help="fresh test namespace token <=20 chars")
    try:
        print(json.dumps(prepare(p.parse_args(argv)), sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("NOT PREPARED: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
