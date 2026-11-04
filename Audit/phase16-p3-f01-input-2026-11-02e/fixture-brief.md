# Synthetic F01 input authoring brief, 2026-11-02e

This authoring brief gives **synthetic test inputs**, not a user's real building
requirements and not evidence of a new Max execution. It adapts the real seed
schema at `examples/dimensions.json`; seed files themselves remain untouched.

## Authoritative wall facts read from the actual plan

Read `Audit/AGENT_PLAN_poly_surface_shell.md` §G.1 lines 668–693, specifically
670–673, and §A.5 lines 172–179. The analytical wall has inner Y=0, X/u 0…400,
Z 0…300, outward (0,-1,0), thickness30 cm. Door u50…150 / Z0…210;
window u230…330 / Z90…210. These are given source values. Historical measured
results in that plan and `Audit/EVIDENCE_2026-10-27.md` are comparison targets
only; no historical measurement is relabeled as this project's measurement.

The physical direction authority is the analytical plan statement, **not** the
south facade label, footprint winding, supplied vector, signed volume or normals.

## Given synthetic schema-support values (not supplied by the analytical plan)

- Project ID `phase16-p3-f01`; building ID `BLD-F01`, name `F01 input support`,
  typology `synthetic_wall_fixture_support`. These labels assert no real building.
- Site ID `SITE-F01`, polygon CCW [[0,0],[400,0],[400,600],[0,600]] cm,
  ground0 cm, rotation reference label `north`, setback300 cm. The 600 cm support
  depth and 300 cm setback are fixture author choices, not F01 wall dimensions.
- Rotation0 deg is an explicit support assumption A-001, adapted from the seed;
  it must not be used to establish the physical outside of the wall.
- Structure ID `STR-F01`, system `synthetic_schema_support`, grid `bay_spacing`,
  X bays[400], Y bays[300,300] cm, column section[40,40] cm.
- Single level index0 / `LVL-00`, use `synthetic_wall_fixture_support`, elevation0
  and height300 cm. The level only binds the wall's actual vertical range.
- Core ID `CORE-F01`, type `synthetic_schema_support`, polygon
  [[0,300],[400,300],[400,600],[0,600]] cm, spans[0], wall thickness25 cm.
- Single floor plate `FP-00`, level0, thickness30 cm, net usable12 m².
- Roof `flat_parapet`, deck thickness30 cm, slope2 deg, parapet height90 cm,
  thickness30 cm, coping3 cm, drainage `internal_downpipe`. These real seed values
  are retained as synthetic support choices, not analytical wall source facts.
- Exactly one facade `F-S`, name `south`, facing label180 deg, endpoints[0,0]
  and[400,0] cm. The endpoints match F01; the required compass label is schema
  support only. There are no dimension-opening records. Rough openings are
  declared faithfully and exclusively in walls; no fictitious second bay.
- Wall block `BLK-F01`, run `RUN-F01`, openings `DOOR-F01` / `WINDOW-F01`,
  route `poly_surface_shell_v1`, inner reference, no returns. All wall geometry
  comes from the cited analytical source; stable IDs/selector are fixture inputs.
- Tolerances linear0.5 cm / area0.05 m² / angle0.01 deg are retained verbatim from
  the real seed. Numerical epsilon0.001 cm and unit epsilon0.000001 are explicit
  fixture choices, separate from physical tolerance and not inferred defaults.
- Per-run ceilings15 grid polygons /12 active base polygons /96 evaluated
  triangles are explicitly selected comparison ceilings for historical F01,
  never claims of this project's measured topology.

All other scalar/array quantities in dimensions are computed using documented
existing formulas: total height300 cm, overall390 cm, site area24 m²,
width400 cm, depth600 cm, interior X lines[], Y lines[300] cm, column count0,
core area12 m², plate gross24 m², building gross24/net12 m², roof deck300 cm,
facade length400 cm, bay widths[400] cm, bay count1. Their origins name those
formula inputs rather than claiming that the plan directly supplies them.
