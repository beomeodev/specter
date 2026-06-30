#!/usr/bin/env python3
"""Deterministic SPECTER TAG-chain backstop.

Validates the *mechanizable* subset of the ``@SPEC -> @TEST -> @CODE`` chain:
every tagged ``@CODE`` anchor must resolve to a matching ``@SPEC`` and ``@TEST``
anchor, and each ``@CODE`` id must be unique. Semantic correctness (does the
test actually cover the spec) stays an agentic ``/ms.review`` concern and is
intentionally NOT checked here -- this only proves the chain is *wired*.

No-op when the tree contains no ``@CODE`` anchors yet (fresh template / early
project state), so it never blocks scaffolding.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

# Only product code / spec / test trees carry real TAG chains. Allowlisting
# these (rather than denylisting vendor dirs) keeps the SPECTER tooling itself
# -- .claude skill/agent examples, docs, README -- out of scope. Those files
# contain illustrative @CODE:AUTH-001 snippets that are teaching material, not
# product chains, and must never trip the gate.
SCAN_ROOTS = ("backend", "frontend", "src", "app", "lib", "packages", "specs", "tests")

# Vendor / build dirs that may live under a scan root.
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".ruff_cache", ".serena", "dist", "build"}

# Text source files where TAG blocks live.
SCAN_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".md"}

# Anchor form "@CODE:AUTH-001". The reference form "@SPEC: specs/..." has a
# space after the colon and is excluded by requiring an id char immediately.
ANCHOR_RE = re.compile(r"@(SPEC|TEST|CODE|DOC):([A-Za-z0-9][A-Za-z0-9._-]*)")


def iter_source_files(root: Path) -> Iterator[Path]:
    """Yield scannable source files under the product scan roots."""
    for name in SCAN_ROOTS:
        base = root / name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_dir():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix in SCAN_SUFFIXES:
                yield path


def collect(root: Path) -> tuple[dict[str, list[str]], set[str], set[str]]:
    """Return (@CODE id -> locations, set of @SPEC ids, set of @TEST ids)."""
    code: dict[str, list[str]] = {}
    spec: set[str] = set()
    test: set[str] = set()
    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "@CHAIN" in line:
                continue  # chain restatement line, not an anchor declaration
            for kind, tag_id in ANCHOR_RE.findall(line):
                if kind == "CODE":
                    code.setdefault(tag_id, []).append(f"{path.relative_to(root)}:{lineno}")
                elif kind == "SPEC":
                    spec.add(tag_id)
                elif kind == "TEST":
                    test.add(tag_id)
    return code, spec, test


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    code, spec, test = collect(root)
    if not code:
        return 0  # nothing has opted into the chain yet

    errors: list[str] = []
    for tag_id, locations in sorted(code.items()):
        if len(locations) > 1:
            errors.append(f"duplicate @CODE:{tag_id} at {', '.join(locations)}")
        if tag_id not in spec:
            errors.append(f"@CODE:{tag_id} has no matching @SPEC anchor ({locations[0]})")
        if tag_id not in test:
            errors.append(f"@CODE:{tag_id} has no matching @TEST anchor ({locations[0]})")

    if errors:
        print("TAG-chain backstop failed (@SPEC -> @TEST -> @CODE wiring):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(
            "\nWire the missing anchor or drop the @CODE tag. "
            "Semantic chain review stays with /ms.review.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
