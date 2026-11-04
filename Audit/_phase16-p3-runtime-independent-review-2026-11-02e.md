# P3.1 independent runtime source review — 2026-11-02e

**REVIEWED IN PROGRESS; NOT LIVE ACCEPTANCE.** Scope: new
`scripts/wall_surface_runtime.py`, against the approved explicit arm/one-use lease
and the runtime design §4. No Max calls and no source edits by this reviewer.
The earlier design report is preserved unchanged. Only this report and the
additionally assigned `Audit/phase16-p3-state-probes-2026-11-02e/` were authored.

## Frozen observations and verdict

Runtime author was actively editing during this review; results are explicitly
snapshot-specific. The latest complete read reviewed here is **820 lines**, SHA-256
`d88ac5daf0098efca9fd6befca51ad4cab8b83ed74089e2f443f5cce93268792`.
An independent Python `-B` AST/read-only source check on those bytes parsed
successfully and confirmed bytes unchanged during that check. This proves Python
syntax/source structure only, not MAXScript execution or API behavior. Earlier
720/762-line findings were reconsidered after active changes; they are not silently
represented as defects in these newer bytes.

**Correct fail-closed disposition:** lines 699–703 explicitly refuse even when the
bounded observed baseline is equal, with `INCOMPLETE_REPLAY`; first creation logs
`P3_CREATED_UNVERIFIED` and `replay=INCOMPLETE_METADATA` (781). Consequently there is
**no supported clean NO_OP replay yet**, and broad F07 stays blocked. This is
honest incompleteness, not an observed false successful replay. Keep that final
barrier until the concrete coverage/operational issues below are resolved and
the actual artifact has discriminating live evidence.

## Targeted actual-source findings

### R-1 — required missing property becomes an accepted baseline value

**Source fact, latent coverage gap while replay remains blocked.** In
`nodeSnapshot`, lines 641–648 list relevant transform/visibility/layer state but
use `if isProperty ... else #("absent")`. Two unavailable reads therefore compare
equal. This contradicts treating a required unknown reader as unsupported. A
misspelled or differently exposed property does not throw and need not stop first
baseline commitment. `properties node.layer` and the generic graph may expose
some equivalent values, but the source does not prove that equivalence.

Bounded repair: distinguish explicitly required properties from optional,
proven-inapplicable properties. Require a working read or calibrated equivalent
for each required state; do not make arbitrary optional Max properties mandatory.
Use the prepared real/bogus property probe to establish the actual exposure. The
source evidence is the `else #("absent")` branch itself; a live false no-op has not
been demonstrated and is currently prevented by the final refusal barrier.

### R-2 — controller/Shell/dependency safety is checked after mesh evaluation

**Source-order fact with an unmeasured operational consequence.** Line 654 builds
`polySnapshot ..., evaluatedSnapshot ..., graphSnapshot ...`; the evaluated reader
calls `snapshotAsMesh` (611) before the graph enforces controller class/key/custom-
attribute restrictions (531–548). The early Shell check only guards class, count,
inner/outer amount and segments (638–640), not every other tessellation/state
parameter. Known baseline equality is checked only after `nodeSnapshot` returns.

Thus a replay attempt can evaluate a manually changed/wired/scripted controller
or unsupported Shell state **before** rejecting it. A final unconditional replay
refusal does not undo evaluation or guarantee bounded runtime. This is not a claim
that a particular controller already executed malicious code or caused a hang.

Bounded repair: run the cheap exact-reference/class/count/controller/custom-
attribute and supported Shell-parameter comparison before evaluated geometry.
Refuse an unknown state before evaluation. Calibrate actual controller-tree
coverage; do not demand an arbitrary-plugin serializer. Keep timing unaccepted
until the actual bounded sequence is measured.

### R-3 — generic graph readback is not yet proven static/dependency isolation

**Source fact plus explicit evidence gap, not an API-absence claim.** The graph
allows `numKeys == -1` as well as zero (546), discovers outgoing targets recursively
and snapshots dependents (548), but does not explicitly classify every target as
part of the expected clean construction-only graph. Property enumeration alone
does not establish complete native subanim/metadata coverage. `-1` must not be
called proof of no animation without the supported composite-controller positive
and keyed-descendant negative. A dependents snapshot is useful drift evidence;
it is not itself proof that an already present foreign non-node dependent was
disallowed at first baseline construction.

For this admitted empty controlled scene, capture and calibrate the small normal
reference graph, restrict unknown target classes and prove controller descendants
are reached. Check a known changed node/controller/reference target independently.
No save/load/merge durability or unbounded reference security guarantee is needed.
If a complete bounded permitted graph cannot be shown, retain INCOMPLETE replay.

