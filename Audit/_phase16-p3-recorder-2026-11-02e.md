# P3 settled-tree TEST RECORDER — authored 2026-11-02e

**Recorder, not acceptance.** New owned files only:
`Audit/run_phase16_p3_settled.py` and this note. No P2 executable, existing test,
fixture, package, checkpoint or installed copy was changed by this owner.

## Invocation after all source/test/input authors stop

```bash
python -B Audit/run_phase16_p3_settled.py --out Audit/phase16-p3-final-NEW
```

For a second recording without overwriting the first, pass another `--out`, or
opt into `--unique-out` with the original path: it atomically reserves a fresh
`-001`, `-002`, … sibling and prints the actual report directory. The default
continues to refuse an existing directory. An optional repeatable
`--artifact-dir EXISTING_PAIR_DIRECTORY` adds another already-generated pair
and its whole tree to hash-only snapshots; it never builds or executes the pair.

`--out` must not exist. The recorder refuses repository output outside `Audit/`,
all source/spec/example/input-directory overlap, and linked/reparse-point output
ancestors. It does not overwrite an earlier report. `--timeout SECONDS` optionally
sets the per-suite timeout (default 1800). The approved real
`%LOCALAPPDATA%/Temp/opencode` must already exist; disposable child-test activity
uses that parent. Python optimization is refused and removed from child env.

## Exact execution and preservation scope

- Only direct regular `Audit/test_phase16_p3*.py` files are discovered, in exact
  filename order. No recursive discovery, module import/discovery, pytest,
  generic `test_phase16*` execution or P2 suite execution. Every discovered suite
  is invoked as `[sys.executable, "-B", absolute_script_path]`, sequentially, with
  repository cwd, no shell and stdin closed. The six reviewed required suites
  all support `-v`, which is appended for per-test/qualifier evidence. Unknown
  future P3-prefixed suites receive no guessed flags.
  Nonzero test exits do not suppress later suites. Drift/baseline failure or a
  timeout stops the batch; remaining discovered suites are explicitly NOT_RUN.
- Each suite has immutable command metadata, UTC start/end, elapsed seconds,
  returncode/error, separate byte-exact stdout/stderr logs with lengths/hashes,
  before/after full source snapshots including HEAD, and literal stream/line
  references for test lines, summaries, counts and SKIP/xfail/other qualifiers.
  A failing subprocess does not cause its stderr to be rewritten or discarded.
  Counts are observations, not summed evidence or semantic coverage claims.
- Hashes cover all `scripts/*.py` (including the new four P3 modules and their
  dependencies), all direct `Audit/test_phase16*.py` (P2 helper/tests hash-only),
  `Audit/phase16_p3*.py`, this recorder, the full new F01 input tree including its
  direction authority and authoring brief, actual authority-cited source path
  candidates, all example/fixture bytes, root `.skill` bytes, explicit contract/
  grammar/source evidence, accepted P2/preservation manifests and Git HEAD.
  Hash-only scope additionally includes complete preflight, measurement,
  execution, live-controls, runtime/state-probes and main-build preparation
  trees, all direct `_phase16-p3-*` contract/review/MS/JSON evidence, and any
  explicitly supplied artifact directories. Thus test helpers, calibration/
  execution fixtures and a pair main already generated under main-build's
  attempt/published directory are frozen before/after every suite. They are
  **not** executed/discovered as additional suites. Artifact-pair member hashes
  are separately enumerated; missing counterparts are INCOMPLETE, not accepted.
  Directory walks never follow links and exclude bytecode. Missing/unreadable
  inputs are not silently omitted. Root and per-suite manifests are independent
  files, not later overwritten with a newer snapshot.
