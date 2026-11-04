# P3 independent offline analytical oracle — 2026-11-02e

## Outcome and ownership

Created only:

- `Audit/phase16_p3_oracle.py`
- `Audit/test_phase16_p3_oracle.py`
- this report.

No accepted-P2 file, existing fixture, source plan/evidence, checkpoint, installed
copy or archive was edited. No live Max call, installation, git mutation or scene
operation was performed. The coordinator owns stage acceptance and checkpoint.

This is a **repo-only audit oracle**, not a production emitter, QA-profile rollout,
replacement validator, manifest contract, or proof of live execution. It imports
only the Python standard library. It never imports a wall builder/runtime or reads
their predictions. Contract decisions were read from
`Audit/_phase16-p3-contract-2026-11-02e.md` after its publication.

## Independently read authority

Actual grammar: `references/07-spec-grammar.md` §8.9. Source values independently
read: `Audit/AGENT_PLAN_poly_surface_shell.md` §G.1, corroborated with actual
`Audit/EVIDENCE_2026-10-27.md` E-11/E-12/E-14. F01 is **not** the earlier typo variant.

```text
inner X/u: 0..400 cm; Y=0; Z=0..300; physical outward=(0,-1); thickness=30
door: u50..150, sill0/head210; window: u230..330, sill90/head210
u stations: [0,50,150,230,330,400]; v stations: [0,90,210,300]
area = 400*300 - 100*210 - 100*120 = 87000 cm2
volume = 87000*30 = 2610000 cm3
```

An outward vector's perpendicular/unit shape, compass label, mesh winding or
volume does **not** establish the physical outside. This implementation computes
the physical shell from separately supplied authoritative endpoint/Z/thickness/
opening values and the physical outside sign; `walls.outward` is compared against
that authority, never used as its own proof. Geometric normals are exact run
perpendiculars with the corroborated sign, per the contract clarification. Both
raw supplied vectors remain separately reported.

## Public APIs and data boundary

Import with `sys.path.insert(0, "Audit"); import phase16_p3_oracle as oracle`.

### Core prediction

```python
predicted = oracle.predict(walls_dict, dimensions_dict, physical_record)
```

`walls_dict` and `dimensions_dict` must be locked cm/deg source dictionaries.
This oracle checks its used geometry, source selector, project/units/status,
bounded epsilons and ceilings, but **does not claim complete G-1..G-100 validation**.
Use the accepted source validator separately. Origins, ledgers, unknown formulas,
filesystem races and source parsing beyond the explicit adapter remain outside
this core. Numeric tokens already rounded by a caller cannot be reconstructed.

The separate audit-local `physical_record` contains:

```python
{
  "project": "same project", "wall_run_id": "same run", "reference_face": "inner",
  "source_hashes": {
    "walls": oracle.source_digest(walls_dict),
    "dimensions": oracle.source_digest(dimensions_dict)
  },
  "start_cm": [0,0], "end_cm": [400,0], "base_z_cm": 0, "top_z_cm": 300,
  "thickness_cm": 30, "outward": [0,-1],
  "openings": [
    {"id":"actual door id", "kind":"door", "u_range_cm":[50,150], "sill_cm":0, "head_cm":210},
    {"id":"actual window id", "kind":"window", "u_range_cm":[230,330], "sill_cm":90, "head_cm":210}
  ],
  "evidence": {"locator":"actual source and section", "sha256":"actual source byte SHA-256",
               "reviewer":"independent reviewer", "reviewed":True}
}
```

`source_digest` is explicitly a canonical **semantic JSON** hash, not the original
file byte hash. It binds these supplied dictionaries, not an invented path. Source
byte authentication must not be inferred from it. `verify_authority_source` can
check independently read bytes against the reviewed locator/hash; this checks hash
binding, not arbitrary-source semantics. Core `predict` requires a reviewed record
but cannot independently authenticate assertions in a dictionary.

For the **actual F01 only**, the separate operational-record adapter is available:

```python
physical_record = oracle.physical_from_f01_authority(
    walls_dict, dimensions_dict, closed_direction_authority,
    walls_bytes=actual_wall_file_bytes,
    source_bytes=actual_analytical_plan_bytes,
    reviewer="independent reviewer")
```

