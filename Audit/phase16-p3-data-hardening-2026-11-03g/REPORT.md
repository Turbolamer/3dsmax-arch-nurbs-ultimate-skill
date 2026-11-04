# Phase 16 P3.1 — limited VData/EData source hardening

**Status: OFFLINE / INCOMPLETE / NOT ACCEPTED.** This is a narrow source change
and an independent offline structural/model check. It is not a MAXScript parse,
Max execution, API-behavior measurement, safety evaluation, or acceptance claim.
The historical EData3 error was not investigated or resolved.

## Scope and preservation

Only these scopes were written:

* `scripts/wall_surface_runtime.py` — the requested runtime edit.
* `Audit/phase16-p3-data-hardening-2026-11-03g/` — this report, exact snapshots,
  diff, independent tests/runner, raw logs, and result ledger.

No existing test was edited. No Max/MCP call, MAXScript execution, install,
package/archive update, git operation, reset/checkout, save, or scene mutation
was performed.

Before editing, the source was read and hashed as required:

```text
command: python -B <exclusive snapshot/hash heredoc>
expected source sha256: 3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf
observed source bytes: 58990
observed source sha256: 3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf
snapshot: Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py
snapshot bytes: 58990
snapshot sha256: 3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf
snapshot creation: exclusive (`xb`); byte-for-byte readback matched
```

The gate matched, so work continued. A mismatch would have stopped without
creating the directory or snapshot.

## Runtime change

The existing `polySnapshot` data tuple and field order are retained. The limited
change is fail-closed validation only:

1. V/E element counts `nv`/`ne` and V/E channel counts `vn`/`en` must be actual
   MAXScript `Integer`, nonnegative, and within existing operational ceilings
   (`nv <= 64`, `ne <= 256`, `vn <= 100`, `en <= 100`), retaining the original
   operational ceilings. These are resource refusal bounds, **not** calibrated
   channel-domain or allocation claims. The independently cited Autodesk
   documentation states a different EData limit; its relationship to the actual
   count/getter behavior here remains unverified, so no EData support conclusion
   follows and an API throw remains incomplete.
2. VData/EData channel support must be exactly `BooleanClass`; no truthiness or
   numeric coercion is accepted.
3. A supported live entry must be an `Integer`, `Integer64`, `Float`, or `Double`.
   `freeze` is called with `dataOnly:true`, producing a newly constructed tagged
   scalar record. Its existing Float/Double self-equality and magnitude checks
   reject NaN/infinite or out-of-conservative-range values.
4. Entries identified as dead by a `BitArray` use an explicit `#("dead")`
   sentinel; strict-Boolean-false support uses `#("unsupported")`. This changes
   those two payload representations but retains all data fields. It does not
   prove the semantic completeness of the dead reader or that Boolean false
   proves absence/allocation semantics. A supported alive `undefined`, wrong
   type, getter throw, or malformed result is intended to reach the existing
   refusal/catch path rather than becoming an equality record.
5. Explicit source guards prevent the data loops from intentionally issuing
   support/value calls on zero counts; channel loops use only `1..count`. Whether
   those indices are actually valid for a particular Max API/build is unverified.
   No new support or EData3 behavior is asserted.

The unconditional `INCOMPLETE_PRECREATE` and `INCOMPLETE_REPLAY` refusals and
the existing inspect-only residual/cleanup behavior were retained. No handle
fallback, construction enablement, replay enablement, or new support claim was
added.

## Independent offline tests

`test_data_hardening.py` is confined to this new directory. It uses a hypothetical
Python API model and source text checks; it does not parse or execute MAXScript.
The final run covered wrong count types, negative/over-limit/nonfinite counts,
wrong/throwing support, undefined/wrong/non-scalar/NaN/infinite values, dead
entries, zero counts, finite scalar detachment, value edits, and the refusal
ordering. Final result:

```text
python -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py
15 tests, OK, exit 0
```

The unchanged existing protection suite also ran without modification:

```text
python -B Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py
21 tests, OK, exit 0
```

The unchanged legacy runtime suite remains qualified, not green:

```text
python -B Audit/test_phase16_p3_runtime.py
42 tests, 1 failure, exit 1
failure: test_cleanup_exact_current_attempt_refs_only
```

That failure is the pre-existing assertion requiring the removed
`getAnimByHandle createdHandles[i]`/`delete exactNode` cleanup branch. The test
was not weakened or changed. The final suite also confirms the previous helper
count incompatibility from an intermediate draft is gone; only this known
cleanup assertion remains.

The final recorder `run_checks.py` stored raw stdout/stderr and input hashes.
Its final command was:

```text
python -B Audit/phase16-p3-data-hardening-2026-11-03g/run_checks.py v3
```

It reported Python AST parsing `OK` for the runtime, pre-edit snapshot, new
test, and runner; new data tests `15/15 OK`; protection tests `21/21 OK`; old
runtime `42 run / 1 FAIL`; all recorded input hashes stable. The runner exits
1 because the old suite failed, rather than hiding that result.

## Hash ledger

