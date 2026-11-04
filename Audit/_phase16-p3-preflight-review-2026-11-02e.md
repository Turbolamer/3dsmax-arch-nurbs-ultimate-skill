# Phase 16 P3 — preflight preservation/ownership review (2026-11-02e)

## Status and ownership

**OFFLINE PREPARED; no Max calls made, no live preflight verdict.** This review
owns only this new report and `Audit/phase16-p3-preflight-2026-11-02e/`. No source,
accepted fixture, installer, archive, installed copy, backup, scene, renderer or
material assignment was changed. The coordinator brief and
`Audit/_phase16-p3-live-entry-2026-11-02e.json` supply the entry observations:
0 objects, 0 selection, unnamed scene, save-required false, **native mm / 1.0**.
Those are main's executed evidence, not this reviewer's fresh observation.

Reviewed `AGENTS.md`, current `CHECKPOINT.md`/`PLAN.md` scope,
`scripts/env_preflight.py` and `scripts/scene_units.py`. Accepted class API facts
remain accepted; nothing here claims a changed/absent API. No broad historical
re-investigation is necessary for this P3 entry task.

All paths below are relative to **`Audit/phase16-p3-preflight-2026-11-02e/`**
unless explicitly rooted otherwise. All MAXScript files are **prepared, not
Max-parsed or executed**. Exact canonical body bytes and hashes are recorded in
`preparation.json`; they are not repaired silently.

## Actual canonical surface and safety

The current script defines **10 checks, 8 MAXScript bodies, 2 typed-tool keys**.
Historical `PASS 9` prose is not the current emitted row count. Offline emission
is not execution and gives all ten checks SKIP.

| Exact check name | Exact body path | Preservation/ownership assessment | Work bound and P3 recommendation |
|---|---|---|---|
| `bridge` | none (typed evidence) | No MAXScript body. Main owns capture from `3dsmax-mcp_get_bridge_status`; not this task. | Do not infer from a TCP/FileStream failure. |
| `max_version` | `canonical/max_version.ms` | **Strict read-only**: `maxVersion()` and array/string reads. | One API call; appropriate to refresh. |
| `units` | `canonical/units.ms` | **Strict read-only**: reads `units.SystemType`/`SystemScale`; each read catches separately. Does not set units. | Two reads; appropriate to refresh. |
| `nurbset_present` | `canonical/nurbset_present.ms` | Resolves and constructs one transient **non-node `NURBSSet`**, not a scene read-only query. Does not instantiate `NURBSNode`. No scene deletion. Canonical resolution lacks positive/bogus controls. | Finite one-class construction, but no measured time here. Inherit accepted P1 fact; do not re-derive without necessity. An error is not absence. |
| `loft_not_creatable` | `canonical/loft_not_creatable.ms` | Attempts construction: under accepted baseline it throws before creating a node. **Conditionally mutating if behavior changes**; a returned node is not cleaned up by original. No positive/bogus controls. | One ctor attempt. Do not run original as a preservation-safe class discovery. Optional cleanup-hardened variant below, not needed routinely. |
| `sweep_creatable` | `canonical/sweep_creatable.ms` | Constructs one transient **non-node modifier**, not strict query-only. Bare modifiers cannot be deleted as scene nodes. Does not attach, create a scene node, or modify a stack. | One constructor. Existing accepted fact; no need to repeat for straight zero-modifier P3. |
| `sweep_on_shape` | `canonical/sweep_on_shape.ms` | **Scene mutation**: creates a Rectangle, sets dimensions, attempts one Sweep attach. Deletes exact local `s`, not name/prefix. Width/length setup or later unguarded formatting can fail before cleanup; cleanup exceptions are swallowed. Default `mods=0` can mask a read error. | One node/one modifier attempt, no stack ladder. Do not run original unchanged for a new preservation gate. |
| `quadpatch_creatable` | `canonical/quadpatch_creatable.ms` | **Scene mutation**: creates a QuadPatch, then deletes exact local `p`. A formatting/property failure before `delete p` bypasses cleanup; cleanup is unguarded. | One node. Not needed for P3 straight poly subset. Optional hardened variant below. |
| `plugins_absent` | none (typed evidence) | Main owns `3dsmax-mcp_get_plugin_capabilities` capture and verified normalization. Missing keys are not absent plugins. | No call by this reviewer. |
| `materials` | `canonical/materials.ms` | Three transient unassigned material constructors. No scene node/assignment, but not strict query-only. Canonical `=absent` tokens have no calibrated positive/bogus controls. | Fixed 3 iterations. **Exclude from P3 work: materials remain out of scope.** |

