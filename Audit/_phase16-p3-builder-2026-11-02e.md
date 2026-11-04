# P3.1 orchestrating builder — working integration report, 2026-11-02e

Implemented and independently exercised offline within the owned coordinator
boundary. This is **not live geometry acceptance or Phase 16 completion**.
Owned files only: `scripts/build_wall_surface.py`, `Audit/test_phase16_p3_builder.py`, this report.

## Minimal integration interface requested

- Inputs (actual implemented API): `load_inputs(project_dir, *, namespace,
  system_type, system_scale)` returns `walls`, `dimensions`, `input_snapshots`
  (filename -> exact bytes), `input_hashes` (filename -> SHA-256), `input_sources`
  (stem -> original absolute path); `verify_inputs_unchanged(snapshot)` rechecks
  original membership/path/bytes. Coordinator additionally reparses snapshot bytes,
  compares both consumed documents, and binds absolute-path raw-byte hashes.
- Runtime: `build_plan(walls, dimensions)`; `generate_script(plan, identity,
  namespace, expected_units) -> str | bytes`. `identity` is a lowercase SHA-256
  string shared with the manifest, not the manifest hash. `expected_units` has
  `system_type`, `system_scale`, `cm_per_unit`, `units_per_cm`.
  Plan must expose JSON-safe `predictions`, `node_names` (or a `node_names(namespace)`
  callable), and may expose `subset`; actual runtime naming is deterministically
  `<namespace>__wall`, subset `single_standalone_straight_inner_wall`.
  Topology budgets come from the wall input, not predictions.
- Publisher: `publish_new_directory(out_dir: Path, artifacts: dict[str, bytes])`
  returns `{filename: raw_byte_sha256}` after readback/no-replace publication.
- Authority `source_file`: **process-current-working-directory-relative** (explicit
  coordinator decision), or an absolute local path; no directory guessing/fallback.
  Invoke F01 CLI from repository root. Both raw source token and resolved canonical
  path are retained in the manifest/identity; actual source bytes are hashed.
  This supersedes provisional authority-directory/repository-root-relative notes. No traversal,
  ambiguous Windows path components, symlinks,
  junctions, or other reparse points. Source bytes are independently read/hashed;
  no arbitrary source/formula text is executed or claimed semantically proven.

## Implemented boundary

- Required flags only, no option abbreviation/duplicate flags/draft/force. Namespace
  is exact ASCII; SystemType is exact canonical lowercase, scale uses the unchanged
  accepted-P2 strict JSON parser. Type/scale/factor remain separate in identity and
  runtime configuration, including equal-factor/different-pair discriminators.
- Closed 12-field authority, finite/nonboolean exact numeric comparisons against
  independently parsed wall values, exact wall/source/record byte hashes. Source
  attestation is **not automated semantic proof**; arbitrary source text is never
  evaluated. Independent physical-source review remains main/oracle's obligation.
- Snapshot documents are reparsed with accepted-P2 `strict_json_loads` and compared
  against the adapter's documents; raw byte hashes are retained without JSON
  reserialization laundering. Original input/authority/source/code/contract hashes
  are rechecked before publication; adapter rechecks inventory/path membership.
- Identity contains canonical source/configuration/dependency-code/contract hashes.
  Local helper import closure includes `from ... import function` dependencies;
  unrelated preimported modules do not change identity. Stdlib/interpreter bytes
  are not a claimed reproducible environment. Manifest hashes script, script binds
  canonical identity, no manifest/script circular-hash requirement.
- Manifest is `produced_offline_unverified`, never locked/assembly-spec echo. It
  separates declared budgets, planning ceilings, tighter F01 initial execution
  admission, declared/geometric outward vectors and unmeasured predictions, and
  records exact expected units, node name, declared stack and code/source hashes.
