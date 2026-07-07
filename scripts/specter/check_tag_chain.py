#!/usr/bin/env python3
"""Deterministic SPECTER TAG-chain backstop.

Validates the *mechanizable* subset of the ``@SPEC -> @TEST -> @CODE`` chain:
every tagged ``@CODE`` anchor must resolve to a matching ``@SPEC`` and ``@TEST``
anchor, and each ``@CODE`` id must be unique. Semantic correctness (does the
test actually cover the spec) stays an agentic ``/ms.review`` concern and is
intentionally NOT checked here -- this only proves the chain is *wired*.

``/ms.fix`` track exemption: ``@CODE:FIX-*`` ids carry no governing spec by
design (their block records ``@SPEC: (fix — no spec)``), so the same-id
``@SPEC`` anchor requirement is waived for them. The ``@TEST`` anchor stays
required unless the same file declares the presentational marker
``@TEST: (presentational — no test)``. Uniqueness applies to FIX ids too.

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
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    ".serena",
    "dist",
    "build",
}

# Text source files where TAG blocks live.
SCAN_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".md",
}

# Anchor form "@CODE:AUTH-001". The reference form "@SPEC: specs/..." has a
# space after the colon and is excluded by requiring an id char immediately.
ANCHOR_RE = re.compile(r"@(SPEC|TEST|CODE|DOC):([A-Za-z0-9][A-Za-z0-9._-]*)")

# /ms.fix track: ids with this prefix have no governing spec.
FIX_PREFIX = "FIX-"

# Presentational-fix marker (declares "no test" explicitly in the TAG block).
PRESENTATIONAL_RE = re.compile(r"@TEST:\s*\(presentational")


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


def collect(root: Path) -> tuple[dict[str, list[str]], set[str], set[str], set[str]]:
    """Return (@CODE id -> locations, @SPEC ids, @TEST ids, presentational-exempt FIX ids)."""
    code: dict[str, list[str]] = {}
    spec: set[str] = set()
    test: set[str] = set()
    presentational: set[str] = set()
    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_code_ids: list[str] = []
        file_has_marker = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if PRESENTATIONAL_RE.search(line):
                file_has_marker = True
            if "@CHAIN" in line:
                continue  # chain restatement line, not an anchor declaration
            for kind, tag_id in ANCHOR_RE.findall(line):
                if kind == "CODE":
                    code.setdefault(tag_id, []).append(
                        f"{path.relative_to(root)}:{lineno}"
                    )
                    file_code_ids.append(tag_id)
                elif kind == "SPEC":
                    spec.add(tag_id)
                elif kind == "TEST":
                    test.add(tag_id)
        if file_has_marker:
            presentational.update(t for t in file_code_ids if t.startswith(FIX_PREFIX))
    return code, spec, test, presentational


def default_root() -> Path:
    """Repo root = two directories above this script (scripts/specter/)."""
    return Path(__file__).resolve().parent.parent.parent


def main(root: Path | None = None) -> int:
    if root is None:
        root = default_root()
    code, spec, test, presentational = collect(root)
    if not code:
        return 0  # nothing has opted into the chain yet

    errors: list[str] = []
    for tag_id, locations in sorted(code.items()):
        is_fix = tag_id.startswith(FIX_PREFIX)
        if len(locations) > 1:
            errors.append(f"duplicate @CODE:{tag_id} at {', '.join(locations)}")
        if tag_id not in spec and not is_fix:
            errors.append(
                f"@CODE:{tag_id} has no matching @SPEC anchor ({locations[0]})"
            )
        if tag_id not in test and not (is_fix and tag_id in presentational):
            hint = (
                " (presentational fix? declare `@TEST: (presentational — no test)`)"
                if is_fix
                else ""
            )
            errors.append(
                f"@CODE:{tag_id} has no matching @TEST anchor ({locations[0]}){hint}"
            )

    if errors:
        print(
            "TAG-chain backstop failed (@SPEC -> @TEST -> @CODE wiring):",
            file=sys.stderr,
        )
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