**No canonical body contains deletion-by-prefix or lookup-by-name deletion.** The
unsafe aspects are exceptional cleanup paths, conditional unexpected construction,
and inadequate calibration for interpreting an absence—not a prefix sweep that
needs replacing. Never “clean up” suspected remnants by names/prefixes. Labels
are not ownership. If an unexpected constructor creates a node before returning
its reference, these small scripts cannot claim crash-atomic recovery; stop and
inspect rather than broad-delete.

Bounded-work assessment is static: one body per sequential
`3dsmax-mcp_execute_maxscript` call, expected under roughly 2 seconds under the
repo rule, **not a measured hard deadline**. No renderer construction, file I/O,
reset/save, layer modification, global variable/function registration, viewport
change, unbounded loop, or modifier ladder is proposed. If a call times out, do
not repeat it or assume the bridge is dead; main follows the established cheap
status/read-only diagnostic rule.

## Recommended fresh native-unit preflight

1. Main first re-reads the live snapshot/entry state if intervening work may have
   changed it. Run `canonical/max_version.ms` and `canonical/units.ms` separately,
   retaining complete tool responses and actual returned strings. No unit switch
   to centimetres is needed or allowed by these scripts.
2. Run **`modified/01_native_units_readonly.ms`**, a **modified calibration, not
   canonical `env_preflight.py` output**. It refuses a nonempty/selected/named or
   non-mm/1 scene, embeds the actual unedited `scene_units.emit_unit_preamble`
   output, and independently reads Max's unit parser:

   - `c = 0.1 cm/native unit`, `f = 10 native units/cm`;
   - `units.decodeValue "1cm" = 10.0`;
   - `units.decodeValue "10mm" = 10.0`;
   - `units.decodeValue "1mm" = 1.0`.

   It compares parser values and conversion factors at `1e-6`, and reports
   `unitOk=true` / `unchanged=true` only if all tested invariants match. The latter
   covers object/selection count, native units, file/path and dirty flag. A
   throw/`__MCP_MS_ERR__:`/missing field is not PASS and says nothing about API
   absence. This is real native-unit runtime work **when main executes it**;
   the offline calculation alone is not runtime evidence.
3. If main needs a geometric native-unit write/read control, use optional
   **`modified/02_native_box_roundtrip.ms`**, again **modified calibration, not
   canonical**. It has the same entry guards. Exactly one local-reference Box,
   zero modifiers, is created from canonical cm values using the actual preamble:

   | Quantity | Canonical cm | Independent expected native mm/1 |
   |---|---|---|
   | dimensions X/Y/Z | 10 / 20 / 30 | 100 / 200 / 300 |
   | Box position (XY centre, base Z) | [100, 200, 300] | [1000, 2000, 3000] |
   | bbox min | [95, 190, 300] | **[950, 1900, 3000]** |
   | bbox max | [105, 210, 330] | **[1050, 2100, 3300]** |

   Bboxes are checked against **literal independent native expectations**, not
   against the emitted factor echoed back, at `0.0001 native unit`. All work is
   under try/catch; cleanup runs before result formatting, deletes only the exact
   locally returned reference `__node`, and reports cleanup exceptions/liveness.
   Required fields: `probeThrew=false`, `measureOk=true`, `cleanupThrew=false`,
   `ownedAlive=false`, `censusOk=true`, `unitsOk=true`, `fileOk=true`. Retain
   `minNative`/`maxNative` and re-snapshot independently afterwards.

