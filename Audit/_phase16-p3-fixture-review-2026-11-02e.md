# P3.1 F01 input-only fixture — independent byte/source review

Reviewed 2026-11-03; artifact name retains the coordinator's 2026-11-02e run identity. **Only this report was written.** No fixture, source, test, previous report, Max, installer, installed-copy, archive or Git operation was changed/performed. This is bounded input review, not emitter acceptance or live geometry evidence.

## Finding

**No substantive source/geometry/provenance discrepancy was found in the actual F01 input bytes reviewed.** The corrected coordinates are present in both the actual analytical source and the fixture, not merely asserted by the fixture report. Independent executions of the unchanged accepted-P2 validator reproduce both stored reports exactly: **exit 1, PASS 62 / FAIL 4 / WARN 0 / SKIP 23**. The four failures are exclusively absent downstream inventory documents, not failures in required wall inputs. This does **not** turn either whole-pipeline result into PASS or accept the unimplemented/live obligations.

### 1. Source and independently recomputed numerical contract

Read the actual `Audit/AGENT_PLAN_poly_surface_shell.md` §G.1 lines 670–693, §A.5 lines 172–179, `Audit/EVIDENCE_2026-10-27.md` lines 201–255, the main decided contract `Audit/_phase16-p3-contract-2026-11-02e.md`, the fixture report, all four actual domain inputs and separate authority/lock/brief/raw validation evidence.

The actual source explicitly states inner **Y=0**, outward **(0,-1,0)**, X/u **0…400 cm**, Z **0…300 cm**, thickness **30 cm**; door **50…150 / 0…210**, window **230…330 / 90…210**. Independent reconstruction from the input opening intervals, not from stored predictions, gives:

| Quantity | Independent result | Source/input agreement |
|---|---|---|
| u stations, cm | `[0,50,150,230,330,400]` | Exact §G.1 line 673 and actual opening bounds |
| Z stations, cm | `[0,90,210,300]` | Exact §G.1 line 673 and actual sill/head values |
| Grid vertices / quads | 24 / 15 | 6×4 vertices, 5×3 cells |
| Opening quads, row-major | `[2,7,9]` | Door crosses two rows; window removes face 9 |
| Active edges / quads | 36 / 12 | Independent edge-incidence enumeration |
| Boundary edges / cycles | 24 / 2 | Every boundary vertex degree 2; explicit connected-component traversal |
| Active area | **87,000 cm²** | `400×300−100×210−100×120` |
| Thickness product | **2,610,000 cm³ = 2.61 m³** | `87,000×30`; analytical prediction, not measured volume |
| Face 9 centre | **[280,0,150] cm** | Correctly converts historical `[2800,0,1500]` mm |
| Expected outer bounds | **min [0,-30,0], max [400,0,300] cm** | Separately sourced -Y direction, not inferred from volume |
| Predicted shelled polygons / triangles | 48 / 96 | Two copies of 12 active quads plus 24 boundary quads; historical comparison only |

The alternative stations `[0,80,140,220,340,400]` are **not** in the fixture. That alternative removes `60×210+120×120=27,000 cm²`, leaving **93,000 cm²**, and is not the cited F01. No source was rewritten to force agreement.

### 2. Authority binds the exact source and wall bytes

The operational authority contains exactly the 12 keys specified by the main contract, with schema `p3-direction-authority-1`. It binds project `phase16-p3-f01`, run `RUN-F01`, the exact `walls.json` hash and the exact actual plan hash. Its endpoints, Z bounds and outward vector equal the actual run and the explicitly read analytical source. The source-location citation identifies §G.1 670–673 and §A.5 172–179 correctly. The actual §A.5 text preserves inner Y=0 and records negative-Y exterior bounds; it is not merely a south-label or winding assertion.

All **9** `input-lock.json.files_sha256` entries match current actual bytes, including the main contract, source plan/evidence, authority, authoring brief and four domain documents. All **14** recorded protected before/after entries in `validation-record.json` also match current bytes; its before and after maps are equal.

**Limit:** this is a source-specific human-authored attestation corroborated by this read, not an authenticated signature, an immutable-filesystem lock or generic automated semantic verification of arbitrary source text. The authority's source path is explicitly repository-root-relative; a consuming adapter must honor that declared base or refuse rather than reinterpret it relative to `project/`. No claim is made here that the evolving input adapter implements that behavior.

### 3. Closed input/provenance and honest source graph

The project directory has **exactly four files**: `assumptions.json`, `conflicts_resolved.json`, `dimensions.json`, `walls.json`; all are locked input documents. There is no assembly echo, manifest, stage output, QA declaration/result or `.ms` anywhere in the fixture tree. The source references openly distinguish the new synthetic support brief from the actual F01 analytical source and the old pavilion brief.

Independent duplicate-key-rejecting JSON reads and explicit key-set comparisons checked the closed wall top level, source object, block, run, opening and three-field topology budget, plus authority format. The wall's six envelope keys are first and in order. Actual wall origins cover the selector, face, two epsilons, one block, one run, two openings and empty returns, all explicitly `given`; there is no fabricated derived wall formula or ledger claim. The main contract's single-block/single-run/no-returns subset is met. Topology ceilings **15 / 12 / 96** equal the independently computed F01 predictions and are stated as fixture ceilings, never measurements/defaults.

`origin_inputs` is exactly `facades[0]`, `levels[0]`, `tolerances`, all owned by `dimensions.json`; the contour resolves uniquely to its one `F-S` facade, with the exact complete run endpoints. The selected facade's derived length/bay count/bay widths have explicit local dependencies. The only assumption is support plot rotation 0, bound to A-001 and explicitly not used as physical direction authority; conflicts are honestly empty. The seed precedence definitions and dimensional/wall tolerances match the actual unchanged seed values. No massing/NURBS/facade-grid/component source path is declared or reached by this wall input.

