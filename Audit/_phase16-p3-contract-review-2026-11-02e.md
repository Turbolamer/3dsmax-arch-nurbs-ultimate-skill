# Phase 16 P3 — bounded emitter contract review, 2026-11-02e

**Review only; proposed decisions for coordinator approval, not an implemented or accepted interface.**
P2 is accepted **offline only**. The proposal's P2-blocked/live-permission premises are obsolete;
the newest explicit permission allows necessary Max work, **main alone** operates Max. This review
made no Max calls, executions, installs, fixture edits or git writes. Only this new report is owned.

## 1. Recommended first delivery: P3.1, not the whole wall route

Freeze a named `single_straight_inner_v1` **emitter capability**, outside the closed wall input schema:

| Admit | Refuse the complete request before publication or scene mutation |
|---|---|
| One block, exactly one straight vertical `wall_runs[]` entry, `reference_face=inner`, explicit poly selector; one uniquely resolved, physically sourced facade reference. | Extra blocks/runs, all nonempty `upper_returns`, corners/miter/seams, intersections, enclosure, instances, slab/roof interfaces, unsupported source contours or outer reference. Do not silently select one run. |
| Zero or more rectangular openings within the bounded operational envelope; `0 < lo < hi < L`, `0 <= sill < head < H`; positive gaps between different openings' u intervals. | Openings touching the run ends/top, touching one another, overlapping, or creating unresolved numerical slivers. No resizing, snapping, one-opening-per-bay rule or inferred opening-to-dimensions join. |
| Full Cartesian station grid over this one run; exact duplicate station values share one station. `sill=0` is an outer-boundary notch; `sill>0` is a hole, independently of `kind`. | Locally terminating subdivisions and any claim to F08's economical local topology. Distinct stations too close for declared numerical precision/native Float32 must fail, not merge. |

This is a standalone **wall fragment**, never a complete building/enclosure PASS. Report valid but
unsupported declarations as `UNSUPPORTED_SCOPE`, not physically impossible architecture. The existing
`specs/fixtures/poly-shell-input/walls.json` is **not** this subset: it has two blocks, two runs and a
return. Preserve it; use it as a whole-request refusal control, not a partially emitted positive.
Its README explicitly identifies synthetic P2 input, dependent on `examples/`, not F01 or produced output.
Create a separate authentic F01 input/output project later under explicit ownership; never relabel an echo.

## 2. Close schema/provenance and input readiness at the right boundary

1. Consume the actual §8.9 schema, not the older plan's draft table: no `defaults`, extra source keys,
   implementation classes or authority/ownership fields inside `walls.json`; world XY/Z, run-local u/v,
   exact three inherited tolerances, two independent bounded epsilons, per-run three integer ceilings.
2. Strict-parse **bytes**, including used upstream files and ledgers; duplicate keys, unsafe numeric
   decoding, non-finiteness, overflow and excessive nesting must refuse before output. Reject ambiguous
   paths/owners/IDs. Preserve raw numeric meaning through geometry preparation; checking rounded Python
   objects cannot recover lost source digits.
3. Validate the **consumed input closure** from the same immutable snapshot used to emit. Require locked,
   same-project/schema/units inputs, exact leaf-origin/ledger bindings, stage direction, acyclicity and
   actual source reads. Record every read path and file hash, including sources checked for authority.
   A successful path join is not source-content truth or proof of the declared arithmetic.
4. Minimal first support: wall domain origins are `given` from an actually reviewed synthetic brief;
   do not launder `derived` into `given`. Defer wall-local derived formulas/derived annotations until
   a separate recomputation/linkage oracle exists. Reached upstream unknown G-32 formulas or provenance
   incompleteness refuse; known formulas must retain dependency coverage and independent recomputation.
   Unrelated, unreached legacy SKIPs need not block this closure.
5. Explicitly classify input, artifact and runtime obligations. Do **not** demand a future manifest,
   produced assembly or runtime PASS to enter S4w, and do not bypass input checks with `--allow-draft`.
   An absent assembly, or its known empty draft placeholder, is not a produced output; its expected
   output-stage incompleteness is not an input waiver. Any supplied assembly contradiction/route mixing
   still refuses. Existing grammar G-92/G-96 and runtime SKIPs must not be relabeled PASS by the emitter.

## 3. Physical outward authority is an independent input, not a winding check

**Approve a separate, closed, versioned build-authority record before coding its reader.** It belongs
outside `specs/pipeline/`, not in `walls.json`. Minimum binding: project/run, exact wall-input hash,
reference-face plane/segment, physical outward side, source file/hash plus precise locator, and the
independent review evidence. Pin the record and actual source bytes in the build lock. An `APPROVED`
string, copied vector, source filename, origins coverage, compass label or normal alone is not evidence.

