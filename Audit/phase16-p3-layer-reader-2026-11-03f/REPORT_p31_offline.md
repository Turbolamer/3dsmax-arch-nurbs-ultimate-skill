# P3.1 bounded layer-reader helper — offline report

## Disposition

**INCOMPLETE / OFFLINE CANDIDATE ONLY.** Added `layer_reader_p31_offline.ms`,
`README_p31_offline.md`, and `test_p31_offline.py` in this directory only.
No runtime, installed copy, Max scene, lease, baseline, replay, or existing
evidence was changed. The MAXScript helper was not compiled, parsed, `fileIn`-ed,
timed, or executed.

## Content

The helper uses `node.layer` → `layerAsRefTarg` exact reference plus handle
roundtrip, detached scalar profiles for the observed 33 interface / 34 backing
fields (including `degrade`), nested 18-field GI reads, bounded witness-based
membership, parent/children refusal, and conservative dependency guards. It
rejects null/unreadable/unknown state, does not call anim APIs on a mixin, and
never uses a layer name as identity. Equal double reads remain
`INCOMPLETE`/partial observation only.

## Verification

`python -B Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py -v`
ran **14 tests, OK**, structural-only. The first run had 2 failures in 11
tests: an incorrect source-token expectation for the manager function argument
and a line-break-sensitive report assertion. Those test expectations were
corrected; further structural checks were added. This is not a Max or replay
pass. Exact live gaps are listed in `README_p31_offline.md` and include
parse/timing, manager witness, hierarchy, membership/dependency completeness,
all-field live controls, lifecycle and same-name replacement, production
integration, and replay/construction safety.
