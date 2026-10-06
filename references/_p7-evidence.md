# `_p7-evidence.md` — P7 probe transcripts, executed live 2026-10-05

**P7 was cancelled by the user mid-stage** (materials will be applied by hand). These probes had
already been executed when the decision was taken, so they are recorded rather than discarded —
they are real measurements against Max 2026.3.2 and they close several P0/P3 open questions.

**Transport for every probe:** `MaxClient` direct over the instance pipe
`\\.\pipe\3dsmax-mcp-pid-17152`, protocol 2, `mainThread`, `safeMode: true`.
The MCP tool layer was **not** exposed in the session that ran these (only the Rhino server was
connected), so the probes went through `C:/3dsmax-mcp/src/max_client.py` directly. This is the same
wire protocol the tools use and the same main-thread execution context — see §"Bridge access" below
for the one caveat.

Every batch carries a control. The standard control is `TotalGarbageXYZ123`, which must read
`undef=true` / `THREW`, and a known-positive which must read `undef=false`.

---

## 1. Renderer detection and switching — the P0 open question, now closed

`07` §4.2 and PLAN §4.2 said "detect the engine, set Corona, never hardcode". The bridge has **no
tool** for this (§5 below), so the route was found in MAXScript.

```
probe: for code in #("TotalGarbageXYZ123", "renderer", "renderers", "renderOutputMessage", "renderProgressive")
  → TotalGarbageXYZ123 => threw=false undef=true  cls=UndefinedClass
    renderer           => threw=false undef=false cls=Name
    renderers          => threw=false undef=false cls=StructDef
    renderOutputMessage=> threw=false undef=true  cls=UndefinedClass
```

```
probe: renderers.current, renderers.production, RendererClass.classes, Material.classes
  → current=Arnold
    renderer_global=production
    --renderers--
    Default_Scanline_Renderer / VUE_File_Renderer / Quicksilver_Hardware_Renderer /
    A360_Cloud_Rendering / Corona / ART_Renderer / Arnold / Missing_Renderer
    material_class_total=77
```

`getPropNames renderers` →
`#(#ClearDraftRenderer, #medit, #renderDialogMode, #target, #activeShade, #GetDraftRenderer,
#renderButtonText, #current, #production, #medit_locked)`

### The setter needs an INSTANCE, not a class

This is the trap. `renderers.current = Corona` **throws**:

```
renderers.current = Corona
  → "-- Unable to convert: Corona to type: Renderer"
```

The bridge's own read at `capabilities.py:15` uses `classOf renderers.current`, which returns the
class name as a **Name** — so it reads fine and looks like the thing you can assign back. It is not.

The working route, executed:

```maxscript
local c = Corona()            -- construct an INSTANCE
renderers.production = c      -- OK
renderers.current    = c      -- OK
```

```
probe result:
  made=Corona
  before_cur=Arnold before_prod=Arnold
  prod_assign_ok
  after_prod=Corona
  cur_assign_ok
  after_cur=Corona
```

| Fact | Evidence |
|---|---|
| `Corona()` constructs and returns a `Renderer` **instance**; `classOf` reads `Corona` | `Corona() threw=false undef=false cls=Corona` |
| `superClassOf Corona` is **`MAXWrapper`**, not `Renderer` — the plugin classes are not `Renderer` subclasses in the usual sense, so `isKindOf` on `Renderer` is not a valid membership test | probe returned `superCorona=MAXWrapper` |
| `RendererClass.classes` is the **only** way to enumerate available engines, and it **includes `Corona`** | 8 entries listed above |
| Assignment to `renderers.production` works and reads back `Corona`; same for `renderers.current`. **Both slots changed** — they are not aliases | `after_prod=Corona after_cur=Corona` |
| **`Corona()` costs ~3.5 s on first call, ~0.4 s warm.** It initialises the whole renderer on construction | `durationMs: 3490` cold vs `395` warm |

> **Operational rule: call `Corona()` in its own `execute_maxscript` call and expect it to blow the
> ~2 s budget.** Under the standing "one script per call, under ~2 s" rule this call must be
> exempted or the first call will read as a timeout.

**Left in place:** the user's Max is now on **Corona for both slots**, confirmed by a separate probe
after the sweep (`renderers.current=Corona production=Corona`). The user chose to keep it.

