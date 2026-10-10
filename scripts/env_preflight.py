#!/usr/bin/env python3
"""Environment preflight for the 3ds Max architectural/NURBS skill.

Re-verifies the live 3ds Max 2026 environment and prints an aligned PASS/FAIL
report. Standard library only. Never raises: a failing probe becomes a FAIL row,
not a traceback.

WHY THIS IS NOT A DIRECT PROBE
------------------------------
This script cannot talk to 3ds Max itself. It is a helper the agent runs inside
a live MCP session. It works in two modes:

1. EMIT MODE (default, no ``--results``): prints the ready-to-paste MAXScript
   probe bodies so the agent can run each one through the
   ``3dsmax-mcp_execute_maxscript`` tool, then feed the captured outputs back in
   mode 2. Every MAXScript-dependent row is reported as SKIP.

2. EVAL MODE (``--results FILE``): reads a JSON object mapping check name ->
   captured output, evaluates every check, and exits 0 only when nothing FAILs.
   Keys in the results file match the check names printed in emit mode.
   When ``--require-complete`` is supplied, exits 1 if any check is SKIP or missing.

MAXSCRIPT PROBES REQUIRED (run each via ``execute_maxscript``, paste the returned
string back under the matching key):

    max_version          maxVersion()                       -> "major=2026 full=#(...)"
    units                units.SystemType / SystemScale      -> "SystemType=centimeters SystemScale=1.0"
    nurbset_present      NURBSSet resolves AND constructs    -> "CREATED:NURBSSet"
    loft_not_creatable   Loft resolves but does NOT construct
                                                       -> "resolved=true THROWS created=false"
    sweep_creatable      Sweep()                             -> "OK classOf=sweep ..."
    sweep_on_shape       addModifier (Rectangle()) (Sweep())  -> "ctor=ok attach=THROWS mods=0"
    quadpatch_creatable  QuadPatch()                          -> "OK classOf=quadPatch ..."
    materials            OpenPBR / PhysicalMaterial / Standard -> "OpenPBR=ok Physical..."

Five of the eight bodies below are transcribed verbatim from a live verification pass
against the running 3ds Max 2026 bridge. ``loft_not_creatable`` and ``sweep_on_shape``
were re-shaped afterwards so that the throw is reported as a flag and the value
separately; their measured outcomes are unchanged. See
``references/12-nurbs-gotchas.md`` section "MAXScript surface gotchas found by live
probe" for why each earlier form was wrong.

NON-MAXSCRIPT KEYS (from typed MCP tools, also accepted in the results file):

    bridge               get_bridge_status()                 -> "namedpipe"
                          (or {"transport": "namedpipe", ...}; --transport overrides)
    plugins_absent       get_plugin_capabilities() forestPack /
                         forestLite / tyFlow / railClone / phoenixFD
                          -> {"forestPack": false, ..., "phoenixFD": false}

EXIT CODES
----------
    0   no FAIL rows (and in --require-complete mode, no SKIP rows)
    1   at least one FAIL row (or any SKIP row in --require-complete mode)

Usage
-----
    python scripts/env_preflight.py
    python scripts/env_preflight.py --require-complete
    python scripts/env_preflight.py --results results.json --json
    python scripts/env_preflight.py --results results.json --require-complete
    python scripts/env_preflight.py --transport namedpipe
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# Expected environment (verified 2026-10-04 against live 3ds Max 2026)
# --------------------------------------------------------------------------- #

EXPECTED_VERSION = 2026
EXPECTED_TRANSPORT = "namedpipe"
ABSENT_PLUGINS: tuple[str, ...] = (
    "forestPack",
    "forestLite",
    "tyFlow",
    "railClone",
    "phoenixFD",
)
MATERIAL_CLASSES: tuple[str, ...] = (
    "OpenPBR",
    "PhysicalMaterial",
    "Standard",
)

try:
    from scripts.scene_units import SYSTEM_TYPE_FACTORS
except ImportError:
    try:
        from scene_units import SYSTEM_TYPE_FACTORS
    except ImportError:
        SYSTEM_TYPE_FACTORS = {
            "centimeters": 1.0,
            "millimeters": 0.1,
            "meters": 100.0,
            "kilometers": 100000.0,
            "inches": 2.54,
            "feet": 30.48,
            "miles": 160934.4,
            "yards": 91.44,
        }

# ``maxVersion()`` returns an array whose index 8 is the major version.
_VERSION_MAJOR_RE = re.compile(r"major\s*=\s*(\d+)")

SOURCE_MAXSCRIPT = "maxscript"
SOURCE_MCP = "mcp"

SEVERITY_FAIL = "fail"
SEVERITY_WARN = "warn"
SEVERITY_INFO = "info"

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARN = "WARN"
STATUS_SKIP = "SKIP"


class ProbeUnavailable(RuntimeError):
    """Raised when no captured result exists for a probe."""


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Probe:
    """One reported row of the report table."""

    name: str
    expected: str
    actual: str
    ok: bool
    status: str
    note: str


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one check function."""

    actual: str
    ok: bool
    note: str = ""