It accepts exactly the coordinator's twelve-key `p3-direction-authority-1`
record, verifies actual wall/source byte hashes, checks the supplied wall dict
against those bytes, reads the actual G.1 section and checks its explicit source
sentences. It independently fixes physical F01 values from those sentences,
including thickness/openings **not present in the operational direction record**.
Opening IDs are taken only as identity bindings; physical coordinates are not
copied from the wall. Opposite authority sign or stale bytes refuse. A changed or
unknown source requires fresh semantic review and is not auto-parsed as F01.
Adapter refusal raises `OracleProblem` carrying `status` (`FAIL` or `INCOMPLETE`).

### Separate measurement checker

```python
assessment = oracle.check_measurements(predicted, normalized_capture)
# Convenience only; still composes the two separate APIs:
assessment = oracle.assess(walls_dict, dimensions_dict, physical_record, normalized_capture)
```

Normalized captures contain:

```python
{
  "evidence": {
    "kind":"scene_capture",       # tests MUST use "synthetic_test"
    "capture_id":"actual capture identity",
    "artifact_sha256":"actual emitted artifact hash",
    "source_hashes":predicted["source_hashes"],
    "project":predicted["project"], "wall_run_id":predicted["wall_run_id"],
    "length_unit":"cm"
  },
  "grid": {"vertices_cm":actual_grid_xyz, "faces":actual_grid_quads, "index_base":0},
  "base": {"vertices_cm":actual_base_xyz, "faces":actual_active_base_quads, "index_base":0},
  "evaluated": {"vertices_cm":actual_evaluated_xyz, "faces":actual_evaluated_quads,
                "triangles":actual_evaluated_triangles, "index_base":0}
}
```

Explicit `index_base` may be 0 or 1. Actual IDs/order need **not** be row-major.
Normalize dead-slot/active-index details in a caller-specific adapter without
manufacturing missing vertices/faces. `adapt_capture(raw, cm_per_scene_unit=..., 
index_base=...)` is a separate minimal coordinate adapter using raw `vertices`
instead of `vertices_cm`. It requires explicit scale/index base, preserves arrays
and evidence, and does not infer scene units or convert a missing observation into
a prediction. Actual type/scale pairing is a separate runtime gate; equal factors
do not establish equal scene state. No future emitter/manifest wire shape is assumed.

**Known measurement integration gap:** the independent measurement author's
`Audit/_phase16-p3-measurement-2026-11-02e.md` currently supplies evaluated triangles
but not actual evaluated polygon loops. This oracle deliberately returns
**INCOMPLETE**, not PASS, when evaluated `faces` are absent. Direction, signed
volume, triangle topology and exact triangle void/solid coverage still execute.
It does not relabel predicted 48 polygons as measured 48. Grid before deletion
also requires an actual earlier-stage capture; the checker cannot recover it
from the after-cut base or echo an emitter's station grid. Coordinator must close
those evidence gaps or explicitly accept a narrower check scope; this author
does not waive them.

### Return values and checks

Both core/checker return dictionaries with overall `status`, individual `checks`,
and separately `prediction` or `measured`. Contradiction wins FAIL; otherwise any
required missing/unsupported evidence yields INCOMPLETE, never PASS. An offline
prediction PASS means only bounded analytical/source agreement. Measurement PASS
is scoped to supplied payload and retains `evidence_scope`; a dictionary's
`scene_capture` label cannot prove that the caller actually measured Max.

