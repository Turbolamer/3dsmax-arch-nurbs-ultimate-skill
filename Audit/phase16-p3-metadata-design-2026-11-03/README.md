# P3.1 native-state audit and calibration design — 2026-11-03

**Verdict: INCOMPLETE; P3.1 remains NOT ACCEPTED.** This is an independent
source/evidence review and an unexecuted candidate, not a runtime repair or live
result. Only main may operate Max. No reset, save, dirty-flag clearing, cleanup of
pre-existing data, lease rearm, P2 edit or package installation is authorized by
this report. `Main03`'s exact lease remains POISONED. Read a fresh state/witness
before any later main-only action.

Source audited: `scripts/wall_surface_runtime.py`, SHA-256
`bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15`.
Line references below refer to these bytes. Contract: `Audit/_phase16-p3-contract-2026-11-02e.md:28-33,39-48`;
resume: `Audit/_phase16-p3-resume-2026-11-02e.md:84-127`. The requirement is a
bounded, actually compared supported state, not proof of every possible Max
plugin or a forensic history of edits and perfect reversions.

## 1. What the source does — and exactly what it does not establish

All entries in the right column are **INCOMPLETE**, not asserted absent. A
source-level reader existing is not proof it works, enumerates its entire domain,
or detects mutations. In the actual Main03 run, initial baseline acquisition
failed earlier on layer-interface conversion; no complete baseline was committed
and no successful no-op occurred. Lines 743-748 deliberately refuse even if the
observed snapshot matches. Do not remove that barrier on the strength of the
table or a single calibration.

