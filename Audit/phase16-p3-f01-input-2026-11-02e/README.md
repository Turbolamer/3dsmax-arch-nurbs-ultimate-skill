# F01 standalone synthetic wall — LOCKED INPUT ONLY

This directory is an **input project**, not a generated model, produced assembly,
emitter result, or live acceptance fixture. `locked` means only that the four
domain input documents are fixed for consumption. No `assembly.json`, stage
output, wall manifest, script, QA result, or Max evidence is fabricated here.
The builder must create a **different, new output directory**.

## Source reconciliation: do not use the task's contradictory variant

The actual F01 source is `Audit/AGENT_PLAN_poly_surface_shell.md`, §G.1,
lines 668–693. It specifies a 400 × 300 cm inner wall at Y=0, outward -Y,
thickness 30 cm; **door u=50…150, sill=0, head=210; window u=230…330,
sill=90, head=210**. Its stations are u=[0,50,150,230,330,400],
v=[0,90,210,300]. §A.5 independently states the preserved inner Y=0
and growth in -Y. `Audit/EVIDENCE_2026-10-27.md` §E-11/12 corroborates the
same geometry and records the historical measurements.

The assignment's alternative u=[0,80,140,220,340,400], door=80…140 and
window=220…340 has area **93,000 cm²**, not 87,000. It is not the cited F01.
Following the explicit instruction to verify the actual source and not invent
values when it differs, this project uses the actual F01 above. No source file
was changed to make the conflicting figures appear consistent.

Analytical predictions, **not new measurements**:

- Gross surface: 400 × 300 = 120,000 cm².
- Rough voids: 100 × 210 + 100 × 120 = 33,000 cm².
- Active surface: **87,000 cm²**; thickness product **2,610,000 cm³**.
- Global station grid: 24 vertices / 15 quads; 3 opening quads removed,
  leaving 12 active quads. Expected boundary cycles: outer door-notch cycle
  and internal window cycle. The historical 96 evaluated triangles are a
  **declared ceiling and historical comparison**, not a measured result here.
- Row-major face9 center: **[280,0,150] cm**, matching the historical
  [2800,0,1500] mm source entry; not measured in this project.

## Minimal source graph and honest adaptation

`dimensions.json` adapts the real envelope and dimensional structure of
`examples/dimensions.json`, but it is a **new synthetic project** with a new
project ID and a new source, not the historical pavilion brief. Its original
source claims/conflicts/assumptions do not apply to a changed 400 cm fixture.
`fixture-brief.md` explicitly gives every supporting non-wall fixture value.
Documented formulas remain `derived` with exact, acyclic dependencies;
given source facts are not mislabeled as derived merely to satisfy a join.

The dimensions support context (footprint/grid/core/plate/roof) supplies the
existing schema's required value tree only. It is **not** a request to model
a building. Exactly one wall block and one complete straight run are declared;
there are no returns, corners, partial-building extraction or placement outputs.
`dimensions.openings=[]` is deliberate: the two rough wall openings live only
in `walls.json`. The wall grammar §8.9.5 requires no one-to-one join to the
independent legacy one-opening-per-bay representation; two openings in the
single 400 cm support bay are not forced into false dimension-bay records.

`assumptions.json` records the support-only plot rotation, preserving its real
seed value 0 but explicitly **not** claiming it proves outward direction.
`conflicts_resolved.json` retains the actual seed precedence definitions and an
honest empty conflict ledger: the contradictory task arithmetic is documented
above, not disguised as a conflict in the unrelated pavilion brief.
All tolerances are copied unchanged from the real seed. Numerical epsilons
and topology ceilings are explicit fixture operational inputs, not defaults,
not technology accuracy claims, and not inferred from historical float noise.

## Direction authority and paths

`direction-authority.json` has exactly the separate operational format in
`Audit/_phase16-p3-contract-2026-11-02e.md`. Its `source_file` is a
**repository-root-relative path** to the actual plan, and `source_location`
identifies the analytical inner-Y0 / outward-minus-Y statement, not a compass
label or inferred winding. Its hashes lock the actual plan bytes and wall bytes.
This is a human-authored source attestation; neither P2 path validation nor
hashing is an automated semantic proof of arbitrary source text.
`input-lock.json` records the actual domain, authority, authoring-brief, plan,
evidence and contract bytes; it is fixture input metadata, **not** the future
builder's produced manifest or live acceptance record.

Run the accepted validator from the repository root:

```bash
python -B scripts/validate_specs.py --dir Audit/phase16-p3-f01-input-2026-11-02e/project --json
python -B scripts/validate_specs.py --dir Audit/phase16-p3-f01-input-2026-11-02e/project --json --build --warnings-as-errors
python -B Audit/phase16-p3-f01-input-2026-11-02e/verify_inputs.py
```

The domain inputs are under `project/`, isolated from operational records so
P2's sibling discovery does not mistake evidence JSON for project documents.
The unmodified accepted P2 validator has whole-pipeline inventory obligations
for missing `massing`, `nurbs`, `facade_grids` and `components_registry` even
though this wall input reads none of them. Their four inventory FAILs must not
be hidden or repaired by fabricated outputs. See the accompanying exact raw
reports and top-level audit for actual PASS/FAIL/WARN/SKIP counts and scope.
G-92/G-96 remain incomplete without a produced assembly; emitted/live gates
remain SKIP. A clean scoped wall-input assessment is not whole-pipeline PASS,
scene geometry acceptance, or a substitute for the original P2 produced tests.

The local verifier explicitly expects the four inventory FAILs and preserves
both raw validator reports unchanged. Its exit0 means its **bounded assertions**
held, not that the accepted validator returned0 (it returns1 for both commands).
It checks source-specific analytical lines, authority shape+hashes+values,
sixteen documented dimensional formulas via P2, the input-only file boundary,
and before/after hashes of the inputs, actual sources, seed files and validator.
