# Phase 16 P2 — orchestration verification, 2026-11-02d

**Coordinator verdict: P2 ACCEPTED in the bounded offline scope after final independent
review; P3 is now eligible for contract/implementation, not implemented.** This file is
filled only from independently observed results. Prior interruption reports are
historical evidence, not settled-tree acceptance. No Max access, installer,
archive/global update or AutoBackup operation has been performed in this session.

## Preservation and environment

- Initial tracked/untracked state was read with `git status --short`; no reset,
  checkout, cleanup or deletion was run. Initial hashes and preservation inventory:
  `_phase16-p2-start-hashes-2026-11-02d.json`,
  `_phase16-p2-preservation-inventory-2026-11-02d.json`.
- `git diff --check` initially exited 0 (LF/CRLF warnings only).
- Read-only installer source/effects inspection is recorded in
  `_phase16-installer-readonly-2026-11-02d.json`. Every target rebuilds the archive;
  globals overwrite and prune. At that instant each global had 6 differing shipped
  files, 2 additions, 0 prune candidates. This is not future install authorization;
  recompute effects immediately before any eventual installation.
- Test runner: `run_phase16_settled.py` records full subprocess logs, command
  exits, all SKIP/xfail qualifier lines and before/after source+fixture hashes.
  It uses the approved OpenCode temporary parent. Zero exit alone is not acceptance.

## Acceptance matrix — accepted offline partition, remaining evidence explicit

| Boundary | Required evidence | Verdict |
|---|---|---|
| G-8 / strict JSON depth | Calibrated deep input, no internal error or false PASS | Executed; 128-container file boundary |
| Transitive provenance | Four faults with independently clean/acyclic controls | Executed; negatives remove broad wall PASS |
| Used upstream strict JSON | Duplicates, precision/overflow, CLI file/rule boundaries | Executed; invalid bytes refuse |
| Legacy builder refusal | Explicit wall lifecycle, route/out modes, byte sentinels | Executed; bounded recovered-I/O guarantees |
| G-82 | Missing cells/host, equal-volume faults, precision, REVIEW/build boundary | Executed; REVIEW/unsupported not PASS |
| Scaffold | Explicit seed provenance/project/force safety, bounded write guarantees | Executed; per-file, not project transaction |
| Original offline harnesses | Both executed on stable hashes; all skips explained | 18 methods + 21 SKIP; 102 OK |
| Additional regressions | Every relevant `Audit/test_phase16_*`, xfail disposition | All 20 scripts exit 0; one API xfail NOT PASS |
| Three historical projects | lint, warnings-as-errors, build, real offline emitter bytes | All three pass; pre-P2 byte parity |
| Poly produced/runtime artifacts | Absent; do not replace with synthetic echoes | NOT RUN — P3+ |

Synthetic wall declarations and draft assemblies test input validation only. They
are not produced assembly, measured Max geometry, physical-direction proof, or
poly QA evidence. No skipped case is converted to PASS by aggregate test counts.

## New review findings before final freeze

The grammar reviewer reported two reproducible G-32 gaps on validator `3675bd7f...`:
changing `building.total_height_cm.derives_from` to unrelated
`site.ground_level_cm` still gives formula PASS, and reaching an upstream derived
value with no formula oracle leaves wall G-10/G-93 PASS. See the precise controls
in `_phase16-grammar-review-2026-11-02d.md`. The validator owner was explicitly
reopened to address these; its earlier source-stop and 122-case report are no
longer final-tree evidence. Main-thread independent retest is still required.

A separate read-only runner review found observation scripts whose zero exit
asserts reproduction of overwrite/truncation. These are labeled observations in
the recorder, not safety PASS. Optimization is cleared in child environments so
plain `assert` controls remain active. Endpoint hashes cannot rule out
change-and-revert; all worker edits must also be stopped before the final run.

The independent builder reviewer returned 14 tests, **11 OK / 3 FAIL** with no
skips/xfails; legacy-build 10 and extra-builder 11 passed on its intermediate
snapshot. New red controls cover B-D1 second-file I/O mixed pair, B-D2 final
wall-route swap and B-D3 final parent-directory substitution. They are genuine
open failures; a separate source owner was assigned repair. Independent test
assertions are not to be weakened. Review artifact:
`_phase16-builder-independent-2026-11-02d.md`.

Separate read-only preservation check found 172/172 inventoried files present,
archive bytes unchanged, 13 example + 36 fixture files unchanged, and 5 recipe
files unchanged. This excludes ignored files not originally inventoried. No
AutoBackup file was accessed. This is preservation evidence, not behavior.

Scaffold/harness independent review returned concrete strict-import laundering
on historical no-wall seeds (duplicate keys and `1e-400` erased before rewriting).
Initializer repair was opened; valid no-selector compatibility is retained, but
ambiguous invalid JSON must refuse before writing. The old numeric parity test
was separately found stale for `9007199254740992.0`: validator and initializer
have deliberately different parser magnitude policies. It will be corrected to
test each boundary, not suppress the real initializer rejection. All observations
and pre-repair reports remain preserved. Historical builder duplicate-key parsing
was likewise referred to the builder owner for actual production-read refusal.