---

## 2. Corona material classes — 16 exist, **15 construct**, 1 throws

```
probe: construct each of the 16 names found in Material.classes, plus the bogus control
  CoronaHairMtl         OK cls=CoronaHairMtl         super=material
  CoronaVolumeMtl       OK cls=CoronaVolumeMtl       super=material
  CoronaShadowCatcherMtl OK cls=CoronaShadowCatcherMtl super=material
  CoronaToonMtl         OK cls=CoronaToonMtl         super=material
  CoronaFabricMtl       OK cls=CoronaFabricMtl       super=material
  CoronaLightMtl        OK cls=CoronaLightMtl        super=material
  CoronaLayeredMtl      OK cls=CoronaLayeredMtl      super=material
  CoronaRaySwitchMtl    OK cls=CoronaRaySwitchMtl    super=material
  _CoronaPhysicalMtl    OK cls=_CoronaPhysicalMtl    super=material
  CoronaLegacyMtl       OK cls=CoronaLegacyMtl       super=material
  CoronaPortalMtl       THREW
  CoronaScannedMtl      OK cls=CoronaScannedMtl      super=material
  CoronaSlicerMtl       OK cls=CoronaSlicerMtl       super=material
  CoronaSkinMtl         OK cls=CoronaSkinMtl         super=material
  CoronaSelectMtl       OK cls=CoronaSelectMtl       super=material
  CoronaOutlineMtl      OK cls=CoronaOutlineMtl      super=material
  TotalGarbageXYZ123    THREW
  constructed=15 of 17
```

| Fact | Evidence |
|---|---|
| **The architectural material is `_CoronaPhysicalMtl`, with a leading underscore.** `CoronaPhysicalMtl` is not a name in this build. 171 properties, enumerated in §3 | the list above; `classOf` read-back |
| **`CoronaPortalMtl` constructs `THREW`** while all 15 siblings construct — it is present in `Material.classes` but not instantiable. This is the **third** instance in this repo of "listed in the class list ≠ constructible" (after `CScatter`/ChaosScatter and the P0 `NURBSSet` false negative) | 15 of 17, with the bogus control also THREW so the probe discriminates |
| All 15 constructible Corona classes have `superClassOf` = `material`, so the standard `Material` contract applies | `super=material` on every row |
| `Material.classes.count` = **77** in this build | probe |

---

## 3. `_CoronaPhysicalMtl` — all 171 real property names

Read with `getPropNames m`, which **works on materials** even though CHECKPOINT records it as
failing on the NURBS plugin classes. `getPropNames_threw=false count=171`.

Naming is **camelCase**, not snake_case, and slot groups follow a strict quadruple:
`<slot>` / `<slot>Texmap` / `<slot>TexmapOn` / `<slot>MapAmount`.

Full list, in the order returned:

```
baseColor baseLevel baseTexmap baseTexmapOn baseMapAmount
metalnessMode
opacityColor opacityLevel opacityTexmap opacityTexmapOn opacityMapAmount opacityCutout
baseRoughness baseRoughnessTexmap baseRoughnessTexmapOn baseRoughnessMapAmount
baseAnisotropy baseAnisotropyTexmap baseAnisotropyTexmapOn baseAnisotropyMapAmount
baseAnisoRotation baseAnisoRotationTexmap baseAnisoRotationTexmapOn baseAnisoRotationMapAmount
baseIor baseIorTexmap baseIorTexmapOn baseIorMapAmount
refractionAmount refractionAmountTexmap refractionAmountTexmapOn refractionAmountMapAmount
dispersionEnable dispersion useThinMode useCaustics
clearcoatAmount clearcoatAmountTexmap clearcoatAmountTexmapOn clearcoatAmountMapAmount
clearcoatIor clearcoatIorTexmap clearcoatIorTexmapOn clearcoatIorMapAmount
clearcoatRoughness clearcoatRoughnessTexmap clearcoatRoughnessTexmapOn clearcoatRoughnessMapAmount
sheenAmount sheenAmountTexmap sheenAmountTexmapOn sheenAmountMapAmount
sheenColor sheenColorTexmap sheenColorTexmapOn sheenColorMapAmount
sheenRoughness sheenRoughnessTexmap sheenRoughnessTexmapOn sheenRoughnessMapAmount
volumetricAbsorptionColor volumetricAbsorptionTexmap volumetricAbsorptionTexmapOn volumetricAbsorptionMapAmount
volumetricScatteringColor volumetricScatteringTexmap volumetricScatteringTexmapOn volumetricScatteringMapAmount
attenuationDistance scatterDirectionality scatterSingleBounce
sssAmount sssAmountTexmap sssAmountTexmapOn sssAmountMapAmount
sssRadius sssRadiusTexmap sssRadiusTexmapOn sssRadiusMapAmount
sssScatterColor sssScatterTexmap sssScatterTexmapOn sssScatterMapAmount
displacementMinimum displacementMaximum displacementWaterLevelOn displacementWaterLevel
displacementTexmap displacementTexmapOn
selfIllumColor selfIllumLevel selfIllumTexmap selfIllumTexmapOn selfillumMapAmount
alphaMode gBufferOverride anisotropyOrientationMode anisotropyOrientationUvwChannel
renderElementPropagation materialLibraryId
baseBumpTexmap baseBumpTexmapOn baseBumpMapAmount
bgOverrideReflectTexmap bgOverrideReflectTexmapOn
bgOverrideRefractTexmap bgOverrideRefractTexmapOn
translucencyFraction translucencyFractionTexmap translucencyFractionTexmapOn translucencyFractionMapAmount
thinAbsorptionColor thinAbsorptionTexmap thinAbsorptionTexmapOn thinAbsorptionMapAmount
clearcoatAbsorptionColor clearcoatAbsorptionTexmap clearcoatAbsorptionTexmapOn clearcoatAbsorptionMapAmount
clearcoatBumpTexmap clearcoatBumpTexmapOn clearcoatBumpMapAmount
metalnessTexmap metalnessTexmapOn
roughnessMode preSet
edgeColor edgeTexmap edgeColorTexmap edgeColorTexmapOn edgeColorMapAmount
translucencyColor translucencyColorTexmap translucencyColorTexmapOn translucencyColorMapAmount
useComplexIor complexIorNRed complexIorNGreen complexIorNBlue
complexIorKRed complexIorKGreen complexIorKBlue iorMode
baseTail baseTailTexmap baseTailTexmapOn baseTailMapAmount
normalFilteringMode enableVolumetricCaustics
baseFilmIor baseFilmIorTexmap baseFilmIorTexmapOn baseFilmIorMapAmount
baseFilmMaxThickness baseFilmThicknessTexmap baseFilmThicknessTexmapOn baseFilmMinThickness
baseFilmAmount baseFilmAmountTexmap baseFilmAmountTexmapOn baseFilmAmountMapAmount
npEnable npReflectionColor npReflectionLevel npReflectionTexmap npReflectionTexmapOn npReflectionMapAmount
npRefractionColor npRefractionLevel npRefractionTexmap npRefractionTexmapOn npRefractionMapAmount
```

> **`edgeTexmap` appears in the executed list but is not in the `*color*` / `*base*` filtered dumps in
> §3's earlier probe and is easy to mis-transcribe.** The quadruple for `edgeColor` is
> `edgeColor` / `edgeTexmap` / `edgeColorTexmap` / `edgeColorTexmapOn` / `edgeColorMapAmount` —
> the Texmap slot is named `edgeTexmap`, **not** `edgeColorTexmap`. That is a genuine irregularity
> in the plugin, not a transcription error.

### Write / read-back, and enum defaults — VERIFIED

```
m = _CoronaPhysicalMtl()
m.baseRoughness = 0.25          → read 0.25
m.baseColor = color 200 180 160 → read (color 200 180 160)

defaults:
  metalnessMode=Integer 0     roughnessMode=Integer 0    iorMode=Integer 0
  alphaMode=Integer 0         normalFilteringMode=Integer 2
  baseIor=Float 1.5           useComplexIor=false
  baseLevel=Float 1.0         clearcoatAmount=Float 0.0
  selfIllumLevel=Float 0.0    gBufferOverride=Integer -1
  renderElementPropagation=Integer 0
  materialLibraryId=undefined

m.TotalGarbageProp = 1     → THREW
m.TotalGarbageProp         → THREW
```