For F01, `AGENT_PLAN_poly_surface_shell.md` §G.1 explicitly supplies **inner Y=0 / outward -Y** in cm;
bind that exact analytical fixture authority. The P2 fixture's hypothetical brief does not authenticate
the example's physical building, and the P1 spike is not execution evidence for new emitter output.
Real projects lacking an independently reviewed physical-face/sign source remain INCOMPLETE/build-refused.

Keep three assertions separate: (a) source establishes physical outside; (b) declaration agrees with
source; (c) actual base normal/thickness agree with that side. For a near-unit/perpendicular declaration,
preserve the supplied vector, derive the geometric unit perpendicular from run endpoints and choose
its **sign** only after authority agreement. Shell offsets along that geometric normal; do not model
a skew offset by multiplying an imperfect supplied vector. Record/compare both vectors under the
dimensionless epsilon. Required negatives: flip winding alone, then flip both winding and declaration
against unchanged physical authority. The second must still fail despite declaration/mesh agreement.

## 4. Geometry, budgets and safe operating envelope

- Use measured route A and **returned** vertex/face IDs, common IDs along common edges, complete cell
  boundaries and one collected opening-face deletion. Verify every API return; do not generalize F01
  face numbers or reuse pre-deletion IDs afterward. Conversion invalidates references (E-6/E-13).
- Predict separate grid/active-base/evaluated counts, then measure each live. For this conforming quad
  subset, count active edges/vertices from incidence; let F be kept quads and B boundary edges. Predicted
  Shell polygons = `2F+B`, triangles = `4F+2B` for one segment. These remain predictions until measured;
  dead elements and retained unused vertices must be separately reported, not hidden in active counts.
- Check finite positive cells, shared adjacency, no duplicate faces/coincident vertices, manifold
  edge incidence and connected vertex fans. Base open edges are intentional. With separated openings
  and a retained top web, expect one connected base, `1 + count(sill>0)` boundary cycles and
  `chi = 1 - count(sill>0)`. Independently verify actual topology; zero evaluated open edges is not
  sufficient solid proof. Stack: exactly one Shell, inner 0, outer thickness*f, segments 1; no Boolean.
- Enforce each supplied ceiling **and** independent operational ceilings; never increase budgets or
  optimize silently. Recommended initial live work envelope: no more than F01's 24 created vertices,
  15 grid quads and 96 evaluated triangles; retain the separate active-base ceiling, rather than
  treating F01's 12 active faces as universal. This deliberately bounds the number of openings/stations.
  It is a proposed conservative admission limit, **not** a measured universal time guarantee.
- Freeze script/JSON byte, input-size, census/fingerprint-work and API-operation limits too. Main must
  calibrate one build/readback/cleanup batch under ~2 s before expansion. One modifier is within the
  standing <=5-per-call rule. A runtime timer cannot interrupt a blocking Max API call safely; do not
  accept arbitrary counts merely because a timeout exists. Do not re-run dangerous modifier ladders.
- Preflight transformed native Float32 coordinates/offsets: finite values, distinct representable
  stations, nonzero cells/thickness, error bounded by the explicit numerical policy. Reject huge-world
  precision loss; do not hide it behind the 0.5 cm design tolerance. Compare expected and live **both**
  SystemType/SystemScale plus factor before any mutation, including equal-factor/different-pair negatives.

## 5. Freeze executable boundary, input lock and pair publication

Recommended emitter-only CLI surface: project input directory, **new** output run directory, explicit
stable namespace/owner token, expected scene type/scale and approved authority record. No implicit scene
execution, overwrite, reset, unit change, migration or output installation. Reject additional switches
that silently broaden scope; normal stdout may contain diagnostics, not an acceptance claim.
Define deterministic string escaping and injective node-name mapping, including Max/Windows case and
length collisions; IDs/source strings are data, never executable MAXScript or unvalidated path fragments.

Before implementing, agree a closed manifest version containing: capability/route/project/run identity;
input/authority/helper-code hashes; expected native units and f; raw inputs plus explicit coordinate/
normal mapping; node names/ownership policy; exactly declared stack; per-run ceilings and separately
named predictions; publication/build digest. Deterministic bytes exclude wall-clock time and live handles.
Use one digest of canonical input/config/code identity embedded in both artifacts; manifest may hash
the script. Do not require mutually recursive full-file hashes. Live receipt/baseline is a separate
record binding **both actual artifact hashes**, units and scene/node identities, never a rewritten spec.