| State | Current readback / exact remaining gap |
|---|---|
| Base V/E/F | `polySnapshot` 595-611 records counts, dead bitsets, **live** vertex position/flags, edge endpoints/flags, ordered face vertices/flags, face material ID and smoothing. It does **not** read `polyop.getEdgeFaces` or `polyop.getFaceEdges`; incidence equivalence from endpoints/loops is an unproved invariant. Dead entries become only `#("dead")`: their other stored data is not compared. Prove they cannot be relevant/revived in the admitted state, reject their unsupported state, or supply a reader. |
| Polygon internals | No base-face diagonal/triangulation or internal hidden-face-corner representation is independently captured. Face loops and flags do not by themselves prove those records equal; evaluated triangle comparison may observe some changes but cannot prove all internal state. Autodesk's `MNFace::GetTriangles` describes internal diagonal-based triangulation; `polyop.setDiagonal` is a documented **candidate mutation**, not a proven reader. |
| Map/color/UV | 612-628 records channel support from `-2` through `getNumMaps-1`, live map vertices and map faces, with caps. This is actual source coverage, not a blanket omission. It assumes those bounds encompass every admitted map/hidden channel, all relevant face indices are readable, and returned arrays are detached; none is mutation-calibrated by the tiny zero-map evidence. Map counts are only implicit in array lengths. Dead-face map data is replaced by a sentinel. Addition/removal, coordinate, same-count face-index and hidden-channel mutations need separate controls. Evaluated mesh readback has **no** mapping/color channels. |
| VData/EData, crease/weights | 629-645 compares `getNumVDataChannels`/`getNumEDataChannels`, each reported channel's support and live per-vertex/per-edge values. This is not a missing reader. The limits, no/unsupported/support distinction, live value mutation and domain completeness have not been calibrated for this actual route. Dead-entry values are skipped. Returned scalar numeric types/finite values are not independently validated. A zero count in the old quad is a single measurement, not proof that later channel additions cannot occur. |
| Selection, flags and native extra data | 644-645 includes V/E/F selection bitsets and 605-611 the component flags; the environment includes global `subObjectLevel`. There is no independent proof that these exhaust mesh-level selection/display state, soft-selection weights, hidden per-corner data, arbitrary native/custom component channels, or native mesh-wide flags. `pointSelection` and a candidate custom channel need positive/edit/unknown discrimination; do not infer coverage or absence from generic properties. |
| Specified/explicit normals | **No base specified-normal table is read**: per-corner specified flag, corner-to-normal ID, explicit flag, normal vector, and sharing/splitting identity are not captured. 658-661 calls `getNormal` once per evaluated **vertex**, not once per face corner; Autodesk describes that as a normal based on adjacent faces/smoothing. Even unchanged evaluated vertex normals would not establish specified/explicit metadata equality. Per-corner `meshop.getFaceRNormals` is a candidate *evaluated rendering* reader only, not proof of base normal IDs/flags. |
| Controllers / timing | 559-593 walks `refs.getReference`, compares generic properties and direct controller class/`numKeys`; static-class whitelist includes PRS/position/rotation/scale and permits `numKeys == -1`. There is no calibrated proof that every transform, visibility, base and Shell animatable descendant appears in that traversal; no `numSubs`/`getSubAnim` traversal; no proof all descendants are static, non-wired, non-scripted or that current-time property values capture other-time keys. `-1` means that particular controller does not support keyframing according to Autodesk, **not** that descendants have no keys. Class tests and `getPropNames` do not establish equivalence with the subanim tree. |
| Shell properties | 681-683 explicitly require the class, one modifier and three dimensions, and 696-699 read its three enable flags. The generic graph *intends* to read all `getPropNames` on reachable targets; it is not proven that Shell/its param blocks/controllers are all reached or that `getPropNames` covers every native field. A different editable Shell field and a keyed/wired Shell parameter need their own negative controls, before evaluation. |
| Layer | 684-699 includes `#layer`; `freeze` 509-534 sends `MixinInterface` to `exactRef`, whose `getHandleByAnim` throws on this actual layer. `properties node.layer` is reached only after that conversion succeeds. The later positive default-layer equality/readback evidence does not establish different-layer identity, assigned-layer changes or mutation completeness. Never use `refs.dependents == undefined` as an empty set. |
| Node state | 684-691 reads many listed fields, but an unavailable requested property becomes `#("absent")`, allowing two unsupported reads to compare equal. `#pivot`, `#pos`, `#rotation`, `#scale`, group/container membership and other native state are not separately required by this list; matrix/object-offset or generic-property equivalence is **unproved**, not disproven. If a field is required, `isProperty == false`, throw, type mismatch, unbounded count or uncalibrated alternative must be INCOMPLETE, not a comparable absence sentinel. `getUserPropBuffer` is kept raw rather than explicitly copied; detachment under mutation is unproved. |
| Dependencies | 552-593 snapshots outward refs and `refs.dependents` if traversal succeeds; 692-693 explicitly rejects other **nodes** sharing the base, and 701-714 restricts node census. It does not explicitly classify outgoing/incoming references against a proven construction-only set, or prove the subanim/reference walks equivalent, or disallow every pre-existing foreign **non-node** dependent. `refs.dependents` is materialized before the 128-item check; `pending` can grow before the 128-visited guard. A returned `undefined`, uncomparable reference, foreign dependent or incomplete list is INCOMPLETE, not an empty list. Cleanup's census/base-sharing guards do not separately establish absence of all non-node dependents. |
| Exact values and order | `freeze` copies many scalar/point/matrix/array values, but Point2/3/4, Color and Quat components are not individually checked for finiteness; VData/EData values are not run through `freeze`. Some direct arrays/buffers are retained without an explicit deep copy; value-type detachment and comparison must be proved. 699 calls `evaluatedSnapshot` **before** `graphSnapshot`, so an edited/unsupported controller, dependency or additional Shell property may be evaluated before that guard rejects it. Reorder only after preserving the complete checks; do not advertise evaluation as safely bounded yet. |

This table identifies read calls and missing *explicit* calls; an external SDK
page does not prove what the running bridge can access. An opaque baseline match
must not be presented as proof that all these independent fields were read.

## 2. What old evidence actually permits

* `Audit/_phase16-p3-runtime-probe-results-2026-11-02e.json:2-7,23` and
  `Audit/phase16-p3-runtime-probes-2026-11-02e/02_poly_state.ms` measured one
  four-vertex, one-face base: map count 0, `-2`/`-1` returned `false`, VData/EData
  counts 0, PRS `numKeys=-1`; some dead/flag/material/smoothing reads succeeded.
  There was no added-channel or keyed-descendant control. The fixture is not
  F01, and without changed-channel controls these outputs are not a general
  default, reliable absence proof or demonstrated detection capability. That
  particular script did not attach Shell or run the full runtime snapshot.
