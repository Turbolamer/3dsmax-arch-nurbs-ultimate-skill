# P3.1 bounded emitter contract — coordinator decisions, 2026-11-02e

This records implementation decisions, not completed acceptance. P2 is accepted offline. Necessary Max work is authorized by the user; only main operates Max. Preserve all prior files and accepted P2 executable bytes. No installation/package update until the whole method is ready.

## First supported subset

- One complete standalone straight vertical inner-reference wall: exactly one block and one run, `upper_returns=[]`, contour `dimensions.json:facades:<id>`, explicit poly selector. No subset extraction from a larger building; no corners, returns, instances, local-dividing mesh, host hiding or automatic assembly changes.
- Rectangular openings strictly internal in u, below the top; sill may equal zero. Strictly separated u intervals; exact shared stations permitted, distinct near-stations refused. No coordinates snapped or silently changed.
- Closed existing walls schema is unchanged. Required locked input/provenance/formula gates must pass. Expected missing future output/runtime evidence does not require an output on input. Existing contradictory output is refused. Unsupported required source formulas cause refusal.
- Initial operational ceiling independent of input topology budgets: at most 32 grid polygons, 64 grid vertices, 256 evaluated triangles, 6 openings, one modifier, one created scene node. Any lower declared budget still applies. These are refusal ceilings, not architecture defaults. F01 is within these limits. Short sequential main-thread calls only; no general throughput claim.

## Public boundary and authority

CLI: `python -B scripts/build_wall_surface.py --in PROJECT --out NEW_RUN_DIR --namespace TOKEN --system-type millimeters --system-scale 1 --direction-authority RECORD.json`.

`--out` must not exist and must not contain inputs; repeated publication to the same directory is refused. No `--force` or draft mode. Namespace is explicit ASCII `[A-Za-z][A-Za-z0-9_]{0,39}`. Unknown flags/units and ambiguous strings refuse. Expected type, scale and factor are separately checked before every scene mutation/no-op inspection; no unit setting.

Direction authority is a separate operational JSON record, NOT a new wall-spec field. Closed format `schema_version: "p3-direction-authority-1"`, `project`, `wall_run_id`, `walls_sha256`, `source_file`, `source_sha256`, `source_location`, `inner_start_cm` (2), `inner_end_cm` (2), `base_z_cm`, `top_z_cm`, `outward` (2). Source file is read, byte-hashed, and retained in the input lock. The authority values are separately compared with wall declaration. Absence/conflict refuses. This is an explicit human-authored source attestation, NOT automated semantic proof that arbitrary source text agrees. The synthetic F01 authority must cite the actual analytical plan specifying Y=0 and outward -Y. Independent oracle must read/check that source and not derive physical sign from the supplied wall vector, winding, volume or manifest.

Path convention: a relative `source_file` is resolved once against the explicit process working directory, with no fallback search; absolute local paths are admitted only under the same no-reparse policy. Record the original token and resolved path. CLI usage must state this CWD convention.

## Geometry, files and publication

- Deterministic global station grid in cm; analytical P(u,v) and outward winding. Track actual returned vertex/face IDs, gather opening faces before one deletion; validate each API return. Base has shared IDs. Add exactly one Shell with inner 0, outer thickness*factor, segments 1. No Extrude/Boolean. Actual output must be fileIn-ed and measured.
- New artifact pair `wall_surface.json` and `wall_surface.ms`. Manifest `schema_version: "p3-wall-surface-1"`, `spec: "wall_surface"`, status `produced_offline_unverified`, project/route/subset, owner namespace/id, input hashes/source authority, expected units/factor, node names, declared budgets and separately-labelled predictions. Offline production is NOT locked scene acceptance or a fabricated assembly echo. MAXScript class names may occur in generated operational artifact, not domain spec.
- Manifest contains script SHA-256; script contains canonical input/contract identity but not manifest SHA (avoid circular hashes). Evidence record later links both exact artifact hashes. Output pair is built in memory then atomically published as a new directory with Windows no-replace rename and read-back hashes; no existing data overwritten. Recovered failures clean only exact owned staging artifacts; retain recovery path if cleanup fails. No arbitrary adversarial-race/crash-durability claim.

