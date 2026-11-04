#!/usr/bin/env python3
"""Static extraction/safety checks, NOT a MAXScript parser or live acceptance."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_ms_comments_and_strings(text: str) -> str:
    # Sufficient only for these short bodies (no verbatim strings/block comments).
    output = []
    in_string = False
    line_comment = False
    index = 0
    while index < len(text):
        c = text[index]
        if line_comment:
            if c == "\n":
                line_comment = False
                output.append(c)
        elif in_string:
            if c == "\\":
                index += 1
            elif c == '"':
                in_string = False
                output.append(" ")
        elif text[index : index + 2] == "--":
            line_comment = True
            index += 1
        elif c == '"':
            in_string = True
            output.append(" ")
        else:
            output.append(c)
        index += 1
    assert not in_string, "unterminated string"
    return "".join(output)


def main() -> None:
    prepared = json.loads((HERE / "preparation.json").read_text(encoding="utf-8"))
    for rel, expected in prepared["source_hashes_before"].items():
        assert sha(ROOT / rel) == expected, f"source drift: {rel}"
    env = runpy.run_path(str(ROOT / "scripts/env_preflight.py"))
    canonical = {spec.name: spec.script for spec in env["build_checks"]() if spec.script}
    for name, body in canonical.items():
        assert (HERE / f"canonical/{name}.ms").read_bytes() == body.encode("utf-8")
    for p in HERE.glob("*.py"):
        ast.parse(p.read_text(encoding="utf-8"), filename=str(p))

    bodies = []
    for p in sorted(HERE.rglob("*.ms")):
        raw = p.read_text(encoding="utf-8")
        code = strip_ms_comments_and_strings(raw)
        stack = []
        pairs = {")": "(", "]": "[", "}": "{"}
        for c in code:
            if c in "([{":
                stack.append(c)
            elif c in ")]}":
                assert stack and stack.pop() == pairs[c], str(p)
        assert not stack, str(p)
        for forbidden in ("formattedPrint", "resetMaxFile", "saveMaxFile", "clearUndoBuffer", "setSaveRequired", "getNodeByName"):
            assert re.search(r"\b" + forbidden + r"\b", code, re.I) is None, (p, forbidden)
        assert re.search(r"units\.(SystemType|SystemScale)\s*=(?!=)", code, re.I) is None
        deletions = re.findall(r"\bdelete\s+(\w+)", code)
        allowed_refs = {
            "canonical/sweep_on_shape.ms": ["s"],
            "canonical/quadpatch_creatable.ms": ["p"],
            "modified/02_native_box_roundtrip.ms": ["__node"],
            "modified/loft_not_creatable.ms": ["candidate"],
            "modified/sweep_on_shape.ms": ["shapeNode"],
            "modified/quadpatch_creatable.ms": ["patchNode"],
        }
        rel = p.relative_to(HERE).as_posix()
        assert deletions == allowed_refs.get(rel, []), (rel, deletions)
        bodies.append({"path": rel, "sha256": sha(p), "local_delete_operands": deletions, "balanced_delimiters": True})

    result = {
        "status": "OFFLINE_STATIC_CHECKS_OK_NOT_MAXSCRIPT_PARSE_OR_EXECUTION",
        "limitations": ["No Max calls", "No native MAXScript parser", "No time bound measured", "No live preservation proof", "Canonical evaluator alone does not assess appended cleanup fields"],
        "canonical_exact_bytes": len(canonical),
        "source_hash_drift": False,
        "body_static_checks": bodies,
    }
    data = (json.dumps(result, indent=2) + "\n").encode("utf-8")
    output = HERE / "static-verification.json"
    if output.exists():
        assert output.read_bytes() == data, "refuse unequal existing verification"
    else:
        with output.open("xb") as handle:
            handle.write(data)
    print(json.dumps({"status": result["status"], "canonical_exact_bytes": len(canonical), "total_ms_bodies": len(bodies), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
