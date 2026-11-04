#!/usr/bin/env python3
"""MAIN ONLY, AFTER authors stop: publish a new offline pair and prepare an arm.

Never calls Max, fileIn, an installer, or git. Never executes the arm. Each
attempt directory is exclusive; refused/drifted attempts are retained unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import traceback

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
FIXTURE = ROOT / "Audit/phase16-p3-f01-input-2026-11-02e"
PROJECT = FIXTURE / "project"
AUTHORITY = FIXTURE / "direction-authority.json"
CONTRACT = ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"
PLAN_SOURCE = ROOT / "Audit/AGENT_PLAN_poly_surface_shell.md"
WRAPPER_SOURCE = ROOT / "Audit/phase16-p3-execution-2026-11-02e/pair_filein.py"
NAMESPACE = "P3E_F01"
UNITS = {"system_type": "millimeters", "system_scale": 1.0,
         "cm_per_unit": 0.1, "units_per_cm": 10.0}
PINNED = {
    PROJECT / "walls.json": "bbd433c76b83a709845c9a20941414bbadc786dbe6ceac907f9259d9876bfa9f",
    PROJECT / "dimensions.json": "985bd129c01537c5bb5b0632054fe7f24e53237db0a2a4b9bbc01b544e8dfa26",
    PROJECT / "assumptions.json": "54c0a86e852c3e3a6cbf3ed0beb6dbad420bda67fa7063d250540a1cb28ffcb1",
    PROJECT / "conflicts_resolved.json": "18627ae616e75aa630eba4647aa414d1a888d6fa72dbf921e7c22c9f260cb836",
    AUTHORITY: "af3686f8105896cddadcee2ad659badab4e250377ca86853dc9a665bb0a201cb",
    PLAN_SOURCE: "37813bb8f6b8d2e445c69a0424d78997f80a3752303ccffebee802e1d84ee672",
    ROOT / "scripts/validate_specs.py": "616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def decode(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate operational JSON key: " + key)
            result[key] = value
        return result
    def invalid(token):
        raise ValueError("non-finite JSON token: " + token)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
    require(isinstance(value, dict), "operational JSON must be an object")
    return value


def regular(path: Path) -> None:
    for part in reversed((path, *path.parents)):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                "link/reparse path refused: " + str(part))
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "non-regular/hard-linked file: " + str(path))


def read(path: Path) -> bytes:
    regular(path)
    return path.read_bytes()


def files_under(directory: Path) -> list[Path]:
    found = []
    for parent, dirs, names in os.walk(directory, followlinks=False):
        for name in dirs:
            child = Path(parent) / name
            info = child.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "linked directory refused: " + str(child))
        found.extend(Path(parent) / name for name in names)
    return sorted(found)


def snapshot() -> tuple[dict, dict[Path, bytes]]:
    paths = set((ROOT / "scripts").glob("*.py")) | set(files_under(FIXTURE)) | set(PINNED)
    paths |= {CONTRACT, Path(__file__).resolve(), WRAPPER_SOURCE, ROOT / "references/07-spec-grammar.md",
              ROOT / "Audit/EVIDENCE_2026-10-27.md",
              ROOT / "Audit/_phase16-p3-f01-input-2026-11-02e.md"}
    raw = {p: read(p) for p in sorted(paths)}
    return {str(p): {"sha256": digest(b), "bytes": len(b)} for p, b in raw.items()}, raw


def write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)
    require(read(path) == raw, "new-file readback mismatch: " + str(path))


def save(path: Path, value: object) -> None:
    write_new(path, canonical(value))


def normalized(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def checked_mapping(mapping: object, before: dict) -> dict[str, str]:
    require(isinstance(mapping, dict) and bool(mapping), "missing identity hash map")
    locked = {normalized(p): row["sha256"] for p, row in before.items()}
    result = {}
    for token, value in mapping.items():
        require(isinstance(token, str) and Path(token).is_absolute(), "hash path is not absolute")
        path = normalized(token)
        require(path not in result and locked.get(path) == value, "unlocked/drifted identity source: " + token)
        result[path] = value
    return result


def stable(before: dict) -> dict:
    after, _ = snapshot()
    require(after == before, "SOURCE/INPUT/CONTRACT DRIFT: retain attempt; use a NEW run-id after review")
    return after


def run(args, attempt: Path) -> None:
    before, raw = snapshot()
    save(attempt / "protected-before.json", before)
    for path, expected in PINNED.items():
        require(digest(raw[path]) == expected, "accepted F01/P2 pin mismatch: " + str(path))
    authority = decode(raw[AUTHORITY])
    require(authority["source_file"] == "Audit/AGENT_PLAN_poly_surface_shell.md" and
            authority["source_sha256"] == digest(raw[PLAN_SOURCE]), "actual analytical source authority mismatch")
    nonce_hash = digest(args.nonce.encode("ascii"))
    for request in BASE.glob("*/request.json"):
        require(decode(read(request)).get("nonce_sha256") != nonce_hash, "nonce already used in an owned attempt")
    out = attempt / "published"
    require(not os.path.lexists(out), "output must never have existed")
    command = [sys.executable, "-B", str(ROOT / "scripts/build_wall_surface.py"),
               "--in", str(PROJECT), "--out", str(out), "--namespace", NAMESPACE,
               "--system-type", "millimeters", "--system-scale", "1",
               "--direction-authority", str(AUTHORITY)]
    save(attempt / "request.json", {"authors_stopped": "operator_assertion_not_automatically_proven",
         "cwd": str(ROOT), "argv": command, "nonce_sha256": nonce_hash,
         "arm_execution": "PROHIBITED_BY_THIS_RUNNER", "scene_access": "NONE"})
    stable(before)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=300, check=False)
    write_new(attempt / "cli-stdout.txt", result.stdout)
    write_new(attempt / "cli-stderr.txt", result.stderr)
    save(attempt / "cli-exit.json", {"exit_code": result.returncode})
    stable(before)
    require(result.returncode == 0, "actual CLI refused; see retained stdout/stderr")
    require(not result.stderr, "unexpected CLI stderr; retain pair for inspection")
    pair = {name: read(out / name) for name in ("wall_surface.json", "wall_surface.ms")}
    require({p.name for p in out.iterdir()} == set(pair), "published directory is not the exact artifact pair")
    hashes = {name: digest(b) for name, b in pair.items()}
    prefix = b"produced_offline_unverified: "
    require(result.stdout.startswith(prefix) and decode(result.stdout[len(prefix):]) == hashes,
            "CLI publication hashes differ from actual pair bytes")
    manifest = decode(pair["wall_surface.json"])
    require(manifest["schema_version"] == "p3-wall-surface-1" and manifest["spec"] == "wall_surface"
            and manifest["status"] == "produced_offline_unverified", "unrecognized produced manifest")
    identity = manifest["identity"]
    require(isinstance(identity, str) and re.fullmatch(r"[0-9a-f]{64}", identity) is not None,
            "invalid canonical artifact identity")
    require(manifest["project"] == "phase16-p3-f01" and manifest["route"] == "poly_surface_shell_v1"
            and manifest["subset"] == "single_standalone_straight_inner_wall", "wrong authentic F01 scope")
    require(manifest["owner"] == {"namespace": NAMESPACE, "id": identity}
            and manifest["expected_units"] == UNITS and manifest["node_names"] == [NAMESPACE + "__wall"],
            "namespace/unit/owner metadata mismatch")
    require(manifest["script"] == {"file": "wall_surface.ms", "sha256": hashes["wall_surface.ms"]}
            and manifest["direction_authority"] == authority, "script or authority identity mismatch")
    actual_inputs = checked_mapping(manifest["input_hashes"], before)
    require(set(actual_inputs) == {normalized(p) for p in (*PROJECT.glob("*.json"), AUTHORITY, PLAN_SOURCE)},
            "consumed authentic input closure mismatch")
    generators = checked_mapping(manifest["generator_hashes"], before)
    require({normalized(ROOT / "scripts" / name) for name in (
        "build_wall_surface.py", "wall_surface_inputs.py", "wall_surface_runtime.py",
        "wall_surface_publish.py", "validate_specs.py", "scene_units.py")} | {normalized(CONTRACT)} <= set(generators),
        "manifest does not lock the actual coordinator/runtime/contract closure")
    record = {"schema_version": "p3-wall-surface-identity-1", "project": manifest["project"],
              "route": manifest["route"], "subset": manifest["subset"], "namespace": NAMESPACE,
              "input_hashes": manifest["input_hashes"], "generator_hashes": manifest["generator_hashes"],
              "direction_authority": authority, "expected_units": manifest["expected_units"],
              "authority_source_resolution": {"base": "process_current_working_directory",
                  "raw_token": authority["source_file"], "resolved_path": str(PLAN_SOURCE)}}
    require(digest(canonical(record)) == identity, "canonical manifest identity does not recompute")
    # Imports occur only AFTER the actual CLI and stable-source checks. No Max API.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "scripts"))
    runtime = importlib.import_module("wall_surface_runtime")
    require(normalized(runtime.__file__) == normalized(ROOT / "scripts/wall_surface_runtime.py"), "runtime import substitution")
    stable(before)
    plan = runtime.build_plan(decode(raw[PROJECT / "walls.json"]), decode(raw[PROJECT / "dimensions.json"]))
    require(manifest["predictions"]["values"] == plan["predictions"], "published/runtime plan predictions differ")
    generated = runtime.generate_script(plan, identity, NAMESPACE, manifest["expected_units"])
    require(generated.encode("utf-8") == pair["wall_surface.ms"], "runtime plan does not reproduce exact published script")
    arm = runtime.generate_arm_script(plan, identity, NAMESPACE, manifest["expected_units"], nonce=args.nonce)
    require(isinstance(arm, str) and identity in arm and args.nonce in arm, "arm does not bind exact identity/nonce")
    registry_matches = re.findall(r'^    local registryKey = "(__P3W_[0-9a-f]{64})" as name$', generated, re.MULTILINE)
    require(len(registry_matches) == 1, "actual generated registry binding unavailable/ambiguous")
    registry_key = registry_matches[0]
    require('local registryKey = "' + registry_key + '" as name' in arm,
            "arm/wall registry binding differs")
    # Reuse the actual offline wrapper's rendering/read-hash API, but publish
    # its text here via this owner's exclusive writer. Never call its CLI writer
    # (which correctly confines writes to the other owner's directory).
    module_spec = importlib.util.spec_from_file_location("p3_main_pair_filein", WRAPPER_SOURCE)
    require(module_spec is not None and module_spec.loader is not None, "wrapper import unavailable")
    pair_wrapper = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(pair_wrapper)
    pair_wrapper.inspect_pair(out / "wall_surface.json", out / "wall_surface.ms",
                              hashes["wall_surface.json"], hashes["wall_surface.ms"])
    wrapper = pair_wrapper.render_wrapper(out / "wall_surface.json", out / "wall_surface.ms",
                                         hashes["wall_surface.json"], hashes["wall_surface.ms"])
    stable(before)
    save(attempt / "operational-plan.json", plan)
    write_new(attempt / "main_only_arm.ms", arm.encode("utf-8"))
    write_new(attempt / "held_pair_filein.ms", wrapper.encode("utf-8"))
    save(attempt / "arm-record.json", {"status": "MAIN_ONLY_GENERATED_NOT_EXECUTED",
         "not_produced_geometry_artifact": True, "identity": identity, "namespace": NAMESPACE,
         "registry_key": registry_key,
         "expected_units": manifest["expected_units"], "nonce_sha256": nonce_hash,
         "runtime_sha256": before[str(ROOT / "scripts/wall_surface_runtime.py")]["sha256"],
         "manifest_sha256": hashes["wall_surface.json"], "script_sha256": hashes["wall_surface.ms"],
         "plan_sha256": digest(read(attempt / "operational-plan.json")),
         "arm_sha256": digest(read(attempt / "main_only_arm.ms")),
         "held_wrapper_sha256": digest(read(attempt / "held_pair_filein.ms")),
         "wrapper_source_sha256": before[str(WRAPPER_SOURCE)]["sha256"],
         "main_must_retain_exact_lease_witness": True, "live_execution": "NOT_RUN"})
    for name, original in pair.items():
        require(read(out / name) == original, "published pair changed during arm generation")
    save(attempt / "protected-after.json", stable(before))
    save(attempt / "completion.json", {"status": "PREPARED_OFFLINE_UNVERIFIED_NOT_ARMED_NOT_EXECUTED",
         "identity": identity, "namespace": NAMESPACE, "expected_units": manifest["expected_units"],
         "registry_key": registry_key,
         "artifact_pair_sha256": hashes,
         "all_prior_attempt_file_sha256": {p.relative_to(attempt).as_posix(): digest(read(p)) for p in files_under(attempt)},
         "next_action": "Main independently reviews exact bytes/hashes and fresh scene; runner never executes arm/wall."})
    print(json.dumps({"attempt": str(attempt), "completion_sha256": digest(read(attempt / "completion.json")),
                      "artifact_pair_sha256": hashes, "status": "OFFLINE_ONLY_NOT_EXECUTED"}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--authors-stopped", action="store_true", required=True,
                        help="Main's explicit confirmation; never inferred/polled by this runner")
    parser.add_argument("--run-id", required=True, help="New ASCII attempt name; existing paths refuse")
    parser.add_argument("--nonce", required=True, help="Main's fresh 16..128 ASCII alphanumeric/underscore token")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}", args.run_id) or not re.fullmatch(r"[A-Za-z0-9_]{16,128}", args.nonce):
        parser.error("invalid run-id or fresh nonce spelling")
    attempt = BASE / args.run_id
    try:
        attempt.mkdir()  # Exclusive: no exist_ok, no deletion, no resume/overwrite.
    except OSError as exc:
        print("REFUSED before publication: " + str(exc), file=sys.stderr)
        return 1
    try:
        run(args, attempt)
        return 0
    except Exception as exc:
        diagnostic = {"status": "REFUSED_RETAIN_ALL_FILES_NEW_RUN_ID_REQUIRED",
                      "error": str(exc), "traceback": traceback.format_exc(),
                      "arm_execution": "NOT_RUN", "scene_access": "NONE"}
        try:
            after, _ = snapshot()
            diagnostic["protected_hashes_at_refusal"] = after
            diagnostic["retained_file_sha256"] = {p.relative_to(attempt).as_posix(): digest(read(p)) for p in files_under(attempt)}
        except Exception as read_exc:
            diagnostic["diagnostic_read_failure"] = str(read_exc)
        try:
            save(attempt / "refusal.json", diagnostic)
        except Exception as save_exc:
            print("Diagnostic write failed: " + str(save_exc), file=sys.stderr)
        print("REFUSED; retained attempt " + str(attempt) + ": " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
