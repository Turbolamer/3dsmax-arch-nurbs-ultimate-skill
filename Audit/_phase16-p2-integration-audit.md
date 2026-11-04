# Phase 16 P2 integration audit — `poly_surface_shell_v1`

**Basis.** Read-only audit against the frozen `graphify-out/.evidence-brief.md`, the current
`CHECKPOINT.md`, and `Audit/AGENT_PLAN_poly_surface_shell.md` sections B/C/P2/E/I. No Max probe,
graph update, implementation, installation, or evidence re-derivation was performed. Current
state remains P0+P1 complete; P2 is queued and there are no `walls.json`, `wall_surface.json`,
`build_wall_surface.py`, or poly QA artifacts.

## Integration hooks that P2 must wire

1. **Grammar contract (`references/07-spec-grammar.md`).** Add the `walls.json` inventory row,
   a complete §8 schema, §9 `G-92`…`G-100` predicates, the separate `numeric_epsilon` policy,
   and the §12 six-step extension record. The schema must remain data-only: no `Extrude`,
   `Shell`, Editable Poly, plugin, or MCP-class names. Because this is a defined/auditable file,
   the contract also needs `origin_inputs`/`origins` semantics; those are absent from the P2
   sketch in plan §B.3 and cannot be left implicit.

2. **Validator registry and dispatch (`scripts/validate_specs.py`).** Extend `SpecDef`/
   `SPEC_INVENTORY` and therefore `SPEC_BY_NAME`, `RULE_TITLES`, and the relevant
   `CROSS_FILE_RULES`. Add a single route resolver at the session/dispatch boundary and pass its
   result to assembly checks. Today `run_checks()` unconditionally calls `check_assembly_rules()`;
   that function unconditionally calls legacy `G-76`, `G-77`, `G-81`, `G-82`, and `G-83`. The
   planned conditional branches must be enforced there, not inferred independently inside each
   predicate.

3. **Route compatibility.** Resolution must be: explicit `walls.json.wall_technique` selects
   `legacy_cells_v1` or `poly_surface_shell_v1`; no selector and no walls file means **legacy**.
   The poly default belongs to a *new* `init_project.py` scaffold only, never to a validator-wide
   fallback. For poly, `assembly.json.wall_technique` is the echo and `wall_ref` points to the
   generated wall manifest; `wall_cells[]` and `opening_cuts[]` are absent. For legacy, preserve
   the existing arrays, builders, and G-76/77/81/82/83 behavior unchanged.

4. **Scaffold (`scripts/init_project.py`).** Add a defined `walls.json` inventory entry, a
   dedicated scaffold shape, and the file to the new-scaffold plan with explicit
   `wall_technique: "poly_surface_shell_v1"`. Update the ownership/manifest list and the
   `--from examples` path without silently rewriting the existing worked example. A legacy
   example/project lacking the selector must remain loadable; do not make `check_inventory()`
   turn that historical absence into a FAIL. Do not route this new defined file through the
   reserved-file helper unless its status/ownership contract is deliberately changed.

5. **Builder/artifact boundary.** P2 may validate declarations and route consistency, but the
   future `wall_surface.json` manifest and `wall_surface.ms` are P3 outputs. Manifest existence,
   emitted-script needles, live `fileIn`, scene census, idempotence, unit refusal, and measured
   topology/volume are not static JSON PASS conditions. Missing or unmeasured artifacts must be
   `SKIP`/`INCOMPLETE` (or a build-gate FAIL where the contract requires a locked artifact), never
   a fabricated PASS. `place_components.py` remains the legacy builder until the later route
   integration phase; P2 must not make it consume poly data prematurely.

## Concrete compatibility risks

- Making `walls.json` unconditionally required would break current `examples/`, existing
  fixtures, and old projects. The inventory must be conditional on an explicit/new poly route;
  absence without a selector is the legacy compatibility case.
- Applying the poly default in `validate_specs.py` would route old `assembly.json` files into
  checks that expect `wall_ref` and no `wall_cells[]`. Keep the default in scaffolding only.
- `G-74` currently enumerates the four legacy assembly tables. Poly node ownership and the
  `WS_` namespace must be specified separately; do not silently broaden the old name rule.
- `resolve_source_id_selector()` currently accepts `<spec>.json:<collection>:<id>` only for names
  in `SPEC_BY_NAME`. A new `contour_ref` must either use that exact selector shape or receive a
  separately specified resolver; accepting arbitrary strings would create unverifiable joins.
- The current grammar says derived-file tolerances are copied verbatim from `dimensions.json`,
  while the plan gives walls an additional `numeric_epsilon`. P2 must define whether the three
  arithmetic values are inherited exactly and epsilon is wall-local, including its unit and
  conversion; otherwise `G-33`/cross-file tolerance logic can disagree.

## Bounded missing details to close before P2 can be considered complete

1. **`contour_ref`.** Declare the permitted target files/collections and whether the reference
   resolves to `dimensions.facades[]`, `massing.elements[]`, or another closed collection. Define
   whether `start_cm`/`end_cm` must equal the resolved contour endpoints, and how a missing,
   duplicate, or geometrically disagreeing target fails. The existing selector grammar is the
   safest bounded compatibility choice, but that is a contract decision, not an assumption.

2. **Coordinates and winding.** State the origin and frame for `start_cm`/`end_cm`, whether they
   are project/world cm or a wall-local plan frame, and how local coordinates become scene/world
   coordinates. Define the relation among `outward`, `reference_face`, contour winding, and Shell
   displacement. Also define whether opening `u_range_cm` and sill/head are measured from the
   run's base and start, and how blocks spanning different elevations are joined.

3. **`upper_returns[]`.** The sketch only says “upper closing runs.” Specify its item schema,
   owning block/run relationship, plan endpoints/contour reference, thickness, z interval,
   outward direction, uniqueness, and the enclosure obligation when a return is omitted. The
   later `QA-V1-ENCLOSURE` requirement cannot be validated from the current array description.

4. **Topology budget.** Replace “closed object” with exact field names, units, integer/range
   rules, and scope. At minimum distinguish the station-grid/base polygon budget from evaluated
   post-Shell triangles, state whether counts are maxima or expected exact values, and state how
   returns and multiple openings contribute. Preserve the F01 oracle (15 base quads; 48 final
   polygons/96 triangles) as a test fixture, but do not make those numbers a universal default.
   G-97 must report declared and measured categories separately and forbid silent optimization.

5. **Artifact and future QA gates.** Record where `wall_surface.json`, `wall_surface.ms`, live
   measurements, and later `qa-request`/`qa-results` live, and which gate owns each. `G-95`/`G-98`
   …`G-100` and the poly QA profile are future artifact/runtime gates, not P2-only schema passes.
   P2 should reserve their route names and statuses without claiming the wall surface exists.

## P2 acceptance boundary

P2 is integrable only when current examples/builders still validate with their existing semantics;
an old no-selector project resolves to legacy; a fresh scaffold explicitly declares poly; malformed
wall specs and route mismatches fail negative tests; and a locked poly declaration without the
required `wall_surface` manifest is visibly incomplete/failing rather than passing. This audit
does not authorize implementation or any live Max work.
