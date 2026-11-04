# Main authentic F01 publication preparation — runner only

Prepared `Audit/phase16-p3-main-build-2026-11-02e/prepare_main.py` without running
it, the builder CLI, runtime imports, arm generation or Max. The runtime author
is still working per main's explicit steering; no owner/status polling occurs.
Main alone may run this **after all code/runtime/contract authors stop**. No
original fixture/report/source/evidence file was edited. Ownership is only this
new report and the new preparation directory. No install/git/Max operations.

## Main's command, after source freeze

From the repository root in Bash, with a never-used run-id:

```bash
python -B Audit/phase16-p3-main-build-2026-11-02e/prepare_main.py --authors-stopped --run-id Main01 --nonce "$(python -B -c 'import secrets; print(secrets.token_hex(24))')"
```

The explicit acknowledgement is an operator assertion, not automated proof that
authors stopped. The nonce is generated fresh by **main's invocation**, not copied
from a reusable example. It is an operational lease token, not a secret. Prior
owned attempt request hashes are checked to refuse known nonce reuse. There is no
general external freshness proof. Use a new run-id for every attempted invocation;
any existing attempt directory refuses, including a previous failed attempt.

## Exact actual CLI and publication

The runner records the real argv and invokes `scripts/build_wall_surface.py` as
a `python -B` subprocess, with explicit repository-root CWD (authority source
resolution is process-CWD-only, as the decided contract now states):

```text
--in Audit/phase16-p3-f01-input-2026-11-02e/project
--out Audit/phase16-p3-main-build-2026-11-02e/Main01/published
--namespace P3E_F01 --system-type millimeters --system-scale 1
--direction-authority Audit/phase16-p3-f01-input-2026-11-02e/direction-authority.json
```

Actual argv uses canonical absolute paths. The output directory must be absent;
the actual builder/publisher owns pair publication. The runner does not fabricate
a manifest, replace outputs, retry publication or delete failed artifacts.
Actual stdout/stderr/exit are retained before interpretation. Builder exit0 is
only `produced_offline_unverified`, never live acceptance.

## Freeze/hash and identity gates

Before the CLI, record byte hashes and sizes for every `scripts/*.py` source
(membership included), the complete original input fixture tree, accepted input
report, analytical plan/evidence, current decided contract, grammar and this
runner. The actual four F01 domain JSONs, authority, actual analytical source and
accepted P2 validator additionally have independently accepted fixed hashes.
Current P3 code/contract hashes are captured at invocation, **not prematurely
pinned to a still-changing runtime**. The original fixture's historical input
lock is preserved as bytes; it is not silently rewritten to the expanded current
contract. The actual builder's new identity binds the current contract snapshot.

Repeat membership/hash equality before CLI, after CLI, before/after runtime
imports/generation and before completion. Any observed source/input/contract
drift refuses; published files and diagnostics stay for inspection, and a fresh
new output/attempt is required after review. This is observed-drift checking in
a controlled local single-writer directory, not adversarial race/crash immunity.
No original input bytes or Python bytecode are written.

Read back the exact two published files; compare actual CLI returned hashes,
manifest script hash, authentic project/route/subset/owner/namespace/node name,
exact four-field unit object, complete consumed input paths/hashes and generator
closure hashes. Independently recompute the manifest's canonical identity using
the actual public identity record layout. Schema/API drift refuses instead of
guessing. No output is accepted only because subprocess exit0 was observed.

## Actual arm API and separation

Read API sources:
`Audit/_phase16-p3-runtime-2026-11-02e.md` §Public API,
`Audit/phase16-p3-runtime-probes-2026-11-02e/04_arm_protocol.md`, and actual
`scripts/wall_surface_runtime.py` functions. The current manifest contains
predictions, not the full operational plan. Therefore reconstruct the **same**
plan via actual `runtime.build_plan` using the before-hashed raw authentic
walls/dimensions bytes, compare plan predictions with the manifest, and require
actual `runtime.generate_script` to reproduce the exact published script bytes.
Only then call:

```python
runtime.generate_arm_script(
    plan, manifest["identity"], "P3E_F01", manifest["expected_units"],
    nonce=main_supplied_fresh_nonce,
)
```