- Explicit accepted P2 SHA-256 constants protect exactly `init_project.py`,
  `place_components.py`, `validate_specs.py`, `wall_cell_coverage.py`. Exactly
  **49** legacy example/fixture paths and expected bytes are read from the actual
  accepted `Audit/phase16-p2-final-2026-11-02d/hashes-before.json`; its four P2
  source references must agree with those constants. The package must retain its
  pre-P3 preserved SHA-256. Comparisons run before, between and after suites,
  including the best-effort process-exit snapshot. HEAD is read only through
  `git rev-parse --verify HEAD` with optional Git locks disabled.

## Missing coverage is not a pass

`availability.json` has an explicit six-name offline checklist: builder, inputs,
publication, runtime, oracle and independent suites. A missing name is
**NOT_AVAILABLE**, not an invented SKIP or accepted equivalent. Additional direct
P3-prefixed suites still run; the checklist is not an acceptance matrix. At the
first inspection runtime/oracle files were still pending. On main's follow-up,
all six required filenames are present; their existence is explicitly **not**
execution evidence. Main reported prior counts publication39, inputs31,
runtime40, builder34, oracle65; independent remained pending. These are retained
as reported review baselines, not fabricated current results. Final execution
requires a literal positive `Ran N tests` observation per required suite; no
positive count, a count below main's reported baseline, missing suite or NOT_RUN
remains an explicit coverage qualification. Extra tests are not treated as a
failure. Availability and evidence are recomputed at the actual invocation.
The standalone oracle helper is not itself an executable test suite.

The optional generated-pair availability row remains NOT_AVAILABLE if no pair
exists; that absence does not block an **offline-only** test recording and is
never supplied by a fabricated pair. Main's genuine prepared pair is included
automatically when present under the explicitly hashed main-build tree; another
location can be supplied with `--artifact-dir`. All presence/execution/count
fields coexist with `complete_phase16_or_p3: false`.

All reports retain `acceptance: NOT_ASSESSED` and
`complete_phase16_or_p3: false`. Exit 0 means only successful recording on the
observed stable protected tree; SKIP/xfail and passing fault observations still
require review. Exit 1 means observed drift, protected-byte mismatch, missing
HEAD/read error, failed/aborted execution or no discovered suites. Exit 2 means
the run recorded normally but its required suite/source checklist still has
NOT_AVAILABLE entries or lacks sufficient positive test-count observations
(or ordinary argument/preflight refusal before creating a
report). A process-exit marker distinguishes a normal end from interruption.
Its later snapshot can invalidate the earlier verdict and explicitly reports
FAILED on drift; Python's returncode was already selected before that atexit
snapshot, so both records must be inspected.

No actual F01 fileIn, live units/geometry/void/census/stack checks, three real
no-op replays or edit/collision/cleanup controls are supplied by this recorder.
It never invokes Max, install/archive generation, Git write, resets, cleanup of
user inputs or legacy fixture repair. It does not repeat P2; main can invoke the
existing accepted recorder separately if needed. Authored tests are trusted
programs, not sandboxed; endpoint snapshots cannot exclude change-and-revert,
arbitrary concurrent writers or child side effects outside the manifest. A timed
out test's grandchildren are not broadly killed, so no further suites launch.

## Verification performed by this owner

Executed a bytecode-free `compile(..., 'exec')` syntax check under `python -B`:
**SYNTAX_OK**. No recorder/test behavior run before the other authors settle;
no final recording or P3 acceptance is claimed. Main must inspect the new
recorder and run it only after all authors finish. No installer or package
rebuild is allowed for this unfinished method.

Follow-up verification executed Python **AST parsing only** of the revised
recorder and six direct P3 suites: **AST_PARSE_OK**, no imports, runtime calls
or test execution. Static `test_*` method counts at this inspection were
builder34 / independent22 / inputs31 / oracle65 / publication42 / runtime40.
Publication already has three more method definitions than main's prior39;
this is source inspection, not a 42-test result or author-freeze assertion.
The current six filenames and their documented entrypoint argument handling
were inspected to keep discovery deterministic. Main alone will perform the
final recording after the source/test/tool authors stop.