## Preliminary SKIP/xfail disposition (must compare final run)

The independent harness review inventories 21 skips in the original
`test_phase16_p2.py --require-p2`: 2 full produced-poly methods, 2 real-assembly
array cases, 3 real-assembly echo cases, 13 wall mutations needing its supplied
real-fixture path, and 1 future poly-QA/request method. Do not supply a synthetic
locked assembly to clear them: its shape-only guard can accept one. The separate
input-only adapter executes those 13 wall mutations with a **draft** assembly,
not a produced poly output. Missing P3/QA evidence remains NOT RUN.

The sole expected failure in spatial review is the direct API's inability to
recover an already-rounded JSON decimal. The reviewer verified its traceback
reaches the final REVIEW-vs-PASS assertion after the clean and representable-gap
controls. It is a demonstrated API limitation, excluded from passing coverage;
production lossy-token refusal must independently pass before G-82.

The 102-case harness permits alternative rules. Five malformed opening cases
reach G-93 with G-94 SKIP rather than independently exercising G-94. Valid-schema
outside/overlap controls do reach G-94. Aggregate green does not prove every
alternative fired. Complete per-case attribution and rule-level legacy SKIPs are
in `_phase16-scaffold-harness-review-2026-11-02d.md`; final logs must reconfirm.

## Main-thread direct oracle check (not final whole-tree acceptance)

`python -B Audit/test_phase16_legacy_coverage.py LegacyCoverageTests -v`
executed **27 tests OK**, no skips/xfails, in 0.057 s. This independently reached
missing-cell/host, equal-volume gap/overlap, no-opening NOT_APPLICABLE,
REVIEW threshold and thin gaps, unsupported/resource guards, signed frames and
three baselines. It exercises the unchanged spatial oracle directly; integration
and builder scripts were still being repaired, so the complete 37-case suite
and all other required tests remain for the final stopped-source run.

Main also inspected the new builder commit/rollback implementation and executed
`python -B Audit/test_phase16_builder_repair_d.py -v`: **11 tests OK**, no
skips/xfails, 1.736 s, stable builder `7f8d4415aa9a95298f13b16d6b28e6c5e40feaed481564cfc841800f131b9cd4`
and units helper. Production historical duplicate inputs now refuse; both ordinary
replace errors preserve sentinels, deterministic late route/parent substitutions
refuse, rollback-incomplete is honestly reported with retained recovery files.
This does not prove crash atomicity or arbitrary-race resistance. Validator and
initializer edits were still active; whole-tree final repeats remain mandatory.

Independent validator review subsequently found unrelated existing `conflict_ref`
on **given** upstream and wall origins still retains broad wall G-10/G-93 PASS.
The owner's repair was extended with those exact independent CLI tests; its
intermediate G-32 repairs had already discriminated both new formula controls.
Review: `_phase16-validator-independent-2026-11-02d.md`. This is another open
scope/control blocker, not justification to mark all provenance false forever;
final stable targeted retests determine closure.

The initializer owner subsequently reported all used historical seeds strictly
parsed before creation and per-file descriptor staging replacing direct truncating
writes. Main read the repair report, not yet the final full behavioral gate.
Ordinary affected-file I/O preservation does **not** imply whole-project rollback;
earlier complete file commits may remain. Existing non-wall `--force` semantics
are unchanged. Obsolete observation assertions are explicitly being superseded
with new-path protective injections while historical evidence remains preserved.

Builder post-repair static review found a lexical `..` alias self-refusal and a
staging-error/unlink-error diagnostic gap; owner reopened only those concrete
edges. Earlier 11-case main run remains accurate for its named bytes but not the
future full final snapshot. All final runs wait for explicit edit stops.

Main independently repeated the four calibrated transitive controls plus the
four new formula/annotation controls on stopped validator
`616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f`:
`test_phase16_validator_review_d.py FourTransitiveControls` and four selected
`ProvenanceScope` methods — **8 tests / 18 CLI calls OK**, no skips/xfails,
`SOURCE_DRIFT {}`, `OBSERVED_SOURCE_DRIFT {}`. Each clean control passes; all
four transitive faults remove wall G-10/G-93 PASS; wrong formula input and given
annotations fail; unknown reached formula gives wall SKIP, not PASS.
An initial invocation misspelled the test class as `FourHandoff`, producing one
unittest loader error while its four named methods passed. This was a command
selection error, not a validator defect or accepted pass; the corrected complete
8-test selector above supersedes it.

## Final independently executed all-suite run

Command after every author/reviewer edit stop:

```text
python -B Audit/run_phase16_settled.py --out Audit/phase16-p2-final-2026-11-02d
```

