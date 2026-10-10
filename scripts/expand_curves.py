"""scripts/expand_curves.py - Curve expansion, verification, and station recommendation CLI.

Implements microtasks 05.3 & 05.4 for Form-precision Stage 05:
- Expansion mode (--out FILE): Discretize draft sections with generators, validate against
  dimensions.json form_references, update origins, and perform safe atomic write (A-WRITE/M34).
- Verification mode (--check): Recompute points, verify <= 0.001 cm deviation, and ensure
  parameters match dimensions.json form_references.
- Suggestion mode (--suggest-count): Recommend station count satisfying tol-cm tolerance.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    from scripts import curve_gen
except ImportError:
    import curve_gen


class ArgumentParserExit2(argparse.ArgumentParser):
    """ArgumentParser subclass ensuring exit code 2 on CLI usage errors."""

    def error(self, message: str) -> None:
        sys.stderr.write(f"Usage error: {message}\n")
        sys.exit(2)


def resolve_dimensions_path(project_dir: Path | str) -> Path | None:
    """Resolve dimensions.json in project_dir (under specs/pipeline/ or directly)."""
    p = Path(project_dir)
    c1 = p / "specs" / "pipeline" / "dimensions.json"
    if c1.is_file():
        return c1
    c2 = p / "dimensions.json"
    if c2.is_file():
        return c2
    return None


def read_draft(path: Path | str) -> dict[str, Any]:
    """Read and parse a JSON spec into memory."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    doc = json.loads(content)
    if not isinstance(doc, dict):
        raise ValueError(f"expected JSON object at root of {path}, got {type(doc).__name__}")
    return doc


