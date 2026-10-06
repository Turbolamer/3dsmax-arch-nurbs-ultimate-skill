#!/usr/bin/env python3
"""Build and install the 3dsmax-arch-nurbs-ultimate skill pack.

Supports:
1. Building a portable .skill ZIP archive (preserving the references/, snippets/, scripts/,
   agents/, specs/ and examples/ layout, plus the top-level PLAN.md / CHECKPOINT.md / AGENTS.md).
2. Installing to ~/.claude/skills/3dsmax-arch-nurbs-ultimate and ~/.agents/skills/3dsmax-arch-nurbs-ultimate.
3. Optional --mcp-repo <path> to merge directly into a local cl0nazepamm/3dsmax-mcp checkout's skills/3dsmax-mcp-dev/ directory.
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "3dsmax-arch-nurbs-ultimate"
SKILL_ARCHIVE = SKILL_ROOT / f"{SKILL_NAME}.skill"

TOP_LEVEL_FILES: tuple[str, ...] = ("SKILL.md", "PLAN.md", "CHECKPOINT.md", "AGENTS.md")
PACKAGE_DIRS: tuple[tuple[str, frozenset[str] | None], ...] = (
    ("references", None),
    ("snippets", None),
    ("scripts", frozenset({".py"})),
    ("agents", frozenset({".md"})),
    ("specs", frozenset({".json"})),
    ("examples", frozenset({".json", ".ms", ".csv"})),
)
SKIP_DIR_NAMES = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".tmp", "tmp", "temp", "backups"}
)
SKIP_SUFFIXES = frozenset({".pyc", ".pyo", ".skill"})
SKIP_NAME_MARKERS = ("test_", "_test.", "selftest", "self_test", "scratch", "backup")


def _is_packaged(path: Path, suffixes: frozenset[str] | None) -> bool:
    parts = path.relative_to(SKILL_ROOT).parts
    if any(part in SKIP_DIR_NAMES for part in parts[:-1]):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    name = path.name.lower()
    if any(marker in name for marker in SKIP_NAME_MARKERS):
        return False
    return suffixes is None or path.suffix.lower() in suffixes


def collect_files() -> list[Path]:
    files = [SKILL_ROOT / n for n in TOP_LEVEL_FILES if (SKILL_ROOT / n).is_file()]
    for sub, suffixes in PACKAGE_DIRS:
        subdir = SKILL_ROOT / sub
        if subdir.is_dir():
            files.extend(p for p in subdir.rglob("*") if p.is_file() and _is_packaged(p, suffixes))
    return sorted(files, key=lambda p: p.relative_to(SKILL_ROOT).as_posix())


def build_archive(files: list[Path]) -> Path:
    with zipfile.ZipFile(SKILL_ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            rel = f.relative_to(SKILL_ROOT).as_posix()
            zf.write(f, f"./{rel}")
    print(f"[OK] Built portable archive: {SKILL_ARCHIVE} ({len(files)} files)")
    return SKILL_ARCHIVE


def install_to_dir(dest: Path, files: list[Path]) -> None:
    if dest.is_symlink() or (hasattr(dest, "is_junction") and dest.is_junction()):
        dest.unlink()
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        rel = f.relative_to(SKILL_ROOT)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
    print(f"[OK] Installed {len(files)} files to {dest}")


def merge_into_mcp_repo(mcp_repo: Path, files: list[Path]) -> None:
    mcp_skill_dir = mcp_repo / "skills" / "3dsmax-mcp-dev"
    if not mcp_skill_dir.is_dir():
        raise SystemExit(f"ERROR: {mcp_skill_dir} not found. Pass the root of cl0nazepamm/3dsmax-mcp.")
    install_to_dir(mcp_skill_dir, files)
    # Also copy new reference files flat into skills/3dsmax-mcp-dev/ so legacy build_skill.py finds them
    for f in (SKILL_ROOT / "references").glob("*.md"):
        shutil.copy2(f, mcp_skill_dir / f.name)
    print(f"[OK] Merged ultimate skill + references into {mcp_skill_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build & install 3dsmax-arch-nurbs-ultimate skill")
    parser.add_argument(
        "--target",
        choices=["archive", "global", "all"],
        default="all",
        help="Where to install: 'archive' (.skill only), 'global' (~/.claude & ~/.agents), or 'all'",
    )
    parser.add_argument(
        "--mcp-repo",
        type=Path,
        default=None,
        help="Optional path to a local cl0nazepamm/3dsmax-mcp repository to upgrade in-place",
    )
    args = parser.parse_args()

    files = collect_files()
    build_archive(files)

    if args.target in ("global", "all"):
        for base in (Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"):
            install_to_dir(base / SKILL_NAME, files)

    if args.mcp_repo is not None:
        merge_into_mcp_repo(args.mcp_repo.resolve(), files)


if __name__ == "__main__":
    main()
