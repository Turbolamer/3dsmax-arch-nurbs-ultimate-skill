# Phase 16 P3.1 — bounded, fail-closed runtime contract proposal

Date: 2026-11-02e. **Design only; no implementation, Max execution or acceptance.**
Owner of this review changed only this new report. Main must decide the contract and
execute the probes. `CHECKPOINT.md` and `Audit/_phase16-p3-main-brief-2026-11-02e.md`
supersede the historical P2-unaccepted status in the earlier design proposal.

## 1. Recommendation and hard boundary

Adopt a deliberately small **armed, same-scene, same-Max-process lease**, not a
durable scene ownership system. First creation is allowed only in the freshly
inspected, explicitly authorized **empty test scene**. Produce exactly one wall
node, with one uniquely owned base object and one uniquely owned Shell. Subsequent
executions of the identical trusted artifact either:

1. read and prove the complete supported baseline, then return **NO_OP** without
   changing scene state or registry fields; or
2. return **REFUSED**, without repairing, retagging, rebuilding, deleting, hiding,
   selecting, changing layer/material/units, or adopting any node.

Never implement a replay replacement branch in this initial version. NO_OP is a
preservation claim, not new geometry acceptance. A generated file does not reset,
open or save a scene, create a layer/material/helper, or reconstruct lost ownership.
Allowing an initial empty scene does **not** establish coexistence with arbitrary
user scenes; that remains a later contract and gate.

**Do not claim arbitrary edit detection from mesh coordinates plus Shell amounts.**
The full supported readback below is a prerequisite. Missing/throwing/ambiguous
readback is REFUSED/UNSUPPORTED, not an unchanged state. Where complete state cannot
be bounded and measured, stop rather than weaken the promise. Some runtime APIs
needed for this contract are presently **UNVERIFIED**; §8 is the main-only probe list.

## 2. What constitutes the lease and ownership

### 2.1 Explicit arm operation; missing registry is never permission

The emitted `.ms` must **not** initialize a new ownership registry merely because
its global variable is `undefined`. Otherwise loss of the global and deletion or
retagging of the original wall become indistinguishable from a first run.

Proposed protocol, to be separately approved by main:

- Main explicitly arms a fresh, one-use lease after read-only inspection and
  permission for the particular empty scene, artifact and exact node name.
- Main retains the exact registry-instance reference in its outer local test
  harness as an independent witness. It checks that the global still equals that
  instance before every `fileIn`; this is additional evidence, not a name lookup.
- The file requires an existing, correctly typed/schema-checked ARMED or COMMITTED
  instance. `undefined`, a replaced struct, wrong schema, wrong artifact or any
  other state causes refusal. It never auto-arms on first or later load.
- A new explicit arm is not an automatic recovery command. Never re-arm over
  surviving nodes, after ownership ambiguity, or after a poisoned/failed attempt.
  Main resolves those situations separately without touching user data.

This means the `.ms` is a **standalone wall builder**, not a zero-setup arbitrary
session bootstrap. If zero-setup first execution is required, the registry-loss
guarantee cannot honestly be made by the missing-global heuristic; that is a
contract conflict for main to resolve, not a hidden fallback.

### 2.2 Registry contents (conceptual schema, not proven MAXScript syntax)

One global struct instance may contain the following bounded values. Struct
construction, reference equality and repeated `fileIn` scoping require probe R1.
Do not redefine/overwrite a global struct or helper during a refusal/no-op path.

| Field | Required meaning |
|---|---|
| schema/runtime version | Exact supported values, not loose property presence |
| state | ARMED, BUILDING, COMMITTED or POISONED; no implicit transition on replay |
| lease nonce | Fresh explicit caller-supplied opaque ASCII token for this arm |
| artifact identity | Project/run ID, exact namespace/name, canonical input fingerprint, generator/template fingerprint, expected unit pair and factor |
| scene witness | Main's retained registry reference; root-node reference if R2 proves its useful identity semantics; initial empty census and relevant scene context |
| owner nonce | Fresh explicit owner token, separate from readable node name |
| exact node identity | Live node reference and independently captured handle; handle lookup is only a cross-check |
| exact component identities | Actual base-object and modifier references, not only their class names |
| baseline | Detached typed scalar/array readback after successful creation and validation |
| attempt ownership | Exact references actually created in this attempt, captured immediately; never a wildcard query |

