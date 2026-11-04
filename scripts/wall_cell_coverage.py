"""Independent, offline spatial coverage check for legacy wall-cell assemblies.

Call ``check_wall_cell_coverage(assembly, massing, dimensions)`` with the three
decoded JSON objects.  The returned ``CoverageResult`` has a ``status`` of
``PASS``, ``REVIEW``, ``FAIL`` or ``NOT_APPLICABLE``, plus structured findings.
This is *additional* to the existing G-82 volume-budget check, not a replacement.
All three inputs must explicitly declare ``units.length == 'cm'``. A present
assembly wall-technique selector must be ``legacy_cells_v1``.

The supported domain is axis-aligned rectangular facade-wall prisms, rectangular
clean-through cuts, and axis-aligned box cells.  Facade start/end coordinates,
including their sign, and level elevations locate cuts; names and ``volume_cm3``
are not geometric evidence.  Each host referenced by a cut is checked, including
when no cells exist.  The dimensions opening-to-cut join is also checked so that
removing both a host's cuts and its cells cannot hide declared openings.  This is
not a full schema validator, a wall-envelope census, a live-scene check, or a
poly-surface-shell check.  Other gates must still validate the rest of the model.
Opening prisms are also checked against one another: positive-volume intersection
is reported independently even when the cells correctly exclude their union.

Tolerance policy, deliberately *not* the G-82 volume budget: decimal inputs are
represented as exact rationals; no boundaries are snapped and every nonzero
spatial discrepancy is reported.  A connected discrepancy whose bounding box's
smallest span is <= dimensions.tolerances.linear_cm is REVIEW, not PASS: it may
be an endpoint/rounding discrepancy or an extensive thin defect.  Its bounds and
actual volume are always included.  A discrepancy with all three bounding spans
> linear_cm is FAIL.  The same REVIEW/FAIL distinction is used for nonzero
endpoint disagreements.  REVIEW is inconclusive, and must never be converted to
PASS or silently discarded by a caller.  In particular, linear_cm is *not* an
allowed gap width; no claim is made that a REVIEW is physically acceptable.
There is no hidden numerical epsilon or change to the existing volume gate.
Exactness applies to the already-decoded values: a Python float cannot preserve
decimal digits already lost when parsing JSON. Detect or reject such loss at the
input parsing boundary; this oracle cannot reconstruct the original JSON token.
If a diagnostic rational is too large for Python's decimal integer-to-string
limit, it is emitted exactly as ``exact_hex:<numerator>/<denominator>`` using
signed Python-style hexadecimal integers. This changes diagnostics only, not
the rational comparison or classification of any discrepancy.
Unsupported/ambiguous or missing geometry fails closed.  A resource limit also
fails closed, rather than sampling or reporting a partial check as a pass.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any


@dataclass(frozen=True)
class CoverageResult:
    """Result independent of the validator's Report implementation."""

    status: str
    findings: list[dict[str, Any]]
    checked_hosts: tuple[str, ...]
    linear_tolerance_cm: float | str | None

    @property
    def ok(self) -> bool:
        """Only an actual complete spatial pass is true; REVIEW is not a pass."""
        return self.status == "PASS"


class _InputError(ValueError):
    pass