| Fact | Evidence |
|---|---|
| **A bogus property name THROWS on both write and read.** Unlike the NURBS constructors (which silently swallow unknown keywords), a Corona material rejects a bad name loudly. This makes `materials.json` slot maps safe to write blind — a typo fails the build instead of silently doing nothing | both reads and writes THREW above |
| **The enum modes are Integers, not Name constants.** `metalnessMode`, `roughnessMode`, `iorMode`, `alphaMode`, `normalFilteringMode`, `gBufferOverride` all read `Integer`. Any JSON schema that records these must record integers, and the integer→meaning mapping is **not discoverable from MAXScript** — it would have to come from Corona's own docs | the `cls=Integer` column |
| `getProperty m #name` requires a **Name**, not a String. `getProperty m ("baseIor" as name)` works; passing the String threw `No "map" function for undefined` and killed the enclosing script | two probes, the second aborted |

---

## 4. Material assignment — works; **sub-material selection does not**

Aborted probes, recorded because the failures are the findings:

```
b.materialID                       → '__MCP_MS_ERR__:-- Unknown property: "materialID" in $Box:...'
getProperty b "materialID"         → '__MCP_MS_ERR__:-- No "map" function for undefined'  (String, not Name)
materials.count                    → '__MCP_MS_ERR__:-- Unknown property: "count" in undefined'
```

Calibrated sweep, on both `Box` and `Edit_Poly`, with `TotalGarbageXYZ123` alongside:

```
materialID         Box:threw=true,undef=true  Edit_Poly:threw=true,undef=true
subMaterialID      Box:threw=true,undef=true  Edit_Poly:threw=true,undef=true
matID              Box:threw=true,undef=true  Edit_Poly:threw=true,undef=true
materialId         Box:threw=true,undef=true  Edit_Poly:threw=true,undef=true
TotalGarbageXYZ123 Box:threw=true,undef=true  Edit_Poly:threw=true,undef=true
```

| Fact | Evidence |
|---|---|
| **A node's sub-material / material-ID index is NOT reachable from MAXScript in this build.** Four spellings, both a parametric primitive and a modifier-class object, all throw. This is a **verified negative** | the sweep above; the bogus control throws identically, so the probe is calibrated |
| **Whole-material assignment is a different matter and is not blocked by the above** — `node.material = m` is the P6-verified path and needs no ID | P6 live gate, 136 instances placed |
| **`materials` is `undefined` in this build** — there is no global material library collection to enumerate or count, the same family as `layers` (P3) and `RendererClass` being the working substitute | `materials_is=UndefinedClass` |
| The MCP error surface is **two different shapes**: a *successful* response whose `result` begins `__MCP_MS_ERR__:--`, and `error: ""` with `success: true`. **A caller that checks only `success` sees a pass.** Any probe must check for the `__MCP_MS_ERR__` prefix | every aborted probe above returned `success: true` |

---

## 5. Bridge access — a route that worked when the tool layer did not

The MCP server `3dsmax-mcp` is configured in `opencode.jsonc` and **is running** (`uv`/`uvx`
processes present, `3dsmax.exe` alive), but **none of its tools were exposed to the session**, and
`list_mcp_resources` reported only `context7` and `rhinomcp`. `list_mcp_resource_templates` said
`MCP server "3dsmax-mcp" does not support resources` — so the server was reachable as a *server* but
contributed no callable tools.

Direct `MaxClient` use worked immediately against the same pipe the server uses:

```python
import sys; sys.path.insert(0, "C:/3dsmax-mcp/src")
from max_client import MaxClient, discover_instance_pipes
discover_instance_pipes()   # → [(17152, '\\.\pipe\3dsmax-mcp-pid-17152')]
MaxClient(timeout=25.0).send_command(<maxscript>, cmd_type="maxscript")
```