The lease/owner token is **not a security secret**. Tags, names and struct fields
are copyable. The trust boundary excludes deliberate hostile modification of the
registry, emitted code or harness itself. Ordinary manual node/property edits and
copied names/tags remain inside the refusal requirement. Without that distinction
no editable in-process registry can authenticate itself.

### 2.3 Node tag, name, handle and duplicate rules

- One emitted exact name and one canonical owner-tag buffer are readable evidence,
  **never authority to adopt/delete**. Avoid `getNodeByName` for ownership resolution.
- Enumerate the complete bounded node census first. Require exactly the expected
  registered node set on replay; an added node, including a differently named copy,
  causes refusal in this initial empty-scene profile. A foreign prefix-only node
  is left untouched; refusing the replay is acceptable conservative behavior.
- Compare all exact-name occurrences and every matching owner/node token. More
  than one, a token on a different live reference, an absent/malformed token, or a
  name mismatch causes refusal. Do not trust Max auto-renaming to prevent a copy.
- Require both exact live-reference agreement and handle round-trip agreement.
  A handle alone, a same-name replacement, a same-class replacement, or matching
  tags alone is insufficient. Handle persistence/reuse across sessions is not
  assumed. Preserve numeric handle type; do not decimal-format and reparse it.
- Retain actual base/modifier identities. A newly substituted but numerically
  equal base or Shell is still a manual edit and must refuse.

### 2.4 Session boundary, reset, load and merge

No save/load/merge durability is claimed. A lease ends at scene reset/open/new,
load/merge, Max restart, registry loss, failed identity readback or explicit
disarm. Main must not carry its witness across those operations. A reset/load
deleting or replacing the recorded live reference refuses; an added merged node
refuses by the exact census. Saving to a different path may conservatively refuse
if the scene-context comparison observes it; saving does not authorize rebuilding.

There is no presently proven native session/scene UUID in this review. **Do not
invent one, or use file path, `objects.count`, root name or PID as such a UUID.**
Root-reference stability and invalidation are UNVERIFIED until R2. Automatic
detection of every possible load/merge event needs separately calibrated lifecycle
notifications; until then the admitted protocol is the uninterrupted, no-yield
main-owned test session, with no such operation between calls. Outside that
protocol return UNSUPPORTED, not a durable-ownership PASS. An operation that leaves
all observed state unchanged cannot be inferred merely from its absence in a
snapshot. The initial test must not save/load/merge user files to explore this.

## 3. Artifact and equality contract

The emitter can deterministically hash canonical consumed input bytes plus its
template/generator version and expected unit pair. Store those identities in both
the artifact and registry. They bind the selected generated recipe, not live state.
Main should retain and check the **whole emitted file SHA-256 externally immediately
before each `fileIn`**, using the immutable published file in the bounded test.
An embedded self-declared digest does not prove the code being executed is that
digest; no recursive whole-file self-hash or unproven .NET serializer is necessary.
If execution must authenticate bytes itself later, that is another measured API
and path-race contract, not something solved by a literal fingerprint field.

For replay use **typed component-by-component exact equality** on supported
readback, not `as string`, printed coordinates, JSON round trips, volume/bbox alone
or a collision-prone ad hoc rolling hash. Geometry acceptance tolerances are not
replay tolerances: a changed representable coordinate must refuse, even if it is
within a modelling tolerance. Exact equality of readback does not prove that a
sub-Float32 edit existed before storage. Treat NaN/non-finite/unreadable values as
refusal; never let an unsuccessful comparison default to equal.

Point/matrix/array values must be flattened into detached scalar copies; storing
a reference to a mutable matrix/array/controller as the baseline can let an edit
alter both sides. Runtime identity checks use retained live references; mutable
parameter comparisons use scalar copies. R1/R4 must distinguish those two cases.
A hash of the typed baseline may be useful for logs only after the actual complete
comparison; it is not a replacement for it.

## 4. Required baseline/readback and fail-closed restrictions

The baseline is read **after** construction, unit checks, stack/geometry checks and
owner-tag write; then compared immediately with a second read. Do not derive the
baseline solely from manifest predictions. The following is the proposed supported
state, not a claim that every candidate property/API already works.