@dataclass(frozen=True)
class CheckSpec:
    """Everything needed to run and describe one check."""

    name: str
    expectation: str
    source: str
    script: str
    severity: str
    run: Callable[["ResultsRunner"], CheckResult]


# --------------------------------------------------------------------------- #
# Result access
# --------------------------------------------------------------------------- #


class ResultsRunner:
    """Supplies captured tool output to check functions.

    Acts as the ``runner`` callable. Raises :class:`ProbeUnavailable` for any
    probe with no captured result, which the harness turns into a SKIP row
    instead of a failure.
    """

    def __init__(
        self,
        results: Optional[Mapping[str, Any]] = None,
        transport: Optional[str] = None,
    ) -> None:
        self._results: Mapping[str, Any] = results or {}
        self._transport = transport

    @property
    def has_capture(self) -> bool:
        return bool(self._results)

    def text(self, key: str) -> str:
        value = self._results.get(key)
        if value is None:
            raise ProbeUnavailable(
                f"no captured result for {key!r}; run the MAXScript probe via "
                "execute_maxscript and pass the output in --results"
            )
        if isinstance(value, (dict, list)):
            return json.dumps(value, sort_keys=True)
        return str(value)

    def json_value(self, key: str) -> Any:
        value = self._results.get(key)
        if value is None:
            raise ProbeUnavailable(
                f"no captured result for {key!r}; supply it via --results"
            )
        return value

    def transport(self) -> Optional[str]:
        return self._transport


# --------------------------------------------------------------------------- #
# MAXScript probe bodies (printed by emit mode, run by the agent via MCP)
# --------------------------------------------------------------------------- #

# ``maxVersion()`` returns an ARRAY, not a string, and ``get3dsMaxVersion()`` does
# not exist in this build (it is undefined). The major version is index 8.
SCRIPT_MAX_VERSION = """(
local v = maxVersion()
"major=" + ((v[8]) as string) + " full=" + (v as string)
)"""

SCRIPT_UNITS = """(
local st = undefined
local ss = undefined
local out = ""
try ( st = units.SystemType as string ) catch ( st = "THREW" )
try ( ss = units.SystemScale as string ) catch ( ss = "THREW" )
out += "SystemType=" + st + " SystemScale=" + ss
out
)"""

SCRIPT_NURBSET_PRESENT = """(
-- NOTE: do NOT use "get #NURBSSet" to test for this class. It returns
-- undefined even when the class exists, which makes the probe pass vacuously.
-- Resolve the identifier and construct it instead.
local id = undefined
try (id = execute "NURBSSet") catch ()
local made = "no-class"
if id != undefined then
(
    try (local o = id(); made = "CREATED:" + ((classOf o) as string))
    catch (made = "not-creatable")
)
made
)"""

SCRIPT_LOFT_NOT_CREATABLE = """(
-- Report the throw and the constructed value SEPARATELY, never folded into one
-- concatenated string. getCurrentException() does work inside a catch on this
-- build (measured 2026-10-05, 6 of 6 throw kinds; the old rule that it throws
-- itself was withdrawn as false), but its return value is exactly the kind of
-- thing that must not be string-concatenated into a probe result.
-- Resolve first, construct second, so "the class is absent" and "the class is
-- present but not creatable" cannot be confused for each other.
local out = ""
local id = undefined
try (id = execute "Loft") catch ()
local resolved = (id != undefined)
local threw = false
local created = false
if resolved then
(
    try (local o = id(); created = true) catch (threw = true)
)
out += "resolved=" + (resolved as string)
if threw then out += " THROWS" else out += " NOTHROW"
out += " created=" + (created as string)
out
)"""

