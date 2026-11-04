# Phase 16 P3.1 — independent preservation check

This is a preservation-only observation, not an acceptance or test verdict.

## Scope and timing

* Inventory: 2026-11-03 17:35:06.070147–17:35:09.818629 UTC. Sequential SHA-256 reads of **832** enumerated working-tree files, including tracked, untracked, ignored and hidden files. Excluded root `.git` metadata, this new evidence directory, transient `__pycache__` directories and `.pyc`/`.pyo` bytecode only. No enumeration/read anomalies or symlinks were recorded.
* Manifest comparison: 2026-11-03 17:35:09.819735–17:35:10.192179 UTC. Against all **827** `all_current_preserved_files` entries in `Audit/_phase16-p3-post-publication-2026-11-02e.json`: **826 match, 0 missing, 1 changed, 0 indeterminate**. A separate SHA-256 pass using `hashlib.file_digest` likewise checked all 827 and found the same sole mismatch.
* This was **not an atomic snapshot**: files were read sequentially and other agents could create or change disjoint files while the walk ran. The inventory represents files and hashes as observed, not a guarantee about a later moment. Per-file observation times and sizes appear in `inventory.json`; the five enumerated paths absent from the historical manifest are in `comparison.json`.

## Exactly missing/changed historical entries

Missing: **none**.

| Changed path | Historical expected SHA-256 | Observed current SHA-256 |
| --- | --- | --- |
| `graphify-out/cache/last_query_stamp` | `c6d5293f4b7894cc831cc7498408a8ed8f6935646a95a67e68961c688c6f3cdb` | `6980623a2aa48778f3bac7d0f0c8d2c79e4ec4455d088d6b1a0e76a89d80828a` |

The changed entry is reported as observed; no cause is assigned and no attempt was made to restore it. Its observed filesystem mtime was 2026-11-03 17:28:19.003224 UTC. The three documents separately recorded as tested-versus-published in the historical manifest each match their **published** hash, not their earlier tested hash; this is not additional post-publication drift.

## Explicit protected checks

* HEAD matches historical `7951e3f584be83e7655072a11bb193c1982128fe`.
* Package `3dsmax-arch-nurbs-ultimate.skill` matches historical SHA-256 `dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a` (1,370,910 bytes). The historical external backup also matches its recorded SHA-256 `b2c1262a46e5c3cedab0c50de70ba8dd9b326a27a3aafe7b41a6e9811e1574bb` (8,037,954 bytes). Both were read as bytes; no installation, archive creation, extraction or deletion was performed.
* All six original Main01/Main02/Main03 `published/wall_surface.json` and `published/wall_surface.ms` files match both the post-publication manifest and each run's unchanged `completion.json` pair hashes. All six paths and individual expected/current hashes are recorded in `comparison.json` under `main_pairs`.
* Historical `Audit/phase16-p3-f01-input-2026-11-02e/input-lock.json` matches its recorded SHA-256 `f4c7b2393e345280aab635567cef5d868921e9aec53b8ea10e7aaa7efcbc8050`. Its nine referenced targets were separately checked: **8 match the historical lock; 1 does not**, the already-documented contract. For `Audit/_phase16-p3-contract-2026-11-02e.md`, historical lock expected `25a017893a2b42bfa5cd22539a6f8ff8e55d8a0dfc2ef4f92d10cc2c2b934aca`, current `4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f`; the current contract matches the post-publication manifest. The historical lock was not rewritten and is not a fresh nine-file lock.
* The manifest bytes used have SHA-256 `2ebde0a346e2ee21eb1bf8aae6598fb79b68c72e885ab55491a116f363008c6d`, unchanged on an end read. Its own path, absent from its preserved-file map, is included in the continuation inventory.

## Artifacts and limits

* `inventory.json`: full current non-Git file census, per-file hash, metadata and observation times.
* `comparison.json`: full 827-entry expected/current comparison, exact drift, HEAD, package, backup, Main pairs, input-lock target and historical document checks.
* `check_preservation.py`: read-only census/comparison program, with exclusive creation of the two JSON outputs. The independent corroborating hash pass was executed separately.

This agent performed no Max calls, tests, Git mutation, installer or modifications outside this new directory. SHA-256 equality supports byte equality to the recorded evidence, not live-model correctness or stage acceptance.
