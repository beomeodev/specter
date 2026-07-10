"""Tests for docs/templates/scripts/specter-gate.sh (deterministic gate checker).

Covers the 2026-07-10 false-FAIL fixes found in the suseonglm/atlas transcript
audit: Feature numbers with a leading zero and a 8/9 digit ("069") must not be
parsed as octal, and a per-feature checklist that pins a split-slate map via its
``**Feature Map**:`` field must be hashed against that file, not the master
``docs/prd/feature-map.md``.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "templates"
    / "scripts"
    / "specter-gate.sh"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_gate(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )


def gate_json(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def write_feature_files(
    repo: Path, feature: str, *, map_field: str | None, sha: str
) -> None:
    checklists = repo / "docs" / "prd" / "checklists"
    checklists.mkdir(parents=True, exist_ok=True)
    map_line = f"**Feature Map**: {map_field}\n" if map_field else ""
    (checklists / f"feature-{feature}.checklist.md").write_text(
        f"# Feature {feature} Checklist\n\n"
        f"**Mode**: per-feature\n"
        f"**Feature**: Feature {feature}: sample feature\n"
        f"{map_line}"
        f"**Feature Map SHA256**: {sha}\n"
        f"**Result**: PASS\n"
    )
    for agent in ("codex", "antigravity"):
        (checklists / f"feature-{feature}.{agent}-verify.md").write_text(
            f"# {agent} verify\n\n**Result**: PASS\n"
        )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A project tree where the global gate and Constitution baseline pass."""
    prd = tmp_path / "docs" / "prd"
    prd.mkdir(parents=True)
    master_map = prd / "feature-map.md"
    master_map.write_text("# Feature Map\n\nmaster slate\n")
    (prd / "feature-map.checklist.md").write_text(
        "# Global Checklist\n\n"
        "**Mode**: global\n"
        f"**Feature Map SHA256**: {sha256(master_map)}\n"
        "**Result**: PASS\n"
    )
    memory = tmp_path / ".specify" / "memory"
    memory.mkdir(parents=True)
    (memory / "constitution.md").write_text(
        "## IX. Project-Specific Constraints\n\n- Established constraint.\n"
    )
    return tmp_path


def test_global_gate_passes(repo: Path) -> None:
    data = gate_json(run_gate(repo))
    assert data["overall"] == "PASS"
    assert data["reasons"] == []


def test_feature_number_with_leading_zero_and_high_digit(repo: Path) -> None:
    """"069" must be treated as decimal 69, not an invalid octal literal."""
    write_feature_files(
        repo, "069", map_field=None, sha=sha256(repo / "docs/prd/feature-map.md")
    )
    data = gate_json(run_gate(repo, "069"))
    assert data["feature"] == "069"
    assert data["overall"] == "PASS"


def test_split_slate_feature_map_is_hashed_not_master(repo: Path) -> None:
    """A checklist pinning its own split map must not FAIL against master."""
    split_map = repo / "docs" / "prd" / "feature-map_006_sample.md"
    split_map.write_text("# Feature Map (006 split slate)\n\nseparate set\n")
    write_feature_files(
        repo,
        "006",
        map_field=(
            "docs/prd/feature-map_006_sample.md "
            "(separate-set; master feature-map.md frozen)"
        ),
        sha=sha256(split_map),
    )
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "PASS"
    assert data["checks"]["feature_checklist_sha_ok"] is True


def test_master_map_feature_still_passes(repo: Path) -> None:
    """Checklists without a **Feature Map** field keep the master-map hash."""
    write_feature_files(
        repo, "006", map_field=None, sha=sha256(repo / "docs/prd/feature-map.md")
    )
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "PASS"


def test_stale_split_slate_sha_still_fails(repo: Path) -> None:
    """The split-map fix must not weaken the gate: a stale SHA still FAILs."""
    split_map = repo / "docs" / "prd" / "feature-map_006_sample.md"
    split_map.write_text("# Feature Map (006 split slate)\n\nseparate set\n")
    write_feature_files(
        repo,
        "006",
        map_field="docs/prd/feature-map_006_sample.md (separate-set)",
        sha="0" * 64,
    )
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "FAIL"
    assert any("SHA256 stale" in r for r in data["reasons"])


def test_missing_split_slate_map_reports_missing(repo: Path) -> None:
    write_feature_files(
        repo,
        "006",
        map_field="docs/prd/feature-map_006_sample.md (separate-set)",
        sha="0" * 64,
    )
    (repo / "docs/prd/feature-map_006_sample.md").unlink(missing_ok=True)
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "MISSING"
    assert any("feature-map_006_sample.md" in r for r in data["reasons"])
