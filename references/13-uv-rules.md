# 13 — UV / unwrap rules for a hand-materialed architectural model

> **VERIFIED 2026-10-06 against live Max 2026.3.2, P15.** Every row below is an executed
> transcript, not inference. Probe standard: each batch carried a hit, a miss and a known-bogus
> control. Control names used: `totalBogusXYZ` (property), `TotalGarbageXYZ_Mod` (modifier),
> `TotalGarbageXYZ123` (global), `totalBogusXYZ` (NURBS surface property).
>
> **Scope.** UVs are **not a pipeline stage** — P7 (materials + UVs) was cancelled by the user on
> 2026-10-05; materials are made by hand. This file exists so that hand-off is **informed**: it
> states what the delivered 254-node model does and does not carry, which route produces
> world-scale UVs, and which traps cost a full chain.
>
> **Read with:** `agents/max-orchestrator.md` §5 (the hand-off), `references/09-defaults.md`
> (the value vocabulary), `references/07-spec-grammar.md` §8 (what the builders emit).

---

## 1. The headline: what the delivered model carries

Measured on `examples/massing.ms` + `examples/nurbs.ms` + `examples/assembly.ms` loaded in order —
**254 nodes, 0 modifiers in the scene.**

| Group | Nodes | Channel 1 present? |
|---|---|---|
| `PROTO_*` + `PLC_*` (panel system, reference-instanced) | **165** | **no** — a fresh `Box` has no map channel at all |
| `EL_*`, `SP_GROUND_PAD`, `WAL_*` (massing + wall cells) | **74** | **no** |
| `GRP_*` `Dummy` groups | 5 | n/a — `snapshotAsMesh` throws `Cannot get mesh from this object` |
| `SUR_001`…`SUR_006` (NURBS surfaces) | 6 | **yes**, and it is `0..1` |
| `DRV_001`, `DRV_003` (`Editable_Poly`), `DRV_002` (`SplineShape`), `SUR_007` (`NURBSCurveshape`) | 4 | **no** |

**Three distinct starting states, not one.** Any hand-off that says "the model needs unwrapping" is
wrong in a way that costs time: the NURBS surfaces already have UVs, and they are the *wrong*
ones for world-scale texturing (§3).

`meshop.getNumMapVerts` **throws** on `Box`, `NURBSSurf` and `Editable_Poly` —
`Runtime error: Mesh operation on non-mesh: Box`. Those are not meshes. **Always
`snapshotAsMesh <node>` first**, then read channel 1 off the `TriMesh`. A probe that reads the node
directly reports a false absence on every object in the model.

```maxscript
fn uvSpan nd =
(
    local mm = snapshotAsMesh nd
    local c = 0
    local t = false
    try ( c = meshop.getNumMapVerts mm 1 ) catch ( t = true )
    if t then return "ABSENT"
    local mn = [1e9,1e9,0]
    local mx = [-1e9,-1e9,0]
    for i = 1 to c do (
        local v = meshop.getMapVert mm 1 i
        mn = [amin mn.x v.x, amin mn.y v.y, 0]
        mx = [amax mx.x v.x, amax mx.y v.y, 0]
    )
    (mx.x - mn.x) as string + " x " + ((mx.y - mn.y) as string)
)
```

`polyoop` works **on the node** (`polyoop.applyUVWMap <Editable_Poly> #planar channel:1`) and
`meshop` works **on a snapshot**. `polyoop == undefined` reads **`true`** and
`execute "polyoop"` reads **`undefined`**, yet `polyoop.applyUVWMap` works — the false-absence
family again, one layer down. `isProperty polyop "applyUVWMap"` → `true`, `"totalBogusXYZ"` →
`false`, which is the calibrated test that does reach it.

---

## 2. Class census — what exists, with controls

Constructed via `(Cls())`, `totalBogusXYZ_Mod` throws in the same batch:

| Name | Result |
|---|---|
| `Unwrap_UVW` | **constructs**, `classOf` = `Unwrap_UVW` |
| `Uvwmap` / `UVWMap` | **constructs**, both `classOf` = `Uvwmap` |
| `MapScaler` | **constructs** |
| `surface` (lowercase) | **constructs** |
| `Unreal_UVW` | **throws** |
| `UVW_Channel_Select` | **throws** |
| `Camera_Map` | **throws** |

