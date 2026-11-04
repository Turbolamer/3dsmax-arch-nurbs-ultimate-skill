"""New non-atomic preservation record after all 03g authors stop.

Read-only except for an exclusive new JSON output. No Max, tests, git command,
installer, package changes, deletes or rewrites of historical evidence.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "Audit/_phase16-p3-post-publication-2026-11-03f.json"
OUT = ROOT / "Audit/_phase16-p3-post-publication-2026-11-03g.json"
EXPECTED_OLD = "10610b260e3c4dd3d60350dc7de20ab50bb5b523db625ee695989f9b61bb584e"
EXPECTED_PACKAGE = "dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a"
EXPECTED_HEAD = "7951e3f584be83e7655072a11bb193c1982128fe"
ALLOWED_CHANGED = {"CHECKPOINT.md", "scripts/wall_surface_runtime.py", "graphify-out/cache/last_query_stamp"}


def digest(raw):
    return sha256(raw).hexdigest()


def head():
    git = ROOT / ".git"
    value = (git / "HEAD").read_text(encoding="ascii").strip()
    if value.startswith("ref: "):
        ref = value[5:]
        if ref.startswith("/") or ".." in ref.split("/"):
            raise ValueError("unexpected HEAD ref")
        loose = git / ref
        if loose.is_file():
            value = loose.read_text(encoding="ascii").strip()
        else:
            rows = (git / "packed-refs").read_text(encoding="ascii").splitlines()
            found = [r.split()[0] for r in rows if r and not r.startswith(("#", "^")) and r.split()[1] == ref]
            if len(found) != 1:
                raise ValueError("ambiguous packed HEAD")
            value = found[0]
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("invalid HEAD")
    return value


def main():
    if OUT.exists():
        raise ValueError("refusing to overwrite post-publication output")
    start = datetime.now(timezone.utc).isoformat()
    old_raw = OLD.read_bytes()
    if digest(old_raw) != EXPECTED_OLD:
        raise ValueError("03f manifest hash drift; do not silently compare an unverified authority")
    old = json.loads(old_raw)
    files, anomalies = {}, []
    for parent, dirs, names in os.walk(ROOT, followlinks=False):
        parent = Path(parent)
        dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"})
        for name in list(dirs):
            p = parent / name
            st = p.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
                anomalies.append({"path": p.relative_to(ROOT).as_posix(), "reason": "reparse directory"})
                dirs.remove(name)
        for name in sorted(names):
            p = parent / name
            if p == OUT or p.suffix in {".pyc", ".pyo"}:
                continue
            key = p.relative_to(ROOT).as_posix()
            try:
                before = p.lstat()
                if not stat.S_ISREG(before.st_mode) or getattr(before, "st_file_attributes", 0) & 0x400:
                    raise ValueError("not an ordinary file")
                raw = p.read_bytes()
                after = p.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise ValueError("changed during read")
                files[key] = {"sha256": digest(raw), "size": len(raw)}
            except (OSError, ValueError) as exc:
                anomalies.append({"path": key, "reason": str(exc)})
    changed, missing = {}, []
    for key, before in old["all_current_preserved_files"].items():
        current = files.get(key)
        if current is None:
            missing.append(key)
        elif current != before:
            changed[key] = {"before": before, "after": current}
    old_after = digest(OLD.read_bytes())
    current_head = head()
    package = files.get("3dsmax-arch-nurbs-ultimate.skill", {}).get("sha256")
    unexpected = sorted(set(changed) - ALLOWED_CHANGED)
    problems = []
    if missing:
        problems.append("MISSING_HISTORICAL_FILES")
    if anomalies:
        problems.append("CENSUS_ANOMALIES")
    if unexpected:
        problems.append("UNEXPECTED_HISTORICAL_DRIFT")
    if old_after != EXPECTED_OLD:
        problems.append("HISTORICAL_MANIFEST_DRIFT_DURING_READ")
    if current_head != EXPECTED_HEAD:
        problems.append("HEAD_DRIFT")
    if package != EXPECTED_PACKAGE:
        problems.append("PACKAGE_DRIFT")
    record = {
        "scope": "Separate non-atomic post-publication preservation observation, not a test or live/phase acceptance",
        "started_utc": start,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "acceptance": "P3.1_NOT_ACCEPTED",
        "prior_publication": "Audit/_phase16-p3-post-publication-2026-11-03f.json",
        "prior_publication_sha256_before_and_after": [digest(old_raw), old_after],
        "old_entries": len(old["all_current_preserved_files"]),
        "missing": missing,
        "changed_old_entries": changed,
        "unexpected_changed": unexpected,
        "anomalies": anomalies,
        "head": current_head,
        "package_sha256": package,
        "problems": problems,
        "all_current_preserved_files": files,
        "qualification": "Non-atomic sequential read after author-stop; not a filesystem lock or a guarantee against change-and-revert. The output excludes itself. Existing tests are not rerun by this record. Live current scene must be freshly inspected; historical Main03 witness is not re-created or re-armed.",
    }
    raw = (json.dumps(record, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with OUT.open("xb") as stream:
        stream.write(raw)
    if OUT.read_bytes() != raw:
        raise ValueError("record readback differs")
    print(json.dumps({"path": str(OUT.relative_to(ROOT)), "sha256": digest(raw), "files": len(files),
                      "old_entries": record["old_entries"], "missing": missing, "changed": sorted(changed),
                      "unexpected_changed": unexpected, "problems": problems, "head": current_head,
                      "package_sha256": package}))


if __name__ == "__main__":
    main()
