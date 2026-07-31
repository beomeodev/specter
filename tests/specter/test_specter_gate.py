"""Tests for the lean, state-free SPECTER gate."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "docs" / "templates" / "scripts" / "specter-gate.sh"


def run_gate(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )


def output(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs/prd/checklists").mkdir(parents=True)
    (tmp_path / ".specify/memory").mkdir(parents=True)
    (tmp_path / "docs/prd/PRD.md").write_text("# PRD\n\nStore items.\n")
    feature_map = tmp_path / "docs/prd/feature-map.md"
    feature_map.write_text(
        "# Feature Map\n\n"
        "## Feature 006: Storage\n\n"
        "### In scope\n- Store items\n\n"
        "### Done criteria\n- Items persist\n- CI passes green\n"
    )
    map_sha = hashlib.sha256(feature_map.read_bytes()).hexdigest()
    (tmp_path / "docs/prd/feature-map.checklist.md").write_text(
        "**Mode**: global\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\n"
    )
    (tmp_path / ".specify/memory/constitution.md").write_text(
        "## IX. Project-Specific Constraints\n\nNone.\n"
    )
    (tmp_path / "docs/prd/checklists/feature-006.checklist.md").write_text(
        "**Mode**: per-feature\n"
        "**Feature**: Feature 006\n"
        "**Feature Map**: docs/prd/feature-map.md\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\n"
    )
    return tmp_path


def digest(repo: Path, station: str = "verify", scope: str = "006") -> str:
    result = run_gate(repo, "hash", station, scope)
    assert result.returncode == 0, result.stderr
    return str(output(result)["input_sha256"])


def write_reports(
    repo: Path,
    current_digest: str,
    first: str = "PASS",
    second: str = "PASS",
    first_availability: str | None = None,
    second_availability: str | None = None,
) -> None:
    base = repo / "docs/prd/checklists"
    for lane, result, availability in (
        ("codex", first, first_availability),
        ("antigravity", second, second_availability),
    ):
        extra = f"**Availability**: {availability}\n" if availability else ""
        (base / f"feature-006.{lane}-verify.md").write_text(
            f"**Mode**: {lane}-verify\n"
            "**Scope**: 006\n"
            f"**Input SHA256**: {current_digest}\n"
            f"**Result**: {result}\n"
            f"{extra}\n"
            "## Findings\n\nNone.\n"
        )


def test_version_is_lean_and_state_free(repo: Path) -> None:
    data = output(run_gate(repo, "version"))
    assert data == {
        "contract": "lean-verification-v1",
        "subcommands": ["hash", "reduce"],
        "stateful": False,
    }


def test_hash_tracks_inputs(repo: Path) -> None:
    before = digest(repo)
    checklist = repo / "docs/prd/checklists/feature-006.checklist.md"
    checklist.write_text(checklist.read_text() + "changed\n")
    assert digest(repo) != before


@pytest.mark.parametrize(
    ("results", "expected"),
    [
        (("PASS", "PASS"), "PASS"),
        (("PASS", "WARN"), "WARN"),
        (("PASS", "FAIL"), "FAIL"),
    ],
)
def test_reduce_uses_worst_result(
    repo: Path, results: tuple[str, str], expected: str
) -> None:
    current = digest(repo)
    write_reports(repo, current, *results)
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == expected
    assert (result.returncode == 0) is (expected != "FAIL")


def test_one_unavailable_caps_at_warn(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current, "PASS", "WARN", None, "UNAVAILABLE (binary missing)")
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == "WARN"


def test_remaining_fail_survives_unavailable_peer(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current, "FAIL", "WARN", None, "UNAVAILABLE (binary missing)")
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == "FAIL"


def test_both_unavailable_fail(repo: Path) -> None:
    current = digest(repo)
    write_reports(
        repo,
        current,
        "WARN",
        "WARN",
        "UNAVAILABLE (binary missing)",
        "UNAVAILABLE (binary missing)",
    )
    assert output(run_gate(repo, "reduce", "verify", "006"))["verdict"] == "FAIL"


def test_stale_hash_fails(repo: Path) -> None:
    write_reports(repo, "0" * 64)
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == "FAIL"
    assert "stale" in result.stdout


def test_missing_or_multiple_result_fails(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current)
    report = repo / "docs/prd/checklists/feature-006.codex-verify.md"
    report.write_text(report.read_text() + "**Result**: PASS\n")
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == "FAIL"
    assert "exactly one Result" in result.stdout


def test_wrong_report_scope_fails(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current)
    report = repo / "docs/prd/checklists/feature-006.codex-verify.md"
    report.write_text(report.read_text().replace("**Scope**: 006", "**Scope**: 007"))
    result = run_gate(repo, "reduce", "verify", "006")
    assert output(result)["verdict"] == "FAIL"
    assert "Scope does not match" in result.stdout


def test_legacy_gate_accepts_current_global_and_feature_evidence(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current)
    result = run_gate(repo, "006")
    assert result.returncode == 0
    assert output(result)["overall"] == "PASS"


def test_legacy_gate_rejects_stale_feature_map_binding(repo: Path) -> None:
    current = digest(repo)
    write_reports(repo, current)
    checklist = repo / "docs/prd/checklists/feature-006.checklist.md"
    checklist.write_text(
        checklist.read_text().replace(
            "**Feature Map SHA256**:", "**Feature Map SHA256**: stale #"
        )
    )
    result = run_gate(repo, "006")
    assert result.returncode != 0
    assert output(result)["overall"] == "FAIL"


def test_review_hash_tracks_code_but_ignores_review_outputs(repo: Path) -> None:
    spec_dir = repo / "specs/006-storage"
    spec_dir.mkdir(parents=True)
    for name in ("spec.md", "plan.md", "tasks.md"):
        (spec_dir / name).write_text(f"# {name}\n")
    (repo / "app.py").write_text("VALUE = 1\n")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-qm",
            "base",
        ],
        cwd=repo,
        check=True,
    )
    (repo / "app.py").write_text("VALUE = 2\n")
    before = digest(repo, "review", "006")
    (repo / "docs/review").mkdir()
    (repo / "docs/review/006.codex-review.md").write_text("report output\n")
    assert digest(repo, "review", "006") == before
    (repo / "app.py").write_text("VALUE = 3\n")
    assert digest(repo, "review", "006") != before