| Fact | Evidence |
|---|---|
| **The instance pipe is live and healthy even with zero MCP tools exposed.** `MaxClient` → RTT 2.4–3.8 ms, `durationMs` 0–7, `safeMode: true`, `mainThread` — identical to every P0–P6 transcript | every probe in this file |
| `maxVersion()` → `#(28000, 68, 0, 28, 3, 2, 30788, 2026, ".3.2 Security Fix")` — **same build as P0–P6** | first probe |
| This is a **workaround for a missing tool surface, not a replacement for it.** The typed tools carry
  argument validation the direct path does not, and the repo's convention is to prefer
  `3dsmax-mcp_*`. Use direct `MaxClient` only when the tools are absent, and say so when reporting | — |

---

## 6. What this closes, and what stays open

**Closes**

| Question | Answer |
|---|---|
| PLAN §4.2 / P0: how do you set Corona when the bridge has no setter? | `renderers.production = Corona()` — instantiate, do not assign the class |
| P0: "16 Corona classes" — which, and do they build? | Listed in §2; **15 build**, `CoronaPortalMtl` throws; the one you want is `_CoronaPhysicalMtl` |
| P0: is the active renderer assumption safe? | No — `renderers.current` and `renderers.production` were both `Arnold` and are independently settable |
| P3: "layer enumeration is unavailable" — same for materials? | Yes, confirmed: `materials` is `undefined` |

**Left open, unverified, not guessed**

- The integer→meaning mapping of `metalnessMode` / `roughnessMode` / `iorMode` / `alphaMode` /
  `normalFilteringMode` / `gBufferOverride`. Only their defaults are measured.
- Whether `baseTexmap` accepts a `Bitmaptexture` and reads back — **not probed**; P7 was cancelled
  before the texture-binding step.
- **UV rules for NURBS surfaces vs poly-modified geometry** — the other half of P7, and the part most
  likely to matter for a hand-materialed building. **Not started.** The NURBS committed-sub-object rule
  from P4b almost certainly applies, but that is an *inference* and is labelled as one.
- Whether `node.material` survives `copy` + `baseObject` assignment. **MEASURED, and the answer
  overturned the hand-off** — see §4b.

---

## 4b. Material propagation through a shared `baseObject` — **it does not happen**

This was the pack's central hand-off claim and it was never tested; it had been inferred from the
instance route. It is false. Every row executed twice: once on the built 254-node scene, once on a
fresh 3-node test with no chain involved.

| Step | Result |
|---|---|
| `i1.baseObject == proto.baseObject` | **`true`** / **`true`** — the sharing is real |
| material on the **prototype** → read on each of its **10** instances | **`0` inherit**, all `undefined` |
| material on **each instance** | **10 of 10** set, independently |
| material on an **instance** → read on the prototype | unaffected — **no back-propagation** |
| `i1.baseObject.material = m` | **THREW** `Unknown property: "material" in Box` |
| negative control: the other 28 prototypes | **0** leaked — the probe discriminates |
| cleanup: `o.material = undefined` on every node | all read `undefined` again |

Transcripts:

```
proto.material=PROTO_MAT inst1=UNDEF inst2=UNDEF
after_inst_assign inst1=INST_MAT proto=PROTO_MAT inst2=UNDEF
```

and on the built scene:

```
A_proto_only: instances_inheriting=0 of 10
B_each_instance: set_on=10 of 10
D_baseObject_material => THREW: -- Unknown property: "material" in Box
```

**The lesson generalises past materials:** a shared `baseObject` is a **memory optimisation, not an
inheritance mechanism**. Never conclude "set it once on the source and the copies follow" from "they
share a mesh". Both `SKILL.md` §5.1 and `agents/max-orchestrator.md` §5.2 asserted the opposite and
were corrected.

---

## 7. Probe-hygiene notes for whoever runs this next

Four of the probes in this file **aborted mid-script** and left orphans in the scene, each time for
the same reason: an unguarded property access that threw and killed the whole script before the
cleanup block. The cleanup was redone in a following call; the scene was confirmed at
`objects.count = 0` before the chain run.

Standing rules this added:

1. **Wrap every property probe in its own `try ( ) catch ( )`.** One unguarded read takes down the
   sweep and every result after it.
2. **Put the cleanup block FIRST, not last**, or keep a separate sweep call ready. See the P3 row
   "A failed/aborted probe leaves its objects in the scene".
3. **`getProperty` takes a Name.** `(cs as name)`, never the raw String.
4. **`materials` and `layers` are both `undefined`.** Do not build a plan on either.