* `Audit/_phase16-p3-runtime-2026-11-02e.md:159-183` reports handle/ref-count
  success for particular node/base/Shell/PRS values and native `DummyClass`
  dependents; the layer interface rejected anim handles/ref counts. It did not
  classify the entire permitted graph or prove subanim coverage.
* `Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt:1-57`
  is actual later evidence: same/default layer comparisons and some detached
  typed reads, real/bogus controls; not a second layer, membership mutation or
  identity proof. Both `r4-r5-single-quad-readers.ms` and
  `r7-single-quad-readback-discriminators.ms` remain **prepared, not shown
  executed**. Their large multi-question form is not a substitute for independent
  bounded changed-state controls. The former's `n.position.controller` and similar
  forms are candidates, not verified controller access paths.
* `Audit/_phase16-p3-identity-probes-2026-11-02e.json:10-17` proves one measured
  conversion/handle round trip with exact cleanup, not universal identity
  continuity. Main03's layer failure/cleanup is in
  `Audit/_phase16-p3-main03-live-result-2026-11-02e.json`.

## 3. Main-only calibration protocol and interpretation

Before each call: freshly inspect scene, selection, file identity, units, dirty
flag, active layer and exact lease witness. Never touch Main03's retained lease.
The candidates below are **separate**, sequential, short main-thread calls; their
specific syntax, execution time and cleanup are unverified. Use one freshly owned
tiny node per call, normally an empty unnamed controlled scene with no selection;
enforce this admission rather than assuming it. Bind exact returned node/handle
immediately. On unexpected census, ownership, hierarchy or dependency ambiguity,
leave residue and report `INCOMPLETE_RESIDUE`, not guessed name-based deletion.
Always record cleanup, before/after census and selection, errors, dirty state and
timing. Deletion does not restore dirty/undo history; no flag clearing. A timeout,
bridge error marker, throw, untyped/ambiguous return, failed mutation or absent
control is INCOMPLETE, never `false`, `0`, empty, equality or success.

For **each individual field**, require:

1. **Positive:** repeat identical, detached typed reads of the exact produced
   object's field; compare actual runtime reader output as well as the independent
   observer. Demonstrate current Max time and unrelated guards remain unchanged.
2. **Mutated negative:** mutate just that field on an owned fixture; independently
   prove the mutation landed; require the *actual runtime reader* to differ or
   refuse before evaluated geometry. Check a control field stays fixed. A count
   change is not a substitute for a same-count value/association mutation.
3. **Unknown:** deliberately wrong-typed/unsupported reader or independently
   demonstrated unsupported state; verify named INCOMPLETE/refusal, not equality.
   Calibrate positive and bogus APIs in the same batch, recording throw separately
   from `undefined`. Do not rely on an out-of-range native index being safe.
4. Repeat on actual constructed F01-sized base and Shell once tiny-route behavior
   is established. The real emitted file, not a copied recipe, must then survive
   the contract's three no-op and targeted refusal gates. A candidate probe cannot
   substitute for that gate.

### A. Metadata channels — first feasible tiny calibration

`vdata-channel-control.ms` is a **prepared, unexecuted** one-node/one-quad/one-
Shell candidate. It uses documented, non-Autodesk-reserved VData channel 11,
checks clean count stability, adds support and compares two distinct values,
verifies an unrelated stored vertex/face count, tests a wrong-type unknown and
real/bogus properties, and deletes only the exact created node. It prints
individual results, not an acceptance PASS. It requires initially reported
VData channel count <=10 and refuses instead of changing a preexisting custom
channel. The fixture and Shell are owned; no layer, material, external node,
registry or user's scene data is changed intentionally. This tests a **subset**
of VData only, not the production snapshot or global metadata completeness.
Its cleanup checks identity, census, hierarchy and node-level base sharing, but
**cannot prove the absence of an unknown non-node dependent or callback**; main
must assess the controlled context and timing independently. Its census guard
is not a claim of universal isolation. A construction interruption/timeout,
lost exact node reference, unexpected neighbor or unverified cleanup remains
INCOMPLETE; handle-only adoption is refused during cleanup.

