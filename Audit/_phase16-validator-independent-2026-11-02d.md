# Phase 16 P2 — independent validator review, 2026-11-02d

## Verdict: not accepted; reviewer stopped

**Two additional conflict-annotation scope false PASS cases are independently
reproduced and remain failing in the latest selector run.** The four original
transitive faults discriminate from clean controls on `3675bd7f...`; strict JSON,
depth and numerical controls also worked on that snapshot. Subsequent source
changes mean those are not final-tree acceptance. The final stable full run is
the main session's responsibility. No source repair was made by this reviewer.

Exclusive writes: this report and `Audit/test_phase16_validator_review_d.py`.
No Max, builder, initializer, installer, archive, installed copy or user fixture
was written or invoked. All CLI executions use a frozen three-source snapshot
and disposable copies under the approved OpenCode temporary directory. The wall
is explicitly synthetic **input**; assembly is an **empty draft**, not a locked
echo or claimed produced poly output. No `wall_surface.json`/`.ms` is fabricated.

## Executed runs and hashes

Commands from repository root:

```text
python -B Audit/test_phase16_validator_review_d.py -q
python -B Audit/test_phase16_validator_review_d.py ProvenanceScope.test_non_derived_upstream_annotation_is_not_claimed_as_bound ProvenanceScope.test_non_derived_wall_annotation_is_not_claimed_as_bound -v
python -B Audit/test_phase16_validator_review_d.py ProvenanceScope.test_known_formula_must_bind_its_declared_inputs ProvenanceScope.test_used_upstream_unknown_formula_is_incomplete_not_wall_pass ProvenanceScope.test_non_derived_upstream_annotation_is_not_claimed_as_bound ProvenanceScope.test_non_derived_wall_annotation_is_not_claimed_as_bound -v
```

| Run | Frozen validator | Result and attribution |
|---|---|---|
| Complete earlier harness | `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1` | **25 tests / 148 CLI calls; 0 failures/errors/skips/xfails; exit 0; `SOURCE_DRIFT {}` / `OBSERVED_SOURCE_DRIFT {}`.** Harness then SHA `42f3022c854cdf4d55b326a92f375cfc1da57524cc43fcf4be3752cc0a5b1f15`. Predates two added annotation tests and source changes. |
| Two added annotation tests | same `3675bd7f...` | **2 tests / 4 calls; 2 failures; exit 1; no source drift.** Each mutant has exit 0, zero FAIL, wall G-10/G-93 PASS. |
| Complete expanded harness | `69a05c441ff5ea93bb3c707368d8359d5ca6f0c181c7e090a33c6d4edf4d13b0` | **27 tests / 152 calls; 2 annotation failures; 0 errors/skips/xfails; process exit 2** because source changed during frozen execution to `979056a3...`. **Preliminary**, not stable current-tree evidence. |
| Latest four-test selector | `979056a31a0733fc588fded0cb6f40f5d924b233508ebcc2b152a9e00bf6d1ed` | **4 tests / 8 calls; 2 G-32 controls succeed, 2 annotation tests fail; exit 1; no source drift.** This is not a full run. |

Final owned harness contains **29 tests** and is SHA-256
`f5b014b7dfe4195722deac147115cc17584fca704cf5d2d794c846f0a58a9198`.
It parsed with `ast.parse` without bytecode writes. The full 29-test suite has
**not** been run; run it on the final settled sources. The first development run
failed because the reviewer placed draft assembly envelope keys in the wrong
order; that fixture error was corrected. A subsequent development assertion
wrongly required G-10 rejection for a geometry-only epsilon error; it was scoped
to G-93 instead. Neither is counted as a validator bug or successful control.

Dependencies unchanged across the completed runs:

```text
scripts/wall_cell_coverage.py d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e
scripts/curve_gen.py         4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c
synthetic walls input       b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93
```

The harness captures and hashes **every existing example file** plus the three
sources and input fixture before/after execution; original fixture drift was
empty. Examples' sorted POSIX `path=sha256`, joined with LF, tree digest was
`c22c377c8227ea1092a6e2d7d89c417589ff56e586e0b3bad6057eaecea04bcb`.
Every invocation logs exact rule status scopes and target failures. Internal
error findings, stderr, malformed JSON, and JSON/process exit mismatches fail
the harness. Runtime/report SKIPs are assertions about incompleteness, not
unittest skips or proof. Source drift exits 2 and does not silently attribute
frozen observations to the new workspace.

## Open findings: non-derived conflict annotations

Both independently reproduced on stable `3675bd7f...` **and** `979056a3...`:

1. **Used upstream given value:** select only `roof.deck_thickness_cm` in
   `walls.origin_inputs`. Clean input has
   `dimensions.origins["roof.deck_thickness_cm"] = {"origin":"given"}` and
   gives exit 0, zero FAIL, wall G-10/G-93 PASS. Add the single optional property
   `"conflict_ref":"C-001"` to that same origin. C-001 is a real, valid level
   height conflict, unrelated to the given roof deck thickness. The mutant
   still gives **exit 0, zero FAIL, wall G-10/G-93 PASS**.