20/20 standalone scripts executed, every subprocess exit 0, **no source/fixture
drift**, no Git HEAD change. All **85** recorded file hashes match before/after
and the main thread's subsequent current read. Normal process-exit marker is
present. Complete commands/stdout/stderr/qualifiers/manifests are in that run
directory. Git HEAD: `7951e3f584be83e7655072a11bb193c1982128fe`. Source owners
remained stopped; endpoint hashes alone cannot exclude an unobserved change/revert.

| Suite | Final observed result |
|---|---|
| builder repair / independent review | 13 OK / 14 OK |
| legacy build / extra builder | 10 OK / 11 OK |
| input-only adapter | 1 method, all 13 wall-input subtests, no skips |
| legacy coverage / spatial independent | 37 OK / 17 methods, **1 expected failure** |
| three legacy projects | 2 methods, all three projects and modes, no skips |
| original P2 / cases | 18 methods, **21 SKIP** / 102 OK |
| dependencies / isolated / transitive | 15 OK / 34 OK / 48 OK |
| scaffold independent | exit 0; hardlink substitution refused, sentinel intact |
| scaffold repair / review / safety | 16 OK / 7 OK / 13 OK |
| strict upstream | exit 0; actual strict controls plus labeled counterfactual |
| validator independent / new review | 26 OK / 29 OK (156 CLI calls) |

The unittest logs report 413 discovered top-level methods overall; skips include
subtests, so subtracting 21 to invent a total PASS count would be invalid. The two
standalone diagnostic scripts are not counted as unittest methods. No produced
poly fixture was supplied to the original harness.

### Every remaining skip and expected failure

The original 21 checks remain exactly the 2 produced-poly methods + 2 assembly
array subtests + 3 route echo subtests + 13 locked-wall mutations + 1 future poly
QA/request check enumerated earlier. They are **NOT RUN**, not PASS. Input-only
adapter separately executes all 13 mutation predicates without produced output.
The missing-first-cell legacy check now runs and succeeds; it is no longer skipped.

Main independently reran the original harness with `--require-p2 --fail-on-skip`:
**exit 1**, `OK (skipped=21)`, no unittest failures — correct strict incompleteness
policy. Logs: `phase16-p2-final-supplement-2026-11-02d/strict-harness.*.log`.

Main separately captured the actual expected-failure traceback: after positive
and representable-gap controls, final line 276 receives **PASS rather than REVIEW**
because ordinary JSON already rounded away the decimal gap. Exactly one xfail,
no other errors. Production parser refusals run separately and pass. This API
limitation is excluded from passing evidence, not suppressed as a fixed fault.
Traceback and no-drift supplement result are retained in the supplement directory.

### All legacy finding-level SKIPs

Final lint/strict/build summaries are respectively:
`examples PASS 140 / SKIP 31`, `stepped-tower 147 / 30`, `form-precision 155 / 24`;
all have FAIL 0 / WARN 0. The full final log enumerates each location:
`phase16-p2-final-2026-11-02d/test_phase16_legacy_three_projects.stderr.log`.
No optional/legacy/runtime skip is evidence about geometry:

- G-95/98/99/100: emitted/live wall gates unavailable at JSON lint.
- Absent walls G-1/93/94/97: historical no-selector projects, no wall declaration.
- G-16: no declared numeric range (5 locations, 6 with form QA).
- G-79/80/81, G-70, G-54: script/CSV/committed-Max properties not observed by JSON.
- G-69: no component variants; G-21: no sibling core winding flag.
- G-91: no stepped declarations (executes on stepped-tower).
- G-84/85: no generator; G-86: absent analytical targets; G-87–90 and G-1 QA:
  absent QA on examples/stepped only. Form fixture executes those applicable gates.
- G-1 materials/export: reserved, user-cancelled, not future work.

Both current normal/build emitters actually execute offline into temporary
directories, emitted pair is relinted, and both JSON/MS files match the **actual**
historical builder from `git show 6c0f27b`. This is real offline legacy output,
not new poly/live evidence. All original project bytes remain unchanged.

### Settled executable hashes

```text
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88 scripts/init_project.py
4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac scripts/place_components.py
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f scripts/validate_specs.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
```

Compatibility tightening is explicit: ambiguous/unsafe JSON refuses; legacy
REVIEW/unsupported geometry refuses (including tiny nonzero discrepancies), no
silent fallback; parent-traversal output/input directory spellings refuse. No-cut
oracle is NOT_APPLICABLE, not PASS; the tested real no-opening CLI refusal already
occurred in old G-9. Thick-wall old volume heuristic remains a coverage boundary.
Neither G-32 nor provenance proves arbitrary source truth or physical outward sign;
unknown reached upstream formulas are incomplete and build-refused, wall-local
unknown formulas remain explicit G-32 SKIP. Filesystem safety is recovered bounded
I/O/substitution coverage, not atomic multi-file/crash or arbitrary-race safety.