### R-4 — remaining raw/detached/budget checks need calibration

- `getUserPropBuffer node` is inserted raw (653), whereas `freeze` explicitly copies
  strings elsewhere (490). Verify its returned string is detached under a manual
  user-buffer change or copy it explicitly. No alias leak is asserted without that
  test. There is also no explicit raw-buffer size cap before this readback.
- `referenceSet` (511–515) materializes all supplied dependents without its own
  count cap. The visited/outgoing graph caps do not bound this incoming list.
  A fixed small count gate or refusal is enough for this profile.
- Snapshot equality covers material IDs, smoothing and edge visibility in the
  **evaluated** mesh (618–619), with normal reads (617), but the author correctly
  does not equate this with specified/native base-normal completeness. Preserve
  that qualification; a same-coordinate/same-count metadata edit is an important
  targeted negative before opening NO_OP.

These are bounded-contract issues, not a request to serialize arbitrary material,
layer, plugin or native scene state. Material is intentionally required undefined.

## Safety improvements confirmed in the reviewed newer bytes

- Arm refuses an existing reserved global (389), checks units and empty/unnamed
  context, and publishes a struct witness; missing registry on wall entry refuses
  before node creation (682). Runtime does not auto-arm or adopt by name.
- Exact references/anim-handle round trips, actual returned geometry IDs, exact
  single-node census and raw owner-buffer comparison are present. Copies/conflicting
  neighbors conservatively refuse via census and are not deleted on replay.
- Mesh snapshot disposal is now guarded in both success/error paths (605–632).
  The earlier absence-of-disposal observation is **superseded**, not a current bug.
- Construction-error cleanup now checks exact captured handle, single-node census,
  parent/children and base sharing before deletion (794–805). Earlier direct-delete
  criticism is **superseded**. Non-node foreign-dependency completeness is still
  covered by R-3, not inferred from node census alone.
- Main's exact external struct witness check remains part of the approved protocol.
  The file reading a newly supplied struct is not an independent authentication
  mechanism; this is acceptable within the explicit trusted one-use harness and
  is not a reason to demand a security secret or durable scene UUID.

Main's supplied raw R1 and conversion JSONs were read: R1 discriminates alias vs
independent struct, undefined/wrong type and detached scalar; conversion confirms
one measured exact returned Poly/handle path and cleanup. Those narrow proofs
do not settle the metadata/controller/dependency issues above.

## Prepared next actions, not executed evidence

- `Audit/phase16-p3-state-probes-2026-11-02e/r4-r5-single-quad-readers.ms`
- `Audit/phase16-p3-state-probes-2026-11-02e/r7-single-quad-readback-discriminators.ms`
- Companion `README.md` records restrictions and expected interpretation.

Each candidate file uses at most one owned temporary node, four vertices, one
quad and one Shell, calibrated real/bogus property reads, per-target throw reports
and exact-reference/handle cleanup. No material/layer construction. R7 is reader
discrimination, **not** emitted-file three-run acceptance; neither file has been
executed or timed by this reviewer. Main must inspect every throw and cleanup
result before using a reader. Later runtime edits require final stable-source
review; this moving-source review is not that final gate.

## Main-supplied live layer finding and focused follow-up

Main subsequently reports its corrected01 probe **actually threw** when applying
`getHandleByAnim` and reference APIs to `LayerProperties` (`MixinInterface`), while
layer properties were readable. This is supplied main evidence, not a live call
by this reviewer; the exact raw corrected01 file was not reread here.

This makes the reviewed runtime's layer handling a concrete construction blocker:
`explicitNames` includes `#layer` (646), `freeze` sends non-listed classes to
`exactRef` (502), and `exactRef` calls `getHandleByAnim` (473). A readable Layer-
Properties value therefore reaches an API now known to throw for that value;
generic `graphSnapshot` may also reach a layer interface through its reference
walk. Do not route a MixinInterface through the anim-handle fallback or hide its
failure behind an absent-value sentinel. Use an explicitly measured bounded layer
comparison/readback policy, or fail unsupported. The current final replay barrier
does not make successful first baseline construction possible through this path.

Prepared focused follow-up, **UNEXECUTED**:
`Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-single-node.ms`.
It uses one exact-owned Box; tests repeated `node.layer` equality and both equality
directions against `LayerManager.getLayer 0`, candidate property scalar copies,
per-target throws and real/bogus fields. No layer creation/movement or material
work. Full evidence is written only to the new explicit owned
`layer-comparison-evidence.txt`; an existing destination refuses. Compact stdout
reports status/path. Default-layer equality does **not** establish unique layer
identity, distinguish two layers, or prove mutation detection. Large R4/R5 probes
are superseded operationally by this focused request and are not to run by default.
