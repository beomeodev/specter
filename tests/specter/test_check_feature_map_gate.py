"""Tests for scripts/check_feature_map_gate.py (pre-commit Feature Map backstop).

Each test builds a throwaway git repo and drives the real staged-state checks:
the hook must block a Feature Map edit whose SHA256 is not recorded in the
checklist (i.e. the map changed without /ms.verify or /ms.expand), and stay
silent for everything else.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent / "scripts" / "check_feature_map_gate.py"
)
_spec = importlib.util.spec_from_file_location("check_feature_map_gate", MODULE_PATH)
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

FEATURE_MAP = "docs/prd/feature-map.md"
CHECKLIST = "docs/prd/feature-map.checklist.md"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@local", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    git(tmp_path, "init", "-q")
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-qm", "seed")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(repo_root: Path, relpath: str, text: str) -> None:
    path = repo_root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def checklist_for(map_text: str) -> str:
    sha = hashlib.sha256(map_text.encode("utf-8")).hexdigest()
    return f"# Checklist\n\n**Feature Map SHA256**: {sha}\n**Result**: PASS\n"


def test_commit_not_touching_map_passes(repo: Path) -> None:
    write(repo, "src.py", "x = 1\n")
    git(repo, "add", "src.py")
    assert gate.main() == 0


def test_map_staged_without_checklist_fails(repo: Path) -> None:
    write(repo, FEATURE_MAP, "# Map v1\n")
    git(repo, "add", FEATURE_MAP)
    assert gate.main() == 1


def test_map_staged_with_matching_staged_checklist_passes(repo: Path) -> None:
    map_text = "# Map v1\n"
    write(repo, FEATURE_MAP, map_text)
    write(repo, CHECKLIST, checklist_for(map_text))
    git(repo, "add", FEATURE_MAP, CHECKLIST)
    assert gate.main() == 0


def test_map_edit_with_stale_committed_checklist_fails(repo: Path) -> None:
    map_text = "# Map v1\n"
    write(repo, FEATURE_MAP, map_text)
    write(repo, CHECKLIST, checklist_for(map_text))
    git(repo, "add", FEATURE_MAP, CHECKLIST)
    git(repo, "commit", "-qm", "map v1 + checklist")

    write(repo, FEATURE_MAP, "# Map v2 (edited without /ms.verify)\n")
    git(repo, "add", FEATURE_MAP)
    assert gate.main() == 1


def test_map_edit_with_fresh_committed_checklist_passes(repo: Path) -> None:
    write(repo, FEATURE_MAP, "# Map v1\n")
    new_map = "# Map v2\n"
    write(repo, CHECKLIST, checklist_for(new_map))
    git(repo, "add", FEATURE_MAP, CHECKLIST)
    git(repo, "commit", "-qm", "v1 map, checklist pre-recording v2")

    write(repo, FEATURE_MAP, new_map)
    git(repo, "add", FEATURE_MAP)
    assert gate.main() == 0


def test_map_deletion_passes(repo: Path) -> None:
    write(repo, FEATURE_MAP, "# Map v1\n")
    git(repo, "add", FEATURE_MAP)
    git(repo, "commit", "-qm", "add map")
    git(repo, "rm", "-q", FEATURE_MAP)
    assert gate.main() == 0