| Category | Compare or strictly disallow |
|---|---|
| identity and scene | Exact node/base/Shell references, handles, exact name and owner buffer; entire expected node set; expected units type **and** scale and factor |
| transform and pivot | All scalar components of node and object transforms, position/rotation/scale, object-offset position/rotation/scale and pivot; controller identities/classes and supported static values |
| base geometry | Base class/reference; live/dead V/E/F state; every vertex coordinate, edge endpoint/incidence, ordered face loop, winding, per-face smoothing and material IDs, edge visibility/flags and supported crease/weight data |
| extra geometry state | Map/UV/vertex-color channels, selections/subobject state, explicit/specified normals and custom per-component data: either exhaustively read and compare, or prove absent in the created supported base and prove an addition is detected; unknown state is not ignored |
| evaluated geometry | Non-scene `snapshotAsMesh` readback: ordered vertices/triangles and available face attributes; independent topology/volume/direction QA remains separate. This cannot stand in for the base-state comparison |
| stack | Exactly one Shell, exact modifier identity/order; `innerAmount`, `outerAmount`, verified `segments`, all other editable Shell parameters and enable flags at relevant viewport/render levels; animated/wired/scripted/custom attributes forbidden |
| material | Initially `undefined` and must remain `undefined`. Any material assignment refuses; do not construct/serialize arbitrary materials to inspect them |
| visibility/display/render | Node hidden/frozen/renderable state, visibility value/controller and relevant visibility-inheritance/display/shadow flags; strict baseline of the relevant layer's state as well |
| layer | Exact original layer reference/name and supported relevant layer flags. No layer creation or reassignment by builder. Initial admission requires the approved ordinary layer state; moving the wall or changing layer state refuses |
| hierarchy | No parent other than the proven root convention and no children; compare actual references, not parent/child names. Parent, group/container membership or child additions refuse |
| user properties | Exact complete raw user-property buffer, including the canonical owner fields. Added, removed, changed or reordered text refuses; no attempt to normalize or restore it |
| dependencies | No other node may instance/reference this base/modifier or depend on the wall; no constraints/wires/animation, external references, custom attributes or unknown dependency targets. Compare calibrated dependency readback to the known construction-only set |

**Two levels must not be confused:** the transform/material/user-buffer and known
Shell readbacks are a small achievable first probe set; the mesh metadata,
controller and dependency completeness are additional gates. `getPropNames` alone
does not establish complete state: it can omit subanims, custom attributes,
subobject data and hidden interfaces. A long list of successfully read properties
does not prove that nothing else is editable. Generic plugin serialization is not
part of this recommendation.

If the base-geometry metadata cannot be completely covered with a bounded reader,
main may test a **sticky edit monitor** as additional evidence, not a shortcut:
arm before creation/baseline, mark the lease dirty on any relevant node/base/stack
change, and never clear it on replay. Callback event names, registration semantics,
delivery/queue flushing, undo/redo and removal are **UNVERIFIED** here. Such a
monitor is not accepted until all listed edit classes discriminate against a clean
no-op; a lost/unregistered monitor must itself refuse. Do not add callbacks to the
first implementation based on guessed API names. If neither complete supported
readback nor a calibrated conservative monitor is available, arbitrary edit safety
is **INCOMPLETE**, and broad F07 acceptance must remain blocked.

The guarantee is about an **observable changed state at replay entry**, not a
forensic proof that no edit-and-perfect-revert ever happened. Detecting history
would additionally require the proven sticky monitor; do not silently claim it.

## 5. Execution state machine and zero-write refusal

All checks on a replay are read-only. Do not rename/retag the node, reassign even an
equal amount/material/layer, update a replay counter, call `update` to repair it,
convert/collapse it, or create a temporary scene clone to fingerprint it.

1. **Entry, no writes:** require explicit live lease and external witness, identical
   artifact recipe, valid runtime schema/state, expected units/context and bounded
   full census. Refuse on any reader error or unsupported session state.
2. **COMMITTED:** validate exact identities/duplicates, full supported baseline and
   dependencies. Equal => NO_OP. Different/unknown => REFUSED with named category;
   no mutation of scene **or registry**. Changed input => REFUSED, never rebuild.
