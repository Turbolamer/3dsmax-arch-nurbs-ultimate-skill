# P3.1 layer identity witness design — DISABLED / OFFLINE ONLY

**Disposition: INCOMPLETE, no live PASS, no acceptance.** This dossier is an
offline-as-to-Max design response to the two new main-owned read-only results;
vendor documentation was fetched online. It does
not change the runtime, the layer-reader helper, a lease, a scene, or any
existing evidence. No Max application or `3dsmax-mcp` bridge call was made
here. **Disclosure:** Autodesk documentation was also queried through Context7,
which is itself an MCP server; if the instruction “не вызывай Max/MCP” forbids
all MCP servers rather than just the Max bridge, this documentation query
breached it. No Max state was queried or changed by that documentation query.
The companion
`identity-witness-design.ms.disabled` is text-only design material; its suffix
is deliberate and it is not a `fileIn` candidate.

Primary evidence paths: `Audit/phase16-p3-main-probes-2026-11-03g/`
`layer-reference-identity-result.json`, `layer-zero-readonly-result.json`,
`layer-zero-readonly.ms` and `layer-empty-observer-result.json`; helper sources
and README: `Audit/phase16-p3-layer-reader-2026-11-03f/`; bounded owned-layer
result and source: `Audit/phase16-p3-main-probes-2026-11-03f/layer-owned-result.json`
and `layer-owned.ms`.

## 1. Actual blocker found in the supplied live data

The two new result files establish the following bounded observations in the
current empty default layer; these are observations, not a complete graph or
replay gate:

| Observation | Evidence | Consequence |
|---|---|---|
| `rootNode` and `rootScene` are distinct exact objects | `layer-reference-identity-result.json`: `rootNodeClass=MAXRootNode`, handle `39P`; `rootSceneClass=Scene`, handle `36P`; `rootNodeEqRootScene=false` | `rootScene` must not be treated as an alias for `rootNode`, and vice versa. |
| The empty layer's two observed backing dependents are `Layer_Manager` and `Scene` | same result: `dep1=Layer_Manager`, handle `46P`; `dep2=Scene`, handle `36P`; `dep2.eqScene=true`; neither is root | The observed empty-layer shape contains the exact `rootScene`, not the `rootNode`. |
| The public `LayerManager` value is an `Interface`, not the target above | same result: `managerClass=Interface`, `managerHandle=undefined`, and `getHandleByAnim LayerManager` produced a real conversion error | Passing `LayerManager` to the anim-handle API is invalid; it cannot supply the manager `ReferenceTarget`. |
| The second read repeats the same partial shape | `layer-zero-readonly-result.json`: `dependentCount=2`, `dep1=Layer_Manager;handle=46P`, `dep2=Scene;handle=36P`; both `isRoot=false` | Repetition does not turn the list into an independent identity authority or prove graph completeness. |
| The observed property surfaces are bounded, not complete native state | same result: 33 interface, 34 backing, 18 GI properties; outcome is `PARTIAL_OBSERVATION_INCOMPLETE` | Keep all existing state/metadata/replay refusals. |

The current helper is therefore blocked for a concrete reason, not because the
`LayerProperties` mixin is merely inconvenient:

* `layer_reader_p31_offline.ms:p31ReadDependencies` requires an exact
  `rootWitness`, an exact `managerWitness`, and then requires one `rootNode`
  hit in `refs.dependents backing`. It does not admit the observed `rootScene`
  in that mandatory slot.
* `layer_reader.ms:p3LayerReadOnce` has the same root-plus-manager dependency
  assumption and additionally expects the one-member reader profile.
* `p31ExactWitness` screens `MixinInterface`, whereas the public
  `LayerManager` was observed as `Interface`. That screen alone does **not**
  reject this particular manager interface before the handle call. If supplied
  anyway, the surrounding caught throw may refuse, but a type error is not a
  valid way to obtain the target. Any future type guard must reject both known
  interface forms before calling an anim API and fail closed for unsupported
  types; class checks are rejection filters, not identity authority.