- Pair is assembled in memory and limited to **2 MiB combined** before calling the
  generic publisher (stricter than helper's separate 32 MiB limits). Output must
  be a nonexistent local directory disjoint from project and all consumed paths.
  Rejects ambiguous/traversing/device/UNC/alias paths and existing reparse/link
  ancestors before snapshot/publication; source hard links are refused too.
  Publisher supplies actual Windows directory-level no-replace commit; coordinator
  independently reads both published bytes. It never deletes/replaces old output.

## Executed tests (not final coordinator acceptance)

`python -B Audit/test_phase16_p3_builder.py -q`: latest observed **34 tests OK**,
1.771 s, no unittest skips, before the final explicit declared-stack metadata add.
The final frozen-source repeat and hashes are recorded below after that addition.

Coverage includes each authority field conflict independently, finite/boolean/pair
and closed-record failures, strict duplicate/precision/overflow/depth JSON,
untrusted-text nonexecution, exact source byte vs normalized-text differences,
CWD-only source resolution and no fallback, namespace/unknown/duplicate flags,
units/scale/equal-factor pairs, temp reparse positive/negative controls, snapshot
and late-source drift, source/code hash drift, deterministic identity/hash linkage,
existing-output preservation and strict 2 MiB pair refusal. Optional real symlink/
hardlink creation depends on host capability; mocked reparse control is mandatory
and executed, so no unrun real junction test is claimed.

Actual runtime and actual publisher integration (not mocks) ran on temp-only
coordinator data; this is separate from explicitly labelled fake seam tests.
**Authentic F01 integration also executed**: source fixture copied into private
temporary project, authority copied separately, original cited plan read at the
explicit repository-root CWD. Actual `load_inputs`, `build_plan`, `generate_script`
and Windows publisher ran, repeated into another new directory with identical
artifact hashes. Existing first directory refused without changing its pair.
Actual CLI subprocess also emitted identical bytes. Original fixture/authority/
cited plan hashes remained equal before/after. Predicted values: grid 24 vertices,
38 edges/15 polygons; active 12 polygons/36 edges/B24; area 87,000 cm²; evaluated
48 polygons/96 triangles; volume 2,610,000 cm³. These are **offline predictions**.

## Limitations / main hand-off

No Max calls, fileIn, runtime replay/edit/cleanup tests, installer or git command.
No arbitrary-writer lock/crash-durability guarantee; observed drift checks operate
under controlled local single-writer assumptions. A changed post-commit pair is
retained and reported for recovery, never automatically deleted. Future acceptance
must pin/read-check the actual published pair immediately before main's fileIn and
independently prove physical direction/topology/void/stack/replay against the source.
Contract/other module authors may still change bytes: regenerate/retest after they
freeze; all artifact identities deliberately change on dependency/contract drift.
CHECKPOINT update remains main's ownership, not performed by this agent.

## Final frozen-source repeat (2026-11-02e task; host date rolled to 2026-11-03)

A Python `-B` wrapper hashed 16 actual coordinator/dependency/contract/fixture/source
files before and after running `python -B Audit/test_phase16_p3_builder.py -q`.
Actual result: **34 tests / 1.759 s / OK / exit 0 / drift `{}`**. This includes the
final declared-stack metadata and actual CLI/F01/Windows publication integrations.
No test skip, expected failure or fabricated produced fixture was used.

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
1a4e77a6d4ceae9c8f0d7c69152400238bd04635b7252ff3dd2ca5f99c0a43a5 Audit/test_phase16_p3_builder.py
9354e159809a587248cf46f1fa20776047f01f6054035b8ea6617c89f583a0a2 scripts/wall_surface_inputs.py
f213e133b37e7a562fa2e045f42d599aca089962b23732c9d0c43f7f043ceae3 scripts/wall_surface_runtime.py
c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027 scripts/wall_surface_publish.py
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f scripts/validate_specs.py
b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2 scripts/scene_units.py
4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c scripts/curve_gen.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f Audit/_phase16-p3-contract-2026-11-02e.md
bbd433c76b83a709845c9a20941414bbadc786dbe6ceac907f9259d9876bfa9f F01 project/walls.json
985bd129c01537c5bb5b0632054fe7f24e53237db0a2a4b9bbc01b544e8dfa26 F01 project/dimensions.json
54c0a86e852c3e3a6cbf3ed0beb6dbad420bda67fa7063d250540a1cb28ffcb1 F01 project/assumptions.json
18627ae616e75aa630eba4647aa414d1a888d6fa72dbf921e7c22c9f260cb836 F01 project/conflicts_resolved.json
af3686f8105896cddadcee2ad659badab4e250377ca86853dc9a665bb0a201cb F01 direction-authority.json
37813bb8f6b8d2e445c69a0424d78997f80a3752303ccffebee802e1d84ee672 Audit/AGENT_PLAN_poly_surface_shell.md
```

After this repeat only this report was updated; executable/test bytes above remain
the tested snapshot. Temporary outputs were cleaned by their exact owned temporary
directory contexts; no permanent produced artifact is retained or offered for Max.
