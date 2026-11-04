# P3.1 layer and replay protective controls — offline and pending

**Scope:** tests and a main-runner plan, not a production patch or live Max execution.
All files in this directory are newly authored offline controls. No emitted `.ms` from
these tests is written, executed, or offered as a scene fixture. Synthetic inputs and
lexical snippets calibrate detectors only; they are **not** Max observations, produced
wall artifacts, baseline evidence, or acceptance evidence.

## What the offline suite actually checks

From repo root, without writing `.pyc`:

```text
python -B Audit/phase16-p3-replay-tests-2026-11-03f/test_replay_safety.py
```

To run only the synthetic detector calibrations (not the actual-source checks):

```text
python -B Audit/phase16-p3-replay-tests-2026-11-03f/test_replay_safety.py DetectorControls
```

Expected non-zero exit **until a reviewed implementation meets the new layer-source
checks**. Failures are protective findings, not xfails/skips, and no missing capability
is granted by a green old test. Tests print source/helper/test hashes before and after,
plus the in-memory emitted-script hash. Stop all authors and repeat on a frozen tree;
the three-file guard detects changes during its own run, not a future change or all
consumed dependencies. Freeze/hash the *entire* source/test/fixture/contract closure
using main's settled recorder as a separate step; never overwrite an old run directory.

- `DetectorControls`: paired clean and independently mutated **lexical** specimens.
  Calibrate backing vs GI vs exact-ref removal independently, ignored comments/strings
  and unreachable helper decoys, direct/helper name lookup, swallowed errors, tautological
  bounds, and a missing/conditional/diagnostic-only replay barrier. These controls test
  the detector, not whether the suggested syntax is valid MAXScript.
- `ActualRuntimeTests`: generates text via the **actual emitter** in memory from a
  clearly synthetic, input-only straight wall. Requires the node-snapshot call graph to
  access and enumerate the backing `layerAsRefTarg` and nested `INodeGIProperties`,
  route each into a bounded, error-propagating enumeration, explicitly refuse missing
  backing/GI targets, and require recognized exact backing-reference handle round-trip.
  Rejects `getLayerFromName` anywhere on that call
  path as a conservative review trigger. Backing/GI accessor and identity mutations run
  on actual emitted text once those positive checks pass. The probe's `degrade` finding
  motivates enumerating the **backing object**, not hardcoding a property list or assuming
  that a name is its identity. Name can still be compared as state/corroboration.
- Requires an unconditional `INCOMPLETE_REPLAY` refusal inside the COMMITTED branch and
  rejects a NOOP marker while proofs remain incomplete. An actual-source mutation replaces
  the guard with a diagnostic; it must be detected. An intentional barrier removal after
  independent proofs requires explicit contract/test review, not deleting the assertion
  merely to turn the suite green. A separate lexical check detects common **direct** scene,
  registry or mesh-evaluation operations inside that branch, with positive/negative
  controls; it cannot detect side effects hidden inside called helpers.
- Finds explicit guards on the actual source for material, hierarchy, custom attributes,
  controller whitelist and controller-key state; **each condition** is individually
  removed and separately changed to `or true` in memory, with other guards retained as
  controls. This is a narrow static sanity check, **not** proof that the guarded checks
  execute on the right target or that every unsupported state is covered.

The detector is a deliberately small, case-insensitive lexical/parenthesis scanner with
an approximate local call graph. It does **not** parse MAXScript, perform dataflow, prove
reachability, correct target binding, detached copying, equality, complete enumeration,
error behavior, invocation, or code safety. It recognizes common local function,
property-access and first-argument patterns; a different safe strategy may fail it.
Do not reshape production to appease a regex or suppress an unrecognized form; main and
an independent reviewer must inspect and adapt the tests to the actual semantics. A
successful scan can be tricked by dead branches or discarded values and is never
evidence that a backing/GI change is detected. The name check is conservative: if a
legitimate diagnostic lookup exists on the snapshot path, manually establish that exact
reference identity precedes it and that it cannot authorize adoption or deletion.

### Snapshot-specific findings

During active source work, one complete run on `wall_surface_runtime.py` SHA-256
`123c567e45643b0f536dc4d0ad0d443a4f365b4bd6d32bfff8e969052f20761f` and
test SHA-256 `833e24821c89a18070eb325401150c41d7d884b38cc6d1a1fed1c5d6b66874ff`
had stable before/after hashes, **14 methods, exit 1 with 7 reported failures**: backing
and GI enumeration were not recognized (2), exact backing identity was not recognized
(1), neither target reached a recognized guarded reader (2), and explicit nonmissing
guards were not recognized for either (2). The seven detector-control methods and four
other actual-source methods passed. Source was being edited concurrently;
**not a settled run**. Repeat the command after all edits stop. Do not treat this snapshot
finding as proof about later source.

