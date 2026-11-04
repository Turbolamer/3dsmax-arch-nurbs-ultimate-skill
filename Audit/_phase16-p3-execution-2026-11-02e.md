# P3 held-read execution wrapper — offline preparation and bounded live controls

Ownership: new `Audit/phase16-p3-execution-2026-11-02e/` and this new report only.
No live Max calls were made by this subagent. Offline preparation did not write
user inputs, save/reset, run an installer or overwrite existing evidence. Main
subsequently executed the controls sequentially and supplied the results recorded
below; no additional Max calls were made to record them. Delegated filenames
retain `2026-11-02e`; the harness date advanced to 2026-11-03 during preparation.

## Status and offline evidence

**Initial offline status was UNVERIFIED IN MAX.** `pair_filein.py` remains an
offline generator, not an executor. The bounded main-reported live observations
below supersede that initial status only for the exact exercised controls.
`offline-tests.json` records 13/13 Python tests, no failure/error/skip, exit 0,
AST parsing of all three Python files and unchanged before/after hashes for 12
source/control artifacts. Tests check exact hash grammar, both mismatch positions,
pair-size bound, same-file refusal, non-pipe paths, output confinement/exclusive
creation, CLI refusal without output, and generated control-flow text. They do
not execute or validate MAXScript syntax, .NET overloads, Windows sharing, lock
behavior, hash interop, fileIn compatibility or cleanup behavior.

## Authentic pair usage

Main supplies the **approved exact two paths and expected hashes** from authentic
publication; do not derive approval from a newly substituted pair. The utility
read-hashes both sources and refuses mismatch before generating anything. It
creates only one new wrapper under its delegated directory using `xb`; existing
wrapper/evidence always refuses. Input files are never opened for write.

```text
python -B Audit/phase16-p3-execution-2026-11-02e/pair_filein.py --manifest APPROVED_RUN/wall_surface.json --script APPROVED_RUN/wall_surface.ms --manifest-sha256 EXACT_APPROVED_64_LOWERCASE_HEX --script-sha256 EXACT_APPROVED_64_LOWERCASE_HEX --out Audit/phase16-p3-execution-2026-11-02e/NEW_AUTHENTIC_WRAPPER.ms
```

Then main executes the wrapper itself with an ordinary `fileIn` (not a direct
bridge function definition), for example `fileIn "D:/.../NEW_AUTHENTIC_WRAPPER.ms"
quiet:true`. **Success returns the actual delegated fileIn value**, including
`undefined`/false if that is what it returns. There is no synthetic OK envelope.
Failure captures `getCurrentException()`, attempts cleanup of both streams and
SHA256, then `throw`s the original exception text; any cleanup failure is appended.
This is exception-text propagation, not preservation of an original stack object.
Main must inspect bridge raw errors/markers and returned result separately.

Generated MAXScript, inside one parenthesized file with local helper definitions:

1. Validates each expected SHA as exactly 64 lowercase hexadecimal characters.
2. Opens both exact ordinary local paths with
   `dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.Read`,
   where the three variables are `dotNetClass` enum wrappers. Main subsequently
   reported successful binding for these exact harmless local-file controls;
   this is not general overload/provider/path coverage.
3. Refuses pair sizes above 2 MiB, creates `.NET SHA256`, rewinds and `ComputeHash`s
   each complete held stream, requires EOF position, converts hex with
   `.NET BitConverter.ToString`/hyphen removal/lowercase, and compares both exact
   digests. Either mismatch throws **before** fileIn.
4. Keeps both read handles alive while executing `fileIn scriptPath quiet:true`.
5. After normal return or caught exception, attempts each close independently,
   retries Dispose after Close failure, checks CanRead=false and reports cleanup
   problems before returning/rethrowing. No `formattedPrint`, file write, node
   operation or scene-setting operation occurs in the wrapper. Only the delegated
   authentic emitter can mutate the scene.

## Harmless controls for main

Control expected hashes and exact absolute paths are in
`phase16-p3-execution-2026-11-02e/controls.json`:

```text
6eb0ca08925b20cff94a83f3d2e9b59128ed6f5ad5f43fa71a9f32d40f1d23ed control_pair.json
f29bf54f8b10aeb6c274077efa989bc07620e7895639e121d58ef58e9cfd3e6a control_pair.ms
```

- `control_pair.ms` contains only `2+2`; main reported actual
  `control_wrapper.ms` fileIn result **4** (details below).
- `control_malformed_hash_wrapper.ms` embeds `not-a-sha256` and should throw
  `P16 malformed script SHA-256; fileIn refused` before source opens or fileIn.
- `control_mismatch_hash_wrapper.ms` embeds 64 zeroes for the script hash; main
  reported its expected mismatch exception was caught with the actual source
  digest below. No separate post-mismatch closed-liveness probe was supplied.
