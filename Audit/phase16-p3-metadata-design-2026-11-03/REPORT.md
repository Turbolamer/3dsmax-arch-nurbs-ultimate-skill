# P3.1 metadata audit — concise verdict

**INCOMPLETE / NOT ACCEPTED.** Audited `scripts/wall_surface_runtime.py` SHA-256
`bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15` against the
P3.1 contract and retained evidence. This is a source audit, not a live result.
Main03 failed at layer baseline, cleaned its exact attempted node and retained its
POISONED lease; the current runtime explicitly refuses replay even after an
observed baseline match. No safe no-op, complete metadata equality, or F01
acceptance is established.

## Exact gaps

* **Base metadata:** runtime reads live V/E/F positions, endpoints, ordered face
  loops, flags, material IDs, smoothing, selections, map support/values and
  VData/EData support/values (`595-645`). It does **not** separately read
  face-edge/edge-face incidence, internal face triangulation/diagonals, dead
  element details or arbitrary native/custom metadata. Proving that the selected
  channels and flags exhaust the supported domain requires actual discriminating
  controls; zero default counts are not such proof.
* **Normals:** per-corner specified status, corner-normal IDs, explicit status,
  vectors and sharing are not compared. Evaluated `getNormal` reads a vertex
  normal, not the base's specified-normal table (`647-661`). Autodesk's
  `Edit_Normals` interface is a test-instrument candidate, not a proven read-only
  base reader; topology changes/collapse may strip that state.
* **Controllers and Shell:** the recursive reference graph records allowed
  controller classes, generic properties and direct `numKeys` (`559-593`); it
  has not established complete transform/visibility/Shell subanim coverage,
  leaf key/wire/script rejection, or all editable Shell fields. `numKeys=-1`
  says nothing conclusive about child controllers. `snapshotAsMesh` runs before
  those graph checks (`696-699`), so changed controllers or Shell state may be
  evaluated before refusal.
* **Dependencies and layer:** the runtime snapshots refs/dependents and checks
  node census/base sharing, but does not classify every initial non-node
  dependent against a proven allowed graph; unknown/undefined is not empty.
  `#layer` is fed to an anim-handle reader that demonstrably throws for the
  current LayerProperties interface. Repeated same-layer equality is not
  different-layer identity, membership or edited-flag proof. Autodesk documents
  `layerAsRefTarg` as a candidate underlying ReferenceTarget; its behavior here
  is untested.
* **Required values:** missing explicit node properties currently become an
  `absent` equality sentinel (`684-691`), rather than INCOMPLETE. Array/string
  detachment, per-component finite checks and full required-property coverage
  remain unproved; see the detailed table in `README.md`.

## Bounded follow-up

`README.md` specifies separate positive, independently confirmed mutation and
unknown controls for channels, face internals, specified normals, controller
descendants, incoming/outgoing dependencies and layer membership. None permits
an unknown field to disappear into equality. The candidate files are **not
executed or timed**:

1. `layer-ref-target-readonly.ms` tests a documented layer-target identity
   candidate, with repeat, root-handle and bogus-property controls; if there is
   no second existing layer, the distinct-layer control is INCOMPLETE. It makes
   no explicit scene/lease writes; lazy handle allocation remains unverified.
2. `vdata-channel-control.ms` creates one guarded disposable quad/Shell, mutates
   only its custom VData channel, and uses exact-reference cleanup. It tests a
   reader subset only; it does not establish the production snapshot or absence
   of foreign non-node dependencies.

**First live action for main:** fresh read-only scene, units, selection, dirty
state and exact retained-lease/witness inspection; do not rearm. Then, if
appropriate, inspect and run the layer candidate. Any throw, unknown, timeout,
failed mutation or uncertain cleanup remains INCOMPLETE. No Max operation,
package installation or pre-existing file change was made by this reviewer.