3. **ARMED:** require still-empty scene, unspent exact name/owner, approved default
   environment and budgets. Immediately repeat critical guards. Only now set
   BUILDING and create; this is an authorized creation branch, not replay.
4. Capture each created exact reference immediately. Prefer a directly created
   Editable Poly **only if R3 proves it constructs as the expected node**. Otherwise
   retain the P1 `Editable_Mesh` → `convertTo` route, but only after R3 proves exact
   identity reacquisition without a name-only lookup. Store every returned vertex/
   polygon ID; perform deletion once with those actual IDs; add only one Shell.
5. Read and verify the full baseline twice, source-bound geometry/stack/direction,
   census, absence of dependency surprises and unchanged surrounding context.
   Commit the exact identities/baseline as one logical registry state transition.
   No COMMITTED state exists if any check is incomplete.
6. On construction exception, attempt bounded cleanup under §6, mark POISONED and
   return FAILED_CLEAN or INCOMPLETE_RESIDUE. No automatic second construction on
   the next `fileIn`. Parse failure, timeout, crash, interrupted execution or a
   BUILDING registry found later is INCOMPLETE, not assumed rollback.

There is no arbitrary-race guarantee against user scripts/plugins executing during
the operation. The admitted initial harness is sequential, on Max's main thread,
no yield/message pumping and no concurrent Max calls. No `Reset`, save, autoBackup
access, global Undo/redo, selection manipulation or scene-wide property setter.
Undo wrapping is not proof of transactional rollback. Global helper replacement or
callback registration on every `fileIn` would also violate the zero-write design.

## 6. Cleanup: exact created references, never discovery by prefix

Successful replay never cleans anything. On an initial construction failure or
explicit test teardown, cleanup is limited to the nodes actually created by that
attempt and recorded as exact references. Since only one wall node is admitted,
there is no hierarchy traversal/deletion loop to justify.

- Verify live identity and handle cross-check again; verify no foreign dependents,
  parent/child attachments or unexpected instance sharing appeared. Do not repair
  those relationships to make deletion possible.
- Delete the exact created live node only. Verify that exact node is no longer in
  the fresh census and that no unknown node disappeared. Do not delete a material,
  layer, user sentinel or another node sharing a prefix/token/name.
- P1 specifically measured that `convertTo` can invalidate the old reference.
  Deletion by the original preconversion reference is therefore not sufficient;
  P1's name-based workaround is **not** an ownership solution. If R3 cannot prove
  handle/reference continuity or another exact reacquisition, do not enter that
  production route. On unexpected loss of identity, leave an explicit residue
  report for main instead of searching by a name and deleting what it finds.
- Non-scene mesh snapshots need their own proven in-memory disposal in a guarded
  block. They must never become scene nodes merely to simplify measurement.
- If an external dependency is found, cleanup fails closed with INCOMPLETE_RESIDUE;
  main decides next action. It must not delete the foreign dependency to continue.
- Deleting temporary test data changes scene dirty/undo history. Do not assert that
  an initially clean scene's complete history is restored, clear its save-required
  flag, save it, or use reset to make a preservation check pass.

## 7. Suggested initial operational ceilings

These are **proposed caps, not measured performance facts or new wall grammar**.
They supplement, never replace or enlarge, the input's three declared budgets.

| Resource | Initial maximum / policy |
|---|---|
| scenes/leases/walls per run | One explicitly armed test scene, one lease, one wall node |
| stack | Exactly one Shell; no other modifiers and no modifier ladder |
| admitted geometry initially | Calibrate one quad, then the measured F01-sized 24-vertex/15-grid-face case; only after timing evidence admit the larger ceilings below |
| larger bounded subset | At most four disjoint rectangular openings; at most ten unique `u` and ten unique `v` stations, 100 generated vertices, 81 grid quads; unsupported contact/returns/corners still refuse |
| evaluated mesh | At most 1,024 triangles and bounded vertex/attribute counts; compare prediction and actual independently against both this cap and spec ceilings |
| readback | Bounded base arrays plus evaluated mesh; no scene clone, no recursive arbitrary-plugin walk, no generic controller/material serializer |
| scene enumeration | Initially 0 before creation / exactly 1 on clean replay. Refusal tests may add a small number of exact test sentinels; enumerate their bounded set, refuse and preserve all of them |
| user properties | One small ASCII owner buffer; cap raw readback, e.g. 4 KiB. Larger/unknown state refuses without rewriting it |
| execution time | Target under 1 s locally; hard operational goal under the standing ~2 s main-thread limit per call. Measure before increasing a cap. Count limits do not establish time safety |
| repeated execution | Exactly three identical-artifact executions as the initial positive replay test; clean/no-op evidence must include exact identities and full readback |

