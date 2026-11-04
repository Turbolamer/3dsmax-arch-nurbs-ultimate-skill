# Phase 16 P3.1 — Independent Runtime Source Review

**Date:** 2026-11-03  
**Reviewer:** Independent Code Auditor  
**Verdict: BLOCKED / INCOMPLETE — P3.1 NOT ACCEPTED.**

---

## 1. Executive Summary & Boundaries

This audit constitutes an independent, offline source and test review of the current runtime (`scripts/wall_surface_runtime.py`) and recent verification results for Phase 16 P3.1.

### Operational Boundaries
- **No mutations to `scripts/`:** `scripts/wall_surface_runtime.py` and all other files in `scripts/` were inspected in read-only mode and left strictly untouched.
- **No deletions:** No existing files, tests, reports, logs, or snapshots across the repository were modified or deleted.
- **Strict directory confinement:** All outputs produced by this audit are strictly confined to `Audit/phase16-p3-runtime-review-2026-11-03h/`.
- **No live 3ds Max / MCP interaction:** No MCP tools, Max bridge calls, `fileIn` operations, or live scene mutations were invoked. All findings are derived from static source inspection, diff analysis, Python-based test suite executions, and cross-examination against peer audit reports.

---

## 2. Source Identity & SHA-256 Verification

The byte sequence of `scripts/wall_surface_runtime.py` was independently hashed and verified:

```text
Expected SHA-256: ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2
Observed SHA-256: ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2
File Size:        60,948 bytes
Status:           EXACT MATCH (Byte-identical)
```

The pre-edit baseline from `Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py` was also verified:

```text
Pre-edit SHA-256: 3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf
Pre-edit Size:    58,990 bytes
Status:           EXACT MATCH
```

---

## 3. Source Diff Analysis (Data Hardening)

A unified diff between `Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py` and `scripts/wall_surface_runtime.py` yields exactly 79 lines of modifications, confined entirely to the `freeze` helper function and the `polySnapshot` data reader:

### Key Code Modifications:
1. **Scalar Data Typing in `freeze` (`lines 555-564`):**
   - Added keyword argument `dataOnly:false`.
   - When `dataOnly:true` is passed, `freeze` explicitly enforces:
     ```maxscript
     if dataOnly do require (cls == Integer or cls == Integer64 or cls == Float or cls == Double) "INCOMPLETE: unsupported/unknown data scalar"
     ```
   - Generic composite types, references, arrays, and `UndefinedClass` are barred from data channel values.
2. **Strict V/E Count and Dead-State Validation (`lines 649-659`):**
   - Added type requirements:
     ```maxscript
     require ((classOf nv) == Integer and (classOf ne) == Integer) "INCOMPLETE: unknown V/E element count type"
     require (nv >= 0 and ne >= 0 and nv <= 64 and ne <= 256 and nf <= 32) "base snapshot operational ceiling"
     require ((classOf deadV) == BitArray and (classOf deadE) == BitArray) "INCOMPLETE: unknown V/E dead-state type"
     ```
   - Eliminates vulnerabilities where invalid types or negative counts could bypass loop bounds or indexing.
3. **Channel Count Type and Bound Validation (`lines 684-688`):**
   - Channel counts `vn` and `en` must be explicit `Integer` types:
     ```maxscript
     require ((classOf vn) == Integer and (classOf en) == Integer) "INCOMPLETE: unknown data channel count type"
     require (vn >= 0 and vn <= 100 and en >= 0 and en <= 100) "INCOMPLETE: invalid data channel count/ceiling"
     ```
4. **Guarded Channel Loops & Strict Tri-State Support (`lines 689-722`):**
   - Loops execute only when `vn > 0` and `en > 0`.
   - Channel support must be strictly `BooleanClass`:
     ```maxscript
     require ((classOf support) == BooleanClass) "INCOMPLETE: unknown VData/EData channel support"
     ```
   - Unsupported channels record `#("unsupported")`.
   - When supported, element loops execute only if `nv > 0` or `ne > 0`.
   - Each element's dead flag must be strictly `BooleanClass`:
     ```maxscript
     require ((classOf dead) == BooleanClass) "INCOMPLETE: unknown VData/EData entry dead-state"
     ```
   - Dead elements record `#("dead")`. Alive elements are frozen via `freeze (polyop.get...DataValue base channel i) dataOnly:true`.

### Diff Assessment:
The diff is minimal, surgical, and adheres strictly to fail-closed semantics. It does not introduce any silent defaults or fallback coercions. Existing tuple layouts, indices, and operational ceilings remain intact.