# A standalone modifier instance is NOT a scene node, so there is deliberately no
# cleanup call here: attempting to delete it fails with
# No "delete" function for sweep:Sweep
# To clean up after a modifier probe, attach the modifier to a real node and delete
# that node instead (see SCRIPT_SWEEP_ON_SHAPE). See also
# references/12-nurbs-gotchas.md, "MAXScript surface gotchas found by live probe".
SCRIPT_SWEEP_CREATABLE = """(
local s = Sweep()
-- No delete: a standalone modifier instance is not a scene node.
-- "delete s" fails with: No "delete" function for sweep:Sweep
"OK classOf=" + ((classOf s) as string) + " superclass=" + ((superclassOf s) as string)
)"""

# ``Sweep()`` CONSTRUCTS on this build but ``addModifier`` THROWS for it: ``Sweep``
# is one of six classes measured to construct and then throw on ``addModifier``
# (the P4b-r "6 unattachable modifiers" finding -- ``Extrude`` ``Sweep`` ``Lathe``
# ``Surface`` ``CrossSection`` ``Bevel_Profile``), re-confirmed at the P6
# bounded-modifier ladder rungs 1-2. The measured outcome is therefore mods=0 plus
# a throw, and check_sweep_on_shape asserts that. DO NOT "fix" the expectation back
# to mods=1 first=Sweep: that is what made this row FAIL on a healthy machine.
# ``ctor=`` and ``attach=`` keep the two possible throws separable, and the throw is
# reported as a flag rather than concatenated with a value.
SCRIPT_SWEEP_ON_SHAPE = """(
local s = Rectangle()
s.width = 40.0
s.length = 40.0
local sm = undefined
local cthrew = false
try (sm = Sweep()) catch (cthrew = true)
local athrew = false
if not cthrew then
(
    try (addModifier s sm) catch (athrew = true)
)
-- Use the .modifiers PROPERTY. The standalone "modifiers s" function form
-- fails with: Type error: Call needs function or class, got: undefined
local mods = 0
try (mods = s.modifiers.count) catch ()
local out = "ctor="
if cthrew then out += "THROWS" else out += "ok"
out += " attach="
if athrew then out += "THROWS" else out += "ok"
out += " mods=" + (mods as string)
if mods > 0 then
(
    local first = "?"
    try (first = s.modifiers[1].name) catch ()
    out += " first=" + first
)
-- delete s, the shape node (a bare Sweep() would NOT be deletable). Guarded so a
-- cleanup failure cannot swallow the result string this probe exists to return.
try (delete s) catch ()
out
)"""

SCRIPT_QUADPATCH_CREATABLE = """(
local p = QuadPatch()
local out = "OK classOf=" + ((classOf p) as string) + " superclass=" + ((superclassOf p) as string)
delete p
out
)"""

# Material class identifiers are internalNames, not display names. The DLL scan
# advertises "OpenPBR Material" but the creatable identifier is ``OpenPBR``
# (instance class ``OpenPBR_Material``). ``PhysicalMaterial`` and ``Standard``
# happen to match their display names. Severity for this probe is INFO: absence is
# reported, never failed.
SCRIPT_MATERIALS = """(
local out = ""
local names = #("OpenPBR", "PhysicalMaterial", "Standard")
for n in names do
(
    local id = undefined
    try (id = execute n) catch ()
    if id == undefined then
    (
        out += n + "=absent "
    )
    else
    (
        local made = "notcreatable"
        try (local mt = id(); made = "ok") catch (made = "notcreatable")
        out += n + "=" + made + " "
    )
)
out
)"""


# --------------------------------------------------------------------------- #
# Check functions
# --------------------------------------------------------------------------- #


def _probe_field(raw: str, key: str) -> Optional[str]:
    """Return the uppercased token that follows ``key`` in captured probe output.

    ``None`` when the key is absent. Callers must treat "the field says X" and
    "the probe never reported the field" as different states: a missing field is
    an aborted or malformed probe, not a value, and collapsing the two is how a
    check starts passing for the wrong reason.
    """
    match = re.search(re.escape(key) + r"\s*([^\s]+)", raw, re.IGNORECASE)
    return None if match is None else match.group(1).upper()