Read cheap identity/class/stack/count guards **before** geometry evaluation or
building large arrays. A changed base above the admitted base-count caps refuses
before `snapshotAsMesh`; an added/replaced modifier refuses before its evaluation.
Propose a hard scan cap of 16 scene nodes and no more than 256 evaluated vertices
for this small profile. Over-cap census is an immediate refusal, not permission
to walk or serialize an arbitrary scene. Any map/controller/dependency reader also
needs a fixed count/depth cap; exceeding it is UNSUPPORTED. These limits are to be
proved with a cheap discriminating count reader before relying on their runtime
protection, rather than constructing a huge intermediate collection to count it.

For flat quad surfaces without extra Shell subdivision, `12 × active_quads` is a
conservative combinatorial triangle upper-bound candidate (two surface copies,
plus up to four two-triangle boundary strips per quad), **not an already measured
guarantee about every Shell parameter/default**. R5 must lock/read all parameters
that affect tessellation; actual count exceeding any ceiling fails.

Do not impose an arbitrary coordinate magnitude and call it a precision proof.
Separately reject any emitted stations/offset surfaces that collapse or become
indistinguishable under the actual supported Float32 path relative to the input
numeric epsilon. Geometry precision, replay exactness and execution time are
different gates. A timeout is INCOMPLETE: main diagnoses with the permitted cheap
bridge status check, never immediately retries the mutating file.

## 8. Main-only calibrated API probes, in dependency order

**None of these probes was executed by this review.** Known-positive geometry APIs
are selected from `Audit/EVIDENCE_2026-10-27.md` E-11–E-15: `Editable_Mesh`, conversion,
`polyop.createVert/createPolygon/deleteFaces`, `update`, Shell attachment and
`innerAmount/outerAmount/segments`, V/E/F/incidence queries and non-scene mesh reads.
P1 proves that geometry route, not registry, handles, full metadata or session
semantics. `isProperty/getProperty`, `classOf`, `try/catch` and error reporting are
the calibrated probe mechanism recorded in `AGENTS.md`.

Use a fresh authorized empty test context and tiny fixtures, one short batch per
question. Each must have a clean positive, a discriminating changed/absent case
and a bogus control where meaningful. Record returned type/value and throw
separately. Do not string-cast matrices/references to test existence. Every
uncertain expression below is a **candidate to probe**, not approved syntax/API.

**Tiny property-probe template (UNEXECUTED):** use one candidate per call, here
`#layer`, alongside `#name` and a bogus name. It does not claim the candidate exists
or serialize its value. It creates/deletes only its exact fresh Box reference;
main must inspect raw output and cleanup before continuing. API-specific edits and
changed-value comparisons in R4/R5 are still necessary after this existence probe.

```maxscript
(
    local n = undefined
    try
    (
        n = Box width:1.0 length:1.0 height:1.0
        for p in #(#name, #layer, #P16BogusPropertyXYZ) do
        (
            local present = undefined
            local v = undefined
            local threw = false
            try (present = isProperty n p; v = getProperty n p)
            catch (threw = true)
            print ((p as string) + " present=" + (present as string) +
                " threw=" + (threw as string) + " undef=" +
                ((v == undefined) as string) + " type=" + ((classOf v) as string))
        )
    )
    catch (print (getCurrentException()))
    if n != undefined do
    (
        try (delete n)
        catch (print ("CLEANUP_INCOMPLETE " + (getCurrentException())))
    )
)
```