`Unwrap_UVW` attaches with plain `addModifier` and is **usable but useless through this bridge**:
attaching it changed nothing (`mapVerts` and the UV range identical before and after), and every
one of its callable members throws when invoked — `mirrorV()` `mirrorU()` `mirrorW()` `scale()`
`align()` `move()` `rotate()`. `getProperty` reports `mirrorV` and `scale` as existing (returning
the method handle `mirrorV()`), and `align`/`move`/`rotate` likewise, while `angle` `alignAngle`
`realWorldMapSize` `tiling` `flip` `utile` `vtile` `mapChannel` `useWorldSpace` `translation`
`rotation` `center` `planarAlign` `planarAngle` all throw. **Do not build on `Unwrap_UVW`.**
Unwrapping is a manual, in-the-UI operation; the bridge cannot drive it.

Free functions: `generateUVs1` `unwrapUVW` `peelUV` `mapUV` `unwrapUV` `resetUVW`
`texMapPlanarUV` all read **`undefined`** and are absent — `setTiling` is the one that resolves.

### `Uvwmap` — the nine verified properties

`maptype` `length` `width` `height` `utile` `vtile` `wtile` `realWorldMapSize` `mapChannel`
all read. `mirrorU/V/W` `offsetU/V/W` `flip` `tiling` all throw.

Defaults on a fresh `Uvwmap`: `maptype`=0, `utile`=`vtile`=`wtile`=1.0, `realWorldMapSize`=`false`,
`mapChannel`=1. On a 100×200×300 box the modifier's own `length` reads **200**, `width` **100**,
`height` **300** — i.e. it picks up the bbox, `length` being the Y axis.

> **`maptype: 4` = Box mapping — RESOLVED, previously UNVERIFIED.** `architecture-exterior-pipelines.md`
> §7 item 2 flagged this as unmeasured. It is measured: `maptype` reads `0` on a default
> `Uvwmap`, and writing `4` **persists across calls** while `utile` written in the *same* call
> does not (§6) — so the discriminator is the persistence, not the read-back.

---

## 3. Route A — NURBS surfaces: `generateUVs1` + `setTiling`

`generateUVs1` is **not a function.** It is a **boolean keyword on the surface constructor** and a
readable property on the **committed** sub-object.

```maxscript
NURBSPointSurface name:"X" renderable:true generateUVs1:true matID:1
```

| Fact | Evidence |
|---|---|
| **`generateUVs1` is read on the committed `NURBSSurface` sub-object, not the node and not an unattached surface.** It is **unreadable** on a `NURBSPoint` | committed sub-object → `generateUVs1` = `true` / `false` exactly as constructed, 2 nodes. On sub-object index 1 (a `NURBSPoint`) every one of `generateUVs1` `generateUVs2` `uTile` `vTile` `uOffset` `vOffset` throws |
| **`generateUVs1:false` produces NO channel 1 at all** — not an identity map, not `0..1`, **absent** | `NURBSPointSurface` and `NURBSCVSurface` pairs, identical geometry: `true` → `mapVerts` 12513, span `0..1`; `false` → `getNumMapVerts` **throws** `Map support not enabled for specified map channel: 1` |
| **`true` gives `0..1` regardless of the surface's size in centimetres.** A 600 cm surface and a 1800 cm surface both give span `1.0 x 1.0` | two `makePointSurfaceGrid` calls, `spX` 150 vs 450, node bbox X 600 vs 1800, uvMax `[1,1]` both |
| **Channel 2 is absent** — `matID` is not a map channel | `getNumMapVerts m 2` throws |
| **`uTile` / `vTile` / `uOffset` / `vOffset` are NOT readable properties.** The only route is the function | property sweep with `matID`=1 as in-batch positive and `totalBogusXYZ` as negative; all four throw |
| **`scaleU` / `scaleV` / `uTile` / `vTile` / `visibility` / `generateUVs` also throw.** `renderable` and `matID` survive | same sweep |
| **`setTiling <surf> <u> <v> channel:1` works, takes 3 args, and returns `"OK"` (`OkClass`)** | the point2 form `setTiling s [4,2] channel:1` → `Argument count error: setTiling wanted 3, got 2` |
| ⚠️ **`setTiling` SILENTLY TRUNCATES ITS ARGUMENTS TO INTEGERS. This is the single most consequential defect in this file** | see the table below |
| ⛔ **`getTiling <surf> channel:1` ECHOES THE REQUEST, not the applied tiling.** It returns `[3.5, 1.5]` after a `setTiling 3.5 1.5` while the UVs come out `3.0 × 1.0`, and it persists across calls | measured in one call and re-measured in the next; the UV range read off `snapshotAsMesh` in the same batch |
| **`setTiling <surf> 0 <v>` degenerates: u collapses to 0 and v becomes the surface's width in centimetres** | `0.0` → `max=[0,750,0]` on a 750 cm surface; `0.5` → the same; a 1500 cm surface at `0.5` → `[0,1500,0]` |