def check_bridge(runner: ResultsRunner) -> CheckResult:
    """Transport must be ``namedpipe``; the TCP listener on 8765 is irrelevant."""
    transport = runner.transport()
    if transport is None:
        raw = runner.text("bridge")
        if isinstance(raw, str) and raw.strip().startswith("{"):
            raw = json.loads(raw).get("transport", raw)
        transport = str(raw).strip()
    ok = transport == EXPECTED_TRANSPORT
    note = "" if ok else f"expected {EXPECTED_TRANSPORT}; 8765 TCP listener is not used"
    return CheckResult(transport, ok, note)


def check_max_version(runner: ResultsRunner) -> CheckResult:
    """Report the running Max version; warn rather than fail on a mismatch.

    The probe emits ``major=<n> full=#(...)`` because ``maxVersion()`` returns an
    array and ``get3dsMaxVersion()`` does not exist. Older capture shapes
    (``"<major> | raw=#(...)"``, a bare dotted ``"2026.3.2"``) are still accepted.
    """
    raw = runner.text("max_version").strip()
    match = _VERSION_MAJOR_RE.search(raw)
    if match is not None:
        major = match.group(1)
    else:
        token = raw.split()[0] if raw.split() else raw
        major = token.split("|")[0].split(".")[0].strip()
    try:
        value = int(major)
    except ValueError:
        return CheckResult(raw, False, f"unparseable version string {raw!r}")
    ok = value == EXPECTED_VERSION
    note = "" if ok else f"baseline verified against {EXPECTED_VERSION}"
    return CheckResult(str(value), ok, note)


def check_units(runner: ResultsRunner) -> CheckResult:
    """SystemType must be certified and SystemScale must be a positive float."""
    raw = runner.text("units").strip()
    match_st = re.search(r"SystemType=\s*([^\s]+)", raw, re.IGNORECASE)
    match_ss = re.search(r"SystemScale=\s*([^\s]+)", raw, re.IGNORECASE)
    if match_st is None or match_ss is None:
        return CheckResult(
            raw or "(empty)",
            False,
            "failed to parse SystemType= and SystemScale= from units probe output",
        )
    st = match_st.group(1)
    ss = match_ss.group(1)

    norm_type = st.lstrip("#").lower()
    if norm_type not in SYSTEM_TYPE_FACTORS:
        return CheckResult(
            f"SystemType={st} SystemScale={ss}",
            False,
            f"uncertified SystemType {st!r}; must be one of {sorted(SYSTEM_TYPE_FACTORS.keys())}",
        )

    try:
        scale = float(ss)
    except (ValueError, TypeError):
        return CheckResult(
            f"SystemType={st} SystemScale={ss}",
            False,
            f"unparseable SystemScale {ss!r}; must be positive finite float",
        )

    if not math.isfinite(scale) or scale <= 0.0:
        return CheckResult(
            f"SystemType={st} SystemScale={ss}",
            False,
            f"SystemScale must be positive finite float, got {scale}",
        )

    return CheckResult(f"SystemType={st} SystemScale={ss}", True, "")


def check_nurbset_present(runner: ResultsRunner) -> CheckResult:
    """``NURBSSet`` must resolve AND construct; the relational NURBS API is real.

    Correction (P1): an earlier version of this check asserted the opposite and
    used ``get #NURBSSet``, which returns undefined even for existing classes,
    so the probe passed vacuously. See references/12-nurbs-gotchas.md.
    """
    raw = runner.text("nurbset_present").strip()
    present = raw.upper().startswith("CREATED")
    note = "" if present else (
        "NURBSSet did not construct; the relational NURBS pipeline is unavailable"
    )
    return CheckResult(raw, present, note)