## Scene ownership and replay

- Session-bounded registry stores exact created node references/handles, artifact identity, namespace and measured baseline. No delete-by-name/prefix. Namespace alone never proves ownership. Node tag is corroboration, not authority. Duplicate name/tag, absent/invalid registry, changed inputs/artifact/units or ambiguous identity causes pre-mutation refusal.
- Replay is identical-input no-op only; never replace/delete an existing wall. Require actual baseline equality for geometry/base refs, topology, stack and all modifier properties/enabled states, transform/controller state, material, layer, visibility/renderability, parent/children, user props and supported dependencies. Missing ability to compare a state must fail closed, not report unchanged. Additional conservative refusal on changed scene census is allowed.
- No save/load/merge/restart durability is claimed initially. Any identity uncertainty after those operations refuses. No reset, save, units/layer/material change, host hiding or unrelated node changes.
- Failure cleanup uses only exact new-node references created during the current attempt, verifies removal, and reports INCOMPLETE/residual identity on cleanup failure. No undo atomicity claim. Manual edits remain untouched on refused replay.

## Reviewed operational clarifications

Independent review: `Audit/_phase16-p3-contract-review-2026-11-02e.md` (read by main).

- Initial fixture execution admission is tighter than the emitter's absolute planning caps: F01 only, <=24 grid vertices, <=15 grid quads, <=96 evaluated triangles, <=2 openings. Broader admitted planning counts are NOT live-calibrated. Input JSON <=2 MiB each, total consumed source <=16 MiB, artifact pair <=2 MiB, scene census <=64 nodes for initial runtime. Refuse excess, not truncate.
- Normalize geometric perpendicular from exact run endpoints and select sign using the separately corroborated supplied/authority vectors. Shell follows the geometric normal, not a skew near-unit declaration. Report both vectors; compare using numeric_unit_epsilon.
- Execution threat model: controlled local private run directory, single writer, read-back hashes immediately before fileIn. No arbitrary concurrent-writer or immutable-handle lock claim. Offline adapter must validate/emit from one private raw-byte snapshot, not validate path A then re-open changed path B; verify original closure hashes before publication and refuse observed drift. An approved manifest hash is not a filesystem lock.
- Replay baseline work itself must remain <=64 scene nodes and bounded mesh/stack/state sizes. Unsupported controllers/dependencies/state serialization causes refusal. No claim of universal scene edit detection beyond explicitly read/tested state. Name resolution only after identity proof; never deletion authority.
- Runtime-design §2 lease clarification approved: first creation requires main to explicitly arm a fresh one-use lease in a freshly inspected **empty controlled test scene**. Generated geometry script never auto-arms an undefined/lost registry. Missing/replaced registry always refuses; main retains an external exact lease-instance witness. This narrows initial runtime admission, not eventual coexistence design. No automatic re-arm after failure/ambiguity. Complete mesh-metadata/controller/dependency readback remains an acceptance gate; a small transform/stack fingerprint cannot be advertised as broad arbitrary-edit safety.
- Main must inspect raw bridge `ok/error`, returned `__MCP_MS_ERR__` marker and diagnostic exceptions, not a transport success flag alone. File emission, predicted counts and P1 historical facts are not current runtime PASS.

## Acceptance boundaries

P3.1 requires frozen offline tests, authentic emitted F01 fileIn and independent direction/area/volume/topology/void/bounds/census/stack checks; unit mismatches including equal-factor different pair; 3 actual no-op replays; target-specific edit/collision negative controls and exact cleanup. Capture/evidence absence remains INCOMPLETE. P3.1 does not accept F02–F05/F08, route assembly integration or future independent poly QA profile. Original 21 P2 skips need later authentic pipeline/QA, not invented echoes.
