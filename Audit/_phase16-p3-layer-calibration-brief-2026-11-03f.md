# Layer calibration — main-executed observations as data

Source: `Audit/_phase16-p3-layer-readonly-2026-11-03f.json`; this is a post-FINAL2
live observation, not source-based inference or an acceptance. Both probes were
read-only; default layer `0` had no nodes, no parent or children. Current scene
was unnamed, objects/selection zero, mm/1, dirty=false when observed.

* `LayerManager.getLayer 0` is `MixinInterface:LayerProperties` and its direct
  `getHandleByAnim` was already shown to throw in earlier evidence.
* `layer.layerAsRefTarg` returns `Base_LayerBase_Layer`; two reads compare equal;
  `getHandleByAnim` produced `48P` and `getAnimByHandle` returned the same backing
  reference in this process. `refs.getNumRefs` returned 0; `refs.dependents`
  returned LayerManager and rootScene. This is a single-layer positive only.
* Interface `getPropNames`: 33, including nested `INodeGIProperties` and
  `layerAsRefTarg`. Backing reference `getPropNames`: 34 and additionally
  `degrade` (boolean false). A routine enumerating only interface fields misses it.
* Nested `INodeGIProperties` had 18 names; all reads succeeded with scalar typed
  values on default layer. Bogus property `#P3BogusGIPropA457` gave false
  `isProperty` and `getProperty` threw; these are calibrated miss controls.
* `getParent()` returned undefined, `getNumChildren()` 0, `nodes &array` returned
  true and filled an empty array. These are this scene's values, not invariants.

Autodesk 2026 MAXScript docs describe `.layerAsRefTarg` as the backing RefTarget,
but their examples do not prove unique/replacement identity or complete metadata:
`https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-78B79975-7BA5-4A03-8FEF-27E78D14B575`.

No distinct-layer comparison, same-name replacement, changed layer property,
mutable snapshot, hierarchy edit, graph completeness, controller/dependency,
native normal metadata, emitted wall, replay or live acceptance is asserted.
