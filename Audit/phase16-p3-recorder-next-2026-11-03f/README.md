# Next frozen P3.1 offline recorder

This is an **independent recorder**, not a P3 acceptance decision. The two older
run directories and their manifests are not modified. Its inputs are measured
at each snapshot, not copied into the result. The genuine Main03 pair and
arm/wrapper are hash-only historical evidence; no generated script, Max, P2
suite, installer or package operation is invoked by the recorder itself.

## Run only after all authors stop

From the repository root, with Python assertions enabled and the approved
`%LOCALAPPDATA%/Temp/opencode` directory available:

```bash
python -B Audit/phase16-p3-recorder-next-2026-11-03f/recorder.py --out Audit/phase16-p3-next-final-2026-11-03f --suite Audit/phase16-p3-replay-tests-2026-11-03f/test_replay_safety.py --suite Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py --input Audit/phase16-p3-replay-tests-2026-11-03f --input Audit/phase16-p3-measurement-next-2026-11-03 --input Audit/phase16-p3-metadata-design-2026-11-03 --input Audit/phase16-p3-layer-design-2026-11-03 --input Audit/phase16-p3-main-probes-2026-11-03f --input Audit/phase16-p3-lease-next-2026-11-03f --input Audit/phase16-p3-runtime-review-2026-11-03 --input Audit/phase16-p3-runtime-hardening-2026-11-03f
```

This command names the additional suites and policy/probe directories that were
present when checked; add any later supplied relevant paths before running it.
It is an instruction for the coordinator, not a record that it ran.

The output must be a **nonexistent direct child of `Audit/`**. Existing paths,
linked/reparse ancestors, auto-discovery-name collisions, and overlap with any
explicit input/suite or protected tree are refused; there is no unique-name
fallback or `--force`. Choose another new output directory for every attempt.

Append `--input PATH` once for **each newly supplied runtime policy/probe source,
helper, fixture, artifact or evidence file/directory** that participates in the
work. Directory inputs are traversed and hashed but never executed. Append
`--suite PATH` for each independently authored test entrypoint outside direct
`Audit/test_phase16_p3*.py`; explicit suites are both hashed and executed.
Both flags are repeatable. Example shape, with the placeholders replaced by
actual existing paths:

```text
... --out Audit/NEW_RUN --input Audit/ACTUAL_POLICY.ms --input Audit/ACTUAL_PROBE_DIR --suite Audit/ACTUAL_INDEPENDENT_TEST.py
```

Do not pass the recorder's output, an ancestor of it (e.g. `Audit/`), or a
nonexistent/link input. Every external dependency cannot be discovered
automatically: a caller who omits a new policy, helper or non-pattern suite has
not frozen it. Do not execute the recorder while files are being edited.

## What it does

* Discovers direct `Audit/test_phase16_p3*.py` files, including future additions,
  the two known replay/measurement independent suite paths when present, plus
  any `--suite`; runs them sequentially as separate Python `-B` processes.
  Seven original named suites are mandatory and have minimum **observed** FINAL2
  method counts 34/7/22/38/65/42/42. Extra suites also need a positive count.
  Known seven use `-v`; other suites receive no guessed flags and must emit a
  recognizable `unittest` `Ran N tests` and `OK` summary, or they fail closed.
  An empty suite is never accepted. No fabricated test or synthetic replacement
  of an unavailable suite is used. Test code is trusted, not sandboxed.
* Stores full, separate stdout/stderr **bytes**, byte counts and SHA-256, argv,
  status, timestamps and before/after input snapshots per suite; overall before,
  after and an explicit final/exit-boundary snapshot. Every snapshot re-enumerates
  suite names and inputs, re-reads HEAD and validates preservation baselines.
* The snapshot includes all `scripts/*.py`, the four current P3 modules, all
  direct Phase16 test files/hash-only helpers, independent oracle, F01 input
  tree, actual CWD-relative authority source, wall/source hash bindings,
  contracts/grammar/status documents and direct P3 evidence, both old full-run
  trees, F01/preflight/measurement/control/state/main-build trees, all example
  and fixture files, package bytes, explicit inputs/suites, and Git HEAD.
  Links/reparse points in hashed paths are refused. Bytecode and cache
  directories are excluded. Newly created/deleted inventoried files cause
  drift. An output name that matches a hash-only discovery prefix is refused so
  the recorder's own evidence cannot enter its input hash map.
* Checks accepted four P2 source hashes, the exact **49** legacy fixture paths
  against the byte-hash-pinned retained P2 manifest, package hash, and four
  reviewed Main03 files. Seven reviewed earlier run-manifest hashes are pinned;
  both whole old-run trees are also snapshotted. The F01 `input-lock.json` is
  retained as historical evidence; its earlier contract entry is **not**
  asserted to match the newer contract. The actual source and wall binding is
  checked separately.
* A nonzero test, absent/zero/short/multiple unittest count, missing/ambiguous OK
  summary, recognizable SKIP/xfail/XPASS/unexpected success, observed drift or
  failed baseline makes the **recorder exit nonzero**. Literal zero-skip
  metadata is not itself a skip. Nonzero test/qualifier outcomes do not suppress
  later suites; observed drift/baseline failure or timeout stops subsequent
  suites and records them NOT_RUN. A timeout can leave grandchildren: review and
  contain them before doing anything further.

`snapshot-verdict.json` and `process-exit.json` retain
`acceptance: NOT_ASSESSED` and do not claim completed P3/Phase16. Exit 0 only
means this recorder observed stable input snapshots and unqualified test
summaries; **main must independently inspect all raw output**, especially for
unrecognized markers or misleading tests. The parser is not a full semantic
test-results oracle, arbitrary test programs can fake logs, child processes are
not sandboxed, and endpoint snapshots cannot exclude change/revert or hostile
filesystem races. `process-exit.json` is written immediately before return;
crash/power-loss durability and post-snapshot stability are not guaranteed.
The original P2 skips, actual Main03 failure and missing live F01/replay gates
remain outside this recorder's evidence.

## Verification performed for this recorder

`selftest.py` builds an isolated fake repository under a **new child of this
directory**. It runs tiny passing, failing, skipped, xfailed, unexpected-success,
zero-test, protected-source drift and explicit-policy drift controls through the recorder; checks raw-log
hashes, explicit input inclusion, snapshots, existing-output refusal and old
evidence preservation. It uses a fake HEAD and tiny fake P2/F01/package data;
these are deliberately **not** P3 evidence. Retained runs:

```bash
python -B Audit/phase16-p3-recorder-next-2026-11-03f/selftest.py --out Audit/phase16-p3-recorder-next-2026-11-03f/selftest-run-005
```

All eight controls produced the expected recorder exit (one clean, seven
refusals); parser checks also exercised xfail/xpass and literal zero-skip
metadata. A read-only snapshot of the actual then-current tree observed 392 files,
49 legacy paths, 7 direct original suites and zero baseline problems; a later
snapshot observed 393 files and zero problems. A snapshot with seven explicit
directories and one independent suite before the measurement suite was added to
discovery observed 410 files, 8 discovered suites and zero baseline problems at
that instant. A subsequent snapshot using all paths in the current command found
417 files, 9 discovered suites and no baseline problems. No snapshot executed the
suites; all are time-specific. Re-snapshot after authors
stop. Prior archived FINAL2 logs were also fed to the parser only; this is not
another test run. No final suite, Max, installation or package rebuild was run.
