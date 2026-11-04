"""Read-only project preservation census; outputs only into this new directory.

Run once from the repository root. Existing evidence is never overwritten.
Concurrent writers can make the resulting inventory non-atomic.
"""

import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess


ROOT = Path.cwd()
OUT = ROOT / "Audit" / "phase16-p3-preservation-2026-11-03f"
MANIFEST_REL = "Audit/_phase16-p3-post-publication-2026-11-02e.json"
LOCK_REL = "Audit/phase16-p3-f01-input-2026-11-02e/input-lock.json"
PACKAGE_REL = "3dsmax-arch-nurbs-ultimate.skill"
MAIN_BASE = "Audit/phase16-p3-main-build-2026-11-02e"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def observe(path):
    """Hash bytes from one open handle, recording whether basic metadata changed."""
    started = utc()
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                return {"status": "non_regular", "observed_utc": started}
            h = hashlib.sha256()
            total = 0
            while True:
                data = handle.read(1024 * 1024)
                if not data:
                    break
                h.update(data)
                total += len(data)
            after = os.fstat(handle.fileno())
        end_path = path.stat()
        before_id = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_id = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        path_id = (end_path.st_dev, end_path.st_ino, end_path.st_size, end_path.st_mtime_ns)
        stable = before_id == after_id == path_id and total == after.st_size
        return {
            "status": "ok" if stable else "unstable_during_read",
            "sha256": h.hexdigest(),
            "size": total,
            "mtime_ns": after.st_mtime_ns,
            "observed_start_utc": started,
            "observed_end_utc": utc(),
        }
    except FileNotFoundError:
        return {"status": "missing", "sha256": None, "observed_utc": utc()}
    except OSError as exc:
        return {"status": "read_error", "sha256": None, "observed_utc": utc(),
                "error": f"{type(exc).__name__}: {exc}"}


def safe_rel(rel):
    path = PurePosixPath(rel)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe manifest path: {rel!r}")
    return ROOT.joinpath(*path.parts)


