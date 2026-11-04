# Closed-contour Shell v2 — production integration review

**Decision:** the six fixtures justify planning `closed_inner_contour_shell_v2`, not production acceptance or a pipeline rewrite now.
Read-only source review, 2026-11-04. This reviewer made no Max calls, changed no production files, and deleted no evidence.
Line references below address the working-tree snapshot reviewed, not HEAD or the installed archive.

## 1. Evidence boundary

- `results.json:2–7` records rectangle/blind, rectangle/three openings on two facades, L, U, oblique trapezoid, and outer-12×8-inset fixtures.
- All report one Shell, `straight=true`, zero open edges, zero non-2 undirected triangle-edge valences, zero degenerate triangles, and positive signed volume.
- Independently recomputed the six analytical volumes in memory against the captured strings: five exact at printed precision; oblique relative difference ≈1.76e-6.
- The oracle is `(area(offset(inner,t))−area(inner))*height − Σ(opening_area*t)` (`probe.py:61–91`), not standalone `base_area*t` around corners.
- Shared corner indices and a whole-floor Z-level union are central to the conforming mesh (`probe.py:66–84,104–105`); do not replace them with separate facade shells or tolerance welding.
- Outer-12×8 has minimum X ≈−3.05e-6 cm (`results.json:7`): Float32 precision is bounded, **not zero error**. Printed wire precision also limits comparisons.
- Main reports calibrated absence of `overrideEdgeMatID`/`matEdgeID`; use `overrideMatID`/`matID`, as emitted at `probe.py:138`. These property controls are not recorded in the six-case results file.
- This is prototype evidence only: no production spec adapter, S1→S5 coexistence, slabs/frames, arbitrary offsets/shapes, exhaustive self-intersection QA, or production replay is established.
- `probe.py:22–36` explicitly implements a fixture-only miter offsetter; do not promote it as a robust general polygon-offset engine.

## 2. Retire experiment-specific runtime bureaucracy, retain useful guards

| Current restriction | v2 recommendation and source |
|---|---|
| One-use arm/nonce/global lease with ARMED/BUILDING/COMMITTED/POISONED states | Retire from the normal production route, retain v1 evidence/harness: `scripts/wall_surface_runtime.py:400–479,982–1031,1187–1208`. |
| Empty unnamed scene, sole node, sole empty layer 0, fixed rootScene reference slots | Retire: these forbid integration after S2/S3; see runtime `:435–439,891–916,961–965,986,1020–1026`. |
| Recursive reflection/freezing of every property/dependency, all map/VData/EData channels, subAnim/controller graph and exact RNormals replay | Retire as mandatory whole-scene admission; keep targeted owned geometry/transform/stack checks and explicit normal/smoothing QA: runtime `:560–733,793–959`. |
| Replay tied to unchanged dirty flag, selection/time, material and all metadata | Retire these acceptance conditions: runtime `:915,935–959,976–1014`. Manual material assignment or unrelated edits must not invalidate owned geometry automatically. |
| Standalone one-run source-authority sidecar and one-node/F01 manifest | Replace with sourced contour semantics, orientation/offset checks and a versioned block manifest: `scripts/build_wall_surface.py:210–257,428–445,468–537`. Winding alone never proves the source is an inner contour. |
| Existing project artifact always refused; output always disjoint from input project | Replace as a production lifecycle rule with explicitly resolved versioned outputs/ownership; retain non-clobber behavior: `scripts/wall_surface_inputs.py:53–80,387–405`; builder `:361–369`. |

**Keep:** strict finite non-boolean inputs, unique IDs/joins, locked input gates, real source/provenance checks, correct cm→scene conversion, live SystemType/SystemScale mismatch refusal before writes, and Float32 distinguishability/error checks.
Useful implementations: builder `:76–134,291–335`; inputs `:293–307,353–380,409–495`; runtime `:279–307,354–375,519–531`.
Do not remove provenance/formula validation merely because the input adapter currently carries many exact-string SKIP exceptions (`inputs:126–190,475–495`); replace with explicit stage-scoped validation applicability.
**Keep:** exact created-reference ownership, collision refusal, short bounded calls, disposal of temporary meshes, no reset, no unrequested save, no dirty-flag manipulation, and stop/inspect on uncertain timeout. Never replace lease bureaucracy with prefix-wide deletion.
`scripts/wall_surface_publish.py:204–251` is a reusable new-run immutable pair publisher, not geometry bureaucracy; its Windows/no-replace policy can remain for retained run artifacts.
Simplify duplicated path checks only behind an explicit publication policy; preserve no-clobber and owned-stage cleanup (`publish:179–201`), without claiming hostile-writer or crash-atomic guarantees.
Current runtime comments still claim unconditional replay/precreate refusal (`runtime:9–25`), while actual branches create and accept NOOP (`:1005–1014,1018–1103`); plan from executable branches, preserve dated evidence.