```text
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2  scripts/wall_surface_runtime.py
3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf  wall_surface_runtime.pre-edit.py
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2  wall_surface_runtime.v3-final.py.bin
3865bacd78f7b468d8dde1670ff4c260981952d4888c011c24ce89098b660045  runtime.v3-final.diff
b59079782c17459c207f531f25d1a102fad9d6a4c66df79f7570586de33ca472  test_data_hardening.py
e289df5c2d61f826134ea2253972ffef0735353ea903669278fe2f2037594900  run_checks.py
02bfe57fbed97301f2c6454b5f6ee8418a8ff41b3dfcb9a3115a798e55af90f8  v3-results.json
eb1008b49d141a4e2c348b4458093413f3b1a028424d0576979b86e63584d12e  ../phase16-p3-metadata-independent-2026-11-03g/REPORT.md (input)
19360d8f54ce667e692d2c30ce6be7ea28e5fad1a82d3b79d8fbd95195d7919d  ../phase16-p3-runtime-hardening-2026-11-03f/test_protection.py (input)
242bb0c4403068246c9e223f769ebed822dbea3931d0dce6052bfc63aee96c38  ../test_phase16_p3_runtime.py (input)
```

The intermediate runtime/diff and test/runner snapshots were also created
with exclusive write before later changes:

```text
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2  wall_surface_runtime.post-edit.py.bin
bd44a0df6812d46ef39bc4645c3f2e63995159a9c9f652f1e6e6b0836df8cb67  runtime.diff
94ae49883cf1fd1396e1ec01a4ed7886103e0f0f3fa513db2260d5fe3b3cf46f  test_data_hardening.v1.py.bin
d24f9e14f7eb54aae13cea9d84b3029803777c5f71048fcab588b9e3b765a2a7  run_checks.v1.py.bin
4d762dbae69f10011a53d7c540d59b154e9aeac675a450e5447e3df77ef7bedb  results.json (intermediate run)
2503fbfcfbe1bc0480512f2f7e3fbcfe740a56f9478f37affdbddeeca8edf56a  wall_surface_runtime.final.py.bin (v2 intermediate, despite filename)
94421c6de27d3bac9d0742791351d72d7b894fd1251c1463491e948af721a6ed  runtime.final.diff (v2 intermediate, despite filename)
80ae5a26f8afd6e94c16b2d8b1d96a5eb24f5a67cae70bf7792f58eb557ff67a  test_data_hardening.v2.py.bin (reconstructed; hash-verified)
84cd23d6297533fec6f28ab00573ca920d94708147e3390911b741930ba4cbfa  run_checks.v2.py.bin (reconstructed; hash-verified)
05988e41972b4e4fadfd9e84a1a8ab9fc4f9679cea54aa27fde036d2b51d21ae  v2-results.json (intermediate run)
```

Raw final log hashes are recorded in `v3-results.json` (data-hardening stderr
`4259c57f208ca3e24088b1b972ffc8c23b828710b51bff64227e602cb0f8122f`,
protection stderr `211f825536f8e7b26fdfde8071f5265bcb10fbb07d16142a351a732895355a2a`,
legacy stderr `3bc7a45d6fa9cfb6c7c989cb8c49e8406da06e2990bd2aaf23bbcb6dcc5fd532`).

## Intermediate command history

The following earlier results are retained rather than represented as final:

* The pre-edit exclusive snapshot/hash heredoc exited 0 before any source edit;
  later exclusive snapshot/diff heredocs preserved each recorded runtime, and
  one exclusive-copy heredoc preserved the first recorded test/runner. After the
  v2 test/runner had already been edited, their exact bytes were reconstructed
  and compared with their previously recorded SHA-256, then saved exclusively;
  they are labeled reconstructed, not misrepresented as contemporaneous copies.
* Initial direct `python -B .../test_data_hardening.py`: 14 run, **2 FAIL**
  (source detector expected the unprefixed helper name; tail comparison mixed
  an unsubstituted template with a substituted emission). The next direct run,
  after repairing the test, reported **14 OK**.
* An ad-hoc `python -B` heredoc importing the test for a diagnostic diff exited
  1 with Python `dataclasses` / `sys.modules` `AttributeError`. It wrote no
  files and was not evidence about MAXScript or the runtime.
* Direct `python -B Audit/test_phase16_p3_runtime.py` on the initial draft ran
  42 tests with **2 FAIL**: the pre-existing cleanup assertion and a new fixed
  helper-count expectation. The source was refactored into the existing freeze
  helper; the existing test was not changed.
* `python -B .../run_checks.py` (intermediate version): data **15 OK**,
  protection **21 OK**, legacy **42 run / 1 FAIL**, recorder exit 1. Its
  `results.json` and raw logs remain unchanged. The EData refusal ceiling was
  subsequently tightened from 100 to 10; `v2` ran on those bytes and produced
  15 OK / 21 OK / 42 run with the same 1 FAIL. In the final v3 source that
  limit was restored to the existing 100 so this work does not presume actual
  EData API behavior. All recorded versions and results are retained.
* A rejected patch attempt and one nonexistent-file read made no changes.
* `COMMANDS.md` contains exact shell commands, results, and the v2/v3 recording
  sequence; logs and per-run input hashes are in the three result ledgers.

## Limitations and verdict

These checks establish only that the Python source emits the intended textual
guards and that the hypothetical model treats unknown observations as
`INCOMPLETE`. They do not establish MAXScript syntax, `polyop` count/support/
value semantics, detached behavior in Max, complete native metadata coverage,
safe cleanup, witness continuity, replay safety, or construction safety.
In particular, the model's hypothetical dead-status list has a fully explicit
length and entries; that is not evidence that the real `BitArray` API exposes or
proves the same domain. The existing dead sentinel itself is not a complete
native dead-element metadata reader. Numeric bounds conservatively reject some
finite extreme magnitudes as well as nonfinite values.

**Verdict: limited offline hardening recorded; P3.1 remains INCOMPLETE and NOT
ACCEPTED. Do not claim safe evaluation or run the emitted method in Max from this
work.**