def match_generator_with_reference(
    section: dict[str, Any],
    gen: dict[str, Any],
    form_refs: list[dict[str, Any]],
) -> tuple[bool, str, int | None, dict[str, Any] | None]:
    """Validate that generator matches referenced analytical geometry in dimensions.json:form_references[].

    Returns (True, "", ref_index, ref_obj) or (False, reason, None, None).
    """
    ref_id = section.get("form_reference_ref") or section.get("reference_ref")
    ref_idx: int | None = None
    ref_obj: dict[str, Any] | None = None

    if ref_id is not None:
        for i, r in enumerate(form_refs):
            if isinstance(r, dict) and r.get("id") == ref_id:
                ref_idx = i
                ref_obj = r
                break
        if ref_obj is None:
            return False, f"reference {ref_id!r} not found in dimensions.json form_references[]", None, None
    else:
        candidates: list[tuple[int, dict[str, Any]]] = []
        for i, r in enumerate(form_refs):
            if (
                isinstance(r, dict)
                and r.get("kind") == gen.get("kind")
                and r.get("plane") == gen.get("plane")
            ):
                candidates.append((i, r))
        if len(candidates) == 1:
            ref_idx, ref_obj = candidates[0]
        elif len(candidates) == 0:
            return (
                False,
                "section has no form_reference_ref and no matching form_reference found in dimensions.json",
                None,
                None,
            )
        else:
            return (
                False,
                f"section has no form_reference_ref and multiple candidates ({len(candidates)}) match in dimensions.json",
                None,
                None,
            )

    ref_kind = ref_obj.get("kind")
    gen_kind = gen.get("kind")

    if ref_kind == "semi_elliptical_barrel":
        if gen_kind != "ellipse_arc":
            return False, f"kind mismatch: generator {gen_kind!r} must be 'ellipse_arc' for barrel reference", None, None
        if gen.get("plane") != "XZ" or ref_obj.get("plane") != "XZ":
            return False, f"plane mismatch: barrel profile plane must be 'XZ', got generator {gen.get('plane')!r} and reference {ref_obj.get('plane')!r}", None, None

        gc = gen.get("center_cm")
        rc = ref_obj.get("center_cm")
        if not (isinstance(gc, list) and isinstance(rc, list) and len(gc) == 3 and len(rc) == 3):
            return False, f"center_cm must be 3-element lists, got {gc!r} and {rc!r}", None, None

        if abs(curve_gen.q6(gc[0]) - curve_gen.q6(rc[0])) > 1e-6 or abs(curve_gen.q6(gc[2]) - curve_gen.q6(rc[2])) > 1e-6:
            return False, f"barrel center_cm[0,2] mismatch: generator ({gc[0]}, {gc[2]}) != reference ({rc[0]}, {rc[2]})", None, None

        st = section.get("station_cm")
        if st is not None:
            if abs(curve_gen.q6(gc[1]) - curve_gen.q6(st)) > 1e-6:
                return False, f"generator center_cm[1] ({gc[1]}) must match station_cm ({st})", None, None
            long_range = ref_obj.get("longitudinal_range_cm")
            if isinstance(long_range, list) and len(long_range) == 2:
                s0, s1 = sorted([float(long_range[0]), float(long_range[1])])
                if not (s0 - 1e-6 <= float(st) <= s1 + 1e-6):
                    return False, f"station_cm {st} outside barrel longitudinal range [{s0}, {s1}]", None, None

        ga = gen.get("semi_axes_cm")
        ra = ref_obj.get("semi_axes_cm")
        if not (isinstance(ga, list) and isinstance(ra, list) and len(ga) == 2 and len(ra) == 2):
            return False, f"semi_axes_cm must be 2-element lists, got {ga!r} and {ra!r}", None, None
        if any(abs(curve_gen.q6(a) - curve_gen.q6(b)) > 1e-6 for a, b in zip(ga, ra)):
            return False, f"semi_axes_cm mismatch: generator {ga} != reference {ra}", None, None

        if abs(gen.get("from_deg", 0.0) - ref_obj.get("from_deg", 0.0)) > 1e-6:
            return False, f"from_deg mismatch: generator {gen.get('from_deg')} != reference {ref_obj.get('from_deg')}", None, None
        if abs(gen.get("to_deg", 0.0) - ref_obj.get("to_deg", 0.0)) > 1e-6:
            return False, f"to_deg mismatch: generator {gen.get('to_deg')} != reference {ref_obj.get('to_deg')}", None, None

        return True, "", ref_idx, ref_obj

    if gen_kind != ref_kind:
        return False, f"kind mismatch: generator {gen_kind!r} != reference {ref_kind!r}", None, None

    if gen.get("plane") != ref_obj.get("plane"):
        return False, f"plane mismatch: generator {gen.get('plane')!r} != reference {ref_obj.get('plane')!r}", None, None

    gc = gen.get("center_cm")
    rc = ref_obj.get("center_cm")
    if not (isinstance(gc, list) and isinstance(rc, list) and len(gc) == 3 and len(rc) == 3):
        return False, f"center_cm must be 3-element lists, got {gc!r} and {rc!r}", None, None

    if any(abs(curve_gen.q6(a) - curve_gen.q6(b)) > 1e-6 for a, b in zip(gc, rc)):
        return False, f"center_cm mismatch: generator {gc} != reference {rc}", None, None

    if abs(gen.get("from_deg", 0.0) - ref_obj.get("from_deg", 0.0)) > 1e-6:
        return False, f"from_deg mismatch: generator {gen.get('from_deg')} != reference {ref_obj.get('from_deg')}", None, None

    if abs(gen.get("to_deg", 0.0) - ref_obj.get("to_deg", 0.0)) > 1e-6:
        return False, f"to_deg mismatch: generator {gen.get('to_deg')} != reference {ref_obj.get('to_deg')}", None, None

    if gen.get("count") != ref_obj.get("construction_count"):
        return (
            False,
            f"count mismatch: generator count {gen.get('count')} != reference construction_count {ref_obj.get('construction_count')}",
            None,
            None,
        )

    if gen_kind == "arc":
        if abs(gen.get("radius_cm", 0.0) - ref_obj.get("radius_cm", 0.0)) > 1e-6:
            return False, f"radius_cm mismatch: generator {gen.get('radius_cm')} != reference {ref_obj.get('radius_cm')}", None, None
    elif gen_kind == "ellipse_arc":
        ga = gen.get("semi_axes_cm")
        ra = ref_obj.get("semi_axes_cm")
        if not (isinstance(ga, list) and isinstance(ra, list) and len(ga) == 2 and len(ra) == 2):
            return False, f"semi_axes_cm must be 2-element lists, got {ga!r} and {ra!r}", None, None
        if any(abs(curve_gen.q6(a) - curve_gen.q6(b)) > 1e-6 for a, b in zip(ga, ra)):
            return False, f"semi_axes_cm mismatch: generator {ga} != reference {ra}", None, None

    if "station_cm" in section and section["station_cm"] is not None:
        st = section["station_cm"]
        plane = gen.get("plane")
        ortho_idx = 2 if plane == "XY" else (1 if plane == "XZ" else 0)
        if abs(curve_gen.q6(st) - curve_gen.q6(rc[ortho_idx])) > 1e-6:
            return False, f"station_cm {st} does not equal reference center_cm[{ortho_idx}] ({rc[ortho_idx]})", None, None

    return True, "", ref_idx, ref_obj