---

## 4. Independent Test Suite Verification

Three test suites were independently executed from the repository root:

| Test Command | Tests Run | Result | Duration | Notes |
|---|---|---|---|---|
| `python -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py` | 15 | **15/15 OK** | 0.015s | Verifies scalar data guards, non-negative ceilings, dead state guards, and refusal ordering. |
| `python -B Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py` | 21 | **21/21 OK** | 0.007s | Verifies precreate guards, dirty lease refusal, cleanup retention, and fail-closed state transitions. |
| `python -B Audit/test_phase16_p3_runtime.py` | 42 | **41 OK, 1 FAIL** | 0.050s | 1 FAIL in `test_cleanup_exact_current_attempt_refs_only` (Expected legacy assertion mismatch). |

### Analysis of the Single Legacy Test Failure:
In `Audit/test_phase16_p3_runtime.py`, `test_cleanup_exact_current_attempt_refs_only` asserts:
```python
self.assertIn("delete exactNode", script)
self.assertIn("getAnimByHandle createdHandles[i]", script)
```
During runtime hardening (Phase 16 P3-f), the unsafe handle-reacquisition fallback and uncalibrated node deletion were intentionally replaced by residual recording:
```maxscript
append residual #("RETAINED_OR_INVALID_CREATED_REF", i, refValid, savedHandle, currentHandle, location)
append cleanupOutcomes #("RETAINED_NO_CALIBRATED_DEPENDENCY_EXCLUSION", i)
```
Because the runtime deliberately refuses to delete nodes without proven exclusion of foreign dependencies, the old test's string expectation fails. This behavior is covered and affirmed as safe by `test_protection.py:test_cleanup_never_promotes_handle_or_deletes_exact_node`, which passes. The legacy test failure is therefore **expected, documented, and non-regressive**.

---

## 5. Verification of Critical Safety Invariants

The runtime source was inspected to confirm that construction and replay remain completely unreachable:

### A. Unconditional Precreate Refusal (`scripts/wall_surface_runtime.py:892-894`)
```maxscript
891:             -- Temporary fail-closed gate: remove only after independent safety verification.
892:             stage = "precreate-safety-refusal"
893:             require false "INCOMPLETE_PRECREATE: independent witness, layer identity, controller/stack/dependencies, cleanup and native metadata safety unproven"
894:             attemptStarted = true
895:             lease[5] = "BUILDING"
...
901:             local node = Editable_Mesh()
```
- **Execution guarantee:** `require condition reason` is defined at line 517 as `if not condition do throw ("P3_REFUSE|" + reason)`. Passing literal `false` forces an unconditional throw.
- **Positioning:** Line 893 precedes `attemptStarted = true` (line 894), `lease[5] = "BUILDING"` (line 895), and node creation (line 901).
- **Classification:** The outer catch block at line 1074 inspects `stage`:
  ```maxscript
  else if stage == "precreate-safety-refusal" then "P3_INCOMPLETE_PRECREATE"
  ```
  It prints `P3_INCOMPLETE_PRECREATE` and rethrows. No scene node can be constructed.

### B. Unconditional Replay Refusal (`scripts/wall_surface_runtime.py:874-880`)
```maxscript
874:         if lease[5] == "COMMITTED" then
875:         (
876:             stage = "replay-read-only"
877:             -- COMMITTED is construction-only, never proof of replay safety.
878:             -- Refuse before inspecting/evaluating any possibly edited stack.
879:             require false "INCOMPLETE_REPLAY: witness lifecycle, controller/stack/dependencies and specified-normal/native metadata unverified; no safe NOOP claim"
880:         )
```
- **Execution guarantee:** Passing literal `false` forces an unconditional throw.
- **Positioning:** Occurs immediately upon entering the `COMMITTED` branch before inspecting the node, evaluating geometry, or emitting any NOOP signal.
- **Classification:** The outer catch block at line 1074 maps `stage == "replay-read-only"` to `P3_INCOMPLETE_REPLAY` and rethrows.

---

## 6. Audit Against P3.1 Contract & Peer Review Blockers

### 6.1 P3.1 Contract Compliance (`Audit/_phase16-p3-contract-2026-11-02e.md`)
- **Operational Ceilings:** The runtime continues to enforce `nv <= 64`, `ne <= 256`, `nf <= 32`, `vn <= 100`, `en <= 100`, and `objects.count == 0` for initial creation.
- **Fail-Closed Semantics:** Absence or type mismatch in channel support or scalar data fails closed with `INCOMPLETE`.
- **Session Identity:** Replay replacement and delete-by-name remain barred.

