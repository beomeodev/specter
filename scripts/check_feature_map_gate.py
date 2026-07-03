#!/usr/bin/env python3
"""Deterministic Feature Map / gate coherence backstop (WI-14).

When a commit's staged changes touch ``docs/prd/feature-map.md``, recompute
its SHA256 from the *staged* content and compare it against the
``**Feature Map SHA256**:`` value recorded in ``docs/prd/feature-map.checklist.md``
(the staged version if that file is also staged in this commit, else the
committed HEAD version). A mismatch means the map changed without a matching
`/ms.verify` (or `/ms.expand`) run and blocks the commit.

Progress bookkeeping is unaffected: after the Progress Ledger split (WI-1) it
lives in ``docs/prd/feature-map.progress.md``, which this check never reads.

No-op when ``docs/prd/feature-map.md`` is not part of the staged changeset --
this hook only guards normative Feature Map edits, not every commit.

Deliberate admin bypass stays possible via ``git commit --no-verify`` -- this
hook constrains the agent, not the human.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys

FEATURE_MAP = "docs/prd/feature-map.md"
CHECKLIST = "docs/prd/feature-map.checklist.md"
SHA_FIELD_RE = re.compile(r"^\*\*Feature Map SHA256\*\*:\s*(\S+)", re.MULTILINE)


def staged_files() -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    return set(result.stdout.splitlines())


def git_show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def main() -> int:
    changed = staged_files()
    if FEATURE_MAP not in changed:
        return 0  # this commit doesn't touch the normative Feature Map

    staged_map = git_show("", FEATURE_MAP)
    if staged_map is None:
        return 0  # feature-map.md was deleted in this commit; nothing to check

    current_sha = hashlib.sha256(staged_map.encode("utf-8")).hexdigest()

    checklist_text = (
        git_show("", CHECKLIST) if CHECKLIST in changed else git_show("HEAD", CHECKLIST)
    )
    if checklist_text is None:
        print(
            "Feature Map gate coherence check failed:\n"
            f"  {FEATURE_MAP} changed, but no {CHECKLIST} exists (staged or committed) "
            "to prove it was verified.\n\n"
            "Feature Map changed without a matching gate. Run /ms.verify or /ms.expand first.\n"
            "(Deliberate override: git commit --no-verify.)",
            file=sys.stderr,
        )
        return 1

    match = SHA_FIELD_RE.search(checklist_text)
    recorded_sha = match.group(1) if match else None

    if recorded_sha != current_sha:
        print(
            "Feature Map gate coherence check failed:\n"
            f"  {FEATURE_MAP} staged SHA256:   {current_sha}\n"
            f"  {CHECKLIST} recorded SHA256: {recorded_sha or '(missing)'}\n\n"
            "Feature Map changed without a matching gate. Run /ms.verify or /ms.expand first.\n"
            "(Deliberate override: git commit --no-verify.)",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