**`setTiling` truncation, measured (all on a 750 × 200 cm surface, read off `snapshotAsMesh`):**

| Call | uv span | Correct? |
|---|---|---|
| `setTiling s 1 1` | `1.0 x 1.0` | yes |
| `setTiling s 2 2` | `2.0 x 2.0` | yes |
| `setTiling s 2.99 3.99` | `2.0 x 3.0` | **truncated** |
| `setTiling s 2.01 2.01` | `2.0 x 2.0` | **truncated** |
| `setTiling s 1.9 1.9` | `1.0 x 1.0` | **truncated** |
| `setTiling s 3.5 1` (350 cm surface) | `3.0 x 1.0` | **truncated** |
| `setTiling s 3.99 1` (350 cm surface) | `3.0 x 1.0` | **truncated** |
| `setTiling s 3.6 1` (350 cm surface) | `3.0 x 1.0` | **truncated** |

It is a **floor, not a round** — `2.99 → 2`, and `1.9 → 1`. Reproduced on three independently
constructed surfaces at three different positions, so it is not a stale-read artefact.

### ⛔ `getTiling` REPORTS THE REQUEST, NOT THE APPLIED TILING

This is why the truncation survived every earlier verification pass, including one that explicitly
claimed to have confirmed the round-trip.

```maxscript
setTiling s 3.5 1.5 channel:1
getTiling s channel:1     -->  [3.5, 1.5]     reads back EXACTLY what was asked
-- and the actual UVs:
snapshotAsMesh <node>     -->  span 3.0 x 1.0  the 0.5 and 0.5 are gone
```

Confirmed across calls — `getTiling` still reads `[3.5, 1.5]` on the next call, so the stored value
genuinely is `3.5`; Max simply applies the integer part. **`getTiling` round-trips perfectly and
tells you nothing about whether the tiling was honoured.**

This retroactively corrects `references/_04-05-evidence.md` §G32 *"CONFIRMED (`getTiling`/`setTiling`
round-trip)"*. The round-trip **is** confirmed — it is just not evidence that the tiling was applied.
The check was calibrated for the wrong question. **`getTiling` is a request-echo, not a measurement:
the only truth is the UV range off `snapshotAsMesh`.**

**Why this matters architecturally.** A wall 350 cm wide needs `3.5` tiles at one tile per metre.
`setTiling` gives `3`. A 210 cm panel needs `2.1`; it gets `2` — **5 % texel-density error on that
panel, and it is silent.** Every surface in a real building has a non-multiple-of-100 width, so
**`setTiling` cannot deliver constant texel density and must not be used to try.**

### The replacement, and it is verified: `Uvwmap` on the NURBS node

`addModifier <NURBSSurf_node> (Uvwmap maptype:0)` **succeeds**, and with `realWorldMapSize:false`
it **multiplies** the `generateUVs1` `0..1` map:

| Surface 350 × 150 cm | Call | uv span | Wanted |
|---|---|---|---|
| `generateUVs1:true` only | — | `1.0 x 1.0` | — |
| `+ Uvwmap maptype:0` (added, `utile` at default) | — | `1.0 x 1.0` | — |
| `utile=3.5 vtile=1.5` | **separate call** | **`3.5 x 1.5`** | `3.5 x 1.5` ✅ |

**Fractional tiling on a NURBS surface works — via `Uvwmap`, not via `setTiling`.** Confirmed
persistent across calls. This is the recommended route and it costs one modifier per node, which
§6 then explains how to make safe.

---

## 4. Route B — poly geometry: `Uvwmap` with `realWorldMapSize`