The code is a proposed test body, not a new verified MAXScript construct. `#name`
must be a readable positive and the bogus property must not become a readable
real field; a uniform all-throw result establishes no candidate absence. For a
function/handle test, use the analogous tiny known Box, alias, independent Box,
and absent/bogus candidate cases described below; do not promote mere global-name
resolution to a claim that invocation or identity semantics work.

### R1 — struct/session registry and detached baseline

- Candidate: a uniquely named struct instance held both globally and by an outer
  local reference, tested through two/three tiny `fileIn` calls. Confirm the file
  can read it without redefining/resetting it, and exact alias comparison differs
  from an independently constructed equal-valued struct. Test global `undefined`
  and wrong-type replacements cause refusal without registry initialization.
- Candidate field read mechanism: `isProperty r #state` then guarded
  `getProperty r #state`; compare a real field, a bogus field and a non-struct.
  Do not infer struct identity from equal field values or class display strings.
- For `point3`, matrix rows and nested arrays, capture typed scalar copies, mutate
  the original test value and confirm baseline stays unchanged while a fresh read
  differs. Confirm repeated stable reads compare equal. No serializer required.

### R2 — exact node/reference/handle and scene witness

- Candidates: `isValidNode n`, `getHandleByAnim n`,
  `maxOps.getNodeByHandle h`, `rootNode`, `rootNode.children`, exact node `==`.
  On a tiny known Box, alias and round-trip must identify the same live node;
  an independent same-shaped Box must not. Invalid/deleted-reference and missing
  handle tests must discriminate without adopting another node.
- Enumerate known visible and hidden temporary nodes and compare with a recursive
  root census. A group/child probe, if needed, is its own bounded batch; do not
  assume `objects` alone includes every special/XRef/container case.
- Confirm rename does not turn a different node into the registered reference.
  No load/reset/save test is required for this initial lease. Root lifetime across
  such operations remains explicitly unproven.

### R3 — safe base construction and conversion identity

- Candidate direct `Editable_Poly()` construction: report return class,
  node-validity, census change and one-quad `createVert/createPolygon` behavior.
  Calibrate against P1's `Editable_Mesh()` and a bogus constructor. Never claim
  constructor absence from one failed call shape or introspection result.
- Separately on one empty temporary mesh, capture exact node/reference/handle,
  call P1's `convertTo`, then compare its return, old-reference validity, new exact
  census and handle round-trip. Determine whether a trustworthy exact reference
  survives or can be reacquired. No `getNodeByName` recovery is an accepted result.
- If neither direct construction nor exact conversion recovery is proven, stop
  emitter implementation at this dependency. Leave uncertain residue to main;
  do not broaden cleanup to guess an owner.

### R4 — node state, user-buffer and layer readers

- For each candidate node property, use one known real property (e.g. `#name`), the
  candidate and a unique bogus property with guarded `isProperty/getProperty`.
  Candidates include `#transform`, `#objectTransform`, `#objectOffsetPos`,
  `#objectOffsetRot`, `#objectOffsetScale`, `#pivot`, `#material`, `#layer`,
  `#parent`, `#children`, `#isHidden`, `#isFrozen`, `#renderable`, `#visibility`
  and relevant display/shadow/inheritance flags. Exact scalar/row access and all
  additional flags required by §4 must be proved individually before use.
- Candidate `getUserPropBuffer n` / `setUserPropBuffer n text`: clean empty read,
  small owner write/read, extra unrelated key, changed owner and copied buffer.
  Require exact complete raw-buffer comparison; a single `getUserProp` is not enough.
- Layer reference identity, readable state and membership are UNVERIFIED here.
  Use existing verified `lyr.addNode n` only for an explicitly approved tiny layer-
  movement negative control; avoid creating a layer if a safe existing test layer
  is not available. Do not run an unsupported layer assignment guess on the wall.
- Candidate controller/subanim readers are UNVERIFIED. Enumerate only the bounded
  known static node/Shell controller tree and prove replacement/one-key edits are
  detected; otherwise animated/wired state cannot receive a clean replay PASS.

### R5 — complete supported base, Shell and evaluated-state readback

- Start with P1's one-quad poly and one Shell; repeat unchanged reads. Candidate
  `polyop.getVert`, `polyop.getFaceVerts` and the per-element metadata readers must
  each distinguish a known changed vertex/loop/flag from the clean fixture.