**Dirty-state limitation:** creating/deleting temporary nodes can set save-required
and affect undo/callback state even with final node census restored. The probe
reports `saveBefore`/`saveAfter` but **does not clear the flag**, save, reset, or
claim whole-scene bitwise preservation. Prefer step 2 if only a read-only native
preflight is required. A temporary-node check is not produced-wall QA or runtime
poly acceptance. It cannot erase P2 produced-poly SKIPs.

## Optional isolated revised equivalents

Prepared only in case main has a reason to refresh one of the existing checks:

| Existing check | Modified body path | Exact revision and limit |
|---|---|---|
| `loft_not_creatable` | `modified/loft_not_creatable.ms` | Positive `execute "1+1"` and bogus `execute "TotalGarbageXYZ123"` controls; separate resolution/throw/value flags; local returned-reference cleanup on unexpected node construction. Inherit P1 by default. |
| `sweep_on_shape` | `modified/sweep_on_shape.ms` | Guarded setup/readback, one Rectangle, one attach attempt, no default false-zero read result; cleanup exact `shapeNode` reference before formatting; cleanup/liveness/census flags. No invented alternative behavior expectation. |
| `quadpatch_creatable` | `modified/quadpatch_creatable.ms` | Guarded constructor/class reads, cleanup exact `patchNode` reference before formatting; cleanup/liveness/census flags. |

All three refuse the known entry state's nonempty/selected/named/non-mm1 drift;
none deletes by name, prefix or scene enumeration. All are **modified calibrations,
not canonical** and none was run live. They retain compatible legacy success
tokens, but **the canonical evaluator does not validate appended cleanup flags**.
Main must independently inspect flags, raw MCP status/error prefix, and final
state before accepting anything. No “new absence” conclusion can be based on an
uncontrolled canonical failure.

## Two-phase capture and scoring contract

- Offline preparation command executed:
  `python -B Audit/phase16-p3-preflight-2026-11-02e/prepare.py`.
- Actual canonical stdout is preserved in `canonical-emit.txt` and
  `canonical-emit.json`. Normal no-capture emit exits 0 with **PASS 0 / FAIL 0 /
  SKIP 10**; `canonical-emit-require-complete.json` records the same ten SKIPs
  with strict exit **1**. This is calibrated emit behavior, not live PASS.
- `results-template.json` has exact check names with **null** values, deliberately
  no fabricated captures. Main should copy to its own run-owned results file and
  replace only keys genuinely captured. Raw responses should be kept separately.
- Live strings belong under their matching check names. Modified checks must be
  explicitly identified as modified in provenance; native-unit calibration has no
  matching canonical check and must remain separate evidence.
- Strict scoring, when actual captures exist:
  `python -B scripts/env_preflight.py --results <actual-results.json> --require-complete --json`.
  An omitted/out-of-scope/unrefreshed row is SKIP, not current PASS. Do not populate
  accepted historical facts as though freshly captured. If materials are not run,
  an honest fresh subset cannot claim a complete ten-check gate. Bridge/version
  mismatches can be WARN by design; inspect the report, not exit status alone.
- Typed bridge/plugin evidence is **main's separate task**, not obtained here.
  Supply all five actual boolean plugin states; do not normalize missing/unknown
  values to false or infer availability from a constructor throw.

## Offline verification and preserved sources

`preparation.json` records exact unchanged source SHA-256 values before/after:

```text
a60103393d11828d7e40547aa02e15c85ac67645c0f507b03694fa447e6b099e  scripts/env_preflight.py
b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2  scripts/scene_units.py
```

The main's already captured native-mm/1 entry value was normalized **offline**
for `check_units`; it is accepted by the existing evaluator. `unit_factor` gives
`c=0.1`, `f=10.0`. This confirms expected input support, **not** live conversion.

`verify_offline.py` checks exact canonical extraction bytes, source hash stability,
Python ASTs, delimiter/string balance, forbidden operations, and exact local
delete operands across the 13 emitted/revised bodies. Its output is
`static-verification.json`. These checks are **not a native MAXScript parser**,
timing measurement, live cleanup proof, or P3 geometry acceptance. Max remains
entirely the coordinator's responsibility.