**`realWorldMapSize:true` makes one UV unit equal one centimetre.** Measured on three
independently placed boxes:

| Box | Position | `maptype` | uv span | 1 unit = |
|---|---|---|---|---|
| 4 × 6 × 2 cm | (1000, 2000, 0) | planar | `4.0 x 6.0` | 1 cm |
| 400 × 600 × 2 cm | (2000, 4000, 0) | planar | `400.0 x 600.0` | 1 cm |
| 300 × 150 × 20 cm | (12000, 0, 0) | planar **and** box | `300.0 x 150.0` | 1 cm |

The mapping is **local to the object**, not world-aligned — a box at `x=2000` maps the same as one
at `x=0`. So a `realWorldMapSize` map is *object-relative*: fine for a repeated panel, wrong if you
need neighbouring objects to share a continuous texture run. For that, use the world-space route
(§4.2).

`realWorldMapSize:false` gives `0..1` per object (`1.0 x 1.0` on the 300 cm box) — the normalised
default, i.e. **texture density varies with object size**, which is the same defect as route A.

`utile`/`vtile` scale linearly and **do** work under `realWorldMapSize:true`, one axis at a time:

| Write | uv span (300 × 150 cm box, planar, rw=true) |
|---|---|
| `utile=1.0 vtile=1.0` | `300.0 x 150.0` |
| `utile=0.01 vtile=1.0` | `3.0 x 150.0` |
| `utile=0.5 vtile=0.5` | `150.0 x 75.0` |
| `utile=0.005` | `0.3725`-class (read on the 135 cm panel) |

**To get one tile per metre on a centimetre-mapped object, set `utile` = `vtile` = `0.01`.**
`300 × 150` → `3.0 x 1.5`, which matches the NURBS route's `3.5 x 1.5` result for a same-sized
surface. That is the cross-check that both routes land on the same physical density.

### 4.1 `meshop.applyUVWMap` / `polyoop.applyUVWMap` — real but different

| Call | Result |
|---|---|
| `meshop.applyUVWMap <mesh> #planar channel:1` | **works**, creates ch1 |
| `polyoop.applyUVWMap <Editable_Poly> #planar channel:1` | **works** on the node directly |
| Either, on a `Box` node | `Runtime error: Mesh operation on non-mesh` — **convert first** |

`meshop.applyUVWMap #planar` produces a **half-extent** map, not world scale: a 100×200×300 box →
`uv 0..25.5 x 0..50.5`; 200×400×600 → `50.5 x 100.5`; 400×800×1200 → `100.5 x 200.5`; 50³ →
`13 x 13`. The `+0.5` offset is constant. Use it for a quick box unwrap; use `Uvwmap` +
`realWorldMapSize` when density has to be right.

### 4.2 Box mapping and the `PLC_` panel sizes — the practical check

`maptype:4 realWorldMapSize:true` on the delivered panel set gives uv span **exactly equal to the
node's X and Z extent in cm**:

| Node | Size (cm) | uv span |
|---|---|---|
| `PLC_001` | 135 × 3 × 90 | `135.0 x 90.0` |
| `PLC_002` | 180 × 3 × 90 | `180.0 x 90.0` |
| `PLC_004` | 135 × 3 × 180 | `135.0 x 180.0` |
| `PLC_005` | 180 × 3 × 180 | `180.0 x 180.0` |
| `WAL_EL_014_C01` | 135 × 20 × 420 | `135.0 x 420.0` |

Box mapping picks the two dominant axes, so a 135 × 90 panel and a 135 × 420 wall cell both come
out in real centimetres. **This is the correct base for hand-texturing the delivered model**:
one material, one tile size, consistent scale across all 165 panel nodes.

---

## 5. Reference instances propagate the modifier — this is the whole game

**A modifier added to a prototype propagates to every node that shares its `baseObject`.**

```maxscript
local b  = Box width:100 length:20 height:50
local i1 = copy b
local i2 = copy b
for i in #(i1, i2) do i.baseObject = b.baseObject   -- the P5 instancing idiom
-- all four: no channel 1
addModifier b (Uvwmap maptype:4 realWorldMapSize:true)
-- SRC, INS1, INS2: all true;  INS1.modifiers.count = 1, INS2.modifiers.count = 1
```

