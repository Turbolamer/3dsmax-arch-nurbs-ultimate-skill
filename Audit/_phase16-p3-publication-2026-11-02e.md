# Phase 16 P3 — bounded new-directory publication helper (2026-11-02e)

## Ownership and status

Implemented only the assigned **new** files:

- `scripts/wall_surface_publish.py`
- `Audit/test_phase16_p3_publication.py`
- this report

This is the accepted narrow publication module contract, **not** acceptance of the
wider wall geometry/runtime method. No existing production script, fixture,
checkpoint, archive, installed copy or scene was changed by this task. No installer,
Max call, reset, save or AutoBackup access occurred. Parent coordinator owns wider
integration, independent review and checkpoint publication.

## API and supported contract

```python
from wall_surface_publish import PublicationError, publish_new_directory

hashes = publish_new_directory(
    out_dir,  # pathlib.Path; new run directory, existing parent
    {"wall_surface.json": complete_json_bytes, "wall_surface.ms": complete_ms_bytes},
)
# hashes: dict[str, str], exact basename -> SHA-256 hexadecimal digest
```

Both complete immutable byte strings must exist before the call. Exact ordinary
`dict` and `bytes` types are required, and names are closed to the two basenames
above. **The combined pair must be at most 2 MiB (2,097,152 bytes)**, inclusive,
enforced by `MAX_PAIR_BYTES` before hashing, path preparation or staging. The older
32 MiB per-artifact cap remains as redundant defense; it does not relax the pair
limit. Empty bytes are valid for this publication-only API: this deliberately does
**not** validate artifact syntax, geometry or provenance. The caller retains
responsibility for those gates.

The helper fails closed unless `os.name == "nt"` and `sys.platform == "win32"`.
Only ordinary Windows drive-letter paths are accepted; relative paths are anchored
once. Traversal, drive-relative, UNC/device paths, alternate streams, reserved
Windows names and trailing-dot/space aliases are refused. Parent directories must
already exist; the helper never creates their hierarchy. It does not certify that
a drive letter maps to a particular storage technology or local/network backend.

Any existing destination refuses, including empty directories, identical previous
outputs, files, symlinks, dangling symlinks and junctions. There is no replay mode,
`--force`, replacement, per-file overwrite or existing-directory merge.

## Publication and recovery

1. Snapshot ancestor `(st_dev, st_ino)` identities using `lstat`, root first; refuse
   links, any Windows reparse point or unavailable file identity. Repeat before
   staging, during the bounded writes and before publication.
2. Allocate a random, newly owned sibling with `tempfile.mkdtemp`; capture its
   identity, check the parent again and require matching device/volume identity.
   "Private" here means a newly owned temporary namespace, **not** a security or
   confidentiality boundary against other users with inherited filesystem access.
3. Create exactly two files with `xb` (exclusive create); record handle identities
   before writes can fail. Handle short writes, flush, then `os.fsync` both files.
4. Require exact directory membership; verify handle/path identities, regular-file
   kind, single hard-link count, exact length, byte-for-byte chunked readback and
   SHA-256. Repeat stage/file path checks before committing.
5. Call **Windows `os.rename(stage, output)`**, whose documented no-replace
   behavior raises for an existing destination. There is intentionally no POSIX
   precheck+rename fallback, `os.replace` or `shutil.move`. No fallible filesystem
   operation is performed after successful rename, and output is never cleaned up.

Recovered failures attempt **non-recursive** cleanup only of exact stage files
recorded as created by this call, with ancestor/stage/file identity checks. The
whole ownership set is checked before any unlink. No unknown file, replacement
file, junction target, user directory or published output is removed. Cleanup
failure/refusal raises `PublicationError` with an explicit original + cleanup
diagnostic and `evidence_path`. A substituted ancestor may have moved the stage:
the diagnostic explicitly identifies this as its **recorded, possibly moved** path.
If cleanup already removed some owned files before a later cleanup failure, only
remaining evidence is retained; no attempt is made to fabricate a recovery pair.

## Executed tests

Command: `python -B Audit/test_phase16_p3_publication.py -v`

