# Phase 16 P2 — independent spatial G-82 review, 2026-11-02

**Stop state:** P2 is not accepted. This is offline evidence for one immutable source
snapshot, not a live 3ds Max measurement. The working validator changed during the
final run; do not attribute the snapshot result to the newer validator without retesting.

## Stable tested snapshot

`HEAD` was `7951e3f584be83e7655072a11bb193c1982128fe`; relevant source SHA-256:

| File | Tested SHA-256 |
|---|---|
| `scripts/wall_cell_coverage.py` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` |
| `scripts/validate_specs.py` | `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d` |
| `scripts/place_components.py` | `8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8` |
| `scripts/scene_units.py` | `b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2` |
| `scripts/curve_gen.py` | `4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c` |
| `Audit/test_phase16_legacy_coverage.py` | `50b97625085c1ffe38b8514a5c6fc45cbbf2b22827e1d8fbf109290cdbff651a` |
| `Audit/test_phase16_spatial_independent.py` | `44cecac2863a0397fbaccd1f685e75f74c55290a678d8b08032cbc682cc7cfe6` |
| `Audit/test_phase16_legacy_build.py` | `4493b3fcba24d7cbf7895a562128c392c469a9971c711aef78f8ecda9aace15c` |

Python 3.14.4 on Windows. An approved-temp byte snapshot contained these scripts and
copies of all three fixture trees; all snapshot source hashes and fixture manifests
were stable before/after the parallel runs:

| Command in isolated snapshot | Result |
|---|---|
| `python -B Audit/test_phase16_legacy_coverage.py -q` | exit 0; **37 tests OK** |
| `python -B Audit/test_phase16_spatial_independent.py -v` | exit 0; **17 tests, 16 OK, 1 expected failure** |
| `python -B Audit/test_phase16_legacy_build.py -q` | exit 0; **10 tests OK**, including historical comparison |

The expected failure is the inherent already-decoded-float limitation below, **not a
PASS**. The full builder suite's historical source came from git commit
`6c0f27b3a5f6c904bd83d5904a513f33b2fd71ff`. Fixture snapshot manifest algorithm:
SHA-256 of sorted UTF-8 lines `relative/path SHA256\n`; `examples` 13 files
`5191e08f466a844056248c2a3342d2cda87f2356edbc1fdc3bcf40ed45a40d02`, stepped-tower
12 files `19a9f72291e706f987429e064c7a9174532ba1f296f0b0b5f7d9c7713ef9c736`,
form-precision 22 files `aeadffb4a9aef8f6d1b359e6eb51848cdf97e8ac488e6be790bf88c801a4c937`.
Tests use in-memory faults or private temp copies; no repository fixture was written.

At the final status read the validator SHA-256 was
`ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356`, **not** the
tested `f49a6fa9…`. All other listed files still matched their tested hashes. The
newer validator has not been tested by this review. Earlier runs made during concurrent
edits, including a timed-out full builder run, are not accepted as final evidence.

## Spatial and status controls

- Worked example and independently specified 10×2×5 prism passed. Removing
  `WAL-EL-014-C01`, all cells of EL-014, the host, or both cuts and its cells failed;
  equal-volume gap+overlap gave separate gap and overlap failures. Spatial proofs do
  not imply a live-scene proof or a complete wall-envelope census.
- Nonzero gaps up to 0.5 cm were REVIEW, never PASS; 0.500001 cm was FAIL. For the
  actual examples CLI, a 0.1 cm gap gave G-82 WARN+SKIP under lint, FAIL+SKIP with
  `--warnings-as-errors`, and FAIL under `--build`. `--rule` filters displayed rows,
  not global process exit; unrelated errors can make a lint process exit 1.
- No openings/cuts/cells gave oracle NOT_APPLICABLE and G-82 SKIP, not PASS;
  missing massing likewise produced no PASS. A diagonal facade, nonrectangular
  profile, duplicate ID, boolean, nonfinite value and exceeded resource caps failed.
  Unsupported geometry with a cut returns FAIL, not NOT_APPLICABLE.
- Old G-82 volume still infers thickness from the smaller plan extent. For the
  10 cm run, 20 cm thickness, zero-tolerance positive prism, spatial PASS and the
  historical volume subcheck FAIL coexist; G-82 correctly does not mask that failure.

## Numeric findings and change made here

At the user's additional authorization, only `scripts/wall_cell_coverage.py` was
modified outside the two owned audit artifacts. Previously a valid 1601-digit integer
geometry with one missing cell raised `ValueError` while decimal-formatting its
4800-digit volume. The fix preserves exact rational comparisons and the resource
guards; when decimal rendering exceeds Python's digit limit, the diagnostic string is
`exact_hex:<signed hexadecimal numerator>/<hexadecimal denominator>`. The test decodes
the fraction and verifies its exact value, JSON serializability and FAIL. A separate
4401-digit-volume, 1 cm-wide defect remains REVIEW; a complete huge positive remains
PASS, and both atom/work cap negatives remain FAIL. Oversized integer level-index
messages also use a hexadecimal fallback rather than throwing. No geometry is snapped
or tolerated by this formatting change.

**Direct API limitation, still present:** `json.loads` can round
`10000000000000001.9` to `10000000000000002.0` before the oracle sees it. A 0.1 cm
gap then appears exact to the oracle; it cannot infer lost token digits from a Python
float. This is the one expected failure, deliberately retained. Do not claim the
oracle itself recovers lexical precision.

The validator and builder owners subsequently introduced parser defenses. On the
tested hashes, a real-example cell boundary token `134.999999999999999` was refused
before evaluation: validator exit 1, unreadable assembly with a precision error,
G-82 SKIP and **no PASS**. A similarly lossy dimensions opening token made the builder
refuse in both normal/`--build` modes without altering existing output bytes; matching
non-lossy controls succeeded. These observations do not establish broader safety of
the changed parsers, nor do they apply untested to the newer validator hash.

## Legacy compatibility and remaining work

- The unchanged historical example still builds byte-identically to the old builder.
  A no-opening example is refused by **both** old and new builders at existing G-9
  empty-array provenance checks before the new spatial gate; do not call this a new
  end-to-end regression. Direct `verify_spatial_coverage` refuses NOT_APPLICABLE.
- A 0.0000004 cm opening-position perturbation makes the old builder round and build,
  while the new builder refuses REVIEW in both modes. A rectangular host with an
  extra collinear point also builds with the old builder and is refused as unsupported
  by the new oracle. Neither case proves refusal is the wrong policy; compatibility
  and explicit review remain necessary before acceptance.
- Repeat the full suite on the final, stable working validator/builder/oracle hashes;
  reconcile cross-agent numeric-parser results and the previously reported P2
  provenance blockers. No scene, installer, package or existing user files were
  touched. No P3, poly runtime QA or live wall acceptance is claimed.
