# Phase16 P3 independent adversarial review — 2026-11-02e

**PRELIMINARY / NOT ACCEPTED.** This report and
`Audit/test_phase16_p3_independent.py` are the only owned files. No production
repairs, accepted-P2 changes, real-fixture edits, Max calls, installs or git
writes occurred. Frozen actual production bytes execute only in isolated approved
temporary directories. Inputs are copied, not fabricated produced assemblies.

## STOP / frozen independent-suite hand-off

Per coordinator instruction, source/test editing and repeated early runs STOPPED.
The 22-method suite is ready for main's stable-tree recorder. **Test 22 retains
the original protective total-pair <=2 MiB refusal assertion unchanged.**
Coordinator approved a publisher-owned repair; no repair acceptance is claimed.
The immediately preceding repeat ran **22 methods: 21 OK / 1 FAIL / 0 ERROR /
0 SKIP**, 131 recorded events, 116.713 s, exit 1. It actually executed OLD publisher
`c43a9e8b...`; after-hash observed publisher `7868798b...` changing during that
run. It did not execute the repaired helper. Runtime was stable in this repeat
at `5df101ab...`. The full source/fixture before/after hashes and drift were printed.

Read-only hashes at STOP (not a tested/final acceptance manifest):

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
03c9accba70648e677fdb837a436256186d2535f438e553910f38cc8725f8c59 scripts/wall_surface_inputs.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
5df101ab21f935d63f061c2f7d7c18659aba3e359970b6d3bb9516b873372ba2 scripts/wall_surface_runtime.py
ddcb702d1f0dd6152cf87714657dac321679abb6472c7e9714d9fe8d48e13dba Audit/test_phase16_p3_independent.py
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f Audit/_phase16-p3-contract-2026-11-02e.md
```

No further run until main explicitly requests it; main will regenerate any old
publisher-bound artifact and assess the final stable recorder run. I-3 below is
the reproduced OLD-source finding, now **repair pending verification**.

## Latest executed result — 22-method run (supersedes earlier runs)

Command: `python -B Audit/test_phase16_p3_independent.py -v` (117.587 s).
**22 methods: 21 OK / 1 FAIL / 0 ERROR / 0 SKIP; 131 reached recorded case events;
overall exit 1.** The source drift guard independently detected
`scripts/wall_surface_runtime.py` changing during the run. The frozen source
actually executed was:

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 build_wall_surface.py
03c9accba70648e677fdb837a436256186d2535f438e553910f38cc8725f8c59 wall_surface_inputs.py
c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027 wall_surface_publish.py
d88ac5daf0098efca9fd6befca51ad4cab8b83ed74089e2f443f5cce93268792 wall_surface_runtime.py
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f coordinator contract
```

### I-3 OPEN: direct publisher lacks the contract's total-pair 2 MiB ceiling

`test_22_publisher_direct_total_two_mib_contract` first executes successful actual
Windows helper publication with a small pair. It then supplies two immutable byte
strings, each **1,126,400 bytes** (1,100 KiB, individually below 2 MiB), total
**2,252,800 bytes**, through the actual helper. Expected protective refusal does
not occur: the actual output directory is published. The assertion fails with
`Exception not raised : publisher must enforce contract pair <=2 MiB`.
Current helper `MAX_ARTIFACT_BYTES` is 32 MiB **per file**, without a pair sum.
No source repair was made; the failing protective test remains red.

**Important scope:** this is a helper-level contract gap, not an observed public
CLI bypass. `test_19` proves the public CLI refuses an actually generated script
padded beyond the pair ceiling. The discriminating `test_21` separately proves
the CLI's **sum** limit: real generated script + 1,400 KiB data comment, valid
authority source locator + 800 KiB data, both output files individually under
2 MiB but pair sum over 2 MiB, produces `artifact pair exceeds 2 MiB`; no pair
is published. Authority and underlying source are genuinely consumed and hashed.

### Explicit arm clause checked offline, not live

`test_20` executes the actual `generate_arm_script()` and actual emitted geometry
source. Clean F01 CLI emission precedes it. Geometry requires the separately
armed registry and contains no `globalVars.set registryKey`; arm refuses existing
registry/nonempty scene, preserves identical identity/binding/registry literals,
and invalid/short/long/control/injection/non-ASCII nonce strings refuse. The
assertions do **not** execute Max or prove missing/replaced registry, exact witness,
poisoned lease, or current scene edit detection. Those remain main's live gates.

Actual F01 output predictions were checked against independently read analytical
source constants: 24/38/15 grid, 3 removed, 12 active faces/36 edges/24 boundary
edges, 87,000 cm², 48/96 evaluated polygons/triangles, 2,610,000 cm³,
`[[0,-30,0],[400,0,300]]` cm bounds and geometric outward -Y. They are still
**predictions**, not measured current geometry. Same-input actual artifact bytes
are deterministic across two distinct new run directories.

Main's physical-source decision was read:
`Audit/_phase16-p3-f01-main-authority-review-2026-11-02e.json` status
`MAIN_REVIEWED_SYNTHETIC_SOURCE_AUTHORITY_NOT_RUNTIME`; the exact actual source,
wall and authority byte hashes match the independently used original inputs.
No production files, accepted-P2 files or real fixtures were modified.

## Prior expanded result — 19 methods (historical)

Latest expanded suite: **19 methods OK, 126 reached case events, 0 failures,
0 errors, 0 skips**, 111.747 s, but overall **exit 1 / preliminary** because the
end-of-run source guard detected concurrent changes in `build_wall_surface.py`,
`wall_surface_inputs.py`, and `wall_surface_runtime.py`. The actual tested frozen
source hashes were:

```text
2c2944b7e0e2bc969e75ef69a16054822a8eefdc9330a862ea24a8a565b7ee24 build_wall_surface.py
5c1b4b400a0c435e9fd971c2364c249eb3dccc5e2d912562eed4b33ebf527a89 wall_surface_inputs.py
c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027 wall_surface_publish.py
805353cafffc16b1ab5cd9a6df35aefa4395412f3ca09b945870780187b4809b wall_surface_runtime.py
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f coordinator contract
```

The complete authentic CLI adversarial cases now ran after successful clean
controls, including source/upstream drift injected **after real script generation**,
native Float32 refusal, source/artifact-pair limits, and unchanged private victims.
This did not accept the still-changing tree. A final repeat is required after
authors stop. The additional source-derived numeric prediction assertions added
after this run executed successfully in the newer 22-method run above.

The coordinator explicitly revised the path contract to **process-CWD-relative**
source paths, no fallback search. The original F01 record now conforms when invoked
from repo root; I-1 is historical/resolved by this approved contract decision, not
a remaining author-path repair request. Tests use an absolute private source path
and identical raw bytes, so they do not depend on caller CWD. I-2 no longer blocks
the latest actual source clean control; no reviewer production repair was made.

## Initial executed history

1. Initial invocation while runtime was absent: exit 2, explicit
   `NOT RUN: missing production modules: wall_surface_runtime.py`; no skip/PASS.
2. After runtime arrived: 15 test methods, 12 errors before CLI due to the F01
   source-authority path mismatch below; the three real publisher tests passed.
3. With an explicitly documented, test-private source rebinding: 15 methods,
   **12 FAIL / 0 ERROR / 0 SKIP**, 3 publisher methods OK. All 12 public-path
   methods fail at their required clean emission control; their later adversarial
   CLI assertions are **NOT RUN**, not presumed protective passes.
   Direct runtime clean planning/script generation plus near-station,
   large-world Float32 and seventh-opening operational refusals executed.
   Source drift during this concurrent authoring run was detected:
   `scripts/build_wall_surface.py`; this is not frozen final acceptance.

Command: `python -B Audit/test_phase16_p3_independent.py -v`.
The script prints exact source/fixture SHA-256 manifests, each reached calibrated
case event and final drift/result JSON to stderr. It exits nonzero on any failure,
error, skip or source/fixture drift. Missing dependencies exit 2, never silently
remove functional assertions. A later settled run supersedes these preliminary
numbers; no final settled run is claimed here yet.

## Initial reproduced blockers (historical, see latest result)

### I-1: original operational authority path did not obey the initial contract

`Audit/phase16-p3-f01-input-2026-11-02e/direction-authority.json` originally uses
`source_file: "Audit/AGENT_PLAN_poly_surface_shell.md"`, documented as
repository-root-relative in the fixture README. The frozen coordinator contract
and builder resolve relative paths from the **authority record's directory**.
That joined path does not exist. Production refuses this request; the test does
not repair the real record. For additional independent tests it reads the actual
repository plan, verifies its exact declared hash, copies the identical raw bytes
into the private request, and explicitly rebinds the private record to that source.
This adaptation is visible in `fixture_source()` and `project()`; it is not a claim
that the original operational fixture is executable unchanged.

### I-2: valid empty legacy opening representation blocks F01 clean control

Input adapter SHA `43b030d156eab30dd93aeff5db12b91d3f0938a294d48dbed23734f4b2d11c6b`
refuses the real F01 dimensions `openings=[]` as unverified input gates:

```text
G-26 dimensions.json: openings is empty; nothing to test (07 section 5.11 allows it)
G-27 dimensions.json: openings is empty; nothing to fit
G-28 dimensions.json: openings is empty; nothing to collide
```

The contract explicitly does not require wall rough openings to be invented in
the legacy dimensions representation. This prevents the mandated authentic clean
CLI control. No helper patch/waiver was made by this reviewer.

## Independently executed protective publisher cases

Actual `publish_new_directory()` clean Windows publication/readback hashes passed,
followed by these targeted negatives (not a claim of naturally scheduled races):

- A collision created immediately inside the actual `os.rename` commit hook:
  real Windows no-replace rename refuses; foreign `private.bin` sentinel is
  unchanged; only owned staging is recovered, no partial pair.
- Second artifact exclusive-open `PermissionError`: no output directory/partial
  pair published, owned staging recovered; clean helper control ran first.
- Private stage artifact substitution before pair verification: refusal preserves
  the substituted private sentinel and parked owned original; recovery evidence
  path is reported rather than deleting foreign data.

## Coverage implemented, public-path assertions awaiting clean control

Actual-output determinism/script hash/source-sign checks; strict raw boolean,
string, nonfinite, overflow, underflow, lossy integer/decimal and duplicate/deep
JSON; closed wall/run/budget/authority schemas; locked status/route/reference;
missing/unknown/derived wall provenance and reached upstream unknown formulas;
known formula arithmetic/dependency faults; source hash/missing/path/authority
binding and outward flip; full larger real fixture/extra block/run/return refusal;
all three per-run lower budgets; namespace/units/scale/duplicate CLI and injection
strings; existing empty/victim/actual-run output preservation; native Float32
overflow and direct runtime numerical/operational refusals. Tests assert desired
protection, never current unsafe behavior, xfail or fabricated output echoes.

## Scope and remaining limits

No test here executes Max or proves current scene ownership/replay, physical
geometry, live unit guards, topology/voids or cleanup. Raw source text is read
independently for authentic F01 -Y authority, not inferred from winding/manifest.
The public contract expressly treats arbitrary source records as human-authored
attestations, not an automated semantic-source oracle. A dishonest, coherently
flipped attestation requires the separate independent physical oracle/live gate;
hash agreement alone must not be reported as source-semantic proof.