def expand(
    project_dir: Path | str,
    in_path: Path | str,
    out_path: Path | str,
) -> tuple[int, dict[str, Any]]:
    """Expansion mode: expand draft sections with generator, validating against form_references."""
    dim_file = resolve_dimensions_path(project_dir)
    if dim_file is None:
        return 1, {"error": f"missing dimensions.json dependency in project dir {project_dir}"}

    try:
        dim_doc = read_draft(dim_file)
    except Exception as exc:
        return 1, {"error": f"failed to read dimensions.json: {exc}"}

    form_refs = dim_doc.get("form_references", [])
    if not isinstance(form_refs, list):
        return 1, {"error": "form_references in dimensions.json must be a list"}

    try:
        doc = read_draft(in_path)
    except Exception as exc:
        return 1, {"error": f"failed to read input file {in_path}: {exc}"}

    sections = doc.get("sections")
    if not isinstance(sections, list):
        return 1, {"error": "sections in input JSON must be a list"}

    has_origins = "origins" in doc and isinstance(doc.get("origins"), dict)
    expanded_ids: list[str] = []
    point_counts: dict[str, int] = {}

    for idx, s in enumerate(sections):
        if not isinstance(s, dict) or "generator" not in s:
            continue
        sec_id = s.get("id", f"SEC-{idx:03d}")
        gen = s["generator"]

        ok, reason = curve_gen.validate_generator(gen)
        if not ok:
            return 1, {"error": f"section {sec_id} generator is invalid: {reason}"}

        match_ok, match_reason, ref_idx, _ = match_generator_with_reference(s, gen, form_refs)
        if not match_ok:
            return 1, {"error": f"section {sec_id} generator does not match reference: {match_reason}"}

        try:
            pts = curve_gen.generator_points(gen)
        except Exception as exc:
            return 1, {"error": f"section {sec_id} generator failed point generation: {exc}"}

        s["points_cm"] = pts
        expanded_ids.append(sec_id)
        point_counts[sec_id] = len(pts)

        if has_origins:
            doc["origins"][f"sections[{idx}].points_cm"] = {
                "origin": "derived",
                "derives_from": [
                    f"dimensions.json:form_references[{ref_idx}]",
                    f"sections[{idx}].generator",
                ],
            }

    new_content = json.dumps(doc, indent=2) + "\n"
    new_content = new_content.replace("\r\n", "\n")
    new_bytes = new_content.encode("utf-8")

    out_p = Path(out_path).resolve()
    in_p = Path(in_path).resolve()

    is_same = (out_p == in_p)
    if not is_same and out_p.exists() and in_p.exists():
        try:
            is_same = os.path.samefile(out_p, in_p)
        except OSError:
            pass

    if out_p.exists() and not is_same:
        existing_bytes = out_p.read_bytes()
        if existing_bytes != new_bytes:
            return 1, {"error": f"differing existing output at {out_p}"}
        return 0, {
            "status": "OK",
            "mode": "expand",
            "in": str(in_path),
            "out": str(out_path),
            "expanded_sections": expanded_ids,
            "point_counts": point_counts,
            "note": "existing output was already identical",
        }

    out_p.parent.mkdir(parents=True, exist_ok=True)
    tmp_p = out_p.parent / f"{out_p.name}.tmp.{os.getpid()}"
    try:
        with open(tmp_p, "wb") as f:
            f.write(new_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_p, out_p)
    finally:
        if tmp_p.exists():
            try:
                tmp_p.unlink()
            except OSError:
                pass

    return 0, {
        "status": "OK",
        "mode": "expand",
        "in": str(in_path),
        "out": str(out_path),
        "expanded_sections": expanded_ids,
        "point_counts": point_counts,
    }