Analytical prediction independently computes globally station-divided cells,
removed cell labels, all active topology, boundary components, Euler, area,
thickness volume, physical bounds, shell patch topology and expected triangles.
F01: grid **24/38/15**, base **24/36/12**, boundary edges **24**, boundary
components **2**, surface components **1**, χ **0**, shell **48** polys/**96** tris.
The distinction avoids the historical evidence table's misleading unqualified
“components” row. Expected row-major `{2,7,9}` are labels, never assumed API IDs.

Measurements recompute:

- Vertex/face/edge counts, active versus retained Euler, boundaries and connected
  components from actual arrays; edge orientation/incidence, duplicate faces,
  isolated vertices and each vertex's link connectivity/degrees.
- Exact bijective tolerance-bounded vertex matching; no silent welding or snapping.
- One-to-one base/grid/evaluated quad coverage against independent physical patches,
  all face normals and base area. Exact rectangles make source void occupancy
  decidable here without unsafe general triangle intersection/ray-casting.
- Evaluated signed displacement in physical outward coordinates and world bounds;
  these execute before evaluated polygon correspondence, even if polygons are missing.
- Actual triangle signed volume and topology, plus exactly two actual triangles per
  authority skin/reveal rectangle, its four boundary edges and one shared diagonal.
  Both triangulation diagonals are accepted; absent/superfluous skin/reveal patches,
  filled windows, artificial door thresholds and shifted holes cannot pass.
- Predicted **and actual** grid/base/triangle counts separately against declared
  nonnegative-integer ceilings. Actual counts are retained even when matching fails.

“No open edges” is explicitly insufficient. A solid closed box without the holes,
duplicate closed triangles, or two tetrahedra pinched at one shared vertex are
negative controls. An X-reflected, relocated-hole shell has the same physical bounds,
outward direction, closed topology and positive volume yet fails spatial matching.
A Y-reflected shell retains positive **2,610,000 cm³**, closed topology and correct
triangle count, but gets a named **EVALUATED_PHYSICAL_DIRECTION FAIL**.

## Supported scope and limits

Exactly one complete standalone straight run, one block, inner reference, no
returns/corners/instances, rectangular openings strictly separated in u and away
from run ends/top; sill zero is supported. No subset extraction. Touching/singular
boundaries, unresolved Shell isolated-vertex behavior, ambiguous near-stations and
unsupported cases return INCOMPLETE. P3.1 absolute planning caps (32 cells/64 grid
vertices/256 triangles/6 openings) are checked; these do not claim broader live
admission than the coordinator's tighter F01 execution caps. The independent
offline working limit defaults to 10,000 cells; capture arrays have finite
10,000-vertex/20,000-face caps to avoid unbounded work.

Coordinate/area/volume slack is a positional numerical error budget, not a design
tolerance. Self-intersection analysis for arbitrary surfaces, extra scene hosts,
census/stack/ownership/replay, transforms/controllers, renderer/material state,
unit snapshot authenticity and building enclosure are **not implemented** here.
Exact bounded patch coverage addresses the supported target geometry only; another
intact scene host behind its opening must be caught by separate census/scene QA.

## Executed verification

```bash
python -B Audit/test_phase16_p3_oracle.py -q
```

The suite uses a separately hand-authored F01 grid, explicitly traced boundary
loops and triangulated shell as **synthetic observations**, never reads predictions
to manufacture an oracle-positive capture, and preserves this evidence scope.
Tests cover F01 exact values, arbitrary captured ID order, both diagonals, explicit
one-based mm normalization, rotated/translated world frame, no openings/window-only/
sill-zero door-only, wrong scale, source/hash/sign/rectangle faults, budgets,
duplicate/open/flipped/pinched mesh defects, missing evidence and unsupported limits.

Also executed a read-only call on the actual new input-only fixture:
`Audit/phase16-p3-f01-input-2026-11-02e/project/{walls,dimensions}.json` plus its
closed `direction-authority.json` and actual plan bytes. Independent source adapter
and prediction returned **PASS, no non-PASS checks**, area **87,000**, volume
**2,610,000**, grid **24/38/15**, base **24/36/12**, boundary **24/2**, χ **0**,
shell prediction **48 polys/96 tris**. This is an analytical input comparison,
**not** a produced fixture, runtime observation or cure for any original P2 SKIP.

Final suite result and syntax/check details are recorded after the final author run
below; there is no Max acceptance claim in this report.

### Final author run (2026-11-03; artifact names retain kickoff suffix)

- `python -B Audit/test_phase16_p3_oracle.py -q`: **54 tests, OK**, 0.227 s;
  no SKIP or expected-failure cases. These are offline synthetic/source tests.
- `ast.parse` on both new Python files: **2/2 OK**, no bytecode written.
- `git diff --check --` the three owned paths: exit 0, no diagnostics. These new
  untracked files are not necessarily covered by git's tracked-file diff scanner;
  syntax and executed behavioral tests above are the substantive verification.
- Actual fixture/authority comparison above was read-only. No live Max evidence,
  evaluated polygon observation, installation, existing-fixture edit or checkpoint
  acceptance was invented to close integration gaps.

## Prepared independent full-capture integration supplement (2026-11-03)

On the coordinator's extended assignment, read the measurement owner's actual
`Audit/phase16-p3-measurement-2026-11-02e/{adapter.py,measure.ms,README.md}`;
modified **none** of those files. Their prepared full schema is
`p3-independent-measurement-1`, final status `CAPTURED_NOT_ACCEPTED`, one-based
world-space `base.vertices/faces`, and world-space `evaluated.vertices/triangles`.
The evaluated polygon count is deliberately null. A successful tool-return envelope
containing `path/sha256` is **not** the full capture: open and hash the actual file.

The inspected corrected `measure.ms` reads base local positions through the actual
object transform once, but snapshotAsMesh positions are already world-space and
receive no second transform. Both normalizers now tested here only divide actual
world arrays by `units.scene_units_per_cm`; they never apply objectTransform.
No live coordinate semantics were asserted by this author. Main owns the separate
translated/rotated live calibration and actual capture provenance.

### Ready-to-use APIs

1. The existing measurement-owner API **works without changes**:
   `adapter.oracle_capture(raw, explicit_evidence, grid_raw=actual_grid_or_None)`
   followed by `oracle.check_measurements(predicted, normalized)`.
2. Added an independent equivalent geometry normalizer inside the owned module:
   `oracle.adapt_independent_measurement(raw, evidence, grid_raw=None)`.
3. Added a full-file assessment entry point:

```python
assessment = oracle.check_independent_capture(
    predicted, raw_full_capture, explicit_evidence,
    grid_raw=actual_earlier_grid_or_None,
    expected_units={"system_type":"millimeters", "system_scale":1,
                    "scene_units_per_cm":10})
```

`expected_units` is independently locked state from main, not inferred from the
capture or from an equal conversion factor. All three values compare exactly;
an equal-factor different type/scale pair **fails**. Omitted expected units remain
INCOMPLETE. The wrapper also carries raw unresolved `issues` to INCOMPLETE and
checks the full capture header. Header/provenance labels remain observations to
authenticate separately, not cryptographic/live proof.

The explicit `evidence` is the earlier normalized evidence contract: kind,
capture ID, exact emitted artifact SHA-256, semantic source hashes, project/run,
and `length_unit=cm`. Main must bind these independently. A concrete shell caller
can import this module using `sys.path.insert(0,'Audit')`, read the actual capture
bytes with `Path(actual_capture_path).read_bytes()`, verify their SHA-256 against
the returned capture envelope, decode that exact byte snapshot with `json.loads`,
and pass its already-verified evidence dictionary to the API above. Source setup
remains `physical_from_f01_authority(...actual wall/source bytes...)` then
`predict(walls,dimensions,physical)`; that adapter already reads the actual F01
plan hash and literal G.1 statements, not wall/manifest numerical predictions.

Returned `profiles.base` and `profiles.evaluated_triangles` summarize **only
available target geometry**; they explicitly do not establish source/capture
authentication and never override overall `status`. With correct final triangle-
only data and no earlier grid, expected result is:

```text
overall status: INCOMPLETE
GRID_CAPTURE: INCOMPLETE
EVALUATED_CAPTURE: INCOMPLETE (no actual evaluated polygon loops)
BASE_SOURCE_AREA / BASE_COVERAGE: PASS
EVALUATED_PHYSICAL_DIRECTION / EVALUATED_BOUNDS: PASS
TRIANGLE_VOLUME / TRIANGLE_TOPOLOGY / TRIANGLE_VOID_AND_SOLID_COVERAGE: PASS
profiles.evaluated_triangles.status: PASS (target geometry scope only)
measured signed volume: 2610000 cm3; base source area: 87000 cm2
```

Missing evidence never becomes an overall PASS or false measured polygon/grid
claim. Conversely, a reversed-direction triangle-only capture yields overall
FAIL while volume can still PASS. The wrapper does not invent grid/quads, silently
drop issues, change the measurement-owner adapter, or claim the original 21 P2
skips are closed.

### Supplement tests

Tests now dynamically import the actual separately owned `adapter.py` read-only,
exercise a separately hand-authored **synthetic full measure.ms schema**, and
confirm equivalent converted geometry against this module's adapter. This tests
wire compatibility, not a live file. Additional protective cases cover short
path/hash envelope refusal, triangle-only qualification with running aperture/
volume/direction checks, independently locked unit-pair mismatch, missing units,
property issues, no second objectTransform, grid identity mismatch, source literal
disagreement despite an updated matching hash, and no caller-data mutation.

Supplement final author run: `python -B Audit/test_phase16_p3_oracle.py -q`:
**65 tests OK**, 0.262 s, no SKIP/expected failures. Both owned Python files
`ast.parse` successfully; owned-path `git diff --check` exits 0. No live Max call,
measurement-owner edit or existing fixture modification occurred.