## 3. Proposed contract, not an implementation

- Introduce explicit `wall_technique: "closed_inner_contour_shell_v2"` with its own documented schema/manifest version; never reinterpret `poly_surface_shell_v1` data silently.
- Declare a sourced, ordered, simple closed inner contour, block/floor Z interval, constant wall thickness per admitted block, segment-linked rectangular rough openings, numerical tolerances and budgets. Unsupported holes, varying thickness, acute-offset collapse or complex joins must refuse explicitly.
- If source geometry is outer-referenced, record that fact and the inset operation/result; the rectangular 12×8 experiment is not blanket authorization to accept outer references in the inner contract.
- Plan one connected vertical Editable Poly surface per admitted closed block; reuse cyclic corner indices at every shared Z station, remove opening cells, then apply exactly one Shell with inner=0, outer=thickness, `straightenCorners=true`, segments=1.
- No need to mandate an Extrude modifier or retain a guide spline: the prototype builds polygon topology directly (`probe.py:121–139`). State the output geometry contract rather than inventing an executed tool chain.
- Replace one-wall caps/predictions (`runtime:45–49,134–154,217–274`; builder `:519–531`): the measured U case already has 75 active base faces and 400 triangles (`results.json:5`), exceeding v1's 32/256 caps.
- Keep measured counts/budgets, segment/opening provenance, shared-vertex topology and ring-volume/bounds expectations per block; calibrate processing bounds before larger live work, not by removing limits altogether.

## 4. Exact S4w / S5 conflict and switch map

**There is no working poly S5 coexistence path today.** Preserving a separate demo in Max or observing that legacy code hides host boxes is not end-to-end integration.

| Integration point | Required planned change |
|---|---|
| Pipeline order | Insert explicit S4w after facade/registry planning and before S5; S5 remains last geometry builder. Current table has no S4w (`agents/max-orchestrator.md:29–36,99–109`). S4w must work in the already populated S2/S3 scene. |
| Wall coordinator/input/runtime | Dispatch versioned adapters/plans instead of hardcoded v1/one run/one block (`build_wall_surface.py:50–52,545–576`; inputs `:310–352,471–474`; runtime `:150–160`). |
| S5 route admission | Update constants, closed shapes/selectors, manifest-location and output-route guards, not just the CLI branch (`place_components.py:193–195,534–568,595–645,656–689,706–730,3054–3086,3297–3306`). |
| S5 assembly production | Add a v2 branch that retains placements/prototypes/scatter and emits route echo + `wall_ref`, **omitting** legacy `opening_cuts`/`wall_cells`; current `build_assembly` rejects nonlegacy and always builds cells (`:1869–1935`). |
| S5 render/validation/reporting | Branch array access, origins/naming/census, legacy spatial checks and summaries: `:1840–1859,2016–2018,2044–2065,2209–2248,2328–2334,2776–2777,2932–2934,3203–3221,3333–3344,3360–3384`. Preserve placement joins/instancing; never satisfy v2 with empty legacy arrays. |
| Host overlap/deactivation | Current hide set derives only from legacy cuts (`:2031,2127–2141`), so it cannot own blind-facade coverage for v2. Specify an explicit verified S2 facade-host replacement set, including blind walls, and one stage responsible for deactivation; never hide/delete NURBS, slabs or WS nodes. |
| Stack law | Keep zero added modifiers for S5 placement/legacy hosts; allow exactly one Shell on S4w-owned v2 walls. Do not apply `:2173–2181` or a scene-wide zero-stack assertion to v2 walls. |

S5 currently calls the independent legacy G-82 oracle unconditionally (`place_components.py:923–944,3344`); dispatch it only for legacy and add a separate v2 wall-coverage gate, not a blanket skip of coverage.
The emitted S5 legacy replay deletes matching names twice (`:2044–2065`); do not copy this into shared-scene v2 ownership. Require explicit ownership-checked NOOP or scoped rebuild semantics and real measured replays.

## 5. QA: retain the building gate, add genuine v2 geometry