def check(
    project_dir: Path | str,
    in_path: Path | str,
) -> tuple[int, dict[str, Any]]:
    """Verification mode: check stored points_cm against recomputed generator_points and form_references."""
    dim_file = resolve_dimensions_path(project_dir)
    if dim_file is None:
        return 1, {"error": f"missing dimensions.json dependency in project dir {project_dir}"}

    try:
        dim_doc = read_draft(dim_file)
    except Exception as exc:
        return 1, {"error": f"failed to read dimensions.json: {exc}"}

    form_refs = dim_doc.get("form_references", [])
    if not isinstance(form_refs, list):
        return 1, {"error": "form_references in dimensions.json must be a list"}

    try:
        doc = read_draft(in_path)
    except Exception as exc:
        return 1, {"error": f"failed to read input file {in_path}: {exc}"}

    sections = doc.get("sections")
    if not isinstance(sections, list):
        return 1, {"error": "sections in input JSON must be a list"}

    checked_ids: list[str] = []
    max_dev = 0.0

    for idx, s in enumerate(sections):
        if not isinstance(s, dict) or "generator" not in s:
            continue
        sec_id = s.get("id", f"SEC-{idx:03d}")
        gen = s["generator"]

        ok, reason = curve_gen.validate_generator(gen)
        if not ok:
            return 1, {"error": f"section {sec_id} generator is invalid: {reason}"}

        match_ok, match_reason, _, _ = match_generator_with_reference(s, gen, form_refs)
        if not match_ok:
            return 1, {"error": f"section {sec_id} generator does not match reference: {match_reason}"}

        try:
            recomputed = curve_gen.generator_points(gen)
        except Exception as exc:
            return 1, {"error": f"section {sec_id} generator failed point generation: {exc}"}

        stored = s.get("points_cm")
        if not isinstance(stored, list):
            return 1, {"error": f"section {sec_id} has generator but points_cm is missing or not a list"}

        if len(stored) != len(recomputed):
            return (
                1,
                {
                    "error": f"section {sec_id} point count mismatch: stored {len(stored)} != recomputed {len(recomputed)}"
                },
            )

        for p_idx, (p_s, p_r) in enumerate(zip(stored, recomputed)):
            if not (isinstance(p_s, list) and len(p_s) == 3):
                return 1, {"error": f"section {sec_id} point {p_idx} is not a 3-element list"}
            for cs, cr in zip(p_s, p_r):
                dev = abs(cs - cr)
                if dev > max_dev:
                    max_dev = dev
                if dev > 0.001:
                    return (
                        1,
                        {
                            "error": f"section {sec_id} point {p_idx} coordinate deviation {dev:.6f} cm exceeds tolerance 0.001 cm"
                        },
                    )

        checked_ids.append(sec_id)

    return 0, {
        "status": "OK",
        "mode": "check",
        "in": str(in_path),
        "checked_sections": checked_ids,
        "section_count": len(checked_ids),
        "max_deviation_cm": max_dev,
    }