Latest source run on Windows / CPython 3.14.4, **2026-11-03 after the pair-limit
repair**: **42 tests, 0 failures, 0 errors, 0 skips**, `OK`, normal exit 0 (0.697
seconds). All writes, injections, symlinks,
hardlinks and junctions were under newly owned per-test directories in
`C:/Users/Turbolamer/AppData/Local/Temp/opencode`.

Coverage includes both payload open/write/partial-write/zero-write/flush/fsync/read
failure positions, corrupt/truncated readback, successful short writes, rename
failure, exact bytes/hashes, deterministic separate new outputs, strict names/types
and inclusive size limit, existing and **late-at-real-Windows-rename** file/empty
directory/symlink/junction collisions, dangling links, symlink/junction ancestors,
parent identity substitution before staging and before publish, junction parent
substitution, stage/file substitution (including after readback), unexpected stage
entries, staged hardlinks, exclusive-create collisions, unlink/rmdir cleanup
failures and explicit evidence diagnostics. Binary sentinel/victim bytes and
replayed output identities are checked. There is a no-write non-Windows refusal
control (injected platform flag), not a real Linux publication run.

The first development run exposed three **test expectation** failures: Windows
`readlink()` returned the `\\?\` namespace prefix. Tests now compare pre/post link
targets and identity instead of asserting a different spelling; no refusal was
weakened. Subsequent 37-test and final expanded 39-test runs passed without skips.

**Independent protective finding and correction (2026-11-03):** the coordinator
reported independent direct-helper `test_22` correctly failing because the helper
published two individually valid 1,126,400-byte artifacts (2,252,800-byte total)
despite the wider 2 MiB pair contract. The earlier 39-test PASS did not cover this
combined-size requirement. The coordinator decided to enforce it in the helper,
not just the CLI. Production now sums both validated immutable byte lengths and
refuses totals above `MAX_PAIR_BYTES = 2 * 1024 * 1024` before any staging.

Added three tests: exact 2 MiB succeeds (balanced and single-payload splits),
2 MiB + 1 refuses, and the exact independent 2,252,800-byte case refuses even
though both individual files are below both caps. Negative controls assert neither
path preparation nor stage creation was reached, and sentinel bytes remain intact.
All 39 previous tests, including no-overwrite/replay/link/junction tests, remain
unchanged and pass in the expanded 42-test suite. The independent author's test
and assertion were **not edited**; this task did not rerun that separate suite.
Its authoritative repeat remains with the independent author/coordinator.

The helper and `specs/fixtures/poly-shell-input/walls.json` are hashed at the start
and end of the test class; both remained unchanged. The fixture is read-only hash
input, never an output fixture or echo of produced geometry. Both owned Python
files also passed `ast.parse` without bytecode output.

Tested bytes (SHA-256):

```text
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
7b62cb2117378c1cb81131c8e7df60eb5a61eeea3dda5051c47566d5ba9ba42d Audit/test_phase16_p3_publication.py
b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93 specs/fixtures/poly-shell-input/walls.json
```

The previous helper hash `c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027`
belongs to the earlier 39-test run. Any new F01 runner should record the repaired
helper hash above and use a **fresh output run directory**. Existing generated
outputs were not touched by this repair and must remain immutable; existing
directories still refuse replay even when their bytes match.

## Explicit limits

This proves bounded ordinary-I/O failure handling and the enumerated detectable
substitutions, **not arbitrary adversarial-race safety**. Identity checks and
path-based operations are not indivisible, held handle-relative capabilities;
substitutions entirely between checks are outside the promise. In-place changes
after verified readback, identity reuse/spoofing, hostile filesystem providers and
arbitrary timing attacks are not claimed safe. A new temp path is not an ACL-based
hostile-process sandbox.

`flush`/`fsync` plus directory rename do **not** establish crash/power-loss
durability; parent directories are not fsynced. Process termination, interruption
at an uncertain commit point, partial cleanup, or external movement can retain
evidence requiring human inspection. The helper does not delete the output or
retry publication to resolve ambiguity. Existing output always refuses.

No material/export, live MAXScript execution, wider builder integration, full P3
acceptance or global installation was attempted or inferred from these tests.
