#!/usr/bin/env python3
"""Deterministic Feature Map / gate coherence backstop (WI-14).

When a commit's staged changes touch ``docs/prd/feature-map.md``, recompute
its SHA256 from the *staged* content and compare it against the
``**Feature Map SHA256**:`` value recorded in ``docs/prd/feature-map.checklist.md``
(the staged version if that file is also staged in this commit, else the
committed HEAD version). A mismatch means the map changed without a matching
`/ms.pre-verify` (or `/ms.expand`) run and blocks the commit.

Progress bookkeeping is unaffected: after the Progress Ledger split (WI-1) it
lives in ``docs/prd/feature-map.progress.md``, which this check never reads.

No-op when ``docs/prd/feature-map.md`` is not part of the staged changeset --
this hook only guards normative Feature Map edits, not every commit.

Deliberate admin bypass stays possible via ``git commit --no-verify`` -- this
hook constrains the agent, not the human.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys

FEATURE_MAP = "docs/prd/feature-map.md"
CHECKLIST = "docs/prd/feature-map.checklist.md"
SHA_FIELD_RE = re.compile(r"^\*\*Feature Map SHA256\*\*:\s*(\S+)", re.MULTILINE)
FEATURE_HEADING_RE = re.compile(r"^## Feature (\d+):")
FENCES = ("```", "~~~")


def global_skeleton(text: str) -> str:
    """The map with every Feature section body removed.

    Must stay byte-identical to ``map_filtered ""`` in
    ``docs/templates/scripts/specter-gate.sh``; the parity matrix in
    ``tests/specter/test_specter_gate.py`` pins the two implementations
    together. A Feature heading is global content — it carries the map's
    decomposition — while the body under it belongs to that Feature, except for
    the ``### Dependencies`` subsection that ``/ms.featuremap`` requires in
    every Feature: the DAG is shared state and stays global.

    Two parser details exist to match awk rather than idiomatic Python:
    records split on ``\\n`` only (never on other Unicode line boundaries), and
    every emitted record is written with a trailing newline, because ``print``
    appends ORS whether or not the file ended with one.
    """
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()

    kept: list[str] = []
    in_feature = False
    in_dependencies = False
    fence_char = ""
    fence_len = 0

    def emit(record: str) -> None:
        if not in_feature or in_dependencies:
            kept.append(record + "\n")

    for record in parts:
        stripped = record.lstrip(" \t")
        if stripped.startswith(FENCES):
            char = stripped[0]
            length = len(stripped) - len(stripped.lstrip(char))
            if not fence_char:
                fence_char, fence_len = char, length
            elif char == fence_char and length >= fence_len:
                fence_char, fence_len = "", 0
            emit(record)
            continue
        if not fence_char:
            if FEATURE_HEADING_RE.match(record):
                in_feature = True
                in_dependencies = False
                kept.append(record + "\n")
                continue
            if record.startswith("## "):
                in_feature = False
                in_dependencies = False
                kept.append(record + "\n")
                continue
            if record.startswith("### "):
                in_dependencies = in_feature and record.startswith("### Dependencies")
                emit(record)
                continue
        emit(record)
    return "".join(kept)


def staged_files() -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    return set(result.stdout.splitlines())


def git_show(ref: str, path: str) -> str | None:
    # Bytes, not text mode: universal-newline translation would fold CRLF to LF
    # here while awk keeps the carriage return, so a CRLF map would hash
    # differently in the two implementations and reject its own checklist.
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


def main() -> int:
    changed = staged_files()
    if FEATURE_MAP not in changed:
        return 0  # this commit doesn't touch the normative Feature Map

    staged_map = git_show("", FEATURE_MAP)
    if staged_map is None:
        # Deletion is the most destructive Feature Map edit and must not pass
        # the backstop silently (2026-07-18 audit finding #17). Deliberate
        # teardown keeps two admin overrides, both human-initiated.
        if os.environ.get("SPECTER_ALLOW_MAP_DELETE") == "1":
            return 0
        print(
            "Feature Map gate coherence check failed:\n"
            f"  {FEATURE_MAP} is being DELETED in this commit.\n\n"
            "Deleting the normative Feature Map dismantles the SPECTER gates.\n"
            "If this teardown is deliberate, re-run with "
            "SPECTER_ALLOW_MAP_DELETE=1 git commit ..., or use git commit --no-verify."
        )
        return 1

    # The global checklist binds to the map's shared content, not to every
    # byte, so refining one Feature's section must not block the commit. The
    # whole-file digest stays accepted for checklists written before scoping.
    skeleton_sha = hashlib.sha256(
        global_skeleton(staged_map).encode("utf-8")
    ).hexdigest()
    whole_sha = hashlib.sha256(staged_map.encode("utf-8")).hexdigest()

    checklist_text = (
        git_show("", CHECKLIST) if CHECKLIST in changed else git_show("HEAD", CHECKLIST)
    )
    if checklist_text is None:
        print(
            "Feature Map gate coherence check failed:\n"
            f"  {FEATURE_MAP} changed, but no {CHECKLIST} exists (staged or committed) "
            "to prove it was verified.\n\n"
            "Feature Map changed without a matching gate. Run /ms.pre-verify or /ms.expand first.\n"
            "(Deliberate override: git commit --no-verify.)",
            file=sys.stderr,
        )
        return 1

    match = SHA_FIELD_RE.search(checklist_text)
    recorded_sha = match.group(1) if match else None

    if recorded_sha not in (skeleton_sha, whole_sha):
        print(
            "Feature Map gate coherence check failed:\n"
            f"  {FEATURE_MAP} staged global SHA256: {skeleton_sha}\n"
            f"  {CHECKLIST} recorded SHA256:        {recorded_sha or '(missing)'}\n\n"
            "Feature Map changed without a matching gate. Run /ms.pre-verify or /ms.expand first.\n"
            "(Deliberate override: git commit --no-verify.)",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