- Retain NURBS census/form precision, component placement and prototype instancing, project coverage/census, applicable legacy wall coverage, units, and real replay checks. Do **not** reduce S7 to four wall predicates (`scripts/qa_check.py:79–123,1405–1453,1648–1700`).
- Current wall direction assumes world Y=0/outward −Y and hardcodes 0.05 scene units (`:1041–1051,1467–1482,1521–1545`); v2 needs sourced per-segment planes/normals, corner/inset bounds and canonical-cm tolerances converted to native units.
- Current emitter writes `abs(evalVol)` (`:1052–1081`); SOLID/TOPOLOGY re-apply abs and test only positive volume/stack (`:1547–1595`). These do **not** prove signed orientation, closed/manifold geometry or absence of self-intersection.
- SURFACE/ENCLOSURE/APERTURE presently reuse deviation/positive-volume tests (`:1597–1641`); no actual aperture clearance or floor enclosure measurement is present there.
- Add independent signed ring-minus-openings volume comparison; open-edge count; undirected edge valence=2; opposite directed-edge use; nondegenerate faces; expected components; base shared-corner conformity; inner-contour and outer-offset agreement; actual rough-aperture clearance; and cross-section/offset self-intersection checks within the admitted subset.
- Measure Shell class/count, enabled states, inner/outer amounts, segments, straightenCorners, normals/smoothing and any promised face IDs. Do not conflate wall manifoldness with building enclosure/slab integration.
- Fail incomplete on absent/unparseable/nonfinite metrics instead of defaulting to zero; support MAXScript Double `d` exponents (`:1290–1312`), which the captured fixture volumes actually use.
- REPLAY currently sets PASS without receipt validation (`:1643–1646`); retain the requirement but bind three real replay observations and compare owned scene/geometry measurements. Existing NURBS/PLACEMENT assessment also checks existence only (`:1425–1453`), not all implied geometric guarantees.
- Extend QA profile/metric vocabulary and wire parsing explicitly (`:79–123,275–277,1022–1085,1290–1312`); preserve missing-observation/coverage and bounded batch controls. Geometry-reader failures must not emit apparently valid defaults.

## 6. Versioned validation, scaffolding and compatibility

- Preserve historical no-wall/no-selector fixtures as legacy and explicit `legacy_cells_v1` as legacy; preserve v1 fixtures/contracts without claiming v2 coverage. Unknown/conflicting/partial routes continue to fail (`validate_specs.py:1716–1763`; grammar `:2238–2255,2357–2389`).
- Version grammar/schema deliberately: current closed v1 objects require runs/facade references and inner-only semantics (`grammar:2391–2412,2551–2614`); adding a contour field without versioned shape dispatch fails closed validation.
- Switch sites: `validate_specs.py:105–107,1869–1878,13268–13279,13894–13924,13998–14074,14177–14216`; preserve shared assembly checks and legacy-only applicability (`:11786–11821`). Keep G-95/98/99/100 as live/output obligations, never JSON-only PASS (`grammar:2980–2996`).
- Initializer sites: constants `init_project.py:152–153`, fresh wall/assembly placeholders `:867–920`, closed seed shapes `:1431–1454`, seed route/echo/exclusivity `:1457–1498`; preserve authored/seeded content and existing overwrite protections.
- Do not make fresh scaffolds production-ready by changing a selector alone. Change the default only after an accepted v2 spec→build→S5→QA integration gate; explicit opt-in fixtures can precede that.

## 7. Packaging and preservation

- `scripts/install_skill.py:24–58` ships Python helpers, references/playbooks, JSON specs and approved example extensions; it excludes both `Audit/` and `experiments/`. Read-only `collect_files()` confirmed all five wall helpers are included, but this experiment and the Audit contract are not.
- **Installed-builder blocker:** `build_wall_surface.py:49–50,376–408` hashes required `Audit/_phase16-p3-contract-2026-11-02e.md`; installing the current helpers without that file leaves this path unavailable. Move the normative production contract into a packaged location or make it self-contained; do not package/delete all Audit history as a workaround.
- Keep experiments/results and historical tests/evidence repo-local; add only reviewed versioned fixtures/specs/playbooks to package scope. Later installation must test an isolated installed copy, not just source execution. Do not run installer or rebuild `.skill` during this review.
- Entry audit observed existing dirty tracked pipeline/docs plus untracked wall helpers, fixtures and substantial Audit work. All preserved. Reviewed core SHA prefixes: builder `a2b053483535`, inputs `5c1e31347563`, runtime `744c2e3c0960`, publisher `7868798b426f`, S5 `4f9735ffbf9d`, QA `18eb61c72665`.

**Next authorized action:** rewrite the plan around this bounded v2 contract and its integration gates; no production implementation, cleanup sweep or further live call follows from this review.