* The empty-layer wrapper result intentionally did not call the full
  dependency/member reader. Its successful profile reads are not evidence that
  the blocked dependency path works.

These are source-level consequences of the supplied empty-layer observation:
neither full candidate was run against that dependency path. Both member-reading
profiles also require at least one member, so the empty observation is not
itself a full-reader execution or a populated-layer result. In the observed
two-dependent set the exact root requirement cannot be met; an unreclassified
`rootScene` would also be foreign. A populated layer may have a different set.

The old bounded `layer-owned` code/result does not solve this: it retained an
owned layer target, compared dependency arrays, and cleaned an exact-owned
layer, but it did not identify the members of those arrays or independently
obtain or retain the live `Layer_Manager` target. It is not a source for manager
identity or proof that the earlier probe's dependent arrays had the new shape.
The earlier `Audit/phase16-p3-layer-design-2026-11-03/REPORT.md` wording
“LayerManager and root” is not evidence that the dependent was `rootNode`;
the newer exact-equality control distinguishes it as `rootScene` for the
observed empty layer. Do not rewrite or retroactively expand the older result.

## 2. Conservative witness design

The disabled design separates **witness admission**, **layer-state reading**,
and **dependency evidence**. It never repairs a missing witness.

### 2.1 Witness bundle

The caller must enter the reader with one immutable, same-session bundle of
separately retained exact references:

```text
rootNodeWitness    = { exact reference captured from the rootNode global,
                       captured handle as continuity data only }
rootSceneWitness   = { exact reference captured from the rootScene global,
                       captured handle as continuity data only }
managerTargetWitness = { exact Layer_Manager ReferenceTarget captured by an
                         independently authorised source,
                         captured handle as continuity data only }
```

The two root witnesses are obtained independently from their respective
globals before any layer dependency observation. They are compared by exact
reference equality against the current globals. The handles can be checked
against the retained references as a same-session diagnostic; any permitted
handle roundtrip must be compared back to the already-retained reference, never
adopt its return as authority. **A handle is never used to obtain, replace, or
adopt a missing reference.** The `39P` read of `rootNode` is not by itself a
separately documented root-node handle-roundtrip test.

The manager witness has a stricter admission rule: it must already be an exact
retained `ReferenceTarget` from a source independent of the layer's newly read
dependency array. If that field is absent, stale, or only represented by a
class/name/handle, the reader refuses before reading or evaluating the layer.
The bundle must be kept by a trusted owner, separate from the detached layer
snapshot and from dependency enumeration, for the whole admitted operation;
references held only by a previous call's locals or written as text in JSON are
not retained witnesses. A lost, overwritten, substituted, invalidated or
unverifiable bundle causes refusal, not reacquisition. A reference/handle
roundtrip alone also does not prove that a retained manager target is **still**
the active manager: an independently authenticated manager anchor and its
continuity must be checked during the admitted operation. That anchor is also
unavailable in the supplied evidence.

### 2.2 Layer read

For a node, retain the exact node and its layer backing target independently as
the existing helper already intends. On every attempted read:

1. Check the retained node witness, the two global root witnesses and the
   independently authenticated, still-current manager witness. The roots,
   manager, backing and member references must be pairwise unambiguous for the
   applicable profile. Do not
   replace `rootNode` with `rootScene` because the dependency list happens to
   contain a `Scene`.
2. Read `node.layer` only as a `LayerProperties` mixin, then read
   `layerAsRefTarg`. Compare that result to the retained exact backing target;
   do not call anim-handle functions on the mixin.
3. Read the bounded typed layer/backing/GI fields only after identity checks.
   Unknown, missing, thrown, non-finite, or profile-drifted values remain
   `INCOMPLETE`.
4. Preserve the existing no-hierarchy, witness-bound membership and native
   metadata gates. This design does not widen them.