2. **Wall-local given value:** clean synthetic wall's collapsed
   `origins["wall_runs[0]"]` is `{"origin":"given"}` and passes. Add only
   `"conflict_ref":"C-001"` there; again **exit 0, zero FAIL, wall G-10/G-93
   PASS**. The existing reference does not resolve the input run's provenance.

The grammar describes `conflict_ref` as information about a derived value's
conflict-resolved inputs. `_wall_trace_source` binds annotations only when
`origin == "derived"`; `_wall_origins` likewise marks unverified linkage only
for that origin. For `given` annotations both paths merely check ID existence
and ledger eligibility, then issue their broader checked-provenance PASS.
Treat unsupported annotations as rejected or explicitly unverified; alternatively
define/document a narrower existence-only policy and avoid implying linkage was
checked. The failing tests deliberately accept either rejection or explicit
incompleteness, but never the broader G-93 PASS. These are targeted semantic
scope findings, **not** numerical/ledger/cycle failures masked by other errors.

## Four original transitive controls — executed on `3675bd7f...`

Each selected source has its own exit-0 / zero-FAIL / wall G-10+G-93 PASS control.
The two registry controls are separately acyclic: only in the disposable data,
component size uses the matching panel-71 width/height and declared thickness;
the historical opening-11 conflict is split so C-002 claims only its head.
This is graph calibration, not evidence of an actual builder reading inputs.

| Single mutation | Observed targeted gates; no wall G-10/G-93 PASS |
|---|---|
| Select `structure.x_bay_cm`; assumptions conflict cross-reference 3 C-003 -> C-999 | exit 1; **G-31 FAIL at assumptions cross-reference**; wall **G-93 FAIL** for source eligibility. |
| Select `components[0].size_cm`; its derives_from -> `NO_SUCH_FIELD` | exit 1; **G-93 FAIL at wall origin_inputs naming NO_SUCH_FIELD**, G-31 SKIP and no unrelated G-31 FAIL; both `--dir`/`--file`. |
| Same acyclic source; registry origin_inputs -> `wall_runs[0].thickness_cm` | exit 1; **G-93 FAIL naming the backward directed input**; G-31 SKIP, no unrelated G-31 FAIL. |
| Select `sections[0].points_cm`; massing locked -> superseded, separately draft | exit 1; **G-93 FAIL naming NURBS's `elements[8].z_range_cm` dependency**; G-31 SKIP. |

The unchanged historical registry is cyclic, so it is not used as an acyclic
positive. This audit does not authorize rewriting that fixture.

## Other scoped results and masking

On `3675bd7f...`, with clean controls:

- **Actual conflict/assumption ownership:** replacing the existing upstream
  `structure.x_bay_cm` C-003 with C-004, replacing registry thickness A-023
  with A-024, and changing derived total-height annotation C-001 to C-004
  each produced only **G-93 FAILs** naming the incorrect claim/linkage. These
  reach the wall transitive predicate, not merely another failing ledger check.
- **Wall ledger bindings:** named assumed/conflict wall controls pass. Existing
  wrong IDs, equal-valued wrong owner/path, wrong primary/resolved claims,
  value mismatch and duplicate assumption ID are refused with wall G-10 FAIL
  and G-93 FAIL. **Masking remains:** G-12/13/14 or G-11 often invalidates the
  whole ledger before the inner wall-binding branch. These prove fail-closed
  integration, not independent execution of every `_wall_ledger_binding` branch.
- **Strict JSON at used boundaries:** status duplicates with bad-first AND
  bad-last order in dimensions, massing, NURBS, facade grids, registry,
  assumptions, conflicts and walls yield **G-7 FAIL on the actual file**, no
  same-file G-7 PASS, and no wall G-10/G-93 PASS, in both `--dir` and `--file`.
  A nested used A-001 `value` duplicate is also G-7 FAIL. Invalid dimensions
  produced 11 FAILs rather than the previous 1573; invalid massing still cascaded
  to 149 FAILs. Those counts are diagnostic noise, not additional independent
  detected faults.
- **Precision/overflow:** `10000000000000001.9`,
  `0.10000000000000001`, `1e-9999`, signed overflow, NaN/Infinity,
  integer `9007199254740992` and 5000-digit integer are G-7 FAIL, no wall PASS.
  Loss/overflow/underflow in *used* dimensions and A-001 ledger values likewise
  fail G-7. Replacing a legacy cell boundary with the lossy token or huge integer
  is refused before G-82; **G-82 SKIP, never PASS**, including filtered CLI.
  This is input-boundary evidence, not direct spatial-oracle measurement of a
  0.1 cm gap or recovery of already-rounded floats.
