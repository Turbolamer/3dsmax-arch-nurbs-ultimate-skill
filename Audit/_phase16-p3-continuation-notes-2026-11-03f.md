# P3.1 continuation notes — 2026-11-03f

This note records current observations separately from the immutable FINAL2 run.
No new acceptance is implied.

## Live stop: one unresolved temporary residue

The **latest** scene state differs from entry and the successful tiny probes
below. Main's `controller-graph.ms` first failed to parse; the retained v2 then
created a Box and attempted Shell but failed with `Mesh operation on non-mesh:
Box`. Its own cleanup did not have a Shell handle and explicitly refused.
`Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2-residue.json`
retains raw responses and read-only census. At that observation: one node
`Box001` handle `2024P`, Shell handle `2044P`, selection0, unnamed mm/1,
dirty=false, default layer0. The independent original locals did not survive
the call: no exact node/modifier witness is retained across calls. Current name,
handle or count are **not** permission for automatic deletion/adoption. Stop
scene mutation and retry, never save/reset/clear dirty/registry. User inspection
and manual removal of the temporary residue are needed; after that, freshly
inspect state rather than assuming the scene empty.
Independent incident analysis
`Audit/phase16-p3-controller-incident-2026-11-03f/report.md` confirms that
the failing source statement is not localized (`update n` is a hypothesis) and
the catch's Shell check means its exact reference **or** handle was unavailable.
One intermediate main message saying the original node was "not lost" was
imprecise: the later node is a candidate residue, not a retained exact witness.

## Changed source and current failing gates

`scripts/wall_surface_runtime.py` current SHA-256
`3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf`;
the other three P3 source hashes still match the historical FINAL2 run. The
prior exact runtime bytes are retained under
`Audit/phase16-p3-runtime-hardening-2026-11-03f/` with the intermediate revision.
The current changed runtime includes explicit `INCOMPLETE_PRECREATE` and
`INCOMPLETE_REPLAY` guards and intentionally does not automatically delete
unproven nodes. Its protective static suite was executed by main: 21/21 OK.
Main's unchanged historical runtime suite: 42 run, one FAIL, since it expects
handle-only recovery and deletion now absent. Main's independent replay/layer
suite on the same current runtime: 14 methods, seven failed subtests, all layer
reader checks; input hashes stable. These are **real current FAILs**, not a
settled green run, and must not be papered over by weakening tests. Consult
`PRECREATE-GATE-REPORT.md` and the actual logs under that hardening directory.
No current genuine F01 emission/fileIn, accepted NOOP, full metadata or
production layer comparator occurred; all future stages remain incomplete.
Main separately ran `Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py`:
13/13 offline diagnostic tests passed, including refusal to call derived triangle
groups native evaluated polygon evidence and INCOMPLETE when grid capture is
missing. The corresponding Max candidate is unexecuted and is not an F01 result.

The independent metadata design `Audit/phase16-p3-metadata-design-2026-11-03/`
was authored from the earlier handoff and includes historic wording that the
Main03 lease "remains POISONED". That describes the previous observed process
only; fresh key absence and process discontinuity above supersede it for the
current process. The report's `layerAsRefTarg` was a candidate when written;
the main-only read-only observations below are later evidence, not part of that
author's claimed execution.

## Max session discontinuity

Fresh main-only read-only inspection and calibrated global-name checks are in
`Audit/_phase16-p3-resume-live-entry-2026-11-03f.json`. The currently connected
Max process started at 2026-11-03T17:27:21.875Z, after FINAL2, with 0 objects,
0 selection, unnamed scene, millimeters/1.0, dirty=false. Main03's key is absent;
reading it throws, while real global-name controls succeed. The historical
POISONED witness was observed in the earlier process, not this one. Its exact
instance cannot be reconstructed. No assumptions are made about the particular
intervening actions. No rearm, registry removal, reset, save, dirty-flag change,
or backup access occurred.

## New layer observations

`Audit/_phase16-p3-layer-readonly-2026-11-03f.json` contains read-only actual
wire values: `layerAsRefTarg` exposes a backing reference with a working handle
roundtrip for this one default layer, and its 34-property enumeration has
`degrade` beyond the 33 interface properties. The nested GI interface has 18
readable properties in this case. Main then ran one controlled temporary-layer
probe `phase16-p3-main-probes-2026-11-03f/layer-owned-result.json`: distinct
backing identity, repeat equality, and detected lock/GI/name changes, with
exact-verified empty-layer cleanup. A separate Box/layer membership control
`phase16-p3-main-probes-2026-11-03f/layer-membership-result.json` actually moved
and restored the exact node's layer and membership arrays with guarded cleanup.
Both are narrow API probes; same-name replacement, production comparator, full
dependency semantics and overall baseline are not yet proven.

## Metadata controls

Main's `phase16-p3-main-probes-2026-11-03f/vdata11-result.json` supports only
the added custom vertex-channel value/change behavior on one disposable quad.
The separate `edata3-result.json` records **actual error / INCOMPLETE** despite
transport success; the error did not identify the individual suboperation.
Both exact temporary nodes were deleted; the independent follow-up snapshot
request `a1fdaf5782604ced9672c302d4c91fa9` reported objectCount/rootCount 0,
no error. No reset/save/flag clearing occurred. More targeted EData diagnostics
are required; the failure is not evidence that the whole EData API is absent.

## Preservation

Independent `Audit/phase16-p3-preservation-2026-11-03f/REPORT.md` checks the
historical publication manifest: 826/827 match, none missing; only
`graphify-out/cache/last_query_stamp` changed. The file is generated graphify
query-cache metadata; a shell invocation in this continuation printed a graphify
query from a hook, and its timestamp falls within this continuation. The exact
writer of the changed stamp is **not independently established**, contrary to
the shorthand in one intermediate message. No attempt was made to restore it.
Original published Main01–03 pairs, `input-lock.json`, HEAD and package match.
