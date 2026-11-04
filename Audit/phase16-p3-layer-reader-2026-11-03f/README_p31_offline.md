# P3.1 layer reader — bounded offline candidate

This directory contains an additional **offline-only** layer-reader candidate.
`layer_reader_p31_offline.ms` is helper text, not an installed or production
runtime change. It has not been `fileIn`-ed, parsed by Max, timed, or run in a
scene. `test_p31_offline.py` is a Python structural test and does not invoke
Max or claim MAXScript compilation.

## What the candidate is designed to guard

The helper accepts independently retained exact witnesses in the form
`#(reference, handle)`. It then:

* obtains `node.layer` and requires its `layerAsRefTarg` to be the exact
  retained backing reference, with a two-way handle round trip;
* keeps the `LayerProperties` mixin separate from the backing `ReferenceTarget`;
  the anim-handle API is rejected for `MixinInterface` before it is called;
* detaches finite scalar values for the observed 33 layer-interface fields;
* reads all 34 observed backing-target fields, including backing-only
  `degrade`, and records `layerAsRefTarg` as an exact backing identity marker
  without recursing through it;
* reads all 18 observed nested GI scalar fields with an exact property-set and
  type check;
* admits only a bounded, witness-supplied member set (1–16 nodes), checks
  `getNumNodes()` against `layer.nodes`, rejects duplicates/foreign members,
  and confirms each member's current `layerAsRefTarg`;
* rejects a non-`undefined` parent or any child layer, and checks a conservative
  root/LayerManager/optional-member dependent shape; and
* reports only `INCOMPLETE` observation statuses. A stable double read is not
  a replay-safe equality result.

Names are detached state only. No name lookup, name-based ownership, handle-only
adoption, or inferred identity is present. Null, stale, unknown, duplicate,
unreadable, non-finite, out-of-profile, or changing values fail closed.

## Evidence used

The design follows the recorded bounded probes:

* `../phase16-p3-main-probes-2026-11-03f/layer-owned-result.json` observed a
  distinct temporary backing target, stable alias lookup, lock/GI/name edits,
  and exact cleanup. It did **not** prove complete state or replay.
* `../phase16-p3-main-probes-2026-11-03f/layer-membership-result.json` observed
  one owned Box moving to another backing target and returning. It did **not**
  prove all member/dependency shapes.
* `../_phase16-p3-layer-readonly-2026-11-03f.json` recorded 33 layer fields,
  34 backing fields including `degrade`, and 18 GI fields.

These observations are inputs to a conservative candidate, not a completeness
assumption.

## Exact gaps / required future live controls

The candidate must remain out of production and replay until the following are
measured independently in short, disposable, coordinator-owned Max calls:

1. **MAXScript validity:** parse/load and timing of this exact file, including
   the `MixinInterface` branch and all getter/exception paths.
2. **Manager witness:** independently retain the actual `LayerManager`
   reference and prove its handle round trip in the admitted process. A name,
   class label, or guessed handle is not a substitute.
3. **Hierarchy:** create and clean an exact-owned parent/child layer case, or
   retain the current conservative refusal with a live proof that all required
   production scenes are unnested. No force hierarchy deletion is implied.
4. **Membership bounds:** test zero, one, multiple, duplicate, foreign and
   changing membership, including the reported `getNumNodes()`/`nodes` contract
   and member dependency behavior. The current two-layer move proves only one
   narrow positive.
5. **Dependency graph:** calibrate root, manager, member and foreign dependency
   shapes; determine whether `refs.dependents` is complete enough for the
   intended use. The allowed shape in the helper is a conservative refusal
   boundary, not a proof of graph completeness.
6. **State coverage:** exercise every admitted layer, backing, GI and
   `degrade` field, getter failure, property-set drift, unsupported type, and
   non-finite value live. Exposed `getPropNames` does not prove hidden native,
   controller, renderer, plugin, mesh, specified-normal, or metadata coverage.
7. **Identity/lifecycle:** measure same-name replacement, equal-detached-state
   distinct layers, deletion/recreation, handle reuse, undo/redo, save/load,
   merge, restart, and external callbacks. Names and handles have no assumed
   persistence across those boundaries.
8. **Production integration:** update and review every layer path in the
   runtime (`#layer` explicit state, `layerAsRefTarg`, graph/dependency paths)
   and order unsupported-state checks before evaluation. Replacing one
   `properties node.layer` call is insufficient.
9. **Replay and construction:** preserve the unconditional
   `INCOMPLETE_REPLAY`/precreate refusal until the broader native metadata,
   controller/stack, dependency, cleanup and witness-continuity gates pass.
   This candidate does not authorize construction, cleanup, baseline, replay,
   or lease changes.

Additional limitations: this candidate only identifies layer/GI interfaces as
`MixinInterface` plus their observed property profiles; it does not separately
authenticate an interface subtype that happens to expose the same profile.
Its member/property/dependency bounds are checked after Max API calls return, so
they do not bound allocations or execution time *inside* those calls. Double
reads are non-atomic and cannot detect a change followed by restoration between
reads. The caller must keep witnesses independently and immutable in the same
session; no snapshot or handle alone establishes continuity. Comparison uses
MAXScript typed value equality, not bitwise floating-point or edit-history
comparison; treatment of signed zero and `Name` casing is not independently
calibrated here.

## Test boundary

Run the structural checks with:

```text
python -B Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py -v
```

The tests inspect text, counts and guard placement only. They do not parse
MAXScript, connect to 3ds Max, create a node/layer, mutate a scene, or convert
an incomplete observation into a PASS.