On the delivered chain this was measured end to end:

| Action | Nodes with ch1 |
|---|---|
| baseline, 244 nodes | **0** |
| `addModifier` on **29** `PROTO_*` nodes only | **165** |

165 = 136 `PLC_*` + 29 `PROTO_*`. Family membership confirmed by `baseObject` identity — e.g.
`PROTO_CMP_001`'s family is `#("PROTO_CMP_001", "PLC_072", "PLC_082", "PLC_092", "PLC_102",
"PLC_112", "PLC_122", "PLC_132")`, exactly 8, and adding the modifier to the prototype put channel 1
on all 8 while `PROTO_CMP_008`'s 11-member family stayed clean.

**So the entire UV hand-off on the panel system is 29 `addModifier` calls, one per prototype** — not
165, and not 244. `agents/max-assembly.md` §5 already parks the prototypes; they are not scene
clutter, they are the handle.

The 74 remaining nodes (`EL_*`, `SP_GROUND_PAD`, `WAL_*`) are **not** instanced and each needs its
own modifier. Adding 29 modifiers took the scene from 0 to 165 UV-carrying nodes with
**165 modifier slots** — one per node, because instances each hold a slot. **Note the interaction
with the 20-modifier freeze rule (`AGENTS.md`): that is 1 per node, nowhere near the boundary, but
the batch is still worth splitting ≤ 5 `execute_maxscript` calls at a time on principle.**

---

## 6. ⛔ NEW TRAP — a modifier property written in the same call that adds it is LOST

This cost more probes than anything else in P15 and is the reason several rows above needed a
second measurement. **It is not a documentation problem; it silently discards your setting.**

```maxscript
-- FAILS. utile reads 0.25 in-call, and reads 1.0 in the next call. 8/8 times.
local b = Box width:100 length:100 height:100
local p = convertToPoly b
addModifier p (Uvwmap maptype:0 realWorldMapSize:true)
p.modifiers[1].utile = 0.25
```

```maxscript
-- WORKS. Write in a LATER call. 5/5 times, geometry included.
addModifier p (Uvwmap maptype:0 realWorldMapSize:true)
-- ... next execute_maxscript call:
p.modifiers[1].utile = 0.25        -- persists, and snapshotAsMesh shows span 25.0
```

**What exactly is lost, measured separately:**

| Written in the adding call | Next call reads | Lost? |
|---|---|---|
| `Uvwmap maptype:0 realWorldMapSize:true` (**constructor kwargs**) | `maptype=0 rw=true` | **survives** |
| `Uvwmap maptype:4 realWorldMapSize:true utile:0.44 vtile:0.44` (**constructor kwargs**) | `maptype=4 rw=true` **`utile=1.0`** | **utile lost** |
| `mod.maptype = 4`, `mod.realWorldMapSize = true` (**properties**) | `4`, `true` | **survive** |
| `mod.utile = 0.25`, `mod.vtile = …` (**properties**) | `1.0` | **lost** |

**`utile` and `vtile` are the only properties measured to be dropped.** `maptype`,
`realWorldMapSize` and the constructor keywords all survive. So this is not "modifier writes are
lost" — it is specifically **the tiling scale**. Which is the one you always need.

**Two things that make it survive, both verified:**

```maxscript
-- (a) write in a LATER call — 5/5
-- (b) force an evaluation between addModifier and the write — 3/3
addModifier p (Uvwmap maptype:0 realWorldMapSize:true)
local mm = snapshotAsMesh p
try ( meshop.getNumMapVerts mm 1 ) catch ()
p.modifiers[1].utile = 0.5        -- persists, span 50.0
```

Evaluating the node **before** adding the modifier does **not** help (measured: add+write after a
pre-evaluation still reverted to `1.0`). The evaluation has to happen **after** the `addModifier`.

**The in-call read-back lies.** Every one of these reads the written value immediately and reports
it correctly — `0.25`, `0.44`, `0.5`. The value is present in the modifier object the script holds
and absent from the stack Max keeps. **A probe that reads back in the same call proves nothing here.**
This is the repo's signature failure mode for the eleventh time, and the second distinct mechanism
after `P4b`'s unattached-surface reads: there, a property was read in the wrong place; here, a value
is read in the wrong *time*.

**Practical rule:** in every emitted `.ms` or bridge script that configures `utile`/`vtile`, put
the writes in a **separate function called after a `redrawViews()`-style evaluation**, or simply in
a second `execute_maxscript` call. `redrawViews()` was not tested as an evaluation trigger — the
measured trigger is `snapshotAsMesh`. **UNVERIFIED: whether `redrawViews()` also works.**

---

## 7. False-absence note — `polyoop` and the calibrated test that reaches it

| Probe | Result | Reality |
|---|---|---|
| `execute "polyoop"` | `undefined`, `classOf` = `UndefinedClass` | **wrong** |
| `polyoop == undefined` | `true` | **wrong** |
| `isProperty polyop "applyUVWMap"` | `true` | **right** |
| `isProperty polyop "totalBogusXYZ"` | `false` | **right** |
| `polyoop.applyUVWMap <poly> #planar channel:1` | works, channel 1 created | — |

