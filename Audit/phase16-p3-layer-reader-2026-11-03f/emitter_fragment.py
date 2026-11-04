"""Standalone, offline-only integration sketch. NOT production wall runtime.

The helper text belongs inside an existing MAXScript ``(...)`` fileIn wrapper.
No arbitrary variable names, profile data, or MAXScript snippets are accepted.
This module does not fileIn, spawn Max, edit production, or enable replay.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


_HERE = Path(__file__).resolve().parent
READER_SHA256 = "0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7"

# A consumer must acquire these exact references independently, in the same
# session, before evaluating these illustrative snippets. This fragment never
# derives ownership from a layer name or a handle.
INITIAL_CAPTURE = '''\
    local p3LayerBaseline = p3LayerSnapshot node p3ExpectedNode p3ExpectedLayerBacking p3ExpectedRoot p3ExpectedLayerManager
    if p3LayerBaseline[2] != "INCOMPLETE" do throw "P3_LAYER_INCOMPLETE|invalid reader status"
    if p3LayerBaseline[3] != "PARTIAL_CAPTURE_ONLY" do throw "P3_LAYER_INCOMPLETE|layer observation failed"
    -- PARTIAL_CAPTURE_ONLY is an observation, not permission to construct.
    throw "P3_LAYER_INCOMPLETE|layer closure, GI completeness and live validation not established"
'''

REPLAY_OBSERVATION = '''\
    local p3LayerCurrent = p3LayerSnapshot node p3ExpectedNode p3ExpectedLayerBacking p3ExpectedRoot p3ExpectedLayerManager
    local p3LayerComparison = p3LayerSame p3LayerBaseline p3LayerCurrent
    -- Even OBSERVED_MATCH remains INCOMPLETE and does not authorize a NOOP.
    throw "INCOMPLETE_REPLAY|layer and native-state completeness unverified"
'''


def emit_local_helpers() -> str:
    """Return the exact reviewed candidate text or refuse any byte drift."""
    raw = (_HERE / "layer_reader.ms").read_bytes()
    if hashlib.sha256(raw).hexdigest() != READER_SHA256:
        raise ValueError("candidate MAXScript bytes differ from frozen SHA-256")
    source = raw.decode("utf-8", errors="strict")
    if "\x00" in source or not source.endswith("\n"):
        raise ValueError("invalid candidate source encoding")
    return source


def emit_example_wrapper() -> str:
    """Illustrate placement only; intentionally fails before scene inspection.

    The real caller cannot use this wrapper as a replacement for the production
    node snapshot: witness acquisition and independent validation are absent.
    """
    return (
        "-- OFFLINE EXAMPLE ONLY. No baseline or replay authorization.\n(\n"
        + emit_local_helpers()
        + '    throw "P3_LAYER_INCOMPLETE|example has no independently held witnesses"\n)\n'
    )
