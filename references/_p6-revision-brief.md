# P6 revision brief — wall tiling replaces the Boolean modifier

Read this whole file before editing anything. Every "MEASURED" row was executed against live
3ds Max 2026.3.2 on 2026-10-05. Do not re-derive them, do not soften them, do not replace
them with a guess. Where this file says UNKNOWN, say UNKNOWN.

## What changed and why

`assembly.json` gained a top-level `wall_cells[]` array, and `assembly.ms` now builds each
`facade_wall` from solid `Box` cells instead of cutting it with Boolean modifiers.

The reason is that **the Boolean modifier cannot be made to cut anything in this build.**

## MEASURED — the Boolean modifier is unusable (all with a bogus-name control in the same batch)

| Probe | Result |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf BooleanMod`, but its paramblock is **Voxel Map's**: `m[1]=SubAnim:voxelSize`, `m[2]=toleranceFactor`, `m[3]=bevelDistance`, `m[4]=bevelDepth`. `VoxelMap()` is itself `NotCreatable`. The Boolean name is shadowed in the class registry |
| `ProBoolean()` | constructs, but `superClassOf` is **`GeometryClass`**, not Modifier. Constructing one **leaves a node in the scene** (3 orphans accumulated during probing) |
| native bridge `native:add_modifier` with `"Boolean"` | genuinely **attaches**: `node.modifiers` reads `#modifiers(Boolean:Boolean)`, `classOf` `BooleanMod`. But the **operand is never set**: `snapshotAsMesh` reports `verts=8 faces=12` — unchanged — for every `params` spelling tried: `operation:1`, `object:NAME`, `object:"NAME"`, `boolobject:NAME`, and combinations |
| the committed modifier's properties | `isProperty m #operation` → `false`, `#object` → `false`, `#boolobject` → `false`. The control `isProperty m #totalBogusProp` is also `false`, so the probe discriminates: these names genuinely do not exist |
| `getModifier 1 node` | **throws** `Type error: Call needs function or class, got: undefined`. `node.modifiers[1]` **works** and returns the modifier. `node.modifiers` prints `#modifiers(Boolean:Boolean)` |

So: **the previous `assembly.ms` opened with `Boolean()` and therefore did nothing.** Its own
`G-80` census still reported success. See "the census defect" below.

## MEASURED — the old G-80 census could not observe failure

The old emitted census was:

```maxscript
local committed = 0
for cut_pair in cut_pairs do ( ... addModifier pair_host pair_mod; committed = committed + 1 )
committed
...
if cut_count != 16 do ( throw "G-80: ..." )
```

It counted **iterations of its own loop**. The live run reported `cut_count = 16` and passed
while `objects.count` was correct at 208 and the modifier stacks were **all empty**
(`nodes carrying modifiers=0`, `max stack=0`). A counter cannot detect a failed attach. The
new census **walks the scene**:

```maxscript
local found_cells = 0
for scene_node in objects do
(
    if (substring scene_node.name 1 4) == "WAL_" do found_cells = found_cells + 1
)
if found_cells != 52 do ( throw "G-80: found " + ... )
```

`07`'s `G-80` row must now say that the census **observes the scene**, and must keep the scene
walk itself as a required needle.

## The replacement: solid cells

`wall_cells[]` — one entry per emitted solid, in `(plan_rect_cm`, `z_range_cm)` plus
`volume_cm3`, `host_ref`, `id`, `node_name`.

* `id` is `WAL-<HOST>-C<NN>`, `node_name` is the same with dashes replaced to underscores:
  `WAL-EL-014-C01` / `WAL_EL_014_C01`. `node_name` is therefore its own id with dashes
  replaced, which is what `G-74` already demands.
* **The tiling** is a column-row decomposition along the facade's run axis: cut at every
  opening's `u` boundary, then inside each column cut at the `v` boundaries of the openings
  covering it. Because every boundary comes from some opening edge, a column is either wholly
  inside an opening's `u` span or wholly outside it — that is what makes it exact, with no gap
  and no overlap.