def check_loft_not_creatable(runner: ResultsRunner) -> CheckResult:
    """``Loft`` must resolve but NOT construct; scripted lofts stay impossible.

    The probe reports three facts separately -- ``resolved=``, the throw token and
    ``created=`` -- instead of concatenating ``getCurrentException()`` into the
    result. ``getCurrentException()`` works inside a catch on this build (measured
    2026-10-05, 6 of 6 throw kinds, the old "it throws itself" rule was withdrawn as
    false), but folding its return value into the probe's own string is not the
    measured standard here: the throw and the value are reported apart.

    Every deviation from the measured baseline FAILs, including ``Loft()``
    becoming constructible -- the single thing this row exists to detect, since the
    real loft path (``NURBSULoftSurface``) is chosen on the strength of it.
    """
    raw = runner.text("loft_not_creatable").strip()
    resolved = _probe_field(raw, "resolved=")
    created = _probe_field(raw, "created=")
    threw = re.search(r"\bTHROWS\b", raw.upper()) is not None
    ok = resolved == "TRUE" and threw and created == "FALSE"
    if created == "TRUE":
        note = (
            "Loft() constructed; scripted loft recipes become viable and "
            "NURBSULoftSurface is no longer the only loft route"
        )
    elif resolved != "TRUE":
        note = (
            "Loft does not resolve at all; the measured finding is 'resolves but is "
            "not creatable' -- re-measure before trusting this row"
        )
    elif created is None or resolved is None:
        note = (
            "probe reported no resolved=/created= field, so it may have aborted; "
            "run this body through execute_maxscript and read the raw string"
        )
    elif not threw:
        note = "Loft neither threw nor constructed; indeterminate -- re-measure"
    else:
        note = ""
    return CheckResult(raw, ok, note)


def check_sweep_creatable(runner: ResultsRunner) -> CheckResult:
    """``Sweep()`` must construct; it is the primary scripted surface tool."""
    raw = runner.text("sweep_creatable").strip()
    ok = raw.upper().startswith("OK")
    return CheckResult(raw, ok, "" if ok else "Sweep did not construct")


def check_sweep_on_shape(runner: ResultsRunner) -> CheckResult:
    """``addModifier`` must THROW for ``Sweep``, leaving the shape at ``mods=0``.

    This is the MEASURED behaviour of this build, not a defect in the probe.
    ``Sweep`` is one of six classes that construct and then throw on
    ``addModifier`` -- the P4b-r "6 unattachable modifiers" finding (``Extrude``
    ``Sweep`` ``Lathe`` ``Surface`` ``CrossSection`` ``Bevel_Profile``),
    re-confirmed at the P6 bounded-modifier ladder rungs 1-2.

    An earlier version of this check expected ``mods=1 first=Sweep``. On a healthy
    machine the probe returned ``mods=0``, the row FAILed, and the documented
    ``PASS 9 / FAIL 0`` gate was unreachable. That expectation is the bug, not the
    build.

    The check is deliberately inverted: it FAILS if ``Sweep`` ever *does* attach,
    because ``agents/max-assembly.md`` sections 6.4 / AP-8 and this file's own
    routing advice are written on the measured six-class set. If this row goes red
    with ``mods=1``, re-measure that set before trusting the model.

    Limitation, stated so the row is not over-read: the probe reports the throw as a
    flag and deliberately does not concatenate the exception message, so it cannot
    say *why* ``addModifier`` threw. ``ctor=`` and ``attach=`` keep the construct
    failure and the attach failure separable.
    """
    raw = runner.text("sweep_on_shape").strip()
    ctor = _probe_field(raw, "ctor=")
    attach = _probe_field(raw, "attach=")
    mods_token = _probe_field(raw, "mods=")
    count = int(mods_token) if mods_token is not None and mods_token.isdigit() else None
    ok = ctor == "OK" and attach == "THROWS" and count == 0
    if count is None:
        note = (
            "probe reported no mods=<n> field, so it may have aborted; run this body "
            "through execute_maxscript and read the raw string"
        )
    elif count > 0:
        note = (
            f"Sweep now attaches to a shape (mods={count}); this build differs from "
            "the measured six-class unattachable set -- re-measure it before "
            "trusting agents/max-assembly.md sections 6.4 / AP-8"
        )
    elif ctor == "THROWS":
        note = (
            "Sweep() no longer constructs; sweep_creatable is the row for that, but "
            "this row's baseline changed -- re-measure"
        )
    elif attach == "OK":
        note = (
            "addModifier did not throw yet attached nothing; the measured failure "
            "mode is a throw, so this is a different fault -- re-measure"
        )
    else:
        note = ""
    return CheckResult(raw, ok, note)


def check_quadpatch_creatable(runner: ResultsRunner) -> CheckResult:
    """``QuadPatch()`` must construct; it is the scripted NURBS surface generator."""
    raw = runner.text("quadpatch_creatable").strip()
    ok = raw.upper().startswith("OK") and "quadpatch" in raw.lower()
    return CheckResult(raw, ok, "" if ok else "QuadPatch did not construct")