Fresh accepted-validator results independently corroborate file hygiene, schema and provenance: all four present-file G-1/G-5/G-7 pass; dimensions G-9 reports exactly-once coverage, G-10 reports 16 resolving derived entries, G-32 reports **16 documented formulas recomputed**; walls G-9 reports 27 leaves / 9 origins with exactly-one coverage; walls G-10/G-93/G-94/G-97 pass. G-31 explicitly names the three selected owners above. No G-32 SKIP exists in either actual report. The necessary local formula/ledger checks therefore are not being hidden behind a downstream inventory failure.

**Limit:** synthetic footprint/core/roof/site labels and support values are documented test support choices, not wall-plan facts or requested building geometry. Empty `dimensions.openings` is allowed because the accepted wall grammar does not require a one-to-one join with the independent legacy opening representation. This one-run input intentionally cannot satisfy the original P2 produced-pipeline helper's two-run duplicate-ID coverage; it must not be restamped as a produced assembly to erase that skip.

### 4. Fresh raw validation, not acceptance by the fixture's verifier

Executed directly, with `-B`, bytecode disabled and optimization cleared:

```text
python -B scripts/validate_specs.py --dir Audit/phase16-p3-f01-input-2026-11-02e/project --json
python -B scripts/validate_specs.py --dir Audit/phase16-p3-f01-input-2026-11-02e/project --json --build --warnings-as-errors
```

Both actual subprocesses exit **1** with empty stderr and **PASS 62 / FAIL 4 / WARN 0 / SKIP 23**. Each full decoded report equals its retained `lint-validator.json` or `build-validator.json` exactly. Each has exactly these four FAIL tuples, and no others:

```text
G-1  massing.json               absent inventory document
G-1  nurbs.json                 absent inventory document
G-1  facade_grids.json          absent inventory document
G-1  components_registry.json   absent inventory document
```

These files remain whole-pipeline obligations, but are not dependencies of this standalone wall's actual source closure under the main contract. Bounded S4w admission may explicitly recognize these exact absent-inventory findings without deleting them from raw evidence or waiving any required-input failure. No conclusion follows that arbitrary future G-1 failures can be ignored. Missing assembly/manifest and runtime/QA evidence remain the visible SKIPs; **no runtime PASS** was earned.

The local `verify_inputs.py` was inspected but **not executed**: it writes reports, input-lock and validation-record into the fixture (lines 115–116, 140–165), which would violate this review's read-only fixture ownership. Independent checks were in-memory and direct read-only validator subprocesses. A first overlong here-document was truncated by the shell interface and failed at Python parse time; it executed no checks or writes. The two shorter corrected checks completed normally. No test pass is claimed from the failed invocation.

Hashes of **19 protected existing files**, including every fixture file and accepted validator/plan/evidence/contract/grammar, were equal immediately before and after the two fresh validator runs. No existing file was written by these review commands. Endpoint equality does not claim protection against an unobserved change-and-revert or concurrent hostile writers.

## Exact SHA-256 read-back

Paths below are relative to `Audit/phase16-p3-f01-input-2026-11-02e/` except the explicit repository paths.

| File | SHA-256 |
|---|---|
| `project/walls.json` | `bbd433c76b83a709845c9a20941414bbadc786dbe6ceac907f9259d9876bfa9f` |
| `project/dimensions.json` | `985bd129c01537c5bb5b0632054fe7f24e53237db0a2a4b9bbc01b544e8dfa26` |
| `project/assumptions.json` | `54c0a86e852c3e3a6cbf3ed0beb6dbad420bda67fa7063d250540a1cb28ffcb1` |
| `project/conflicts_resolved.json` | `18627ae616e75aa630eba4647aa414d1a888d6fa72dbf921e7c22c9f260cb836` |
| `direction-authority.json` | `af3686f8105896cddadcee2ad659badab4e250377ca86853dc9a665bb0a201cb` |
| `input-lock.json` | `f4c7b2393e345280aab635567cef5d868921e9aec53b8ea10e7aaa7efcbc8050` |
| `validation-record.json` | `ba41f56582d5b18ad9e87cd6c3cf790f704bc855f2f8bfc7c9a6fc427e174bde` |
| `verify_inputs.py` (read only, not executed) | `53dcacdfa5c8131c7227260710a587bcb5d6a30e076bdfdbdd9be7b63311f64b` |
| Repository `Audit/_phase16-p3-contract-2026-11-02e.md` | `25a017893a2b42bfa5cd22539a6f8ff8e55d8a0dfc2ef4f92d10cc2c2b934aca` |
| Repository `Audit/AGENT_PLAN_poly_surface_shell.md` | `37813bb8f6b8d2e445c69a0424d78997f80a3752303ccffebee802e1d84ee672` |
| Repository `Audit/EVIDENCE_2026-10-27.md` | `2869308638ba8e87766617a572937a769eb325b0a0699075c64d2cb8452141ad` |
| Repository `scripts/validate_specs.py` | `616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f` |

**Disposition:** the reviewed exact input/authority bytes faithfully encode corrected F01 and satisfy the necessary static wall-input/source checks, with explicit whole-pipeline inventory refusal retained. No fixture repair is recommended. Consumer path-base handling, actual emitted/runtime evidence, scene safety/replay and later assembly/QA integration remain outside this review and unaccepted here.