- Optional **`control_lock_probe_calibrated.ms`** is the current lock probe.
  Its hash is `38bf9d41c8d724c4046d6e385157e2c142edb94466a0864e2c441bdce08d9618`;
  companion `control_lock_probe_calibrated.json` states its intended observations.
  It tests a compatible second read, then an existing-file WRITE-access open
  while both `FileShare.Read` handles are held. No Write/SetLength/Create/Delete
  occurs. After closing held streams it **calibrates the identical WRITE-open
  signature** with `CanWrite=true`, closes that diagnostic handle, verifies held
  readers reported CanRead=false, and performs an exclusive READ reopen/liveness
  check. Expected tuple is `#("P16_LOCK_PROBE_OBSERVED", true, denialText, true,
  true, true, true)`; actual denial text must be inspected, not treated alone as
  lock proof. A failed denied-open without its successful positive is inconclusive.
   Main reported the calibrated tuple below, including the final exclusive
   read; this is bounded exercised binding, not universal sharing coverage.
- Earlier `control_lock_probe.ms` and its original `controls.json` entry remain
  preserved as unexecuted evidence; **use the calibrated probe instead**. The
  earlier version lacks the positive write-open calibration and proves no lock.

If a negative control unexpectedly returns normally, stop; do not infer that its
harmless code did or did not run from transport success alone. Main can re-hash
controls, inspect all raw error strings, and run the separate calibrated probe
after each refused wrapper to check closed-liveness. The malformed-hash control
remains unexecuted in the results supplied to this subagent.

## Main-executed bounded live controls — normalized transcription

**Main executed these sequentially; this subagent made no Max calls.** New records
`phase16-p3-execution-2026-11-02e/live-results.json` and
`phase16-p3-execution-2026-11-02e/live-results-transport-supplement.json` contain
**main-supplied normalized-transcribed data, NOT exact raw-wire evidence**. The
supplement preserves later-supplied envelope values without rewriting the first
record. Main may independently retain exact raw responses. In particular the
sharing-denial path was quoted in the actual diagnostic; the normalized text
does not reconstruct raw literal quote escapes.

| Main-reported call | Request ID | elapsed ms / RTT ms | Observation |
|---|---|---|---|
| Initial direct calibrated lock probe | `07e0f58df6194acaad3391727f473e5a` | 3.86 / 3.822 | Generic OK only; not semantic flag evidence |
| Calibrated lock probe rerun as string | `f9700810011c4c67968a93674c12d2f1` | 2.25 / 2.228 | `P3_LOCK_CALIBRATION` followed by calibrated tuple |
| Actual hash/fileIn positive | `289cbbe2f8ca461597244f4dd8082ecf` | 9.095 / 9.068 | `P3_HASH_FILEIN_CONTROL\|4` |
| Intentional script-hash mismatch | `9100f884d1a041efa5b59d354e1232b3` | 2.331 / 2.312 | caught=true; script SHA-256 mismatch, fileIn refused |

Main supplied each envelope as `ok:true`, `warnings:[]`, `error:null`, transport
`namedpipe`, requested transport `auto`, protocol version 2, fallback error null.
The mismatch exception was deliberately caught inside its probe, so this clean
transport envelope is not a claim that the refused wrapper executed successfully.
Main reports no files touched by the probes.

Normalized lock result:

```text
P3_LOCK_CALIBRATION|#("P16_LOCK_PROBE_OBSERVED",true,<sharing-denial diagnostic>,true,true,true,true)
```

The diagnostic was a .NET exception saying the exact `control_pair.ms` file could
not be accessed because another process was using it. The tuple reports a
compatible second READ, denied WRITE-access open while readers were held, both
readers closed (`CanRead=false`), the **identical WRITE-open signature succeeding
after close** (`CanWrite=true`), and exclusive READ reopen/liveness. This is a
calibrated bounded observation, not an absence inference from one thrown open.

The positive reports actual fileIn value 4. The negative reports actual script
digest `f29bf54f8b10aeb6c274077efa989bc07620e7895639e121d58ef58e9cfd3e6a`
and intentional script-mismatch refusal before fileIn. Full-stream hash/fileIn
control and calibrated local sharing behavior are therefore **main-reported live
observations**, not merely offline predictions.

The recorder independently read current bytes of seven utility/control files;
all six available preserved control-digest comparisons match, and the supplemental
read matches the first transcription. These are **current source hashes**, not
an independently captured at-execution manifest. No source/control file or earlier
JSON evidence was overwritten. Malformed-hash, manifest-mismatch, oversized-pair,
delegated-emitter exception and cleanup-failure injections remain untested in the
supplied live evidence; no separate post-mismatch closed-liveness call was given.

## Exact threat-model boundary

The intended Windows sharing contract excludes subsequent ordinary WRITE/DELETE
opens on each held file while allowing a compatible direct fileIn read. Main's
reported controls exercise calibrated WRITE-open denial/post-close success and
hash/fileIn compatibility on this exact ordinary local file pair. **A DELETE-open
denial control was not supplied**, nor was any arbitrary-race protection tested.
Regular drive-letter local paths avoid the named-pipe FileStream normalization
pitfall. This does not assert immutable parent directories, handle-relative
fileIn, protection against arbitrary adversarial replacement/races, kernel or
process termination cleanup, privileged bypass, hostile providers, reparse-point
or hard-link alias exclusion, persistence, or scene correctness. Parent paths
are not held. Python path normalization is only ordinary-path validation, not a
security guarantee. Use controlled private run directories and a single writer.

The utility is audit-only and does not alter the accepted runtime contract, accept
geometry, remove P2 skips, or authorize broader scene work. Main-reported live
findings are recorded above as new evidence; original generated controls and
their initially-unexecuted metadata remain preserved.
