# Closed inner contour → Editable Poly → outward Shell: live experiment

Executed 2026-11-04 through `3dsmax-mcp_execute_maxscript` in the connected
3ds Max. This is a hypothesis test, **not an upgraded production builder**.

## Method and scene

Entry inspection: 0 nodes, 0 selection, unnamed scene, SystemType millimeters,
SystemScale 1.0, dirty=true. No reset, save, renderer change or unit change.
`probe.py` emits a closed corner spline and one Editable Poly perimeter per case.
The full floor shares a sorted Z grid and corner vertex indices: no T-junctions,
per-wall shells, global Slice, Boolean, lease, nonce or scene-controller audit.
Rectangular opening faces are deleted, with isolated vertices removed. One Shell
adds thickness outside. The native scale is read from `units.decodeValue "1cm"`.

Each of six test scripts was actually `fileIn`-ed. Each removed its own temporary
TriMesh, wall and guide; every result reported before=0, after=0. Subsequently the
user requested retained geometry for visual inspection. `display_rectangle_openings.ms`
was run and left two nodes; the wall was selected and framed with `max zoomext sel`.
The user subsequently visually approved this retained rectangle on 2026-11-04:
«Визуально все отлично, то что нужно». No further live changes were made.

## Captured measurements

Source units below are cm; Max scene units were mm. Every case had exactly one
Shell, `innerAmount=0`, `outerAmount=300 mm`, `straightenCorners=true`.

| Case | Base quads after cuts | Evaluated triangles | Signed volume m³ (wire precision) |
|---|---:|---:|---:|
| Rectangle, blind | 4 | 32 | 19.08000 |
| Rectangle, door + 2 staggered windows | 43 | 248 | 17.02200 |
| L footprint, 2 openings | 36 | 204 | 19.78200 |
| U footprint, 3 openings | 75 | 400 | 30.81900 |
| Trapezoid, oblique corners, 2 openings | 28 | 164 | 16.31980 |
| Outer 12×8 m → inset 300 mm → Shell, 2 openings | 21 | 132 | 33.57000 |

All six: open triangle edges=0; each undirected triangle edge used exactly twice;
zero degenerate triangles; positive signed volume; first base face normal [0,-1,0].
The Python assessment checked base face counts, cleanup, stack, bounding boxes
(0.01 cm tolerance) and volume (1e-5 relative tolerance) against its own offset-ring
area calculation. All six PASS. These are prototype checks, not S7 acceptance.

The volume oracle for these simple non-collapsing offsets and non-overlapping
openings away from corners is:

`V = (area(outer_offset) - area(inner)) * H - Σ(opening_width * opening_height * t)`.

The 12×8 m result spans approximately [0,0,0]..[12000,8000,3000] mm. One minimum
read -0.0000305176 mm, demonstrating Float32 error, **not exact 0.0000 mm**.
The wire's default string conversion also rounds numbers; reported agreement must
not be read as an unrounded numerical certificate.

## Corrections to the supplied audit

1. Calibrated live property probe: Shell `overrideEdgeMatID` and `matEdgeID` are
   absent. Known-positive `innerAmount`, `outerAmount`, `straightenCorners`,
   `overrideMatID`, `matID` etc. returned true and a bogus property returned false.
   Side material IDs use `overrideMatID:true matID:3`; inner/outer override
   properties are real. Property introspection was confirmed against Autodesk's
   Shell MAXScript reference, not substituted for live execution.
2. Shared corner vertices and a conforming horizontal subdivision matter.
   A whole-floor union of sill/head heights is intentionally used for this spike.
   Different per-facade Z grids need explicit corner stitching before production.
3. Outward Shell is **not** a universal guarantee against self-intersections.
   Concave narrow notches can close, acute miter lengths can explode, and inward
   conversion of outer dimensions can collapse small regions. Offset validity,
   minimum clearance, nonlocal intersections and miter limits remain input gates.
   A simple analytical counterexample (not run in Max): a 40 cm wide U-notch
   between opposed inner faces with t=30 cm has only 40 cm of free space for
   60 cm of outward growth. The two fronts overlap by 20 cm. "Outward" is local
   to each segment, not a promise that the rest of the footprint is empty.
4. Closed edges, positive volume and matching bounds alone do not prove absence
   of intersecting triangles, valid vertex links, or correct individual apertures.
5. Frame width=rough opening width is not a universal anti-Z-fighting solution.
   The production manifest must specify installation clearance/overlap, frame
   depth, recess reference and actual contact surfaces.

## Retained visual specimen

- `CCSV2_DEMO_rectangle_openings`: inner 6000×4000 mm, height 3000 mm, wall
  thickness 300 mm; outer 6600×4600 mm. Editable Poly + one live Shell.
- `CCSV2_DEMO_rectangle_openings_InnerSpline`: closed corner guide, hidden but
  retained for inspection. No wall/slab/window solids are falsely described as
  completed: this specimen contains walls and empty openings only.
- South segment: door s=1000..2000, z=0..2100 mm; window
  s=3200..5000, z=900..2100 mm. East: window s=1000..3000,
  z=1100..2400 mm. Origin at the inner southwest corner; CCW traversal.
- Do not auto-clean/rebuild this user-inspection specimen. It may now contain
  manual edits. Read it before any subsequent action.

## Files and reproduction

- `probe.py`: experiment emitter / independent Python assessment, stdlib only.
- Six named `.ms`: executed, self-cleaning fixtures.
- `display_*.ms`: optional retained variants; only the rectangle-openings variant
  was executed. Do not run another variant without choosing placement first.
- `results.json`: captured MAXScript measurement strings, copied from actual MCP
  responses; not full transport envelopes or high-precision mesh exports.
- `scene-and-property-results.json`: entry, calibrated Shell property controls,
  retained-demo build and last framing/scene observation, with request IDs.
- `assessment.json`: generated by `python experiments/closed-contour-shell-v2/probe.py --assess`.

The first fileIn attempt failed at parse time because `by` was used as a local
variable name; it was corrected to `byv` before any geometry was created. The
subsequent six recorded executions succeeded. No timeout or abandoned test node.

Remaining: production schemas/builder, input negatives, offset collision tests,
independent aperture and normal checks, per-corner spatial checks, slabs, frame
placement/clearance, multiple storeys, three rebuilds with foreign scene content,
and full S4w→S5→S7 acceptance. Visual acceptance of the retained rectangle is DONE;
it does not certify the unbuilt integrated pipeline or all six shapes visually.