- Counts/incidences alone are not enough. Calibrate vertex movement, face deletion,
  same-count rewiring/winding, material ID, smoothing, edge/selection metadata and
  map-channel addition/change. Use the actual API names proved in the batch; names
  for those extra metadata operations are intentionally not invented here.
- Candidate `getPropNames shell` plus guarded property reads can discover a bounded
  parameter list, not certify its completeness. Prove the full chosen Shell
  parameter/enable/controller contract; specifically change a parameter other than
  the three known dimensions and detect it, or leave that completeness unaccepted.
- Probe `snapshotAsMesh`, `getVert`, `getFace`, `getNumVerts/getNumFaces` and disposal
  of the returned **in-memory** mesh. Known geometry behavior is not proof that
  every auxiliary face/normal/map attribute is captured by those four readers.

### R6 — dependency isolation and dirty-monitor feasibility

- Candidate `refs.dependents` / `refs.dependentNodes` and any selected instance
  query are UNVERIFIED for this use. Compare the clean base with a known second
  node sharing that base (`copy` then `n.baseObject = src.baseObject`, verified
  construction pattern), and a plain nonsharing copy. Record actual return kinds,
  internal vs foreign references and conservative allowed-set comparison.
- Hierarchy, material/controller/custom-attribute dependencies require their own
  tiny targeted positive/negative cases, not a conclusion from the sharing probe.
  Stop if a bounded complete supported dependency reader cannot be demonstrated.
- Only if needed after the baseline probes: research and calibrate a sticky node-
  change monitor on these tiny fixtures. Do not register guessed notifications,
  callbacks or persistent globals in production. Registration loss, delayed events,
  undo/redo and all requested edit classes must be negative controls before a
  monitor can support an unchanged-state conclusion.

### R7 — actual emitted-file replay/refusal and construction-failure cleanup

After the API prerequisites pass, run the actual frozen emitted file, not a copied
recipe, three times under the same retained lease. Expected statuses:
`CREATED, NO_OP, NO_OP`; all exact references and detached state equal after runs
one/two/three. Verify selection, layer, user properties, units and scene state
remain unchanged on no-op, not merely node count and volume. In particular compare
the save-required/dirty-state readback across each no-op and refusal; do not clear
it to manufacture equality. Undo-history restoration is not claimed.

Use a separate clean lease/fixture per mutation or restore it only through explicit
test-harness ownership. Before each replay capture the **already edited** scene,
then require REFUSED and identical post-attempt state. Controls:

1. transform and pivot/object-offset edits;
2. vertex movement and a same-count topology/metadata change;
3. material assignment;
4. Shell amount/other parameter/enable change, and Shell/base replacement;
5. hide/freeze/visibility/renderability and relevant layer-state/membership changes;
6. parent/child attachment;
7. extra/changed/removed raw user-buffer text;
8. rename and a distinct node with the conflicting exact name;
9. copied owner tag on a differently named node, and a base-sharing instance;
10. lost registry, wrong schema, replaced registry, wrong source fingerprint or units;
11. changed input with untouched scene, and foreign prefix-only neighbor;
12. injected exception immediately after node creation, after conversion, after
    face construction, after Shell and before commit. Cleanup must remove only
    exact created references or honestly report INCOMPLETE_RESIDUE.

An early registry failure must not mask a geometry-readback test: each targeted
mutation has a clean same-lease positive and all unrelated guards valid. The
foreign-neighbor negative intentionally exercises the census guard, separately
from the ordinary single-node edit tests. Never use fabricated output/echo to
turn unimplemented QA gates into PASS.

## 9. Main's minimum go/no-go decision

Proceed to new-file implementation only after approving the explicit arm/lease
restriction, supported-state extent and caps, and after R1–R6 establish every API
actually used by that implementation. First acceptance is only bounded F01-sized
creation plus **observably unchanged-state** replay in that lease, with targeted
edit refusals and exact cleanup evidence. Durability, arbitrary user scenes,
edit-history forensics, return/corner integration and broad F07 completion are
not inherited from that result. Any missing reader, identity continuity or safe
time bound leaves the relevant gate INCOMPLETE; it is not grounds to delete,
normalize, bypass a guard or claim the emitted file alone is done.
