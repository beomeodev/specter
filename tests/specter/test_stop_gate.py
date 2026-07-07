"""Tests for docs/templates/scripts/specter-stop-gate.sh (Stop hook gate).

Covers the 2026-07-07 stop-gate policy: inert without a phase file, allows
unchanged trees and fresh evidence (any verdict, including FAIL), blocks
stale/missing evidence with a 3-block cap then stands down, ignores
gate-irrelevant paths (.specify/, docs/, specs/, *.md), and detects content
edits to untracked files. Hook mode must fail open outside a git repo.
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
    / "specter-stop-gate.sh"
)

PHASE_FILE = ".specify/.ms-stop-phase"
BLOCKS_FILE = ".specify/.ms-stop-blocks"


def run_gate(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the gate script inside ``repo`` (hook mode when no args)."""
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(repo)},
        input="{}",
        capture_output=True,
        text=True,
        timeout=30,
    )


def hook_decision(result: subprocess.CompletedProcess[str]) -> str | None:
    """Return the hook's decision, or None when it allowed the stop."""
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["decision"]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repo with an initial commit and one tracked source file."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.local"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "app.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)
    return tmp_path


def test_inert_without_phase_file(repo: Path) -> None:
    (repo / "app.py").write_text("x = 2\n")
    result = run_gate(repo)
    assert result.returncode == 0
    assert hook_decision(result) is None


def test_fails_open_outside_git_repo(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()
    (tmp_path / PHASE_FILE).write_text("implement\n")
    result = run_gate(tmp_path)
    assert result.returncode == 0
    assert hook_decision(result) is None


def test_allows_when_nothing_changed_since_phase_open(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    result = run_gate(repo)
    assert hook_decision(result) is None


def test_blocks_on_change_without_evidence(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "app.py").write_text("x = 2\n")
    result = run_gate(repo)
    assert hook_decision(result) == "block"
    assert "block 1/3" in json.loads(result.stdout)["reason"]
    assert (repo / BLOCKS_FILE).read_text().strip() == "1"


def test_fresh_evidence_allows_even_fail_verdict(repo: Path) -> None:
    run_gate(repo, "phase", "review")
    (repo / "app.py").write_text("x = 2\n")
    assert hook_decision(run_gate(repo)) == "block"
    record = run_gate(repo, "record", "review", "FAIL")
    assert record.returncode == 0
    result = run_gate(repo)
    assert hook_decision(result) is None
    assert not (repo / BLOCKS_FILE).exists()


def test_evidence_goes_stale_on_further_edits(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "app.py").write_text("x = 2\n")
    run_gate(repo, "record", "implement", "PASS")
    (repo / "app.py").write_text("x = 3\n")
    assert hook_decision(run_gate(repo)) == "block"


def test_untracked_content_edit_detected(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "new_module.py").write_text("y = 1\n")
    run_gate(repo, "record", "implement", "PASS")
    (repo / "new_module.py").write_text("y = 2\n")
    assert hook_decision(run_gate(repo)) == "block"


def test_gate_irrelevant_paths_do_not_trigger(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("d\n")
    (repo / "specs").mkdir()
    (repo / "specs" / "spec.txt").write_text("s\n")
    (repo / "README.md").write_text("m\n")
    result = run_gate(repo)
    assert hook_decision(result) is None


def test_three_block_cap_then_stands_down(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "app.py").write_text("x = 2\n")
    reasons = [json.loads(run_gate(repo).stdout)["reason"] for _ in range(3)]
    assert "block 1/3" in reasons[0]
    assert "block 2/3" in reasons[1]
    assert "final block 3/3" in reasons[2]
    assert "stop attempting further fixes" in reasons[2]
    fourth = run_gate(repo)
    assert hook_decision(fourth) is None
    assert not (repo / BLOCKS_FILE).exists()


def test_phase_clear_removes_state(repo: Path) -> None:
    run_gate(repo, "phase", "implement")
    (repo / "app.py").write_text("x = 2\n")
    run_gate(repo)
    result = run_gate(repo, "phase", "clear")
    assert result.returncode == 0
    assert not (repo / PHASE_FILE).exists()
    assert not (repo / BLOCKS_FILE).exists()
    assert hook_decision(run_gate(repo)) is None


def test_record_rejects_invalid_arguments(repo: Path) -> None:
    assert run_gate(repo, "record", "implement", "MAYBE").returncode == 1
    assert run_gate(repo, "record", "deploy", "PASS").returncode == 1
    assert run_gate(repo, "bogus").returncode == 1