Save `main_only_arm.ms`, `operational-plan.json` and `arm-record.json` beside,
**not inside**, `published/`. The arm is main-only operational harness support,
**not a produced geometry artifact** and not automatically executed. The runner
does not fileIn, arm a registry, inspect/mutate a scene or infer scene permission.
Main must independently re-read/hash approved files immediately before any live
execution, inspect a fresh empty scene/units and retain the exact external lease
witness required by the arm protocol. This runner grants no live acceptance.

## Retained records and test boundary

Each successful future attempt will retain protected-before/after maps,
request/nonce digest, actual CLI stdout/stderr/exit, the published pair, plan,
arm and arm record. `completion.json` hashes every earlier generated attempt
file and both artifacts; its own SHA is printed (no circular self-hash).
Failure retains `refusal.json` with trace/error, available protected hashes and
retained-file hashes. Existing data is never overwritten or cleaned up.

**Prepared only.** The only allowed local verification at authoring time is
Python AST syntax parsing of this new runner; no runtime/API/CLI behavior is
claimed tested. Main must freeze actual authors and review the runner before
invoking it. No artifact pair, arm file or run directory has been generated by
this subagent.

## Executed after main's explicit author-stop/publication authorization

The preparation-only status above describes the first handoff. Main subsequently
confirmed the runtime author stopped/froze, explicitly authorized the actual
offline CLI publication plus arm/wrapper generation, and prohibited live calls.
Executed the documented runner with fresh main-invocation nonce and new `Main01`.
Actual builder CLI **exit0**, empty stderr. Before/after protected maps are
byte-identical; the original fixture/report remain untouched. No Max call or
fileIn occurred. Runtime source was not repaired or weakened to obtain publication.

Actual four new source hashes, checked before and after generation:

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
03c9accba70648e677fdb837a436256186d2535f438e553910f38cc8725f8c59 scripts/wall_surface_inputs.py
5df101ab21f935d63f061c2f7d7c18659aba3e359970b6d3bb9516b873372ba2 scripts/wall_surface_runtime.py
c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027 scripts/wall_surface_publish.py
```

All following paths share base
`Audit/phase16-p3-main-build-2026-11-02e/Main01/`:

| File | Actual SHA-256 |
|---|---|
|`published/wall_surface.json`|`71c71bb66eb4f887863bc29b5e718340c22cb163fcb176d5c5299f6b9b0278f4`|
|`published/wall_surface.ms`|`9df84585dadc25ba4e76e2d756cae8fee2714555f0e0f72d1f1643804fd9b37b`|
|`main_only_arm.ms`|`a36f425a352e4091bf653b35a3c208812897e4a33749ab0a33ac4d053911b06f`|
|`held_pair_filein.ms`|`cf434e3505f449a2d37942cfd8e3c632fcb713ef0a6a09ee73852590d41abfad`|
|`completion.json`|`5863c99e217391ae902cf7a41abfa97faa3b7483c68fd9bac4243093e8e27d3c`|

Artifact identity:
`1ed30f0e79f3565d999d2f329b0872247643b2d2debef4007e27b39f4b17f13e`.
Namespace `P3E_F01`; actual generated registry key:
`__P3W_4dc75f7c0e0989b8e8e83238fe58a98d079d5a754248affb65ac2505185ddccb`.
The runner read this key from the exact emitted source and checked it against
the actual runtime-generated arm, not a separately guessed ownership name.

The held wrapper is rendered through the actual `pair_filein.py` public API
after its actual source-pair hash check, but written exclusively inside this
owner's new run directory; no other owner's output directory was touched.
Its source hash is locked alongside source/contract/input maps. It is not
executed and makes no live locking/interop claim here. Main retains the external
exact lease witness from arm fileIn and checks it before executing this wrapper.

**NOT ARMED / NOT EXECUTED / NOT ACCEPTED LIVE.** The frozen runtime intentionally
has no safe NOOP branch: specified-normal/native metadata remains incomplete.
The known layer-interface generic-handle baseline reader may safely refuse and
clean the new node; this publication does not hide that blocker or claim initial
construction success. Main alone owns recording actual safe refusal/cleanup
or other live results. Produced pair remains exactly the frozen runtime bytes.
