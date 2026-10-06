# Curves and persistent construction

> **OBSOLETE.** This file was written against a **178-tool `3dsmax-mcp` server that is not the one
> connected.** `curve_model`, `inspect_curve`, `edit_curve`, `draw_spline`, `loft_mesh` and
> `geometry_qa` are **absent** — a direct reading of the live tool list, not an inference. **Kept
> for reference only**; nothing below the divider is executable. Same convention as
> `references/railclone.md` and `references/tyflow-graphs.md`.
>
> **Read this instead: [`maxscript-splines-shapes.md`](maxscript-splines-shapes.md).** It is the
> verified route for every curve and shape operation in this build — 502 lines, executed
> claim-by-claim against live Max 2026.3.2 at P4b-r and **largely vindicated**, with ten dated
> corrections. Read it before writing any MAXScript that touches a shape.
>
> **`SKILL.md` labels this file OBSOLETE** as of 2026-10-06, in line with this banner.

## Why OBSOLETE rather than rewritten

Considered and rejected on evidence, not convenience:

1. **There is no verified content to preserve.** Every prescriptive sentence names an absent tool as
   a workflow step; the rest describes that tool's behaviour — a saved parametric recipe, a
   `model_token`, `expected_model` optimistic locking, 16 retained undo states.
2. **The subject is already covered, and covered better, elsewhere.**
   `maxscript-splines-shapes.md` documents all 11 shape constructors, `splineShape` /
   `addNewSpline` / `addKnot` / `updateShape`, knot and segment types, every spline/knot/segment
   method, all 27 `splineOps`, all 14 path- and length-interpolation functions, rendering-spline
   properties, offset/weld, and distribute-along-a-spline — each with a measured result. A rewrite
   would be a smaller, less-evidenced duplicate of a verified file.
3. **The central deliverable has no counterpart in this build.** The recipe below re-parameterises
   a saved sweep cage when `bow` or `width` changes. No such live cage exists here: `loft_mesh` is
   absent, and `Sweep` — though it constructs — **cannot be attached by a hand-written
   `addModifier`**. A rewrite would have had to invent the whole re-parameterisation story, which
   the repo's standing rule forbids.

## Routing table — what replaces each absent tool

| Absent tool | Verified route in this build |
|---|---|
| `curve_model` | `references/maxscript-splines-shapes.md` + MAXScript `splineShape` / `addNewSpline` / `addKnot` / `updateShape` |
| `draw_spline` | `splineShape`, or the `line` / `rectangle` / `circle` / `arc` shape constructors (all 11 constructed and read back at P4b-r) |
| `inspect_curve` | read the cage in MAXScript: `numSplines`, `numKnots`, `getKnotPoint`, `getInVec`, `getOutVec`, `getKnotType`, `curveLength` |
| `edit_curve` | `setKnotPoint`, `setInVec`, `setOutVec`, `setKnotType`, `addKnot`, `deleteKnot`, `close` / `open`, `reverse`, `setFirstKnot`, `refineSegment`, `subdivideSegment`, `weldSpline`, `applyOffset` — then **one** `updateShape` |
| `loft_mesh` | `NURBSULoftSurface` / `NURBSUVLoftSurface` (`references/12-nurbs-gotchas.md`), or the attachable-modifier set below |
| `geometry_qa` | `3dsmax-mcp_execute_maxscript` reading `node.min` / `node.max` / `objects.count` |
| `agent_viewport` | `3dsmax-mcp_capture_viewport` / `capture_multi_view` / `isolate_and_capture_selected` |

### Sweep and surface modifiers — the attachment trap

Six classes **construct** but **throw** on a hand-written MAXScript `addModifier`: `Extrude`,
`Sweep`, `Lathe`, `Surface`, `CrossSection`, `Conform`. (`Bevel_Profile` is unusable through either
route.) For those six use the **typed tool `3dsmax-mcp_add_modifier`**, executed and confirmed to
attach all of them. `modPanel.addModToSelection` is not a workaround — it returns OK and adds
nothing.

Classes that **do** attach with plain `addModifier`, and are safe inside `execute_maxscript`:
`Shell`, `Chamfer`, `Lattice`, `Edit_Poly`, `Uvwmap`, `TurboSmooth`, `Noisemodifier`, `Bend`,
`Twist`, `Taper`, `symmetry`, `SliceModifier`, `SpaceConform`, `Normalmodifier`,
`RetopologyComponent`, `FFD_2x2x2/3x3x3/4x4x4`, `Renderable_Spline`.