def check_plugins_absent(runner: ResultsRunner) -> CheckResult:
    """ForestPack / tyFlow / RailClone / PhoenixFD must be absent.

    Their absence is why the MCP tools listed in
    references/02-mcp-live-orchestration.md section 3 must never be called.
    """
    payload = runner.json_value("plugins_absent")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, Mapping):
        return CheckResult(json.dumps(payload), False, "plugins_absent must be a JSON object")
    missing = [k for k in ABSENT_PLUGINS if k not in payload]
    if missing:
        return CheckResult(
            f"missing: {', '.join(missing)}",
            False,
            f"missing plugin keys in payload: {', '.join(missing)}; missing keys must not inherit false-as-absent",
        )
    states = {k: _as_bool(payload.get(k)) for k in ABSENT_PLUGINS}
    absent = [k for k, v in states.items() if v is False]
    present = [k for k, v in states.items() if v is True]
    ok = not present
    note = "" if ok else f"present: {', '.join(present)}; their MCP tools may now work"
    return CheckResult(f"absent={len(absent)}/{len(states)}", ok, note)


def check_materials(runner: ResultsRunner) -> CheckResult:
    """Report which base material classes are available. Informational only."""
    raw = runner.text("materials").strip()
    available = [n for n in MATERIAL_CLASSES if f"{n}=ok" in raw.replace(" ", "")]
    return CheckResult(
        raw or "(empty)",
        True,
        f"available: {', '.join(available) if available else 'none'}",
    )


# --------------------------------------------------------------------------- #
# Harness
# --------------------------------------------------------------------------- #


def build_checks() -> tuple[CheckSpec, ...]:
    return (
        CheckSpec(
            name="bridge",
            expectation=f"transport={EXPECTED_TRANSPORT}",
            source=SOURCE_MCP,
            script="",
            severity=SEVERITY_WARN,
            run=check_bridge,
        ),
        CheckSpec(
            name="max_version",
            expectation=f"major={EXPECTED_VERSION}",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_MAX_VERSION,
            severity=SEVERITY_WARN,
            run=check_max_version,
        ),
        CheckSpec(
            name="units",
            expectation="certified SystemType, scale > 0",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_UNITS,
            severity=SEVERITY_FAIL,
            run=check_units,
        ),
        CheckSpec(
            name="nurbset_present",
            expectation="NURBSSet constructs",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_NURBSET_PRESENT,
            severity=SEVERITY_FAIL,
            run=check_nurbset_present,
        ),
        CheckSpec(
            name="loft_not_creatable",
            expectation="Loft resolves, is not creatable",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_LOFT_NOT_CREATABLE,
            severity=SEVERITY_FAIL,
            run=check_loft_not_creatable,
        ),
        CheckSpec(
            name="sweep_creatable",
            expectation="Sweep() constructs",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_SWEEP_CREATABLE,
            severity=SEVERITY_FAIL,
            run=check_sweep_creatable,
        ),
        CheckSpec(
            name="sweep_on_shape",
            expectation="addModifier(Sweep) throws, mods=0",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_SWEEP_ON_SHAPE,
            severity=SEVERITY_FAIL,
            run=check_sweep_on_shape,
        ),
        CheckSpec(
            name="quadpatch_creatable",
            expectation="QuadPatch() constructs",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_QUADPATCH_CREATABLE,
            severity=SEVERITY_FAIL,
            run=check_quadpatch_creatable,
        ),
        CheckSpec(
            name="plugins_absent",
            expectation="forestPack/tyFlow/railClone/phoenixFD all False",
            source=SOURCE_MCP,
            script="",
            severity=SEVERITY_FAIL,
            run=check_plugins_absent,
        ),
        CheckSpec(
            name="materials",
            expectation="report OpenPBR/Physical/Standard",
            source=SOURCE_MAXSCRIPT,
            script=SCRIPT_MATERIALS,
            severity=SEVERITY_INFO,
            run=check_materials,
        ),
    )