### 6.2 Peer Metadata Blockers (`Audit/phase16-p3-metadata-independent-2026-11-03g/REPORT.md`)
- **Specified Normals (BLOCKER):** Base specified normals (corner normal IDs, explicit flags, per-corner vectors) remain unread by `polySnapshot`. Evaluated vertex normals from `getNormal` cannot substitute for base corner records.
- **SubAnims & Descendants (BLOCKER):** Controller traversal checks `numKeys == 0 or -1` and class whitelists, but does not recursively audit all subAnim descendants, param blocks, or off-time keys.
- **Dependency Classification (BLOCKER):** Foreign non-node dependencies are not fully classified; incoming/outgoing edge semantics lack calibrated proofs.
- **Pre-Evaluation Ordering (BLOCKER):** While `graphSnapshot` precedes `evaluatedSnapshot`, certain property reads occur prior to full controller classification.
- *Status:* These blockers remain **OPEN and UNRESOLVED**. The presence of `INCOMPLETE_PRECREATE` and `INCOMPLETE_REPLAY` correctly prevents premature execution in their presence.

### 6.3 Peer Layer Review Blockers (`Audit/phase16-p3-layer-independent-2026-11-03g/REPORT.md`)
- **LayerProperties MixinInterface:** Layer handling in the main runtime has not yet integrated the hardened offline candidates (`layer_reader_p31_offline.ms`).
- **LayerManager Identity:** Actual `LayerManager` identity remains unauthenticated across calls.
- *Status:* Remains **OPEN and UNRESOLVED**. The offline layer candidates remain unintegrated and disabled.

### 6.4 Peer Lease Review Blockers (`Audit/phase16-p3-lease-review-2026-11-03g/REPORT.md`)
- **Arm vs Lease Removal Conflict:** Historical arm scripts call `globalVars.remove registryKey` in catch blocks, conflicting with the retain-on-failure lease policy.
- **Provisional vs Committed State:** Runtime sets `COMMITTED` for construction without full replay validation, while wrapper templates reject `COMMITTED` as an initial state.
- *Status:* Remains **OPEN and UNRESOLVED**.

---

## 7. SHA-256 Hash Manifest

Authoritative byte hashes for all files examined during this independent audit:

| SHA-256 Hash | File Path |
|---|---|
| `ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2` | `scripts/wall_surface_runtime.py` |
| `3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf` | `Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py` |
| `b59079782c17459c207f531f25d1a102fad9d6a4c66df79f7570586de33ca472` | `Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py` |
| `19360d8f54ce667e692d2c30ce6be7ea28e5fad1a82d3b79d8fbd95195d7919d` | `Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py` |
| `242bb0c4403068246c9e223f769ebed822dbea3931d0dce6052bfc63aee96c38` | `Audit/test_phase16_p3_runtime.py` |
| `4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f` | `Audit/_phase16-p3-contract-2026-11-02e.md` |
| `eb1008b49d141a4e2c348b4458093413f3b1a028424d0576979b86e63584d12e` | `Audit/phase16-p3-metadata-independent-2026-11-03g/REPORT.md` |
| `c1e96de5d913ae693cd0a2907efc4438bf660142e05b650c6c644f96698b62fe` | `Audit/phase16-p3-layer-independent-2026-11-03g/REPORT.md` |
| `616e6fb631cbb8715a579791950dd2da3ae07e946116301e67529c7166170457` | `Audit/phase16-p3-lease-review-2026-11-03g/REPORT.md` |
| `24a3156c630fedb396ab0df13049eec9735e1d43b89fb3b4687f857452aff456` | `Audit/phase16-p3-data-hardening-2026-11-03g/REPORT.md` |
| `ad5fff9108227b1b32fcd87e479dabbcd03edcbb880151a1611d593bc9ac8d35` | `Audit/phase16-p3-runtime-hardening-2026-11-03f/PRECREATE-GATE-REPORT.md` |

---

## 8. Final Verdict & Required Next Steps

1. **Status:** Phase 16 P3.1 remains **BLOCKED / INCOMPLETE / NOT ACCEPTED**.
2. **Guards:** Both `INCOMPLETE_PRECREATE` and `INCOMPLETE_REPLAY` are active, unconditional, and fully protective.
3. **Prohibition:** No live execution in 3ds Max is permitted until:
   - Specified-normal base metadata reading is resolved and calibrated.
   - Controller subAnim recursive auditing is verified.
   - Layer identity and LayerManager cross-call persistence are calibrated.
   - Lease witness lifecycle and arm retention semantics are reconciled.