**Never assemble more than 5 modifiers per `execute_maxscript` call.** 20 on one node was measured
to freeze Max permanently and cost a reboot. **Do not re-run that ladder** — it is a result, not a
question.

## The verified traps that govern every shape script

Each row was measured. A recipe ignoring these does not work.

| Trap | Measured behaviour |
|---|---|
| `bezierShape()` | Constructs and reports `class = SplineShape`, but `updateShape` **throws** `curve with insufficient knots` at 2, 3 and 4 knots. Plain `splineShape()` with 2 knots updates fine. **Use `splineShape()`.** |
| `updateShape` and 2-knot splines | Throws if **any** spline in a multi-spline shape has only 2 knots. 1 spline × 2 knots is fine; 3 + 3 knots is fine; 3 + **2** throws. Give every spline ≥ 3 knots. |
| `pathParam` | The keyword is **type-checked and inert**. Default, `pathParam:true` and `pathParam:false` all returned the identical point; `pathParam:#bogus` throws. Choose the function — `lengthInterp` / `lengthTangent` for length-based, `pathInterp` / `pathTangent` / `interpCurve3D` / `tangentCurve3D` for vertex-based. |
| `getSegLengths` | Signature accepted, **return shape undocumented**: a 2-segment spline returned **five** values `#(0.657467, 0.342533, 134.36, 70.0, 204.36)` — cumulative params, then per-segment lengths, then the total, which equals `curveLength`. **Never index positionally.** |
| `Arc` angle read-back | `arc` stores angles in **`from`** and **`to`**. There is no `from_angle` / `to_angle`. |
| `setKnotType #bezierCorner` | **Silently no-ops on knot 1** — returns OK, `getKnotType` still reads `corner`. Works from knot 2 onward. Read the knot back if it matters. |
| Path/length conversion values | All 14 functions work, values are not clean. `nearestPathParam` at an L-shape's corner returned `0.25`, not `0.5`. Compare with a tolerance, never `==`. |
| Handles | In/out vectors are absolute handle **positions**, not direction vectors. |
| `delete <base>` | Does **not** delete its instances. Collect and delete them explicitly, or delete the base last. |
| Concatenation | `"x" + someValue` throws. Write `(someValue as string)`. Bites hardest in `try`/`catch` and reporting code. |
| `try { } catch { }` | The brace form **is** a parse error. Use `try ( ) catch ( )`. |
| `getCurrentException()` in a `catch` | **Works** — 6 of 6 throw kinds, with a non-throw control. The "it throws itself" note elsewhere in this repo was **withdrawn 2026-10-05 as false**. Do not "fix" code for it. |
| Function definition | `global fn` and `local function` are parse errors. Use `local fn name args = ( ... )`. |

One behavioural rule from the original survives the loss of its tools: **knot indices can change
after any topological edit.** Re-read after each operation rather than caching indices across calls.

---

*Everything below this line is the original file, retained for reference only, exactly as it was
written. **Do not execute it. Do not cite it. Do not copy from it.** Every workflow in it calls a
tool that is not in the connected bridge.*

---

# Curves and persistent construction

Use `curve_model` when a shape is easiest to describe as a profile, path, or
sequence of sections. Use `draw_spline` for a quick explicit world-point outline.
Use `inspect_curve` / `edit_curve` for precise edits to an existing spline cage.

## Construction loop

1. Define meaningful numeric `parameters` and named `curves` in a `definition`.
2. `curve_model(action="preview", definition=..., parameters=...)` checks the
   recipe locally. Read dimensions, tangent breaks and sampled intersections.
3. `action="create", name=...` creates one editable spline or quad mesh. Its
   recipe is saved in the `.max` file. No extra path/profile nodes are created.
4. Frame and capture it in AGENT VIEWPORT. Inspect the silhouette and highlights.
5. `action="read", name=...` returns controls and a `model_token`. Update named
   parameters with `action="update", expected_model=token, parameters={...}`.

Length values use scene units. Plane points use local coordinates; omitted plane
means XY. `xz` maps the second coordinate to world Z; `yz` maps the first to Y
and second to Z. Custom planes accept `{origin,x_axis,normal}` with perpendicular
directions. Expressions support parameter names, arithmetic, sin/cos (radians),
sqrt, abs, min/max and pi. Arc angles and sweep twist use degrees.

## A tapered armrest

Pass this definition and parameters to `curve_model`, first with `preview`, then
with `create` and a name:

```json
{
  "parameters": {"width":4,"depth":2,"radius":0.4,"height":20,"bow":4},
  "definition": {
    "curves": {
      "section": {"kind":"rounded_rectangle","width":"width","depth":"depth","radius":"radius"},
      "rail": {"kind":"spline","plane":"xz","points":[[0,0],["bow","height/2"],[0,"height"]]}
    },
    "output": {
      "kind":"sweep","profile":"section","path":"rail","up":[0,1,0],
      "path_samples":48,"profile_samples":32,"scale":[1,0.7],"twist":0,"caps":true
    }
  }
}
```

Changing `bow` or `width` recomputes both source curves and the same output cage.
The mesh retains its material, placement and modifiers. Recipe updates preserve
connectivity; changing resolution or a parameter that changes knot/segment count
requires a separate construction. Manual cage edits block parameter updates.
Geometry undo is recognized within 16 retained parameter states; ambiguous or
older states are reported, never guessed. Instanced bases require making unique.

## Curve vocabulary

- `polyline`: `points`, optional `closed`, `fillet` radius, and outward `offset`.
  Fillet and offset operate on local XY polygons. Offsets use miter joins;
  fillets that overlap adjacent edges are rejected rather than reduced.
- `spline`: a cubic interpolating curve through `points`; `tension` is 0..1
  excluding 1. Inspect for overshoot when tracing tight corners.
- `bezier`: exactly four control points, open. For convenient tangent directions
  and lengths, use a `path` with Bézier segments instead.
- `circle`: `radius`, optional `center` and `start_angle`.
- `arc`: `radius`, `center`, `start_angle`, signed `sweep` in degrees.
- `rounded_rectangle`: centered `width`, `depth`, `radius`. Radius must be
  positive and strictly less than half the smaller dimension.
- `path`: `start`, ordered `segments`, optional `closed`. Each segment has a
  `kind`, endpoint `to`, and optional descriptive `label`.

Path segments:

- `line`: endpoint only.
- `arc`: endpoint, `radius`, optional `clockwise`; chooses the minor arc.
- `tangent_arc`: endpoint and initial `tangent`, or inherits the previous
  segment's outgoing tangent.
- `bezier`: endpoint, `start_tangent` (or inherited), `end_tangent`, optional
  positive `start_length` and `end_length`. Tangents point in the direction of
  travel; lengths are handle lengths, not distances along the finished curve.

Circular arcs use cubic approximations suitable for Max splines, not exact CAD
circles. `tolerance` in the definition controls polyline sampling and QA (default
0.01 scene units), not exact arc approximation error.

## Outputs and correspondence

- `{kind:"curve",curve:"outline"}` produces an editable SplineShape. Add
  Extrude/Lathe/Surface/etc. through the usual modifier tools if needed.
- A sweep uses `path` and `profile` names. Profile points are CCW world XY at
  z=0; profile x/y become section offsets. `up` defines initial section Y and
  must not parallel the path tangent. Frames follow the path with controlled
  `twist` and linear `scale:[start,end]`. Closed paths need `caps:false`, equal
  end scales and whole-turn twist. The output is a quad cage with saved source
  curves, not a live Max Sweep modifier.
- A loft uses `sections:["lower","middle","upper"]`. Curves can have
  different knot counts; `profile_samples` gives them matching sampled counts.
  Keep winding consistent. `align:"start"` preserves authored starting points;
  `align:"auto"` chooses nearest cyclic correspondence at creation and locks
  those seams through subsequent parameter changes. Semantic feature matching
  still requires thoughtfully placed section starts and curves.

Surface intersections and thickness are not certified. Tight sweeps can fold
over themselves; visually inspect them and run `geometry_qa` on the output.
Sampled curve QA reports crossings, planarity and tangent breaks, not exact
curve intersection proofs. A corner can be intentional.

## Inspect, target, edit

`inspect_curve(name=..., spline=1, capture=true)` returns world positions,
incoming/outgoing handles, a `curve_token`, and an AGENT VIEWPORT image with
K/I/O labels. Narrow `knot_ids` for legible captures. Use `action="pick"`, image
`x/y`, and the capture's `expected_view` to rank nearby knots/handles. Check
ambiguity: overlapping front/back projections do not establish visibility.

`edit_curve(expected_curve=token, name=..., edits=[...])` preflights every edit
and applies it in one undo step. A position move carries existing handles;
explicit handles are world positions. Use `type:"bezierCorner"` when taking
manual control of a smooth knot's handles. Selection changes don't invalidate
the token; geometry/topology/transform changes do.

Use one `insert`, `delete`, `reverse`, `open`, or `close` operation per call.
Then inspect again: knot IDs can change. Batched `set` edits may target many
distinct knots, each once, without converting or collapsing the modifier stack.