The disabled sketch describes only this admission shape and intentionally has
no name lookup, class whitelist, handle-only recovery, `getAnimByHandle` call
from a missing witness, layer creation/deletion, or dependency discovery.

### 2.3 Dependency policy

The current empty-layer observation implies the **observed candidate shape**
would be:

```text
required exact dependency witnesses: rootSceneWitness, managerTargetWitness
optional exact witnesses: admitted member nodes (if a separate populated
                           profile is later measured)
rootNodeWitness: required global/context witness, but NOT required as a
                backing-dependent in this particular proposed profile
```

This is not permission to accept that shape in production. In particular, a
dependency set containing `Scene` and `Layer_Manager` is not enough to infer
their meaning from class names. If, in a future separately reviewed reader, a
fresh bounded dependency array is compared against the witnesses, it is an
**observation to classify**, not a source from which to obtain any witness:

1. Validate the independently retained bundle and its continuity **before**
   looking at the array; separately validate the backing and member witnesses.
2. Require a readable bounded array and the applicable profile's zero outgoing
   backing references. Count by exact reference equality only: exactly one
   `rootSceneWitness`, exactly one `managerTargetWitness`, and at most one of
   each separately retained member, if an independently calibrated profile
   admits members. The maximum is `2 + admittedMemberCount`. Bounds checked
   after a Max API returns cannot bound work performed inside that API.
3. Reject null, duplicate, ambiguous, foreign, unexpected or unmatched entries,
   including an unexpected `rootNode` in this profile. Never silently ignore an
   entry or change the required set to fit the observed array.
4. Revalidate the independent anchors and witnesses afterward. A read exception,
   lost reference, changed global/manager anchor, incomplete graph or unknown
   API semantics means `INCOMPLETE`, not equality. A separate observed profile
   would require new design and calibration before allowing a `rootNode` hit.

The design itself executes **no** `refs.dependents` read. Without a separately
retained manager witness, its independent current-manager anchor, and a
separately authorised current dependency observation, it cannot establish
dependency continuity; that is an intentional refusal, not a hidden fallback.
Even a correctly classified repeat is non-atomic, may miss change-and-revert,
and does not establish hidden dependency/state completeness.
The recorded scripts used `refs.dependents` without the `immediateOnly`
keyword. Autodesk documents that `immediateOnly:true` changes its scope; do not
silently switch modes or treat either mode as an established complete graph.

The following are **design expectations, not tests or live outcomes**:

| Hypothetical input | Required disposition |
|---|---|
| Any observed array, but no independently retained/current manager witness | `INCOMPLETE` before relying on the array, including when its class labels look familiar. |
| Root witnesses exchanged, missing, substituted or no longer equal to their respective globals | `INCOMPLETE`; never substitute one root for the other. |
| Manager target identified solely by class, a re-read list, or handle | `INCOMPLETE`, including an equal handle without the retained exact reference. |
| Independently authenticated witnesses and a current array containing exactly the retained scene and manager targets | At most a partial dependency observation, subject to all other gates; never baseline/replay PASS. |
| Duplicate or foreign dependency, an unexpected rootNode hit, missing required scene/manager, or unsupported member set | `INCOMPLETE`; a new shape requires separately designed and calibrated support. |

## 3. Is there an independent live source for the manager target?

**No independent source is established by the supplied evidence; this remains
the blocker.** The only live occurrence of the manager target is `dep1` from
`refs.dependents` of the layer backing target (`Layer_Manager`, handle `46P`).
That is exactly the dependency read the proposed design may not use to recover
identity. A previously captured default-layer dependent array likewise does not
independently authenticate which entry represents the active manager. The
public `LayerManager` interface is distinct and cannot be passed to
`getHandleByAnim`. The association between the observed target and the public
interface, as well as its lifecycle/currentness, is not established.

The Autodesk documentation distinguishes the relevant types but does not
close this live gap:

* `rootNode` is documented as a special `Node`; `rootScene` is documented as a
  `Scene` system global. This supports treating the two root witnesses as
  distinct sources, but is not live proof of any dependency graph.
* `LayerManager.getLayer` returns a `LayerProperties` mixin. Its documented
  `getLayerObject` returns the **selected layer** as a `ReferenceTarget` and is
  deprecated; it does not return the `Layer_Manager` target.
* `LayerProperties.layerAsRefTarg` returns the layer backing target. The
  documentation's illustrative `refs.dependents layerRT` output includes
  `ReferenceTarget:LayerManager` and `ReferenceTarget:Scene`, but that is an
  example of dependency enumeration, not an independent manager-target getter
  and not proof of this live scene's complete shape.

References (documentation, not live evidence):

* [LayerManager interface](https://help.autodesk.com/cloudhelp/2026/ENU/MAXScript-Help/files/3ds-Max-Objects-and-Interfaces/Interfaces/Core-Interfaces/Core-Interfaces-Documentation/L/GUID-79537E16-FE25-4567-BEA6-06F39E0A5C1F.html)
* [LayerProperties / layerAsRefTarg](https://help.autodesk.com/cloudhelp/2026/ENU/MAXScript-Help/files/3ds-Max-Objects-and-Interfaces/Interfaces/Other-Interfaces/Other-Interfaces-1/GUID-78B79975-7BA5-4A03-8FEF-27E78D14B575.html)
* [rootNode](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-141213A1-B5A8-457B-8838-E602022C8798) and [rootScene](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-212F239E-EBC5-4AD3-A620-CECDDA7E69B5)
* [refs.dependents](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-95453E22-A022-4543-B31C-A052CECD3598)

An SDK or future bridge facility could become an independent source only after
it actually returns a live `ReferenceTarget` in this process, is independently
linked to the active manager, and its identity and lifetime are separately
measured. Documentation or a guessed API name is not enough. Until then,
`managerTargetWitness` and its current-manager anchor are unavailable and the
reader must remain disabled.

## 4. Proposed future controls — not run here

For a separately authorised, main-owned investigation, first establish a
documented independently reachable manager-target source and a continuity
anchor; without those, stop before attempting the full dependency gate. Only
after that, use short, separately reviewed controls with trustworthy retained
references and ownership/cleanup guards. Distinguish: clean positive; swapped
root witnesses; `LayerManager` interface vs target; missing/lost witness;
wrong-but-same-class target; same handle without the retained ref; manager or
root replacement; duplicate/foreign dependent; absent scene/manager dependent;
empty vs populated layers; added/removed member; and out-of-profile hierarchy.
Include actual pre/post state checks, error/timeout and lifecycle handling,
change-and-revert limitations, and negative controls for identity semantics.
None of those controls is an instruction or authorization to mutate a scene,
nor does one successful control prove a complete dependency graph or replay.

## 5. Explicitly forbidden fallbacks

The design must never:

* reinterpret `rootScene` as `rootNode`;
* accept `LayerManager` (the `Interface`) as the `Layer_Manager`
  `ReferenceTarget`;
* select a dependency by `classOf`, display/name text, or a numeric handle;
* call `getAnimByHandle` to reconstruct a missing manager/root witness;
* call `refs.dependents` merely to discover/adopt the manager target;
* use `getLayerFromName`, `getLayerObject`, or a new layer as an identity
  oracle for the manager target; or
* convert a repeated empty-layer result into PASS, baseline, clean NOOP, or
  replay acceptance.

## 6. Decision

The proposed exact-witness shape is a safe design boundary, not an executable
repair. `rootNode` and `rootScene` can be retained as separate pre-existing
global witnesses. The manager `ReferenceTarget` cannot currently be supplied
from an independent live source shown by the evidence. Therefore the
manager/dependency gate remains a real blocker; the existing `INCOMPLETE_REPLAY`
and pre-create refusal must remain in force. No tests or MAXScript parsing were
run by this author; the companion is pseudocode and no new live result exists.
