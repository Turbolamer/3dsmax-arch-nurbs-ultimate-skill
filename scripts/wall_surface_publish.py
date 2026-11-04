"""Publish a prebuilt wall-surface pair into a NEW Windows run directory.

This is intentionally not a general transaction or hostile-filesystem sandbox.
The caller supplies both complete byte strings; their semantics are not checked.
An existing output (even an identical one or an empty directory) always refuses.
The parent must already exist. Ordinary Windows drive-letter paths are supported.

The two exclusive-create files are flushed, fsynced and read back in a private,
random sibling directory. Windows os.rename publishes that directory without
replacement. Ancestor/stage identities and reparse points are checked at bounded
checkpoints. This does NOT promise arbitrary adversarial-race safety, power-loss
durability, or cleanup after process death. No installer or scene API is involved.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import BinaryIO


ARTIFACT_NAMES = ("wall_surface.json", "wall_surface.ms")
MAX_ARTIFACT_BYTES = 32 * 1024 * 1024
MAX_PAIR_BYTES = 2 * 1024 * 1024
_CHUNK_BYTES = 1024 * 1024
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_Identity = tuple[int, int]


class PublicationError(RuntimeError):
    """Refusal or recovered failure; evidence_path marks retained stage evidence."""

    def __init__(self, message: str, *, evidence_path: Path | None = None) -> None:
        super().__init__(message)
        self.evidence_path = evidence_path


def _require_windows() -> None:
    if os.name != "nt" or sys.platform != "win32":
        raise PublicationError("publication is Windows-only; refusing before filesystem writes")


def _output_path(out_dir: Path) -> Path:
    if not isinstance(out_dir, Path):
        raise PublicationError("out_dir must be a pathlib.Path")
    if ".." in out_dir.parts or (out_dir.drive and not out_dir.root):
        raise PublicationError("parent traversal and drive-relative paths are not supported")
    path = out_dir.absolute()  # Not resolve(): links must remain visible to lstat.
    if len(path.drive) != 2 or path.drive[1] != ":" or not path.drive[0].isalpha():
        raise PublicationError("only ordinary Windows drive-letter paths are supported")
    if path == Path(path.anchor):
        raise PublicationError("a drive root cannot be a new output directory")
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(prefix + digit for prefix in ("COM", "LPT") for digit in "123456789¹²³")
    for part in path.parts[1:]:
        if (not part or part[-1] in " ." or any(ord(c) < 32 or c in '<>:"/\\|?*' for c in part)
                or part.split(".", 1)[0].upper() in reserved):
            raise PublicationError(f"unsupported/ambiguous Windows path component: {part!r}")
    return path


def _identity(info: os.stat_result, *, directory: bool) -> _Identity:
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & _REPARSE_POINT:
        raise PublicationError("link/reparse point is not allowed")
    expected_kind = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected_kind(info.st_mode):
        raise PublicationError("expected an ordinary directory" if directory else "expected a regular file")
    if not info.st_ino:
        raise PublicationError("filesystem does not expose a usable file identity")
    if not directory and info.st_nlink != 1:
        raise PublicationError("staged file must have exactly one hard link")
    return info.st_dev, info.st_ino


def _path_identity(path: Path, *, directory: bool) -> _Identity:
    return _identity(path.lstat(), directory=directory)


def _ancestors(parent: Path) -> dict[Path, _Identity]:
    # Root first: never deliberately descend through an observed reparse point.
    return {p: _path_identity(p, directory=True) for p in (*reversed(parent.parents), parent)}


def _check_ancestors(identities: dict[Path, _Identity]) -> None:
    for path, identity in identities.items():
        if _path_identity(path, directory=True) != identity:
            raise PublicationError(f"ancestor identity changed: {path}")


def _check_stage(stage: Path, identity: _Identity) -> None:
    if _path_identity(stage, directory=True) != identity:
        raise PublicationError(f"staging directory identity changed: {stage}")


def _refuse_existing(path: Path) -> None:
    try:
        path.lstat()  # Includes broken symlinks and junctions; exists() is unsuitable.
    except FileNotFoundError:
        return
    raise PublicationError(f"output already exists; replay/overwrite is forbidden: {path}")


def _open_binary(path: Path, mode: str) -> BinaryIO:
    return path.open(mode)


def _write_artifact(path: Path, content: bytes, owned: dict[str, _Identity]) -> None:
    with _open_binary(path, "xb") as stream:
        identity = _identity(os.fstat(stream.fileno()), directory=False)
        owned[path.name] = identity  # Record ownership before a write/flush/fsync can fail.
        if _path_identity(path, directory=False) != identity:
            raise PublicationError(f"staged file identity changed during creation: {path}")
        view = memoryview(content)
        offset = 0
        while offset < len(view):
            chunk = view[offset:offset + _CHUNK_BYTES]
            written = stream.write(chunk)
            if type(written) is not int or not 0 < written <= len(chunk):
                raise PublicationError(f"invalid/zero short write: {path}")
            offset += written
        stream.flush()
        os.fsync(stream.fileno())


def _readback(path: Path, identity: _Identity, expected: bytes, digest: str) -> None:
    if _path_identity(path, directory=False) != identity:
        raise PublicationError(f"staged file identity changed: {path}")
    with _open_binary(path, "rb") as stream:
        info = os.fstat(stream.fileno())
        if _identity(info, directory=False) != identity or info.st_size != len(expected):
            raise PublicationError(f"staged file identity/length mismatch: {path}")
        actual_hash = hashlib.sha256()
        offset = 0
        while True:
            chunk = stream.read(_CHUNK_BYTES)
            if not chunk:
                break
            if offset + len(chunk) > len(expected) or chunk != expected[offset:offset + len(chunk)]:
                raise PublicationError(f"staged bytes differ from in-memory artifact: {path}")
            actual_hash.update(chunk)
            offset += len(chunk)
        if offset != len(expected) or actual_hash.hexdigest() != digest:
            raise PublicationError(f"staged readback/hash mismatch: {path}")
    if _path_identity(path, directory=False) != identity:
        raise PublicationError(f"staged file identity changed after readback: {path}")


def _verify_pair(stage: Path, identity: _Identity, owned: dict[str, _Identity],
                 artifacts: dict[str, bytes], hashes: dict[str, str]) -> None:
    _check_stage(stage, identity)
    if {p.name for p in stage.iterdir()} != set(ARTIFACT_NAMES):
        raise PublicationError("staging directory does not contain exactly the closed artifact pair")
    for name in ARTIFACT_NAMES:
        _readback(stage / name, owned[name], artifacts[name], hashes[name])
    _check_stage(stage, identity)
    if {p.name for p in stage.iterdir()} != set(ARTIFACT_NAMES):
        raise PublicationError("staging directory entries changed during readback")


def _check_pair_paths(stage: Path, owned: dict[str, _Identity]) -> None:
    if {p.name for p in stage.iterdir()} != set(ARTIFACT_NAMES):
        raise PublicationError("staging directory entries changed before publication")
    for name in ARTIFACT_NAMES:
        if _path_identity(stage / name, directory=False) != owned[name]:
            raise PublicationError(f"staged file identity changed before publication: {name}")


def _rename_no_replace(stage: Path, output: Path) -> None:
    _require_windows()
    # Windows os.rename raises when ANY destination already exists. Do not replace
    # this with os.replace, shutil.move, or a POSIX rename-with-precheck fallback.
    os.rename(stage, output)


def _cleanup_stage(stage: Path, identity: _Identity | None, owned: dict[str, _Identity],
                   ancestors: dict[Path, _Identity]) -> None:
    """Remove only identity-checked entries made by this call, never recursively."""
    if identity is None:
        raise PublicationError("staging identity was not captured; cannot safely clean up")
    _check_ancestors(ancestors)
    _check_stage(stage, identity)
    if {p.name for p in stage.iterdir()} != set(owned):
        raise PublicationError("unowned/missing staging entry; refusing cleanup")
    # Validate the whole ownership set before deleting any of it.
    for name, file_identity in owned.items():
        if _path_identity(stage / name, directory=False) != file_identity:
            raise PublicationError(f"staged file substituted; refusing cleanup: {name}")
    for name, file_identity in owned.items():
        _check_ancestors(ancestors)
        _check_stage(stage, identity)
        path = stage / name
        if _path_identity(path, directory=False) != file_identity:
            raise PublicationError(f"staged file substituted before unlink: {name}")
        path.unlink()
    _check_ancestors(ancestors)
    _check_stage(stage, identity)
    stage.rmdir()  # Fails (preserving evidence) if an unexpected entry appeared.


def publish_new_directory(out_dir: Path, artifacts: dict[str, bytes]) -> dict[str, str]:
    """Return basename -> SHA-256 hex after a Windows no-replace directory rename.

    Exactly wall_surface.json and wall_surface.ms, each an immutable bytes object,
    must be built before this call. Their combined size must not exceed 2 MiB;
    the separate 32 MiB per-artifact limit is redundant defense. Parents are never made.
    Relative paths are anchored once at entry; '..', drive-relative, UNC/device
    paths, Windows alias names and reparse ancestors are refused. A retained stage
    is reported by PublicationError.evidence_path and its explicit diagnostic.
    """
    _require_windows()
    if (type(artifacts) is not dict or any(type(k) is not str for k in artifacts)
            or set(artifacts) != set(ARTIFACT_NAMES)):
        raise PublicationError("artifacts must be a dict containing exactly wall_surface.json and wall_surface.ms")
    pair = artifacts.copy()  # Closed immutable payload snapshot, not a lazy iterator.
    for name, payload in pair.items():
        if type(payload) is not bytes or len(payload) > MAX_ARTIFACT_BYTES:
            raise PublicationError(f"{name} must be immutable bytes of at most {MAX_ARTIFACT_BYTES} bytes")
    if sum(len(payload) for payload in pair.values()) > MAX_PAIR_BYTES:
        raise PublicationError(f"combined artifact pair must be at most {MAX_PAIR_BYTES} bytes")
    hashes = {name: hashlib.sha256(pair[name]).hexdigest() for name in ARTIFACT_NAMES}
    output = _output_path(out_dir)
    stage: Path | None = None
    stage_identity: _Identity | None = None
    owned: dict[str, _Identity] = {}
    ancestors: dict[Path, _Identity] = {}
    try:
        ancestors = _ancestors(output.parent)
        _refuse_existing(output)
        _check_ancestors(ancestors)  # Before staging, not just after payload writes.
        stage = Path(tempfile.mkdtemp(prefix=".wall-surface-stage-", dir=output.parent))
        stage_identity = _path_identity(stage, directory=True)
        _check_ancestors(ancestors)
        if stage_identity[0] != ancestors[output.parent][0]:
            raise PublicationError("staging and destination parent are not on the same volume")
        for name in ARTIFACT_NAMES:
            _check_ancestors(ancestors)
            _check_stage(stage, stage_identity)
            _write_artifact(stage / name, pair[name], owned)
        _verify_pair(stage, stage_identity, owned, pair, hashes)
        _check_ancestors(ancestors)  # Before publication; detectable substitutions refuse.
        _check_stage(stage, stage_identity)
        _check_pair_paths(stage, owned)
        _refuse_existing(output)
        _rename_no_replace(stage, output)
        # No fallible filesystem operation follows the commit point. Never delete
        # output, including when a caller retries after an uncertain interruption.
        return hashes
    except Exception as exc:
        if stage is not None:
            try:
                _cleanup_stage(stage, stage_identity, owned, ancestors)
            except Exception as cleanup_exc:
                raise PublicationError(
                    f"publication refused/failed: {exc}; cleanup refused/failed: {cleanup_exc}; "
                    f"preserved staging evidence (recorded path, possibly moved): {stage}",
                    evidence_path=stage,
                ) from exc
        if isinstance(exc, PublicationError):
            raise
        raise PublicationError(f"publication refused/failed before confirmed commit: {exc}") from exc