- **Domain epsilons, not parser-masked:** maxima 0.01 cm / 0.001 unit pass;
  zero, negative, boolean, just-over-bound and 10000.0 each fail their precise
  G-93 epsilon path with G-7 PASS. G-10 can correctly remain PASS here because
  it claims provenance, not all numerical geometry. Never infer G-93 PASS from it.
- **Depth:** nested-array additions of depth 100 and 127 pass; 128, 450, 800,
  1200 and 4000 fail **G-7 with the nesting diagnostic**, with no traceback or
  internal G-8 error. Root object is an additional container: depth-127 arrays
  reach the 128-container ceiling. This validates the previous open crash's
  bounded rejection, not unlimited depth support.
- **CLI scope:** unknown/local-only/qualified/malformed roots, duplicate
  dimensions owner, and parent/pipeline duplicate walls are refused.
  `--file` discovers the parent duplicate; G-92 FAIL and G-93 SKIP.
  `--rule G-7/G-10/G-31/G-92/G-93` yields precisely the unfiltered matching rows
  but keeps JSON/process exit 1 when another hidden gate fails.
- **Draft/false PASS:** draft with null unit epsilon is G-93 SKIP; a zero normal
  still reaches its G-93 FAIL. An extra null run yields G-93 FAIL and **G-97
  SKIP**, never a budget PASS for remaining runs only. Flipped normal sign can
  pass static checks, whose detail explicitly leaves physical side unproved.

## G-32 scope and latest coordination controls

Wall-local derived thickness 30 -> 31 with unchanged source remains G-10/G-93
PASS while the exact wall G-32 path is **SKIP**, never PASS: no wall formula is
implemented. A self-cycle of that origin then reaches G-10/G-93 FAIL. Known
upstream height +5 does reach G-32 FAIL and blocks the wall, but other height
rules also fail; that test is not isolated proof of the G-32-to-wall dependency.
Wall-local optional derived conflict annotations, matching or unrelated, remain
G-10/G-93 **SKIP** with exit 0; this conservative policy is not checked linkage.

The coordination note reported two more formula gaps in
`Audit/_phase16-grammar-review-2026-11-02d.md`. Added independent controls are
CLI-only and were run against frozen **`979056a3...`**, no source drift:

1. Select total height, remove optional conflict_ref in **both** control and
   mutant to avoid an unrelated annotation mask, then change only derives_from
   to `site.ground_level_cm`. Clean passes; mutant yields **G-32 FAIL at
   dimensions::building.total_height_cm**, explicitly naming missing
   levels[0/1].height_cm, and wall G-93 FAIL/no G-10 PASS. This is an independently
   observed targeted fix on this snapshot, not evidence for all formula patterns.
2. Select `site.ground_level_cm`; given control passes. Make only its origin
   derived from `site.footprint_width_cm` without an available formula. Exact
   upstream **G-32 SKIP**, wall **G-10/G-93 SKIP**, exit 0 and no FAIL. No false
   wall PASS on this snapshot. This is incomplete lint, not formula verification
   or build acceptance. A full regression against the new source is still required.

## Existing-test review: do not overinterpret green counts

- `test_phase16_p2.py::poly_fixture` checks locked JSON/route shape and clean
  G-92 but not production artifact provenance; a synthetic locked echo can
  satisfy its guard. Do not supply one as a real produced fixture to clear skips.
  This independent harness never uses that guard or a locked poly assembly.
- `test_phase16_p2_cases.py::must_fail` accepts **any** listed rule. Opening
  cases list both G-94 and G-93, so passing counts do not prove both predicates.
  Unknown run/kind, reversed/zero-width u, head-at-sill are schema G-93 cases;
  aggregate acceptance does not prove an opening-bound/overlap G-94 check ran.
  Its shared baseline calibration also is not a fresh post-preparation control
  for every helper-mutated precondition. Target-location matching can succeed
  through detail text rather than the row's own location.
- Earlier `test_phase16_validator_independent.py` first exercises two registry
  mutations on a known-cyclic historical control, correctly labels that control
  non-clean, and later supplies acyclic controls. Count only the latter for
  discrimination. Its local wrong-ledger tests have the integration masking
  noted above. Its annotation test allows PASS **or** SKIP for the matching
  case, so success does not prove linkage was verified.
- `test_phase16_p2_transitive_regression.py` has useful exact target messages and
  corrected acyclic controls, but its `run()` builds `LoadedFile.doc` directly;
  those tests bypass byte loading/strict JSON. Separate CLI tests are necessary.
- `test_phase16_strict_upstream.py` constructs a clearly labelled selective-parser
  counterfactual in temporary files; that is not execution of an earlier actual
  validator. Treat its output accordingly.

No broad historical test suite was rerun by this reviewer. No expected failure
is treated as PASS. Full settled-tree legacy compatibility, spatial coverage,
builder refusal/sentinels, produced artifacts, physical side and live S7/poly
QA remain outside this report's acceptance. **Stop edits on this report.**
