# P3.1 standalone layer reader candidate — INCOMPLETE

## Scope and disposition

This directory is a standalone candidate only. It was not `fileIn`-ed, parsed by Max,
timed, installed, added to the package, or integrated into
`scripts/wall_surface_runtime.py`. No live call was made by this work. The reader's
successful offline-model result is deliberately labelled `INCOMPLETE`; the emitter
fragment throws before construction and the replay fragment remains
`INCOMPLETE_REPLAY`.

Evidence used: `Audit/phase16-p3-main-probes-2026-11-03f/layer-owned.ms` and its
successful result, plus the read-only enumeration in
`Audit/_phase16-p3-layer-readonly-2026-11-03f.json`. The observed backing reference
round-trips a handle in that one process; its exact reference is kept separately from
the `LayerProperties` mixin. The detached profiles are exactly the observed 33 layer
interface properties, 34 backing properties (including `degrade`), and 18 nested GI
properties. This is not a claim of all native, renderer, controller, or plugin state.

## Candidate behavior

* `layer_reader.ms` defines local `p3LayerSnapshot` and `p3LayerSame` helpers intended
  to be pasted inside an existing `fileIn` wrapper. It has no globals, file I/O,
  name lookup, `execute`, deletion, layer creation, or cleanup authority.
* Snapshot admission requires independently retained exact node/backing/root/manager
  references, exact handle round-trips, `node.layer` → backing identity, the exact
  observed property-name/type profiles, nested GI reads, `layerAsRefTarg` as an exact
  reference record without backing recursion, finite typed detached values, exact
  node membership, no parent/children, zero outgoing backing refs, and a bounded
  dependency set containing only root/LayerManager/(optional exact node).
* The current observed empty default-layer membership (`members.count == 0`) is not
  generalized: this profile requires one exact member node. A foreign, missing,
  duplicate, unknown, or otherwise unclassified member/dependency yields
  `INCOMPLETE`, not equality. Names are copied as state and never used as authority.
* Double reads are compared only after both reads are detached and independently
  validated. Unknown properties/types, enumeration drift, getter errors, NaN or
  non-finite values, changed handles, unsupported hierarchy/dependencies, or stale
  identity records fail closed. `p3LayerSame` can say `OBSERVED_MATCH` or
  `OBSERVED_DIFFERENT` only under the outer `INCOMPLETE` status; it never returns a
  replay-safe/unchanged claim.

## Python emitter fragment

`emitter_fragment.py` verifies the exact MAXScript SHA-256 before returning source,
provides a wrapper example that fails closed, and contains explicit initial/replay
fragments. It accepts no caller-provided script/name/lookup text and cannot call Max.
The fragment is illustrative integration data, not a production runtime patch.

## Offline tests

`python -B Audit/phase16-p3-layer-reader-2026-11-03f/test_candidate.py -v`
reported **14 tests OK**, covering:

* independently transcribed 33/34/18 profiles and backing-only `degrade`;
* emitter byte-drift/injection refusal and local-wrapper placement;
* exact references/handles, no backing recursion, membership and dependency gates;
* every scalar layer/backing field and every nested GI field mutation;
* missing/unknown/duplicate fields, wrong types, NaN/infinity, unknown nested values;
* rename-as-state, same-handle replacement, stale handles, foreign members/deps,
  parent/children/outgoing-reference changes, and malformed/failed comparisons.

These are static/model tests only. They do not parse MAXScript or prove Max behavior.

## Exact artifacts and gates still open

* MAXScript parse/load and actual Max timing are unexecuted.
* Distinct-layer reassignment, same-name replacement, equal-detached-state distinct
  layers, populated-layer lifecycle, handle reuse, parent/child creation, and all
  mutable-field live controls are unproven. The candidate therefore rejects the
  supported profile unless the caller supplies the strict one-member, no-hierarchy,
  bounded dependency state and still reports only partial observation.
* The allowed root/LayerManager dependency shape is a conservative candidate, not
  a proof of dependency-graph completeness. Controller descendants, native/specified
  normal metadata, mesh metadata, plugin/renderer extensions, and other runtime state
  remain outside this reader.
* Independently identify and retain the actual manager reference; test whether its
  and root's handle round-trips work in the admitted scene. A missing/unsupported
  round-trip stops this candidate; a name or inferred handle is never a substitute.
* The existing production runtime was intentionally not edited. A future integration
  must account for `#layer` in `explicitNames`/`freeze` as well as `layerState`,
  re-review graph traversal and property paths, and place unsupported-state checks
  before evaluation. Replacing only `properties node.layer` cannot fix the earlier
  mixin failure. Resolve all dependency/native-state gates and retain the current
  unconditional `INCOMPLETE_REPLAY` refusal; this candidate is not a safe-replay claim
  or a comprehensive layer comparator.

## SHA-256

```text
0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7  layer_reader.ms
105cbcba7771175e0291a421dea4f874c66b9f51ddb0db3fd5dba340cb8b16b9  emitter_fragment.py
27bf1a85bf483e232a3367fd1dc2321ebbe6b273d1388c614fc6a593182153b4  test_candidate.py
```