def _num(value: Any, where: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _InputError(f"{where} must be a finite JSON number")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise _InputError(f"{where} must be a finite JSON number")
    return Fraction(str(value))


def _output(value: Fraction) -> float | str:
    """JSON-friendly diagnostics, without emitting Infinity on extreme inputs."""
    try:
        number = float(value)
    except OverflowError:
        pass
    else:
        if math.isfinite(number) and (number != 0 or value == 0):
            return number
    try:
        return str(value)
    except ValueError:
        # CPython limits decimal int->str conversion (typically 4300 digits),
        # but a volume can have up to three times as many digits as its input
        # coordinates. Hex has no such conversion limit and preserves the exact
        # rational rather than dropping the evidence or weakening the check.
        return f"exact_hex:{hex(value.numerator)}/{hex(value.denominator)}"


def _identifier(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _InputError(f"{where} must be a nonempty string")
    return value


def _index_text(value: int) -> str:
    """Format an integer index even above Python's decimal digit limit."""
    try:
        return str(value)
    except ValueError:
        return hex(value)


def _index(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _InputError(f"{where} must be an integer")
    return value


def _rows(document: Any, key: str, label: str) -> list[dict[str, Any]]:
    if not isinstance(document, dict) or not isinstance(document.get(key), list):
        raise _InputError(f"{label}.{key} must be an array")
    rows = document[key]
    if not all(isinstance(row, dict) for row in rows):
        raise _InputError(f"{label}.{key} must contain only objects")
    return rows


def _unique(rows: list[dict[str, Any]], key: str, label: str, *, integer: bool = False) -> dict:
    result: dict = {}
    for position, row in enumerate(rows):
        where = f"{label}[{position}].{key}"
        ident = _index(row.get(key), where) if integer else _identifier(row.get(key), where)
        if ident in result:
            shown = _index_text(ident) if integer else repr(ident)
            raise _InputError(f"{where}: duplicate {key} {shown}")
        result[ident] = row
    return result


def _pair(value: Any, where: str, *, ordered: bool = False) -> tuple[Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 2:
        raise _InputError(f"{where} must be an array of two numbers")
    a, b = (_num(value[i], f"{where}[{i}]") for i in range(2))
    if ordered and a >= b:
        raise _InputError(f"{where} must be strictly ascending")
    return a, b


def _host_box(host: dict[str, Any], host_id: str) -> tuple[Fraction, ...]:
    ring = host.get("profile_cm")
    if not isinstance(ring, list):
        raise _InputError(f"host {host_id}: profile_cm must be a rectangular ring")
    points = [_pair(point, f"host {host_id} profile_cm[{i}]") for i, point in enumerate(ring)]
    if len(points) == 5 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) != 4:
        raise _InputError(f"host {host_id}: only four-corner rectangular profiles are supported")
    xs, ys = {p[0] for p in points}, {p[1] for p in points}
    if len(xs) != 2 or len(ys) != 2 or set(points) != {(x, y) for x in xs for y in ys}:
        raise _InputError(f"host {host_id}: profile is not an axis-aligned rectangle")
    if any((p[0] == q[0]) == (p[1] == q[1]) for p, q in zip(points, points[1:] + points[:1])):
        raise _InputError(f"host {host_id}: profile has crossing or degenerate edges")
    z0, z1 = _pair(host.get("z_range_cm"), f"host {host_id} z_range_cm", ordered=True)
    return min(xs), min(ys), z0, max(xs), max(ys), z1


def _cell_box(cell: dict[str, Any], ident: str) -> tuple[Fraction, ...]:
    plan = cell.get("plan_rect_cm")
    if not isinstance(plan, list) or len(plan) != 4:
        raise _InputError(f"cell {ident}: plan_rect_cm must have four numbers")
    x0, y0, x1, y1 = (_num(v, f"cell {ident} plan_rect_cm") for v in plan)
    z0, z1 = _pair(cell.get("z_range_cm"), f"cell {ident} z_range_cm", ordered=True)
    if x0 >= x1 or y0 >= y1:
        raise _InputError(f"cell {ident}: plan rectangle must be strictly ascending")
    return x0, y0, z0, x1, y1, z1


def _check_host(
    host_id: str,
    host: dict[str, Any],
    cuts: list[dict[str, Any]],
    cells: list[dict[str, Any]],
    facades: dict[str, dict[str, Any]],
    levels: dict[int, dict[str, Any]],
    openings: dict[str, dict[str, Any]],
    linear: Fraction,
    findings: list[dict[str, Any]],
    max_atoms: int,
    max_work: int,
) -> None:
    def discrepancy(code: str, message: str, amount: Fraction, **detail: Any) -> None:
        findings.append({"code": code, "severity": "ERROR" if amount > linear else "REVIEW",
                         "host_ref": host_id, "message": message,
                         "difference_cm": _output(amount), **detail})

    box = _host_box(host, host_id)
    storey = _index(host.get("storey_index"), f"host {host_id} storey_index")
    if not cells:
        raise _InputError(f"host {host_id}: has {len(cuts)} cut(s) but no wall cells")
    cell_boxes = [(_cell_box(cell, cell["id"]), cell["id"]) for cell in cells]
    hole_boxes: list[tuple[tuple[Fraction, ...], str]] = []
    frame: tuple[str, int] | None = None
    for cut in cuts:
        cut_id = cut["id"]
        facade_id = _identifier(cut.get("facade"), f"cut {cut_id} facade")
        level_index = _index(cut.get("level_index"), f"cut {cut_id} level_index")
        level_text = _index_text(level_index)
        if frame is not None and frame != (facade_id, level_index):
            raise _InputError(f"host {host_id}: cuts use conflicting facade/level frames")
        frame = facade_id, level_index
        facade, level = facades.get(facade_id), levels.get(level_index)
        if facade is None or level is None:
            raise _InputError(f"cut {cut_id}: facade {facade_id!r} or level {level_text} is missing")
        if storey != level_index:
            raise _InputError(f"cut {cut_id}: level {level_text} differs from host storey {_index_text(storey)}")
        spans = facade.get("spans_level_indices")
        if spans is not None:
            if not isinstance(spans, list) or any(isinstance(i, bool) or not isinstance(i, int) for i in spans):
                raise _InputError(f"facade {facade_id}: spans_level_indices must be an integer array")
            if level_index not in spans:
                raise _InputError(f"cut {cut_id}: facade {facade_id} does not span level {level_text}")
        start = _pair(facade.get("start_corner_cm"), f"facade {facade_id} start_corner_cm")
        end = _pair(facade.get("end_corner_cm"), f"facade {facade_id} end_corner_cm")
        dx, dy = end[0] - start[0], end[1] - start[1]
        if (dx == 0) == (dy == 0):
            raise _InputError(f"facade {facade_id}: run must be nonzero and exactly X- or Y-aligned")
        axis = 0 if dx else 1
        cross = 1 - axis
        direction = 1 if end[axis] > start[axis] else -1
        for actual, expected, name in (
            (box[axis], min(start[axis], end[axis]), "run start"),
            (box[axis + 3], max(start[axis], end[axis]), "run end"),
        ):
            if actual != expected:
                discrepancy("host_facade_mismatch", f"host {host_id} {name} differs from facade {facade_id}", abs(actual - expected), cut_id=cut_id)
        face_offset = min(abs(start[cross] - box[cross]), abs(start[cross] - box[cross + 3]))
        if face_offset:
            discrepancy("host_facade_mismatch", f"facade {facade_id} is not on a host face", face_offset, cut_id=cut_id)
        elevation = _num(level.get("elevation_cm"), f"level {level_text} elevation_cm")
        height = _num(level.get("height_cm"), f"level {level_text} height_cm")
        if height <= 0:
            raise _InputError(f"level {level_text}: height_cm must be positive")
        for actual, expected, name in ((box[2], elevation, "base"), (box[5], elevation + height, "top")):
            if actual != expected:
                discrepancy("host_level_mismatch", f"host {host_id} {name} differs from level {level_text}", abs(actual - expected), cut_id=cut_id)
        if cut.get("kind") != "difference":
            raise _InputError(f"cut {cut_id}: kind must be 'difference'")
        u0, u1 = _pair(cut.get("u_range_cm"), f"cut {cut_id} u_range_cm", ordered=True)
        v0, v1 = _pair(cut.get("v_range_cm"), f"cut {cut_id} v_range_cm", ordered=True)
        opening_id = _identifier(cut.get("opening_id"), f"cut {cut_id} opening_id")
        opening = openings.get(opening_id)
        if opening is None:
            raise _InputError(f"cut {cut_id}: opening {opening_id!r} is missing")
        opening_level = _index(opening.get("level_index"), f"opening {opening_id} level_index")
        if opening.get("facade") != facade_id or opening_level != level_index:
            raise _InputError(f"cut {cut_id}: facade/level differs from opening {opening_id}")
        position = _num(opening.get("position_cm"), f"opening {opening_id} position_cm")
        width = _num(opening.get("width_cm"), f"opening {opening_id} width_cm")
        sill = _num(opening.get("sill_cm"), f"opening {opening_id} sill_cm")
        head = _num(opening.get("head_cm"), f"opening {opening_id} head_cm")
        if width <= 0 or sill >= head:
            raise _InputError(f"opening {opening_id}: invalid width or sill/head")
        for actual, expected, name in ((u0, position - width / 2, "u0"),
                                       (u1, position + width / 2, "u1"),
                                       (v0, sill, "v0"), (v1, head, "v1")):
            if actual != expected:
                discrepancy("cut_opening_mismatch", f"cut {cut_id} {name} differs from opening {opening_id}", abs(actual - expected), cut_id=cut_id, opening_id=opening_id)
        run0, run1 = sorted((start[axis] + direction * u0, start[axis] + direction * u1))
        z0, z1 = elevation + v0, elevation + v1
        for amount, name in ((box[axis] - run0, "run start"), (run1 - box[axis + 3], "run end"),
                             (box[2] - z0, "bottom"), (z1 - box[5], "top")):
            if amount > 0:
                discrepancy("cut_outside_host", f"cut {cut_id} {name} extends beyond host", amount, cut_id=cut_id)
        if u0 < 0 or u1 > abs(end[axis] - start[axis]):
            raise _InputError(f"cut {cut_id}: u range extends outside the facade run")
        if v0 < 0 or v1 > height:
            raise _InputError(f"cut {cut_id}: v range extends outside the level")
        if axis == 0:
            hole = (run0, box[1], z0, run1, box[4], z1)
        else:
            hole = (box[0], run0, z0, box[3], run1, z1)
        hole_boxes.append((hole, cut_id))

    # Compare the sets, not builder-generated decompositions or their stored volumes.
    # Every input boundary is retained.  Each open atom has constant occupancy.
    all_boxes = [box] + [b for b, _ in cell_boxes] + [b for b, _ in hole_boxes]
    coords = [sorted({b[axis] for b in all_boxes} | {b[axis + 3] for b in all_boxes}) for axis in range(3)]
    shape = tuple(len(c) - 1 for c in coords)
    atoms = math.prod(shape)
    if atoms > max_atoms or atoms * len(all_boxes) > max_work:
        raise _InputError(f"host {host_id}: exact coverage grid {shape} exceeds resource limit; no partial PASS")

    def contains(b: tuple[Fraction, ...], i: int, j: int, k: int) -> bool:
        return all(b[a] <= coords[a][idx] and coords[a][idx + 1] <= b[a + 3]
                   for a, idx in enumerate((i, j, k)))

    issues: dict[str, dict[tuple[int, int, int], tuple[tuple[str, ...], tuple[str, ...]]]] = defaultdict(dict)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                pos = i, j, k
                host_here = contains(box, *pos)
                present = tuple(ident for b, ident in cell_boxes if contains(b, *pos))
                holes_here = tuple(ident for b, ident in hole_boxes if contains(b, *pos))
                expected = host_here and not holes_here
                if expected and not present:
                    issues["gap"][pos] = present, holes_here
                if len(present) > 1:
                    issues["overlap"][pos] = present, holes_here
                if len(holes_here) > 1:
                    issues["overlapping_openings"][pos] = present, holes_here
                if host_here and holes_here and present:
                    issues["opening_filled"][pos] = present, holes_here
                if not host_here and present:
                    issues["outside_host"][pos] = present, holes_here

    # Merge face-connected atoms before applying the width diagnostic; subdivisions
    # caused by unrelated box boundaries cannot turn a large defect into a PASS.
    for code, remaining in sorted(issues.items()):
        while remaining:
            seed = next(iter(remaining))
            queue = deque([seed])
            present_ids: set[str] = set()
            hole_ids: set[str] = set()
            lows = [seed[0], seed[1], seed[2]]
            highs = lows.copy()
            volume = Fraction(0)
            count = 0
            while queue:
                pos = queue.popleft()
                data = remaining.pop(pos, None)
                if data is None:
                    continue
                count += 1
                present_ids.update(data[0])
                hole_ids.update(data[1])
                for a in range(3):
                    lows[a] = min(lows[a], pos[a])
                    highs[a] = max(highs[a], pos[a])
                volume += math.prod(coords[a][pos[a] + 1] - coords[a][pos[a]] for a in range(3))
                for a in range(3):
                    for step in (-1, 1):
                        neighbour = list(pos)
                        neighbour[a] += step
                        neighbour_t = tuple(neighbour)
                        if neighbour_t in remaining:
                            queue.append(neighbour_t)
            lo = [coords[a][lows[a]] for a in range(3)]
            hi = [coords[a][highs[a] + 1] for a in range(3)]
            width = min(hi[a] - lo[a] for a in range(3))
            discrepancy(code, f"host {host_id}: {code.replace('_', ' ')} in {count} grid atom(s)", width,
                        bbox_cm=[_output(v) for v in lo + hi], volume_cm3=_output(volume),
                        cell_ids=sorted(present_ids), cut_ids=sorted(hole_ids), atom_count=count)


def check_wall_cell_coverage(
    assembly: Any,
    massing: Any,
    dimensions: Any,
    *,
    max_atoms: int = 250_000,
    max_work: int = 5_000_000,
) -> CoverageResult:
    """Check each legacy cut host independently, with explicit REVIEW semantics.

    All inputs are unmodified. ``max_atoms`` and ``max_work`` bound exact grid
    enumeration per host; exceeding either yields FAIL, never a sampled PASS.
    Findings have ``code``, ``severity``, ``message`` and, where applicable,
    ``host_ref``, geometry, affected IDs and the measured difference.
    """
    findings: list[dict[str, Any]] = []
    checked: list[str] = []
    linear: Fraction | None = None
    try:
        if any(isinstance(x, bool) or not isinstance(x, int) or x <= 0 for x in (max_atoms, max_work)):
            raise _InputError("resource limits must be positive integers")
        for label, document in (("assembly", assembly), ("massing", massing), ("dimensions", dimensions)):
            if not isinstance(document, dict) or not isinstance(document.get("units"), dict) or document["units"].get("length") != "cm":
                raise _InputError(f"{label}.units.length must explicitly be 'cm'")
        if "wall_technique" in assembly and assembly["wall_technique"] != "legacy_cells_v1":
            raise _InputError("assembly.wall_technique must be legacy_cells_v1 when present")
        if not isinstance(dimensions, dict) or not isinstance(dimensions.get("tolerances"), dict):
            raise _InputError("dimensions.tolerances must be an object")
        linear = _num(dimensions["tolerances"].get("linear_cm"), "dimensions.tolerances.linear_cm")
        if linear < 0:
            raise _InputError("dimensions.tolerances.linear_cm must be nonnegative")
        cuts = _rows(assembly, "opening_cuts", "assembly")
        cells = _rows(assembly, "wall_cells", "assembly")
        elements = _rows(massing, "elements", "massing")
        facades = _unique(_rows(dimensions, "facades", "dimensions"), "id", "dimensions.facades")
        levels = _unique(_rows(dimensions, "levels", "dimensions"), "index", "dimensions.levels", integer=True)
        openings = _unique(_rows(dimensions, "openings", "dimensions"), "id", "dimensions.openings")
        _unique(cuts, "id", "assembly.opening_cuts")
        _unique(cells, "id", "assembly.wall_cells")
        element_index = _unique(elements, "id", "massing.elements")
        by_host_cuts: dict[str, list[dict[str, Any]]] = defaultdict(list)
        by_host_cells: dict[str, list[dict[str, Any]]] = defaultdict(list)
        seen_openings: set[str] = set()
        frame_hosts: dict[tuple[str, int], str] = {}
        for cut in cuts:
            cut_id = cut["id"]
            opening_id = _identifier(cut.get("opening_id"), f"cut {cut_id} opening_id")
            if opening_id in seen_openings:
                raise _InputError(f"opening {opening_id!r} has more than one cut")
            seen_openings.add(opening_id)
            host_id = _identifier(cut.get("host_ref"), f"cut {cut_id} host_ref")
            frame = (_identifier(cut.get("facade"), f"cut {cut_id} facade"),
                     _index(cut.get("level_index"), f"cut {cut_id} level_index"))
            if frame in frame_hosts and frame_hosts[frame] != host_id:
                raise _InputError(f"facade/level ({frame[0]!r}, {_index_text(frame[1])}) is claimed by multiple cut hosts")
            frame_hosts[frame] = host_id
            by_host_cuts[host_id].append(cut)
        for cell in cells:
            by_host_cells[_identifier(cell.get("host_ref"), f"cell {cell['id']} host_ref")].append(cell)
        if seen_openings != set(openings):
            raise _InputError(f"opening/cut join is not bijective: missing cuts {sorted(set(openings) - seen_openings)}, unknown openings {sorted(seen_openings - set(openings))}")
        orphan_hosts = set(by_host_cells) - set(by_host_cuts)
        if orphan_hosts:
            raise _InputError(f"wall cells reference hosts without cuts: {sorted(orphan_hosts)}")
        for host_id in sorted(by_host_cuts):
            host = element_index.get(host_id)
            if host is None or host.get("kind") != "facade_wall":
                findings.append({"code": "missing_host", "severity": "ERROR", "host_ref": host_id,
                                 "message": f"cut host {host_id!r} is missing or is not a facade_wall"})
                continue
            try:
                _check_host(host_id, host, by_host_cuts[host_id], by_host_cells.get(host_id, []),
                            facades, levels, openings, linear, findings, max_atoms, max_work)
            except _InputError as exc:
                findings.append({"code": "invalid_or_unsupported_geometry", "severity": "ERROR",
                                 "host_ref": host_id, "message": str(exc)})
            else:
                checked.append(host_id)
        if not cuts and not findings:
            return CoverageResult("NOT_APPLICABLE", [], (), _output(linear))
    except _InputError as exc:
        findings.append({"code": "invalid_input", "severity": "ERROR", "message": str(exc)})
    status = ("FAIL" if any(f["severity"] == "ERROR" for f in findings) else
              "REVIEW" if findings else "PASS")
    return CoverageResult(status, findings, tuple(checked), _output(linear) if linear is not None else None)
