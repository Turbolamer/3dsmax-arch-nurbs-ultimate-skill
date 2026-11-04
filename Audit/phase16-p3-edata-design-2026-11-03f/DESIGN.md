# Phase 16 P3.1: EData3 error — offline diagnosis and draft controls

**Status: INCOMPLETE; designs only; no Max call or actual new measurement.**
Do not run an emitted wall, relax replay, install, or interpret the historical
exception as API/class absence or equality. P3.1 remains NOT ACCEPTED.

## Evidence actually read

* `../phase16-p3-main-probes-2026-11-03f/edata3.ms` SHA-256
  `ae7ddb26e911259d873737f80c7a24988e3fe45b9d6a5931d6d745b55e25ff50`.
  Retained result `../phase16-p3-main-probes-2026-11-03f/edata3-result.json`
  SHA-256 `5e86604ad6af4d55e239ec1054e775288ca077d28980f57d1a3b2815c92ad1a1`.
  Its transport says `ok=true`, but its body says `ERROR=-- Runtime error:
  Vertex data support not enabled for specified vertex data channel: 3` and
  `outcome=INCOMPLETE`. Script cleanup says true and the independent recorded
  postcheck says 0 objects/selection; do not infer anything beyond that event.
* The historical positive VData11 probe is a different node and run: repeat
  0.375 and edit 0.625 observed, not EData evidence. See
  `../phase16-p3-main-probes-2026-11-03f/vdata11-result.json`.
* The original emitted Main03 `published/wall_surface.ms:149-199`, SHA-256
  `91274ffbb1cb9491c6b5fd511ceb238346f45434e56c2d6b467753a7cbdaaf28`, obtains
  `vn`/`en`, loops supported VData and EData separately, and for each supported
  EData channel reads every non-dead edge via `polyop.getEDataValue base channel i`.
  Its returned data retains support states and values; a throw propagates out,
  not an equality observation. Main03 actually failed earlier at the layer
  baseline; the later EData3 candidate is **not** a failure observed in that
  production runtime. That block was also present in `scripts/wall_surface_runtime.py`
  at inspection; the source was concurrently changing, so no frozen-source or
  same-hash conclusion is made here. Compare its settled revision before action.

## What the original trace can and cannot say

The original script puts all lines 15–64 under one `try/catch` and appends its
first detailed progress report only at lines 60–61. Therefore the returned
exception alone does **not** identify the raising operation. The source-ordered
candidates include `setNumEDataChannels` at line 49,
`setEDataChannelSupport` at 50, the first `setEDataValue` at 51, the post-write
count/support reads at 52–53, first/repeated `getEDataValue` at 54–55, second
write/read at 56–57, and even another earlier or later operation throwing the
same message. It is not safe to say the getter was reached, that support was
true, or that any particular setter completed. The exact error message suggests
an interaction with **vertex** channel support, but is not itself a trace of
which check occurred or what storage was read.

Plausible, not demonstrated causes worth separating:

1. A particular EData setter/getter may mistakenly test VData channel 3, or its
   exception text may simply be copied/misnamed; alternatively an undocumented
   prerequisite really may exist. These possibilities are not interchangeable.
2. Setting channel *count* and enabling channel *support* are distinct; the
   support setter might throw, return without enabling support, or change state
   later. The original did not read support until after the first write.
3. Object representation, internal allocation, node/base binding, selection,
   edge validity or channel semantics could be involved. Both node and base are
   documented inputs; this does not prove they have equivalent behavior here.
4. A mistaken index, reserved range or wrong setter argument is a generic
   possibility, but the actual channel 3 and bitarray edge 1 are not obviously
   outside the **documented** EData contract; no conclusion follows without
   localized operations and controls.