def evaluate(spec: CheckSpec, runner: ResultsRunner) -> Probe:
    """Run one check, converting every failure mode into a Probe row."""
    try:
        result = spec.run(runner)
    except ProbeUnavailable as exc:
        return Probe(spec.name, spec.expectation, "SKIP", True, STATUS_SKIP, str(exc))
    except Exception as exc:  # noqa: BLE001 - a probe must never propagate
        return Probe(
            spec.name,
            spec.expectation,
            f"error: {type(exc).__name__}: {exc}",
            False,
            STATUS_FAIL,
            "",
        )
    status = _status(spec.severity, result.ok)
    return Probe(spec.name, spec.expectation, result.actual, result.ok, status, result.note)


def _status(severity: str, ok: bool) -> str:
    if severity == SEVERITY_INFO:
        return STATUS_PASS
    if ok:
        return STATUS_PASS
    return STATUS_WARN if severity == SEVERITY_WARN else STATUS_FAIL


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "available", "present"}
    return bool(value)


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def render_table(probes: Sequence[Probe]) -> str:
    headers = ("CHECK", "STATUS", "EXPECTED", "ACTUAL", "NOTE")
    rows = [
        (p.name, p.status, p.expected, _shorten(p.actual, 60), _shorten(p.note, 48))
        for p in probes
    ]
    widths = [
        max(len(headers[i]), max((len(row[i]) for row in rows), default=0))
        for i in range(len(headers))
    ]
    lines = [
        "  ".join(headers[i].ljust(widths[i]) for i in range(len(headers))).rstrip(),
        "  ".join("-" * widths[i] for i in range(len(headers))),
    ]
    for row in rows:
        lines.append(
            "  ".join(row[i].ljust(widths[i]) for i in range(len(headers))).rstrip()
        )
    return "\n".join(lines)


def render_probes(specs: Sequence[CheckSpec]) -> str:
    blocks = ["MAXScript probes - run each via execute_maxscript", "=" * 46]
    for spec in specs:
        if spec.source != SOURCE_MAXSCRIPT:
            continue
        blocks.append(f"\n-- {spec.name}  ({spec.expectation})")
        blocks.append(spec.script)
    non_ms = [s.name for s in specs if s.source == SOURCE_MCP]
    blocks.append("")
    blocks.append(
        "Non-MAXSCRIPT keys (from typed MCP tools): " + ", ".join(non_ms)
    )
    return "\n".join(blocks)


def _shorten(text: str, limit: int) -> str:
    flat = " ".join(str(text).split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 3] + "..."


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def load_results(path: Path) -> Mapping[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("results file must contain a JSON object")
    return payload


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the live 3ds Max environment for this skill.",
    )
    parser.add_argument(
        "--results",
        type=Path,
        help="JSON file of captured probe outputs (see module docstring).",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Strict gate mode: exit 1 on any check SKIP, missing captured result, or malformed output.",
    )
    parser.add_argument(
        "--transport",
        help="Bridge transport reported by the caller, e.g. namedpipe.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit the report as JSON instead of a table.",
    )
    args = parser.parse_args(argv)

    results: Mapping[str, Any] = {}
    if args.results is not None:
        try:
            results = load_results(args.results)
        except Exception as exc:  # noqa: BLE001 - report, do not traceback
            print(f"error: cannot read results file: {exc}", file=sys.stderr)
            return 1

    specs = build_checks()
    runner = ResultsRunner(results, args.transport)
    probes = [evaluate(spec, runner) for spec in specs]

    if not args.as_json:
        if not runner.has_capture:
            print(render_probes(specs))
            print()
        print(render_table(probes))

    passed = sum(1 for p in probes if p.status == STATUS_PASS)
    failed = sum(1 for p in probes if p.status == STATUS_FAIL)
    warned = sum(1 for p in probes if p.status == STATUS_WARN)
    skipped = sum(1 for p in probes if p.status == STATUS_SKIP)

    summary = f"PASS {passed} / FAIL {failed}"

    if args.as_json:
        print(
            json.dumps(
                {
                    "probes": [
                        {
                            "name": p.name,
                            "status": p.status,
                            "expected": p.expected,
                            "actual": p.actual,
                            "note": p.note,
                        }
                        for p in probes
                    ],
                    "summary": summary,
                    "warn": warned,
                    "skip": skipped,
                },
                indent=2,
            )
        )
    else:
        print(summary)
        if warned:
            print(f"warn {warned}")
        if skipped:
            print(
                f"skip {skipped} - no captured results; rerun with --results to evaluate"
            )
    if args.require_complete:
        if failed > 0 or skipped > 0:
            return 1
        return 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())