Follow with independent tiny tests for VData/EData support toggling and value
edits at existing supported channels (Autodesk reserves VData 1–10 and EData
1–2; use a non-reserved channel for generic custom controls), map 0/1 and each
admitted negative hidden channel, map face-index changes at fixed counts, and
non-finite/over-budget/failed-reader handling. Verify every requested channel
range, type and upper bound with calibrated controls. For vertices, faces,
edges, flags and selections, use the existing R7 design only as a starting point;
separate edits so an earlier failure cannot mask a target. Probe dead entries and
face-edge incidence explicitly. For diagonal mutation keep face vertices and
counts constant and separately observe the actual base triangulation; if only
evaluated triangles are visible, do not infer internal metadata equality.

### B. Specified normals — do not conflate a test instrument with the base

Autodesk documents `Edit_Normals` methods `GetNumNormals`, `GetNormal`,
`GetNormalID face corner`, `GetFaceNormalSpecified face corner` and
`GetNormalExplicit`; setters allow candidate specified/explicit mutations.
They are methods on an **Edit Normals modifier**, not an already verified
read-only interface to the current Editable Poly base. Documentation also says
topology operations/collapse can strip edited normals; therefore neither adding
the modifier to the production wall nor collapsing it is a safe replay reader.

Use a separate exactly owned disposable one-quad calibration, and at most one
additional modifier in that separate call. First show the instrument's unedited
corner/normal IDs, flags/vectors twice, then mutate only one corner's specified
state, and separately a normal's explicit flag/vector and same-value different
ID/sharing. Re-read with the modifier **as the positive independent instrument**;
compare `getNormal` and, separately, `meshop.getFaceRNormals` on a guarded
`snapshotAsMesh` with exact temporary-mesh disposal. Show a bogus/wrong-target
read becomes INCOMPLETE. Do not treat a caught error or unchanged computed normals
as proof there are no specified normals. This alone only calibrates the modifier,
**not base-state visibility**. A subsequent non-mutating base reader, or a
demonstrated supported absence predicate that detects a base-level normal state
after a known independently verified base mutation, is still required. If such
a mutation/reader is unavailable or collapses/strips state, record **INCOMPLETE**;
do not create a false negative or weaken the one-Shell production stack.

### C. Static controller descendants and permitted graph

For a separate owned tiny node + one Shell, record class/handle, `numKeys`,
`numSubs` and guarded `getSubAnim` paths for node transform/position/rotation/
scale/visibility and each relevant Shell parameter/param block. Independently
enumerate `refs.getReference` edges and compare the path sets; counts and names
alone do not prove coverage. First observe static composite and leaf keys. Then
make one key at an **off-current time** on an owned descendant while keeping the
current-time value and time unchanged; independently prove that leaf is keyed and
require the exact runtime graph guard to discover/refuse it. Separately replace
one controller, and test a parameter wire/constraint or scripted controller only
on owned tiny fixtures, with exact known targets and cleanup. Unsupported
subanim/handle/class, unresolved indirect dependency, unbounded traversal or any
missing detection => INCOMPLETE. `numKeys=-1` on the parent is not the result for
its descendants.

Record clean incoming/outgoing edges with identity, immediate/transitive meaning,
target class and role. Calibrate two distinct owned nodes: plain copy versus
shared-base instance, then an owned non-node dependent (for example a separately
owned controller reference or custom-attribute carrier), and a hierarchy edge.
Each mutation must be independently confirmed; all non-owned nodes must remain
untouched. Use separate calls/fresh fixtures if exact removal of an attached
non-node reference is not demonstrably safe. Count caps must be enforced *before*
expensive materialization where an API permits it; otherwise state the residual
resource limit. Establish a closed allowlist of internal references, including
observed native `DummyClass` roles, rather than accepting whatever existed at
baseline. Prove missing/unknown/deleted or uncomparable target => refusal. Never
replace one query's `undefined` with `#()`.

