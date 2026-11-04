"""Read-only preservation census and exclusive separate post-publication record.

No Max, git, tests, installer, deletion, rewriting old evidence or acceptance.
Run only after all authors stop. Endpoints are not an atomic filesystem lock.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "Audit/_phase16-p3-post-publication-2026-11-02e.json"
OUT = ROOT / "Audit/_phase16-p3-post-publication-2026-11-03f.json"
EXPECTED_PACKAGE = "dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a"
EXPECTED_HEAD = "7951e3f584be83e7655072a11bb193c1982128fe"
ALLOWED_CHANGED = {
    "CHECKPOINT.md", "PLAN.md", "scripts/wall_surface_runtime.py",
    "graphify-out/cache/last_query_stamp",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def head() -> str:
    git = ROOT / ".git"
    if not git.is_dir():
        raise ValueError("expected normal repository .git directory")
    value = (git / "HEAD").read_text(encoding="ascii").strip()
    if value.startswith("ref: "):
        ref = value[5:]
        if ref.startswith("/") or ".." in ref.split("/"):
            raise ValueError("unexpected Git ref")
        loose = git / ref
        if loose.is_file():
            value = loose.read_text(encoding="ascii").strip()
        else:
            rows = (git / "packed-refs").read_text(encoding="ascii").splitlines()
            values = [r.split()[0] for r in rows if r and not r.startswith(("#", "^")) and r.split()[1] == ref]
            if len(values) != 1:
                raise ValueError("HEAD ref unavailable/ambiguous")
            value = values[0]
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("invalid HEAD")
    return value


def main() -> None:
    if OUT.exists():
        raise ValueError("exclusive publication output already exists")
    start = datetime.now(timezone.utc).isoformat()
    old_raw = OLD.read_bytes()
    old = json.loads(old_raw)
    files = {}
    anomalies = []
    for parent, dirs, names in os.walk(ROOT, followlinks=False):
        parent = Path(parent)
        dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"})
        for d in list(dirs):
            p = parent / d
            info = p.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                anomalies.append({"path": p.relative_to(ROOT).as_posix(), "reason": "reparse directory"})
                dirs.remove(d)
        for name in sorted(names):
            p = parent / name
            if p == OUT or p.suffix in {".pyc", ".pyo"}:
                continue
            key = p.relative_to(ROOT).as_posix()
            try:
                info = p.lstat()
                if not stat.S_ISREG(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise ValueError("not ordinary regular file")
                raw = p.read_bytes()
                end = p.stat()
                if (info.st_size, info.st_mtime_ns) != (end.st_size, end.st_mtime_ns):
                    raise ValueError("observed changed while read")
                files[key] = {"sha256": sha(raw), "size": len(raw)}
            except (OSError, ValueError) as exc:
                anomalies.append({"path": key, "reason": str(exc)})
    changed = {}
    missing = []
    for key, before in old["all_current_preserved_files"].items():
        current = files.get(key)
        if current is None:
            missing.append(key)
        elif current != before:
            changed[key] = {"before": before, "after": current}
    observed_head = head()
    package = files["3dsmax-arch-nurbs-ultimate.skill"]["sha256"]
    problems = []
    if missing:
        problems.append("MISSING_HISTORICAL_FILES")
    if anomalies:
        problems.append("CENSUS_ANOMALIES")
    if set(changed) - ALLOWED_CHANGED:
        problems.append("UNEXPECTED_HISTORICAL_DRIFT")
    if observed_head != EXPECTED_HEAD:
        problems.append("HEAD_DRIFT")
    if package != EXPECTED_PACKAGE:
        problems.append("PACKAGE_DRIFT")
    record = {
        "scope": "Separate post-publication preservation record; not test, live QA, final2 rewrite or P3 acceptance",
        "started_utc": start,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "acceptance": "P3.1_NOT_ACCEPTED",
        "stopped_at_user_request": True,
        "live_mutations_stopped_after_controller_residue": True,
        "last_live_evidence": "Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2-residue.json",
        "prior_publication": str(OLD.relative_to(ROOT)),
        "prior_publication_sha256": sha(old_raw),
        "old_entries": len(old["all_current_preserved_files"]),
        "missing": missing,
        "changed_old_entries": changed,
        "unexpected_changed": sorted(set(changed) - ALLOWED_CHANGED),
        "anomalies": anomalies,
        "head": observed_head,
        "package_sha256": package,
        "problems": problems,
        "all_current_preserved_files": files,
        "qualification": "Non-atomic sequential reads after author-stop; no change-and-revert, arbitrary-race, active-scene continuity, installed-copy or universal preservation guarantee. Output excludes itself to avoid circular digest. Historical tests are not rerun on these new bytes. Temporary Box001/Shell residue must be operator-inspected; no name/handle adoption or automatic cleanup.",
    }
    raw = (json.dumps(record, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()
    with OUT.open("xb") as stream:
        stream.write(raw)
    if OUT.read_bytes() != raw:
        raise ValueError("new publication record readback mismatch")
    print(json.dumps({"path": str(OUT), "sha256": sha(raw), "files": len(files),
                      "old_entries": record["old_entries"], "missing": missing,
                      "changed": sorted(changed), "problems": problems,
                      "head": observed_head, "package_sha256": package}))


if __name__ == "__main__":
    main()
