"""Offline-only, no-overwrite generator for a bounded held-read MAXScript wrapper.

The generated MAXScript has NOT been executed by this utility. Ordinary Windows
FileStream enum binding, hash calls, fileIn sharing and cleanup need a live probe.
This is a controlled-local-directory aid, not a parent-directory/race defense.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).absolute().parent
MAX_PAIR_BYTES = 2 * 1024 * 1024
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


def require_hash(value: str) -> str:
    if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
        raise ValueError("expected SHA-256 must be exactly 64 lowercase hex digits")
    return value


def ordinary_path(value: Path | str, *, exists: bool) -> Path:
    """Canonical ordinary drive-letter path; NOT ancestor-handle protection."""
    path = Path(value).absolute()
    text = str(path)
    if re.match(r"^[A-Za-z]:[\\/]", text) is None:
        raise ValueError("only ordinary Windows drive-letter paths are supported")
    if any(ord(char) < 32 for char in text) or '"' in text:
        raise ValueError("control characters and quotes are not supported in paths")
    if ":" in text[2:]:
        raise ValueError("alternate-stream path is not supported")
    if path.is_symlink():
        raise ValueError("direct symlinks are not supported")
    path = path.resolve(strict=exists)
    if re.match(r"^[A-Za-z]:[\\/]", str(path)) is None:
        raise ValueError("resolved path is not an ordinary drive-letter path")
    if exists and not path.is_file():
        raise ValueError("source must be an existing ordinary file")
    return path


def ms_literal(value: str) -> str:
    """Regular MAXScript string literal, not Python/JSON-only escape syntax."""
    if any(ord(char) < 32 for char in value):
        raise ValueError("control characters are not supported in MAXScript literals")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def inspect_pair(
    manifest_path: Path | str,
    script_path: Path | str,
    manifest_sha256: str,
    script_sha256: str,
) -> tuple[Path, Path]:
    """Read sources only; refuse source mismatch before producing a wrapper."""
    require_hash(manifest_sha256)
    require_hash(script_sha256)
    manifest = ordinary_path(manifest_path, exists=True)
    script = ordinary_path(script_path, exists=True)
    if os.path.samefile(manifest, script):
        raise ValueError("manifest and script must be two distinct files")
    total = 0
    for path, expected in ((manifest, manifest_sha256), (script, script_sha256)):
        digest = hashlib.sha256()
        with path.open("rb") as source:
            while chunk := source.read(65536):
                total += len(chunk)
                if total > MAX_PAIR_BYTES:
                    raise ValueError("artifact pair exceeds the 2 MiB execution ceiling")
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise ValueError(f"source SHA-256 mismatch before wrapper generation: {path}")
    return manifest, script


_HELPERS = r'''
    -- Definitions are inside this fileIn-loaded file, not a bridge fn call.
    fn p16ExpectedHash value =
    (
        if (classOf value) != String then return false
        if value.count != 64 then return false
        for i = 1 to value.count do
            if (findString "0123456789abcdef" (substring value i 1)) == undefined do return false
        true
    )
    fn p16Digest256 hasher stream =
    (
        stream.Position = 0
        local raw = hasher.ComputeHash stream
        local hex = ((dotNetClass "System.BitConverter").ToString raw) as string
        if stream.Position != stream.Length do throw "P16 incomplete full-stream SHA-256 read"
        toLower (substituteString hex "-" "")
    )
    fn p16CloseRead stream label =
    (
        local problem = undefined
        if stream != undefined do
        (
            try (stream.Close()) catch (problem = getCurrentException())
            if problem != undefined do
            (
                try (stream.Dispose(); problem = undefined)
                catch (problem = getCurrentException())
            )
            if problem == undefined do
            (
                try (if stream.CanRead do problem = "stream still reports CanRead=true")
                catch (problem = getCurrentException())
            )
        )
        if problem == undefined then undefined else (label + ": " + problem)
    )
'''


def render_wrapper(
    manifest_path: Path | str,
    script_path: Path | str,
    manifest_sha256: str,
    script_sha256: str,
    *,
    _malformed_control: bool = False,
) -> str:
    """Render only; public CLI additionally hashes both exact source paths.

    The private malformed-control switch is solely for the harmless control pair.
    It deliberately bypasses offline hash validation to exercise live refusal.
    """
    if not _malformed_control:
        require_hash(manifest_sha256)
        require_hash(script_sha256)
    manifest = ms_literal(str(manifest_path).replace("\\", "/"))
    script = ms_literal(str(script_path).replace("\\", "/"))
    return (
        "-- P16 OFFLINE-GENERATED: enum/hash/fileIn sharing needs main's live probe.\n"
        "-- Ordinary local files only; no named pipes, no parent immutability claim.\n"
        "(\n"
        + _HELPERS
        + f'''    local manifestPath = {manifest}
    local scriptPath = {script}
    local expectedManifest = {ms_literal(manifest_sha256)}
    local expectedScript = {ms_literal(script_sha256)}
    local manifestRead = undefined
    local scriptRead = undefined
    local hasher = undefined
    local result = undefined
    local failure = undefined
    local cleanupProblems = ""
    try
    (
        if not (p16ExpectedHash expectedManifest) do throw "P16 malformed manifest SHA-256; fileIn refused"
        if not (p16ExpectedHash expectedScript) do throw "P16 malformed script SHA-256; fileIn refused"
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        -- Both opens are ordinary FileMode.Open/FileAccess.Read/FileShare.Read.
        -- Enum overload syntax and fileIn's sharing are UNVERIFIED until probed.
        manifestRead = dotNetObject "System.IO.FileStream" manifestPath mode.Open access.Read sharing.Read
        scriptRead = dotNetObject "System.IO.FileStream" scriptPath mode.Open access.Read sharing.Read
        if (manifestRead.Length + scriptRead.Length) > {MAX_PAIR_BYTES} do throw "P16 pair exceeds 2 MiB; fileIn refused"
        hasher = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        local actualManifest = p16Digest256 hasher manifestRead
        local actualScript = p16Digest256 hasher scriptRead
        if actualManifest != expectedManifest do throw ("P16 manifest SHA-256 mismatch; fileIn refused; actual=" + actualManifest)
        if actualScript != expectedScript do throw ("P16 script SHA-256 mismatch; fileIn refused; actual=" + actualScript)
        -- Do not close/reopen either held stream before the delegated script ends.
        -- The delegated AUTHENTIC script is the only possible scene mutator here.
        result = fileIn scriptPath quiet:true
    )
    catch (failure = getCurrentException())

    -- No finally construct assumed: both closes attempted after any caught error.
    local scriptCleanup = p16CloseRead scriptRead "script close"
    local manifestCleanup = p16CloseRead manifestRead "manifest close"
    if scriptCleanup != undefined do cleanupProblems += (scriptCleanup + " | ")
    if manifestCleanup != undefined do cleanupProblems += (manifestCleanup + " | ")
    if hasher != undefined do
    (
        try (hasher.Dispose())
        catch (cleanupProblems += ("SHA256 dispose: " + (getCurrentException()) + " | "))
    )
    if cleanupProblems != "" do
    (
        if failure == undefined then failure = ("P16 cleanup failure: " + cleanupProblems)
        else failure += (" | P16 cleanup failure: " + cleanupProblems)
    )
    -- Return the actual fileIn value, NOT a synthetic OK envelope.
    -- Re-throw captured original exception text after cleanup, never convert to OK.
    if failure != undefined do throw failure
    result
)
'''
    )


def render_lock_probe(path: Path | str) -> str:
    """Optional read-only control: deny a requested WRITE open, then test liveness.

    The Write open is diagnostic only: no Write/SetLength/Create/Delete occurs.
    Success of that open is a probe FAILURE, not permission to write anything.
    """
    literal = ms_literal(str(path).replace("\\", "/"))
    return (
        "-- P16 OPTIONAL READ-LOCK API PROBE: UNEXECUTED. No file bytes are written.\n"
        "(\n"
        + _HELPERS
        + f'''    local path = {literal}
    local firstRead = undefined
    local compatibleRead = undefined
    local writeAttempt = undefined
    local afterClose = undefined
    local writePositive = undefined
    local failure = undefined
    local cleanupProblems = ""
    local deniedWriteMessage = undefined
    local compatibleReadPassed = false
    local firstClosed = false
    local compatibleClosed = false
    local reopened = false
    local writeOpenCalibrated = false
    try
    (
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        firstRead = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.Read
        compatibleRead = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.Read
        compatibleReadPassed = compatibleRead.CanRead
        -- Open an existing file only; do not call any write/resize operation.
        try (writeAttempt = dotNetObject "System.IO.FileStream" path mode.Open access.Write sharing.ReadWrite)
        catch (deniedWriteMessage = getCurrentException())
        if writeAttempt != undefined do throw "P16 probe FAIL: WRITE open unexpectedly succeeded"
        if deniedWriteMessage == undefined do throw "P16 probe FAIL: missing WRITE denial diagnostic"
    )
    catch (failure = getCurrentException())
    local extraCleanup = p16CloseRead writeAttempt "unexpected write handle close"
    local compatibleCleanup = p16CloseRead compatibleRead "compatible read close"
    local firstCleanup = p16CloseRead firstRead "first read close"
    if extraCleanup != undefined do cleanupProblems += (extraCleanup + " | ")
    if compatibleCleanup != undefined do cleanupProblems += (compatibleCleanup + " | ")
    if firstCleanup != undefined do cleanupProblems += (firstCleanup + " | ")
    if firstRead != undefined do try (firstClosed = not firstRead.CanRead) catch (failure = getCurrentException())
    if compatibleRead != undefined do try (compatibleClosed = not compatibleRead.CanRead) catch (failure = getCurrentException())
    -- Calibrate the EXACT attempted WRITE-open signature once held reads are closed.
    -- No write/resize is called; an earlier throw alone is not lock evidence.
    if failure == undefined and cleanupProblems == "" do
    (
        try
        (
            local mode = dotNetClass "System.IO.FileMode"
            local access = dotNetClass "System.IO.FileAccess"
            local sharing = dotNetClass "System.IO.FileShare"
            writePositive = dotNetObject "System.IO.FileStream" path mode.Open access.Write sharing.ReadWrite
            writeOpenCalibrated = writePositive.CanWrite
        )
        catch (failure = getCurrentException())
    )
    local writePositiveCleanup = p16CloseRead writePositive "calibrating write handle close"
    if writePositiveCleanup != undefined do cleanupProblems += (writePositiveCleanup + " | ")
    -- A plain sharing.Read reopen cannot prove closure (compatible reads coexist).
    -- CanRead=false observes closure; exclusive READ reopen also checks liveness.
    if failure == undefined and cleanupProblems == "" do
    (
        try
        (
            local mode = dotNetClass "System.IO.FileMode"
            local access = dotNetClass "System.IO.FileAccess"
            local sharing = dotNetClass "System.IO.FileShare"
            afterClose = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.None
            reopened = afterClose.CanRead
        )
        catch (failure = getCurrentException())
    )
    local afterCleanup = p16CloseRead afterClose "liveness read close"
    if afterCleanup != undefined do cleanupProblems += (afterCleanup + " | ")
    if cleanupProblems != "" do
    (
        if failure == undefined then failure = cleanupProblems else failure += (" | " + cleanupProblems)
    )
    if failure != undefined do throw failure
    if not compatibleReadPassed or not firstClosed or not compatibleClosed or not writeOpenCalibrated or not reopened do throw "P16 probe FAIL: incomplete read/close/calibration/liveness observation"
    #("P16_LOCK_PROBE_OBSERVED", compatibleReadPassed, deniedWriteMessage, firstClosed, compatibleClosed, writeOpenCalibrated, reopened)
)
'''
    )


def write_new_owned(path: Path | str, text: str) -> Path:
    """No overwrite; outputs confined to this explicitly delegated directory."""
    target = ordinary_path(path, exists=False)
    root = HERE.resolve(strict=True)
    if not target.is_relative_to(root) or target == root:
        raise ValueError("output must be under the delegated execution directory")
    if not target.parent.is_dir():
        raise ValueError("output parent must already exist; no hierarchy is created")
    with target.open("xb") as destination:
        destination.write(text.encode("utf-8"))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--script-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest, script = inspect_pair(
            args.manifest, args.script, args.manifest_sha256, args.script_sha256
        )
        output = write_new_owned(
            args.out,
            render_wrapper(manifest, script, args.manifest_sha256, args.script_sha256),
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"REFUSED: {exc}\n")
    print(json.dumps({"wrapper": str(output), "status": "OFFLINE_ONLY_NEEDS_LIVE_PROBE"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
