"""Tests for docs/templates/scripts/speckit-specify-gate-hook.sh (direct-call guard).

2026-07-18 audit #4: the gate-pass token is per-Feature (.ms-gate-pass-<NNN>),
so a live token for one Feature must not admit a different Feature or a
freeform direct /speckit-specify call. Unrelated skills stay untouched.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "templates"
    / "scripts"
    / "speckit-specify-gate-hook.sh"
)


def run_hook(repo: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(repo)},
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )


def decision(result: subprocess.CompletedProcess[str]) -> str | None:
    """Return the hook's permission decision, or None when it allowed."""
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]


def specify_payload(args: str) -> dict:
    return {"tool_input": {"skill": "speckit-specify", "args": args}}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ".specify").mkdir()
    return tmp_path


def test_unrelated_skill_is_allowed(repo: Path) -> None:
    result = run_hook(repo, {"tool_input": {"skill": "other-skill", "args": "x"}})
    assert decision(result) is None


def test_no_token_denies(repo: Path) -> None:
    result = run_hook(repo, specify_payload("## Feature 006: sample feature"))
    assert decision(result) == "deny"


def test_matching_token_allows(repo: Path) -> None:
    (repo / ".specify" / ".ms-gate-pass-006").touch()
    result = run_hook(repo, specify_payload("## Feature 006: sample feature"))
    assert decision(result) is None


def test_other_feature_token_denies(repo: Path) -> None:
    """A live token for Feature 006 must not admit Feature 007."""
    (repo / ".specify" / ".ms-gate-pass-006").touch()
    result = run_hook(repo, specify_payload("## Feature 007: another feature"))
    assert decision(result) == "deny"


def test_freeform_input_denies_even_with_live_token(repo: Path) -> None:
    """Input with no identifiable Feature is freeform — always denied."""
    (repo / ".specify" / ".ms-gate-pass-006").touch()
    result = run_hook(repo, specify_payload("build me a login page"))
    assert decision(result) == "deny"


def test_unpadded_feature_number_matches_padded_token(repo: Path) -> None:
    (repo / ".specify" / ".ms-gate-pass-006").touch()
    result = run_hook(repo, specify_payload("Feature 6 spec input"))
    assert decision(result) is None