def suggest(
    in_path: Path | str,
    section_id: str,
    tol_cm: float,
) -> tuple[int, dict[str, Any]]:
    """Suggestion mode: recommend station count satisfying tolerance tol_cm."""
    try:
        doc = read_draft(in_path)
    except Exception as exc:
        return 1, {"error": f"failed to read input file {in_path}: {exc}"}

    sections = doc.get("sections")
    if not isinstance(sections, list):
        return 1, {"error": "sections in input JSON must be a list"}

    sec = next((s for s in sections if isinstance(s, dict) and s.get("id") == section_id), None)
    if sec is None:
        return 1, {"error": f"section with id {section_id!r} not found"}

    gen = sec.get("generator")
    if not isinstance(gen, dict):
        return 1, {"error": f"section {section_id!r} does not have a generator"}

    try:
        res = curve_gen.suggest_count(gen, tol_cm)
    except Exception as exc:
        return 1, {"error": str(exc)}

    if res.get("exhausted"):
        return 1, {
            "status": "exhausted",
            "section_id": section_id,
            "tol_cm": tol_cm,
            "error": res.get("error") or f"chord bound budget exhausted for tolerance {tol_cm} cm",
            **res,
        }

    return 0, {
        "status": "suggested",
        "section_id": section_id,
        "count": res["count"],
        "method": res["method"],
        "chord_bound_cm": res["chord_bound_cm"],
        "tol_cm": tol_cm,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParserExit2(
        description="Expand draft curves, verify recomputed points, or suggest station counts."
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        type=Path,
        help="Path to project directory containing dimensions.json.",
    )
    parser.add_argument(
        "--in",
        dest="in_file",
        required=True,
        type=Path,
        help="Path to input draft JSON spec.",
    )
    parser.add_argument(
        "--out",
        dest="out_file",
        default=None,
        type=Path,
        help="Expansion mode: path to output expanded JSON spec.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verification mode: recompute points and check deviation <= 0.001 cm.",
    )
    parser.add_argument(
        "--suggest-count",
        action="store_true",
        help="Suggestion mode: recommend station count within tolerance.",
    )
    parser.add_argument(
        "--section-id",
        default=None,
        type=str,
        help="Section ID for --suggest-count mode.",
    )
    parser.add_argument(
        "--tol-cm",
        default=None,
        type=str,
        help="Tolerance in cm for --suggest-count mode.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output result as formatted JSON to stdout.",
    )

    args = parser.parse_args(argv)

    mode_count = sum([args.out_file is not None, bool(args.check), bool(args.suggest_count)])
    if mode_count != 1:
        parser.error("strictly one of --out, --check, or --suggest-count must be provided.")

    if not args.project_dir.exists() or not args.project_dir.is_dir():
        parser.error(f"--project-dir {str(args.project_dir)!r} does not exist or is not a directory.")

    if not args.in_file.exists() or not args.in_file.is_file():
        parser.error(f"--in {str(args.in_file)!r} does not exist or is not a file.")

    if args.suggest_count:
        if args.section_id is None:
            parser.error("--suggest-count requires --section-id.")
        if args.tol_cm is None:
            parser.error("--suggest-count requires --tol-cm.")
        try:
            tol_val = float(args.tol_cm)
            if not math.isfinite(tol_val) or tol_val <= 0:
                raise ValueError
        except (ValueError, TypeError):
            parser.error(f"--tol-cm must be a finite float > 0, got {args.tol_cm!r}.")
    else:
        if args.section_id is not None or args.tol_cm is not None:
            parser.error("--section-id and --tol-cm are only permitted with --suggest-count.")

    if args.out_file is not None:
        code, payload = expand(args.project_dir, args.in_file, args.out_file)
        if code == 0:
            if args.as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(f"OK: expanded {len(payload.get('expanded_sections', []))} section(s) to {args.out_file}")
            return 0
        else:
            err_msg = payload.get("error", "expansion failed")
            if args.as_json:
                print(json.dumps({"status": "error", "error": err_msg}, indent=2))
            print(f"Error: {err_msg}", file=sys.stderr)
            return 1

    elif args.check:
        code, payload = check(args.project_dir, args.in_file)
        if code == 0:
            if args.as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(
                    f"OK: verified {payload.get('section_count', 0)} section(s) "
                    f"(max coordinate deviation: {payload.get('max_deviation_cm', 0.0):.6f} cm)"
                )
            return 0
        else:
            err_msg = payload.get("error", "check failed")
            if args.as_json:
                print(json.dumps({"status": "error", "error": err_msg}, indent=2))
            print(f"Error: {err_msg}", file=sys.stderr)
            return 1

    elif args.suggest_count:
        code, payload = suggest(args.in_file, args.section_id, float(args.tol_cm))
        if code == 0:
            if args.as_json:
                print(json.dumps(payload, indent=2))
            else:
                print(
                    f"Suggested count for {args.section_id}: count={payload['count']}, "
                    f"method={payload['method']}, chord_bound_cm={payload['chord_bound_cm']:.6f} "
                    f"(tol_cm={payload['tol_cm']})"
                )
            return 0
        else:
            err_msg = payload.get("error", "suggestion failed")
            if args.as_json:
                print(json.dumps(payload, indent=2))
            print(f"Refusal notice: {err_msg}", file=sys.stderr)
            return 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