**Locking decision required:** no validate-by-path then reopen-by-path emission. Pin the eligible input
set, validate/emit from the exact bytes read, and retain an approved hash lock. For first execution,
use a controlled private snapshot and a single writer; if claiming Windows concurrent-writer exclusion,
prove the actual deny-write/delete handle and parent-identity mechanism. Repeated stat/hash checks alone
are not locks and must not be advertised as arbitrary-race protection. Input changes require a new run.
Likewise pin and verify **both published output bytes** immediately before execution; a mutable path
passed to `fileIn` is not an artifact lock. Define the controlled execution-read protocol before claiming
protection from output replacement between approval and loading.

Publish both completed files through a **new same-volume staging directory**, readback/hash verification,
then a verified directory-level **no-replace** rename into a nonexistent target. Restrict first support
to a tested local filesystem/path policy; fail closed if atomic visibility/no-clobber cannot be supplied.
Reject links/junctions, traversal and name/normalization collisions; protect the actual target parent,
not only its spelling. No two-file `os.replace` commit, clobber, cleanup of foreign paths or automatic
overwrite of an earlier run. Pre-publication failure preserves all earlier bytes; retain exact recovery
evidence if cleanup fails. Atomic visibility is not a power-loss durability claim. Defer the canonical
`assembly.wall_ref == "wall_surface.json"` deployment/link switch to its own integration contract.

## 6. Ownership/replay: first version is create-or-verified-no-op

Prefix/name is not ownership. Require namespace collision checks, a scene-local registry of exact node
references/handles plus per-node owner tokens, no duplicate tags, and a baseline **read from Max** after
creation. Include topology/geometry, transforms, base/stack identity and parameters/enabled state,
material, layer, visibility/renderability, hierarchy/dependencies and user properties in the supported
state fingerprint. A missing/unreadable state or unrecognized dependency is uncertainty, not unchanged.

Same inputs/artifacts/units plus uniquely matching registry and full baseline => no-op; any user edit,
tag copy, name collision, registry loss, input change or uncertain scene identity => refuse before
mutation. No replacement/rebuild of prior nodes. Initial support may be **same-session only**: after
save/load, merge or registry loss, refuse, rather than claim unproved persistent ownership. Main must
prove safe identity reacquisition across the measured `convertTo` route before using it; unique-name
lookup alone is not a deletion authorization. Cleanup uses only proven current-attempt references,
never a prefix scan; incomplete cleanup reports exact residues and stops. No host hiding or user-node,
layer, material, scene-save or backup manipulation is implied. Read-only baseline inspection is not
the cancelled material-assignment stage.

## 7. Approval/acceptance blockers and next hand-off

**Before implementation:** coordinator freezes the subset, closed authority/manifest/CLI contracts,
same-byte input locking threat model, tested no-replace publication primitive, numeric/operational
limits, and same-session ownership policy. These are real open interfaces in the design, not P2 defects.
**Before live acceptance:** main proves conversion identity/cleanup and full fingerprint availability;
executes the actual published F01 script; independently measures plane/direction, holes/through-void,
surface area, topology, evaluated volume/census/stack; runs three real no-op replays and isolated edit,
unit, authority, publication/collision and partial-failure controls. Preserve unrelated sentinels.
The oracle must read locked source rectangles/physical authority and actual Max geometry, not reuse
emitter station/classification functions or treat manifest predictions as its source of truth. Test
an intact occluding host separately; equal volume and apparently closed solids do not prove open voids.
F01 expectations remain 24/38/15 before cuts; 24/36/12, B=24, two boundary cycles, chi=0 and
87,000 cm2 afterward; Shell 48 polygons/96 triangles, 2,610,000 cm3, inner Y=0 and outer Y=-30 cm.
Different units require normalized measurements; historical mm values are not current scene assumptions.

P3.1 success proves only this emitter subset. Poly QA/integration, legacy coexistence and F02-F05/F08
remain subsequent gates; F06/F07 evidence is required for the units/replay claims actually made here.
No installer/archive/global publication and no Phase 16 completion follows from this review.

**Reviewed anchors:** handoff `Audit/_phase16-p3-resume-2026-11-02d.md`; `PLAN.md` §4.0d;
`Audit/_phase16-p3-design-2026-11-02.md`; `Audit/AGENT_PLAN_poly_surface_shell.md` §§B/C/E/G/I;
`Audit/EVIDENCE_2026-10-27.md` E-1..E-16; `references/07-spec-grammar.md` §§8.9/9.11;
`specs/fixtures/poly-shell-input/{walls.json,README.md}`. No new live facts are asserted.