Autodesk's MAXScript 2026 documentation, via Context7
[`/websites/help_autodesk_view_maxdev_enu/2026`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-4EF4DCB1-AA96-48BF-9985-3518C53C8294),
states that EData indices are 1-based, EData counts are 0–10, channels 1–2 are
reserved (knot and crease), and provides separate count, support and float
get/set APIs. The same page says VData counts are 0–100 and channels 1–10 are
reserved. It does not say EData3 needs VData3 enabled. Documented range/syntax
are reference claims, **not** proof of behavior in this build.
[EditablePoly get/set edge data](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-90843EC5-AE3A-43EB-9406-A3631DAEADEF)
documents `getEdgeData` (selected count/uniform by reference) and `setEdgeData`;
[edge flags](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-0EF108C4-0865-458B-97B8-E03E9B990B14)
document bit 1 as selected. The relationship between its channel integer and
`polyop` EData3 **has not been calibrated here**. The independent reader may
be unsupported, access another index, or have different allocation behavior.
Do not assume it works or that it is API/implementation-independent storage.

## New separately bounded draft probe design

Both files are written but **unexecuted and uncompiled in Max**. They are
illustrative drafts for main's safety/syntax review, not preapproved execution.
Only main may execute live probes, after current-state admission and all
independent safety review. One disposable node per attempt, no concurrent probes;
no loop over candidate indices, no modifier, no script function definitions.
An offline text-level check found balanced delimiters, unique stage labels and
immediately adjacent try/catch on 25 and 24 VData/EData calls respectively;
both contain only `delete orig`. The historical script/result hashes above
were rechecked. This was **not** a MAXScript parser, a test of cleanup, or any
evidence that the drafts execute, finish within budget, or are safe live.

* `probe.ms`: instrumented EData3 path, with one captured try/catch and
  result marker per count, support, target write, target read and repeat/edit.
  `C01` deliberately gives the target getter an invalid `undefined` object and
  expects a throw. `V01`–`V10` make a fresh VData11 positive (0.375/repeat/
  0.625). `E01`–`E05B` read count/support separately; `E06` reads VData3 support
  and stops unless false; `E07` does the original target write; `E08` reads.
  If E07 throws the script stops; if E08 throws, C02–C04 *may* still read what
  E07 wrote, but then must return INCOMPLETE. If both paths succeed, E09–E11
  repeat/edit and C05 cross-checks. C06 checks selected geometry facts, **not**
  full mesh/metadata equality. The VData11 setup and extra support queries mean
  this is a useful localizer but **not an identical reproduction**: unlike the
  original, VData count is 11 (channel 3 remains unsupported). Any behavioral
  difference versus the original remains unlocalized until an independently
  reviewed, otherwise identical fresh-node A/B is executed.
* `alternate-control.ms`: separately bounded positive EData *read* attempt,
  even if `polyop.setEDataValue` fails. On another fresh node after full cleanup
  and new admission, use VData11 and wrong-type controls; independently call
  `orig.setEdgeData 3` and `orig.getEdgeData 3` on selected edge 1. Confirm
  count=1/uniform=true, values 0.375, repeat 0.375, edit 0.625; before/after
  read selected edge 2 as an unselected-edge control. `T01` and `T02` log the
  target `polyop` getter separately; errors do not suppress the alternate edit
  test. Even an observed alternate positive is **not** proof that the two APIs'
  channel indices agree; require target reads to track both writes, and further
  independent channel-identity calibration for attribution. If support setup,
  alternate API, channel index, selection or read/write fails, that control is
  INCOMPLETE; it cannot explain the original error or be replaced with constants.

### Outcome matrix and safe future A/B