Main's separately retained actual default-layer read-only observation is
`Audit/_phase16-p3-layer-readonly-2026-11-03f.json`: one backing layer had 34 enumerated
properties vs 33 on its interface, including backing-only `degrade`, and one nested GI
interface had 18 readable properties. This was **not** detached-state comparison,
mutation discrimination, distinct-layer proof, dependency completeness, or replay.
Earlier authentic Main03 failed the LayerProperties-to-MaxObject conversion, cleaned
its exact attempted node and left the earlier-process lease POISONED; that historical
result is not a successful wall or NOOP. See the handoff and current continuation note
for process discontinuity; never reconstruct, remove, adopt, or retry that lease.

## Main-only runner plan — no executable Max snippets here

1. **Freeze and independently review.** Stop source, fixture, evidence and test writers;
   record exact hashes for the contract, all production dependencies, test suite and the
   intended new artifact pair; run the offline command above and the existing
   `python -B Audit/test_phase16_p3_runtime.py` plus the settled P3 suites. Report each
   result, SKIP/xfail and drift separately. A legacy structural test may require honest
   adaptation for a changed helper shape; do not weaken it to hide a missing gate. A green
   offline run is not a Max run. Recheck hash-stability after all suites, inspect raw logs.
2. **Fresh live entry and permission.** Main alone checks scene name/path, units **type,
   scale and factor**, selection, census, dirty state, exact lease/global state and the
   external witness. No reset/save/dirty-flag clearing, backup access, layer/material edits
   on user data or auto-adoption/re-arm. The earlier POISONED lease belonged to an earlier
   process; its absence now is not a clean replay or authorization to recreate it. If the
   current context is not independently safe and authorized, stop and report INCOMPLETE.
3. **Calibrate layer reader, sequential bounded main-only operations.** A clean unchanged
   positive must compare detached typed snapshots and exact backing reference/handle
   round-trip; compare re-reads on the same object and discriminate a distinct layer. Test
   changed backing-only `degrade` and an independently selected GI field, verifying that
   the target was actually editable/read back before replay and that other gates stay valid.
   Test same-name replacement or collision separately, proving same spelling cannot restore
   identity; do not assume Max permits duplicate layer names. If safe reversible controls
   cannot be arranged within authorized, exact-owned test state, mark them INCOMPLETE.
   Per-target unreadable/throw/undefined, enumeration/depth/count overflows, unknown nested
   value class and unexpected parent/child/dependency states must explicitly refuse, not
   become equal missing values. Parent, membership, reference/dependency direction, nested
   GI and mutable properties still need calibrated proofs: one 33/34/18 count is not a
   completeness guarantee. Include known-good and bogus-name controls and preserve raw
   output, returned classes and exceptions independently of transport success.
4. **Keep replay blocked.** `INCOMPLETE_REPLAY` stays unconditional until independent,
   complete specified-normal/native mesh metadata, controller/stack/dependency, identity
   and lease-lifecycle proofs exist. Cheap unsupported stack/controller/census checks must
   run before evaluated geometry. Unknown/unreadable state refuses; bounded partial
   equality is not broad edit-safety. A source scan cannot justify barrier removal.
5. **Only after prerequisites:** build a fresh non-overwriting authentic artifact pair and
   a separately reviewed explicit lease for the freshly inspected authorized empty scene;
   hash/read-hold/recheck files as in the contract. Main alone fileIns the **actual** emitted
   pair under the externally held exact witness; inspect raw bridge errors, `__MCP_MS_ERR__`
   and cleanup/residual state. No automatic recovery after failed creation. Independently
   measure F01 direction, area, volume, topology, voids, bounds, stack and census. Only
   after complete replay proof, run the contract's **three actual clean no-op replays** and
   paired target-specific geometry/transform/material/stack/layer/identity/dependency/
   collision negatives. For each negative capture the already-edited state first, prove the
   intended guard was reached with the other guards valid, and compare exact post-refusal
   state, neighbors, lease and dirty state. Teardown only exact current-attempt-owned nodes
   under applicable guards; report uncertainty/residue rather than deleting by name.

Any timeout, unresolved disposal/cleanup, unknown reader, missing proof, changed source or
test, or altered context is **INCOMPLETE**, not PASS. F02+ fixtures, route integration,
poly QA and the original 21 P2 skips remain separate; no fabricated fixture closes them.