`meshop` is the control that discriminates: `execute "meshop"` → `StructDef`, not undefined. So the
false-absence is **specific to `polyoop`**, not a general struct problem. `quaternion` is likewise
unreachable by `execute` but is genuinely absent — `quat 45.0 [0,0,1]` works (positive control
`point3 1 2 3` in the same batch) while all three `quaternion` arities throw. **Use `quat`.**

Swept with `execute <id>` for 18 ids, `polyoop` `quaternion` `normalMap` `systemLog` `meshsel` read
undefined; the rest resolved. Of the five, `polyoop` is a **false** absence and the other four are
**true** absences — so `execute`-based absence detection on this list is 4 right, 1 wrong, and
nothing in the result distinguishes the two without a call.

---

## 8. The hand-off in one table

Recommended, all measured, in the order to apply them:

| # | Target | Call | Notes |
|---|---|---|---|
| 1 | 165 panel-system nodes | `addModifier <PROTO_*> (Uvwmap maptype:4 realWorldMapSize:true)` — **29 calls** | propagates by `baseObject`; §5 |
| 2 | 74 massing/wall nodes | same, per node | not instanced |
| 3 | 6 NURBS surfaces | **drop `generateUVs1` from the spec** and use `addModifier <SUR_*> (Uvwmap maptype:0)` with `utile`/`vtile` set **in a later call** | `0..1` is the wrong scale; `setTiling` truncates; §3 |
| 4 | 4 derived `DRV_*` / `SUR_007` | manual in the UI | `Unwrap_UVW` is unusable through the bridge; §2 |
| 5 | density check | `uvSpan` on five differently-sized nodes | a shared material must give the same uv/cm ratio everywhere |

**Step 3 is a spec change, not a runtime fix.** `generateUVs1:true` is currently emitted by
`build_nurbs.py:1976/1981/1996`, `snippets/nurbs_arch_library.ms` (six sites) and
`references/nurbs-complete-guide.md:449` on the strength of an unverified claim. It is now verified
to produce a **normalised `0..1` map**, which is usable but not world-scale. **Whether to change the
builders is a user decision** — it is logged in `references/improvement-log.md` format as a
project-level finding, not applied silently. `G-81`'s zero-modifier rule applies to the *emitted
builder output*; UV is applied by the user after the chain, exactly as materials are.

---

## 9. Left unverified, deliberately

- **`redrawViews()` as an evaluation trigger** — the measured trigger is `snapshotAsMesh`.
- **Whether `utile` on a *second* modifier in a stack behaves the same** — every stack here had one
  modifier. Relevant because §5 gives instances one slot each, but no node in this session had two.
- **UV seams.** Nothing measured `isSeam`, seam edge sets, or whether a `point_grid` surface's
  `0..1` wrap is continuous across a closed section. Relevant to any vault.
- **`getTilingOffset` / `setTilingOffset`** — the sibling pair listed in
  `nurbs-complete-guide.md:294`. Not probed. Given `setTiling`'s behaviour, assume nothing.
- **Whether the `0..1` NURBS map distorts on a non-planar surface.** Only planar grids and one
  sweep were measured for UV range.
- **`Unwrap_UVW` in the UI.** Untestable from here; the modifier exists and is presumably fine when
  a human drives it.
- **Corona material UV requirements.** P7's probes closed the renderer question but not how Corona
  reads channel 1 — out of scope, materials are hand-made.