| Observed stage, once independently executed | Interpretation / next safe action |
|---|---|
| E02/E03 or E04/E05/E05B fails | Localize count vs enable vs support read; no value-operation inference. Stop. |
| E05/B true, E06 false, E07 throws | Target write failed after support observations; alternate control on a **new** node can test edge data separately. Do not enable VData3 on the failed node. |
| E07 succeeds, E08 throws; C04 returns 0.375 | Target getter failed after a separately observed read, subject to channel-selection calibration. Runtime's getter path remains unsafe. |
| Alternate returns the two distinct values but T01/T02 throw/mismatch | Positive alternate reader is bounded evidence; target getter/correspondence still INCOMPLETE. |
| E07/E08 and alternate matching controls all work | Positive bounded observation only; original exception remains unexplained, especially because VData11 count differs. |
| Any missing marker, exception, timeout, residual or changed context | INCOMPLETE. No retry, reset, save, dirty-flag clearing, handle/name-based adoption or neighbor deletion. |

If E07/E08 localizes a VData-related exception, a later A/B is an **additional
design**, not part of either script: two sequential fresh nodes with identical
geometry, VData count 11 and unchanged EData3 setup. A leaves VData3 unsupported;
B enables VData3, recording pre/post support, retaining the same stages and
owned cleanup. Record support and value before/after target operations, compare
with independent EData reads, both wrong-type controls and exact control node
censuses. VData3 is Autodesk-reserved; use it on an owned disposable node only,
never production, and only after an explicit main safety/cleanup decision. A
different outcome supports a **version-specific correlation**, not a conclusion
that Autodesk specifies the dependency or that it is safe to modify production
VData. Conversely equal outcomes do not explain away the original failure.

## Cleanup and execution limits

Draft cleanup requires exact original live reference **and** original handle
roundtrip, same conversion reference if attempted, sole-object exact census,
empty scene selection, no children/foreign parent or base instances, unchanged
root/path/units/layer count/dirty observation, and no unclassified node/base
dependents. Only the bound original reference is passed to `delete`; never a
reacquired handle or name. The conservative dependency rule accepts no node
dependents and only the exact original as a base dependent. Max may normally
show other dependents; then it intentionally leaves the owned node and reports
`RESIDUAL_OR_IDENTITY_UNCERTAIN_NO_DELETE`. A constructor that throws before
returning a reference, or conversion with missing/different candidate, remains
unknown even if the scene later appears empty. Candidate reference/handle strings
are diagnostic only; they confer no deletion authority. A throwing delete is
never retried. Main must inspect actual live residuals without broad deletion.

The scripts admit only an unnamed empty unselected mm/1, clean, one-layer
scene. The dirty and environment checks are intentionally **very conservative**:
legitimate node edits may change `getSaveRequired()`, causing residue rather
than cleanup. Do not clear the dirty flag to force this gate. Exact state and
dependency guards do not prove arbitrary callback absence, process continuity,
interruption recovery, or crash atomicity; an uncaught pre-parse error, bridge
timeout, process interruption or logging failure can prevent even the cleanup
block from running. Review the risk before scheduling; treat timeouts as
unknown state, not a clean result. Fresh read-only admission/pre/post observations
and independent capture of full raw response, timing, SHA-256 and script bytes
are required; `ok=true`, zero count alone, or a final marker cannot substitute
for them. No owned-ref cleanup safety is assumed merely because this draft has
guards; the previously documented dependency/interruption review still applies.

### Exact next actions for main

1. Preserve both original evidence files; hash the settled runtime and retained
   Main03 before comparing, and separately review these unexecuted drafts for
   MAXScript syntax, dependency/dirty behavior, interruption and cleanup.
2. If safe operation cannot be justified, **do not run**; report the blocker and
   design a better independently calibrated cleanup protocol. No neighbors or
   reserved channels may be modified to make a test pass.
3. If main approves, obtain a fresh read-only admission; execute only `probe.ms`
   on one owned quad. Capture the full response and perform a fresh read-only
   postcheck. If fully clean, decide separately whether to run
   `alternate-control.ms` on its own new quad with fresh admission. On ambiguity
   stop and inspect; never run the next probe over residual state.
4. Interpret the stage/error matrix and controls above. Keep production metadata,
   clean replay, F01, and P3.1 INCOMPLETE until independently demonstrated.