* The cross axis always takes the **wall's own** extent: every opening is cut clean through,
  which is now an asserted invariant (`G-83`), not an assumption.
* Order is deterministic: ascending run interval, then ascending `v`.
* `assembly.json` for `pavilion-01` carries **52 cells** over **8 hosts**
  (EL-014: 11, EL-015: 12, EL-016: 6, EL-017: 7, EL-018/019/020/021: 4 each).

## MEASURED — the live gate passed

| Check | Result |
|---|---|
| `fileIn examples/massing.ms` | **27** nodes = 22 `Box` + 5 `Dummy`; idempotent over 3 runs |
| 9 bboxes vs an independent Python prediction (8 walls + ground pad) | worst deviation **0.000000 cm** |
| `fileIn examples/assembly.ms` | **244** nodes = 27 + 136 `PLC_` + 29 `PROTO_` + 52 `WAL_`; no throw; idempotent over 3 runs (244, 244) |
| 52/52 cell bboxes measured in Max vs the spec | worst deviation **0.000000 cm** |
| volume identity per host, from **measured** bboxes vs an **independently re-derived** prediction | error **0.000000 cm³** on all 8 hosts. Total wall 73 800 000 cm³ |
| instances sharing their prototype's `baseObject` | 5/5 |
| **negative control** — a plain `copy`, renamed `CTRL_PLAIN_COPY` so it does not match the `PROTO_` scan | shares → `false` |
| `objects.count` after two delete sweeps | **0** |

## Two new invariants

* **`G-82` — the volume identity.** For every host, the cells' summed volume equals the host's
  volume minus its openings' volume, within `linear_cm²`. This is the rule the Boolean route
  could never have satisfied: a modifier that removes nothing leaves the volume untouched, so
  a "successful" build reads as a wall with every opening still filled.
* **`G-83` — full thickness.** Every cell spans its wall's full thickness in the wall's thin
  axis. A tiling of solid cells cannot express a partial-depth opening, so a cell that stops
  short is a defect.

Both are enforced in **two** places, as the P5 device requires: `scripts/validate_specs.py`
(`_g82_wall_tiling_volume`, `_g83_wall_cell_thickness`) and
`scripts/place_components.py` (`_check_wall_tiling`). Fault injection: **11 of 11 fired** in the
builder and 3 of 3 in the linter, baseline clean.

## Fault injection found a real gap — record this

`G-74` did **not** cover `wall_cells[]` when the tiling landed. Two injected defects passed the
self-check clean: a duplicated `node_name`, and a `node_name` not derived from its id.
`_g74_node_names` now iterates `("placements", "opening_cuts", "wall_cells", "scatter")` and
also checks derivation. **This is the third time in this repo that a rule failed to fire because
the thing it governs was added later; state it as a pattern, not a one-off.**

## The fault-injection harness itself was wrong first

The first harness mutated `examples/assembly.json` and re-ran the builder, and reported
**0 of 8 fired**. That proved nothing: `assembly.json` is the builder's **output**, so every
mutation was overwritten before any rule saw it. The rules are exercised by calling the
predicates directly with a mutated document. Do not repeat the first harness.

## Two more collateral facts worth recording

* **A first harness in the live gate also reported a false PASS.** `VERDICT: PASS` printed
  while **zero** comparisons had been made, because prediction keys used dashes and node names
  use underscores. A verdict must require that the expected number of comparisons actually
  happened, not merely that no failure was recorded.
* **`ProBoolean()` creates a scene node**, so probing it pollutes the scene. Three orphans
  accumulated. Delete test nodes in the same call, and note that some "modifiers" are really
  objects.

## Standing rule that came out of this

**The stage emits zero modifiers.** `G-81` used to be a two-ceiling rule (≤ 5 per call, ≤ 10 per
node, chunking cutters into passes). It is now the strong form: `addModifier` must not appear
at all, and the emitted script additionally asserts that the hosts arrive with empty stacks.
The ladder result still stands as the reason the ceiling is zero rather than small: 5 and 10
rungs were clean and **20 froze Max until the machine rebooted**.