### D. Layer / other native node fields

Distinct-layer identity and typed changed-state calibration remains a separate
main decision: use only exact owned fixtures and an explicitly safe approved
layer; a pre-existing layer's state is not scratch space. With two distinct
layers prove alias equality, inequality both directions and node membership
change, then mutate only an **owned** layer's relevant flags with positive/unknown
controls and verify exact safe layer cleanup; if safe layer ownership/cleanup
cannot be established, remain INCOMPLETE without creating/changing one. Compare
required `pivot`, object offsets and matrix rows by independently measured
equivalence or distinct guarded readers. Prove copied user-buffer detachment
after an owned node edit. Required missing properties must refuse; a bogus
property is only an unknown control, never a normal baseline value.

**New documented candidate, not live evidence:** Autodesk documents the
read-only `LayerProperties.layerAsRefTarg`, returning the underlying layer's
`ReferenceTarget`. `layer-ref-target-readonly.ms` proposes testing this on
`LayerManager.getLayer 0`, with repeated access, known root handle roundtrip,
real/bogus property controls and guarded `getHandleByAnim`/`getAnimByHandle` on
the returned target. If a second layer already exists, it observes a distinct
target; if not, it reports the negative control INCOMPLETE and creates nothing.
This may provide a route around applying anim APIs to the interface *itself*, but
whether target handles round-trip, identify distinct layers, remain stable, or
track node membership must be proven in this build. A target alias alone is not
the layer-flag/state comparison, and the runtime may still encounter other
uncomparable references. The candidate makes no explicit scene/registry writes;
whether querying a target's anim handle causes lazy internal allocation is not
proved, so compare dirty state and treat its side effects as unverified. Review
and run only as a bounded, main-only diagnostic; it does not rearm/alter a lease
or make a construction/replay pass.

## 4. Source references used for candidate design (not live proof)

* Autodesk 2026 [`Edit_Normals` interface and behavior](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-9F33B780-7A98-4638-BD00-A1725FA1DB70): distinction among unspecified, specified and explicit and method signatures; also warns about Editable Poly/topology stripping.
* Autodesk 2026 [`getNormal`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-BD473113-389F-4C96-BE07-217FF75796EF), [`meshop.getFaceRNormals`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-EF78FA1A-A382-4BED-BA10-7C856A7551A5) and [SDK `MNNormalFace`](https://help.autodesk.com/cloudhelp/2026/ENU/MAXDEV-CPP-API-REF/class_m_n_normal_face.html).
* Autodesk 2026 [poly VData/EData/map methods](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-4EF4DCB1-AA96-48BF-9985-3518C53C8294), [face triangulation](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-A16CEBC5-E33D-415D-B1E3-AA97FDBEF9FA) and [SDK `MNFace`](https://help.autodesk.com/cloudhelp/2026/ENU/MAXDEV-CPP-API-REF/class_m_n_face.html).
* Autodesk 2026 [`numKeys`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-B1700B1D-B1EA-4A6C-B4A3-A29DB26C8C02), [`numSubs`/`getSubAnim`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-3F9BC35F-918C-46C6-8617-7DCDDD62FCE3), and [`refs` methods](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-95453E22-A022-4543-B31C-A052CECD3598).
* Autodesk 2026 [`LayerProperties.layerAsRefTarg`](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-78B79975-7BA5-4A03-8FEF-27E78D14B575) documents a layer ReferenceTarget; it does not certify this build's identity or handle behavior.

First live action suggested to main: **fresh read-only scene/units/selection/dirty
and exact retained-lease/witness inspection**, no rearm. Then inspect and, if
appropriate, run `layer-ref-target-readonly.ms`; it creates or deletes nothing.
Only afterwards, if the scene meets the VData candidate's explicit empty/unnamed
admission and main approves a disposable node, inspect and run that separate
control once. A result cannot change P3.1's acceptance status by itself.