def write_once(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def main():
    started = utc()
    if not (ROOT / MANIFEST_REL).is_file() or not OUT.is_dir():
        raise RuntimeError("run from repository root with the owned output directory present")
    for name in ("inventory.json", "comparison.json"):
        if (OUT / name).exists():
            raise FileExistsError(f"refusing to overwrite evidence: {OUT / name}")

    # First enumerate/hash the current working tree, regardless of Git tracking or ignore rules.
    # Only Git's metadata, our own output directory and Python bytecode caches are excluded.
    inventory_start = utc()
    files = {}
    anomalies = []
    excluded_counts = {"git_metadata": 0, "own_directory": 0,
                       "pycache_directories": 0, "bytecode_files": 0}

    def walk_error(exc):
        anomalies.append({"kind": "walk_error", "error": f"{type(exc).__name__}: {exc}"})

    for base, dirs, filenames in os.walk(ROOT, topdown=True, followlinks=False, onerror=walk_error):
        basepath = Path(base)
        kept = []
        for name in sorted(dirs):
            path = basepath / name
            rel = path.relative_to(ROOT).as_posix()
            if rel == ".git":
                excluded_counts["git_metadata"] += 1
            elif path == OUT:
                excluded_counts["own_directory"] += 1
            elif name == "__pycache__":
                excluded_counts["pycache_directories"] += 1
            elif path.is_symlink():
                anomalies.append({"kind": "symlink_directory_not_traversed", "path": rel,
                                  "target": os.readlink(path)})
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(filenames):
            path = basepath / name
            rel = path.relative_to(ROOT).as_posix()
            if rel == ".git":
                excluded_counts["git_metadata"] += 1
                continue
            if name.endswith((".pyc", ".pyo")):
                excluded_counts["bytecode_files"] += 1
                continue
            if path.is_symlink():
                anomalies.append({"kind": "symlink_file", "path": rel, "target": os.readlink(path)})
            entry = observe(path)
            files[rel] = entry
            if entry["status"] != "ok":
                anomalies.append({"kind": "file_" + entry["status"], "path": rel,
                                  "observation": entry})
    inventory_end = utc()

    # Load immutable historical manifest in one byte read and record the actual source hash.
    manifest_path = ROOT / MANIFEST_REL
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    historic = manifest["all_current_preserved_files"]
    historical_start = utc()
    records = {}
    for rel, expected in sorted(historic.items()):
        observation = observe(safe_rel(rel))
        status = observation["status"]
        if status == "ok":
            if observation["sha256"] != expected["sha256"]:
                status = "changed"
            elif observation["size"] != expected["size"]:
                status = "size_mismatch"
            else:
                status = "match"
        records[rel] = {"expected_sha256": expected["sha256"],
                        "expected_size": expected["size"],
                        "current_sha256": observation.get("sha256"),
                        "current_size": observation.get("size"),
                        "status": status,
                        "observation": observation}
    historical_end = utc()
    missing = {p: r for p, r in records.items() if r["status"] == "missing"}
    changed = {p: r for p, r in records.items() if r["status"] in ("changed", "size_mismatch")}
    undetermined = {p: r for p, r in records.items()
                    if r["status"] not in ("match", "missing", "changed", "size_mismatch")}

    head = subprocess.run(["git", "--no-optional-locks", "rev-parse", "HEAD"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    package = records[PACKAGE_REL]
    backup_path = Path(manifest["backup"])
    backup = observe(backup_path)
    backup["path"] = str(backup_path)
    backup["expected_sha256"] = manifest["backup_sha256"]
    backup["hash_matches"] = backup.get("sha256") == manifest["backup_sha256"]

    pairs = {}
    for name in ("Main01", "Main02", "Main03"):
        completion_rel = f"{MAIN_BASE}/{name}/completion.json"
        completion = json.loads(safe_rel(completion_rel).read_bytes())
        pair = {}
        for fname in ("wall_surface.json", "wall_surface.ms"):
            rel = f"{MAIN_BASE}/{name}/published/{fname}"
            record = records[rel]
            pair[rel] = {"historical_expected_sha256": record["expected_sha256"],
                         "completion_expected_sha256": completion["artifact_pair_sha256"][fname],
                         "current_sha256": record["current_sha256"],
                         "status": record["status"],
                         "completion_agrees": completion["artifact_pair_sha256"][fname]
                                                == record["expected_sha256"]}
        pairs[name] = {"completion_record_status": records[completion_rel]["status"],
                       "files": pair}

    lock = json.loads(safe_rel(LOCK_REL).read_bytes())
    locked_targets = {}
    for rel, expected in sorted(lock["files_sha256"].items()):
        current = records.get(rel)
        if current is None:
            observation = observe(safe_rel(rel))
            current_sha = observation.get("sha256")
            observation_status = observation["status"]
        else:
            current_sha = current["current_sha256"]
            observation_status = current["observation"]["status"]
        locked_targets[rel] = {"historic_lock_expected_sha256": expected,
                               "current_sha256": current_sha,
                               "matches_lock": observation_status == "ok" and current_sha == expected,
                               "observation_status": observation_status}

    docs = {}
    for rel, expected in manifest["changed_tested_documents"].items():
        current = records[rel]["current_sha256"]
        docs[rel] = {"tested_sha256": expected["tested_sha256"],
                     "published_sha256": expected["published_sha256"],
                     "current_sha256": current,
                     "matches_published": current == expected["published_sha256"],
                     "matches_tested": current == expected["tested_sha256"],
                     "published_agrees_with_preserved_entry":
                         expected["published_sha256"] == records[rel]["expected_sha256"]}

    manifest_after = observe(manifest_path)
    metadata = {
        "started_utc": started,
        "inventory_start_utc": inventory_start,
        "inventory_end_utc": inventory_end,
        "historical_comparison_start_utc": historical_start,
        "historical_comparison_end_utc": historical_end,
        "scope": "All enumerated regular working-tree files (tracked, untracked, ignored, hidden), "
                 "excluding only root .git metadata, this output directory, __pycache__ directories "
                 "and .pyc/.pyo bytecode. No Git mutations; no Max calls.",
        "atomicity": "Non-atomic sequential walk and reads. Concurrent creators/writers can change "
                     "the tree at any time; presence and hashes apply only when observed. "
                     "Stable metadata checks are not a lock or an atomic snapshot.",
        "repository_root": str(ROOT),
    }
    inventory = {**metadata, "files_enumerated": len(files), "exclusions_encountered": excluded_counts,
                 "anomalies": anomalies, "files": files}
    report = {
        **metadata,
        "historical_manifest": {"path": MANIFEST_REL, "created_utc": manifest["created_utc"],
                                "sha256_of_parsed_bytes": digest(manifest_bytes),
                                "end_observation": manifest_after,
                                "stable_across_use": manifest_after.get("status") == "ok" and
                                                     manifest_after.get("sha256") == digest(manifest_bytes)},
        "historical_records": len(records),
        "match_count": sum(r["status"] == "match" for r in records.values()),
        "missing_count": len(missing), "changed_count": len(changed),
        "undetermined_count": len(undetermined),
        "missing": missing, "changed": changed, "undetermined": undetermined,
        "all_historical_comparisons": records,
        "inventory_paths_not_in_historical_manifest": sorted(set(files) - set(historic)),
        "inventory_observation_anomalies": anomalies,
        "head": {"expected": manifest["head"], "current": head, "matches": head == manifest["head"]},
        "package": {"path": PACKAGE_REL, "expected_sha256": manifest["package_sha256"],
                    "current_sha256": package["current_sha256"], "status": package["status"],
                    "hash_matches": package["current_sha256"] == manifest["package_sha256"]},
        "historical_external_backup": backup,
        "main_pairs": pairs,
        "historic_input_lock": {"path": LOCK_REL, "file_comparison": records[LOCK_REL],
                                "entries": locked_targets,
                                "note": "Historic author metadata, not a new nine-file lock; "
                                        "the previously documented contract hash mismatch is not repaired."},
        "historical_tested_vs_published_document_hashes": docs,
    }
    # Write exclusively; artifacts live only in this agent's newly-owned directory.
    write_once("inventory.json", inventory)
    write_once("comparison.json", report)
    print(json.dumps({"inventory_files": len(files), "inventory_anomalies": anomalies,
                      "historical_entries": len(records), "matching": report["match_count"],
                      "missing": missing, "changed": changed, "undetermined": undetermined,
                      "head": report["head"], "package": report["package"],
                      "backup": backup, "inventory_start_utc": inventory_start,
                      "inventory_end_utc": inventory_end,
                      "comparison_start_utc": historical_start,
                      "comparison_end_utc": historical_end}, indent=2))


if __name__ == "__main__":
    main()
