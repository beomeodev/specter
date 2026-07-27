"""Tests for the specter-gate.sh continuity-v1 additions (2026-07-27).

Covers the C4'/C5' redesign shipped before Features 081-092: `manifest`
(gate-generated declared-coverage inventory), `continuity` (mechanical
re-round packet from immutable round archives), and the `aggregate`
extensions (--expect-protocol / --require-coverage, round archiving,
finding-lineage validation, REVERSAL / COVERAGE_BREACH routing) — see the
suseonglm repo's docs/specter-workflow-redesign.md and the two Codex reviews
it incorporates.
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

MAP = """# Feature Map

## PRD Commitment Index

| C-ID | Source PRD | Short Label | Owning Feature | Handling |
|------|-----------|-------------|----------------|----------|
| C-001 | PRD | Login | Feature 001 | Implemented |
| C-002 | PRD | Logout | Feature 002 | Implemented |

## Implementation Obligations

| D-ID | Supports | Kind | Obligation | Why necessary | Impact | Owning Feature |
|------|----------|------|------------|---------------|--------|----------------|
| D-001 | C-001 | logical-enablement | thing | because | none | Feature 001 |

## Feature 001: Auth

body

## Feature 002: Logout

body
"""

BASELINE = """# Baseline
- [ ] C001 login
- [ ] C002 logout
"""

VERIFY_KEYS = ["feature:001", "map:C-001", "obligation:D-001"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_gate(repo: Path, *args: str) -> dict:
    result = subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    prd = tmp_path / "docs" / "prd"
    (prd / "checklists").mkdir(parents=True)
    (prd / "feature-map.md").write_text(MAP)
    (prd / "featuremap-checklist.md").write_text(BASELINE)
    checklist = prd / "checklists" / "feature-001.checklist.md"
    checklist.write_text(
        "# Feature 001 Checklist\n\n"
        "**Mode**: per-feature\n"
        "**Feature**: Feature 001: Auth\n"
        "**Result**: PASS\n"
    )
    return tmp_path


def coverage_rows(keys: list[str]) -> list[str]:
    return [f"| {k} | PASS | docs/prd/feature-map.md:5 audited |" for k in keys]


def write_v2_report(
    repo: Path,
    agent: str,
    *,
    result: str = "PASS",
    protocol: str | None = "continuity-v1",
    coverage_keys: list[str] | None = None,
    coverage_extra_rows: list[str] | None = None,
    finding_rows: list[str] | None = None,
) -> Path:
    checklist = repo / "docs" / "prd" / "checklists" / "feature-001.checklist.md"
    path = repo / "docs" / "prd" / "checklists" / f"feature-001.{agent}-verify.md"
    lines = [
        "# Report",
        "",
        f"**Mode**: {agent}-per-feature-verify",
        "**Feature**: Feature 001: Auth",
        f"**Checklist SHA256**: {sha256(checklist)}",
    ]
    if protocol is not None:
        lines.append(f"**Protocol**: {protocol}")
    lines.append(f"**Result**: {result}")
    if coverage_keys is not None or coverage_extra_rows is not None:
        lines += ["", "## Coverage", "", "| Key | Result | Evidence |", "| --- | --- | --- |"]
        lines += coverage_rows(coverage_keys or [])
        lines += coverage_extra_rows or []
    lines += [
        "",
        "## Findings",
        "",
        "| ID | Predecessor | Status | Class | Severity | Finding | Evidence | Required Fix |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines += finding_rows or []
    lines += ["", "## Verdict", "", "Done."]
    path.write_text("\n".join(lines) + "\n")
    return path


def write_clean_pair(repo: Path, **kwargs) -> None:
    write_v2_report(repo, "codex", coverage_keys=VERIFY_KEYS, **kwargs)
    write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS, **kwargs)


class TestVersionCapability:
    def test_version_reports_continuity_contract(self, repo: Path) -> None:
        out = run_gate(repo, "version")
        assert out["continuity_contract"] == "continuity-v1"
        assert "manifest" in out["subcommands"]
        assert "continuity" in out["subcommands"]


class TestManifest:
    def test_pre_verify_inventory_spans_all_classes(self, repo: Path) -> None:
        out = run_gate(repo, "manifest", "pre-verify")
        assert out["verdict"] == "PASS"
        keys = set(out["keys"])
        assert {"map:C-001", "map:C-002", "baseline:C001", "baseline:C002",
                "obligation:D-001", "feature:001", "feature:002"} <= keys

    def test_verify_inventory_is_owned_subset(self, repo: Path) -> None:
        out = run_gate(repo, "manifest", "verify", "1")
        assert out["verdict"] == "PASS"
        assert sorted(out["keys"]) == VERIFY_KEYS
        assert "map:C-002" not in out["keys"]

    def test_unknown_station_fails(self, repo: Path) -> None:
        out = run_gate(repo, "manifest", "review")
        assert out["verdict"] == "FAIL"


class TestAggregateCoverage:
    def test_full_v2_pair_passes_with_required_coverage(self, repo: Path) -> None:
        write_clean_pair(repo)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "PASS"
        assert out["reversal"] is False
        assert out["coverage_breach"] is False

    def test_missing_protocol_fails_under_expectation(self, repo: Path) -> None:
        write_v2_report(repo, "codex", protocol=None, coverage_keys=VERIFY_KEYS)
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1",
        )
        assert out["verdict"] == "FAIL"
        assert any("Protocol" in r for r in out["reasons"])

    def test_missing_coverage_fails_when_required(self, repo: Path) -> None:
        write_v2_report(repo, "codex", coverage_keys=None)
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "FAIL"
        assert any("## Coverage" in r for r in out["reasons"])

    def test_coverage_set_inequality_fails(self, repo: Path) -> None:
        write_v2_report(repo, "codex", coverage_keys=["feature:001", "map:C-001", "map:C-999"])
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "FAIL"
        assert any("undeclared" in r for r in out["reasons"])
        assert any("not in the expected inventory" in r for r in out["reasons"])

    def test_unverified_coverage_row_caps_at_warn(self, repo: Path) -> None:
        write_v2_report(
            repo, "codex",
            coverage_keys=VERIFY_KEYS[1:],
            coverage_extra_rows=["| feature:001 | UNVERIFIED | tooling missing |"],
        )
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "WARN"
        assert any("UNVERIFIED" in r for r in out["reasons"])

    def test_fail_row_with_pass_result_is_inconsistent(self, repo: Path) -> None:
        write_v2_report(
            repo, "codex",
            coverage_keys=VERIFY_KEYS[1:],
            coverage_extra_rows=["| feature:001 | FAIL | broken |"],
        )
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "FAIL"
        assert any("inconsistent closure claim" in r for r in out["reasons"])

    def test_legacy_reports_still_pass_without_new_flags(self, repo: Path) -> None:
        checklist = repo / "docs" / "prd" / "checklists" / "feature-001.checklist.md"
        for agent in ("codex", "antigravity"):
            (repo / "docs" / "prd" / "checklists" / f"feature-001.{agent}-verify.md").write_text(
                "# Report\n\n"
                f"**Mode**: {agent}-per-feature-verify\n"
                "**Feature**: Feature 001: Auth\n"
                f"**Checklist SHA256**: {sha256(checklist)}\n"
                "**Result**: PASS\n\n"
                "## Findings\n\n"
                "| Severity | Finding | Evidence | Required Fix |\n"
                "| --- | --- | --- | --- |\n"
            )
        out = run_gate(repo, "aggregate", "verify", "1")
        assert out["verdict"] == "PASS"
        assert out["reasons"] == []


class TestArchiveAndContinuity:
    def test_ledger_run_archives_round_reports(self, repo: Path) -> None:
        write_clean_pair(repo)
        out = run_gate(
            repo, "aggregate", "verify", "1", "--ledger", "--round", "1",
            "--expect-protocol", "continuity-v1", "--require-coverage",
        )
        assert out["verdict"] == "PASS"
        checklists = repo / "docs" / "prd" / "checklists"
        assert (checklists / "feature-001.codex-verify.round-01.md").exists()
        assert (checklists / "feature-001.antigravity-verify.round-01.md").exists()

    def test_reused_round_number_with_changed_content_fails(self, repo: Path) -> None:
        write_clean_pair(repo)
        run_gate(repo, "aggregate", "verify", "1", "--ledger", "--round", "1",
                 "--expect-protocol", "continuity-v1")
        write_v2_report(
            repo, "codex", result="FAIL", coverage_keys=VERIFY_KEYS,
            finding_rows=["| CX-001 | none | NEW | PREVIOUSLY_UNAUDITED | HIGH | x | map:5 | fix |"],
        )
        out = run_gate(repo, "aggregate", "verify", "1", "--ledger", "--round", "1",
                       "--expect-protocol", "continuity-v1")
        assert out["verdict"] == "FAIL"
        assert any("immutable" in r for r in out["reasons"])

    def test_continuity_packet_carries_blocking_findings_verbatim(self, repo: Path) -> None:
        write_v2_report(
            repo, "codex", result="FAIL", coverage_keys=VERIFY_KEYS,
            finding_rows=["| CX-001 | none | NEW | PREVIOUSLY_UNAUDITED | HIGH | wrong owner | map:5 | move owner |"],
        )
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        run_gate(repo, "aggregate", "verify", "1", "--ledger", "--round", "1",
                 "--expect-protocol", "continuity-v1")
        out = run_gate(repo, "continuity", "verify", "1", "--round", "2")
        assert out["verdict"] == "PASS"
        assert out["rounds_archived"] == 1
        assert out["blocking_findings"] == 1
        packet = (repo / out["packet"]).read_text()
        assert "NOT a" in packet and "PASS whitelist" in packet
        assert "| CX-001 | none | NEW | PREVIOUSLY_UNAUDITED | HIGH | wrong owner | map:5 | move owner |" in packet

    def test_continuity_without_archives_reports_empty_history(self, repo: Path) -> None:
        out = run_gate(repo, "continuity", "verify", "1", "--round", "2")
        assert out["rounds_archived"] == 0
        assert any("no archived round reports" in r for r in out["reasons"])


class TestLineage:
    def _archive_round1(self, repo: Path) -> None:
        write_v2_report(
            repo, "codex", result="FAIL", coverage_keys=VERIFY_KEYS,
            finding_rows=["| CX-001 | none | NEW | PREVIOUSLY_UNAUDITED | HIGH | x | map:5 | fix |"],
        )
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        run_gate(repo, "aggregate", "verify", "1", "--ledger", "--round", "1",
                 "--expect-protocol", "continuity-v1")

    def test_reversal_is_flagged_and_routed(self, repo: Path) -> None:
        self._archive_round1(repo)
        write_v2_report(
            repo, "codex", result="FAIL",
            finding_rows=["| CX-002 | CX-001 | REOPENED | REVERSAL | HIGH | prior fix wrong | map:5 | reconcile |"],
        )
        out = run_gate(repo, "aggregate", "verify", "1", "--round", "2",
                       "--expect-protocol", "continuity-v1")
        assert out["verdict"] == "FAIL"
        assert out["reversal"] is True
        assert any("doctrine-dispute" in r for r in out["reasons"])

    def test_coverage_breach_is_flagged(self, repo: Path) -> None:
        self._archive_round1(repo)
        write_v2_report(
            repo, "codex", result="FAIL",
            finding_rows=["| CX-003 | none | NEW | COVERAGE_BREACH | HIGH | late defect | map:5 | fix + reopen class |"],
        )
        out = run_gate(repo, "aggregate", "verify", "1", "--round", "2",
                       "--expect-protocol", "continuity-v1")
        assert out["coverage_breach"] is True
        assert any("closure claim is invalidated" in r for r in out["reasons"])

    def test_unknown_predecessor_fails(self, repo: Path) -> None:
        self._archive_round1(repo)
        write_v2_report(
            repo, "codex", result="FAIL",
            finding_rows=["| CX-004 | CX-999 | REOPENED | NEW_EVIDENCE | HIGH | y | map:5 | fix |"],
        )
        out = run_gate(repo, "aggregate", "verify", "1", "--round", "2",
                       "--expect-protocol", "continuity-v1")
        assert out["verdict"] == "FAIL"
        assert any("unknown Predecessor" in r for r in out["reasons"])

    def test_missing_lineage_columns_fail_on_rerounds(self, repo: Path) -> None:
        self._archive_round1(repo)
        checklist = repo / "docs" / "prd" / "checklists" / "feature-001.checklist.md"
        (repo / "docs" / "prd" / "checklists" / "feature-001.codex-verify.md").write_text(
            "# Report\n\n"
            "**Mode**: codex-per-feature-verify\n"
            "**Feature**: Feature 001: Auth\n"
            f"**Checklist SHA256**: {sha256(checklist)}\n"
            "**Protocol**: continuity-v1\n"
            "**Result**: FAIL\n\n"
            "## Findings\n\n"
            "| Severity | Finding | Evidence | Required Fix |\n"
            "| --- | --- | --- | --- |\n"
            "| HIGH | old-style row | map:5 | fix |\n"
        )
        out = run_gate(repo, "aggregate", "verify", "1", "--round", "2",
                       "--expect-protocol", "continuity-v1")
        assert out["verdict"] == "FAIL"
        assert any("lineage columns" in r for r in out["reasons"])

    def test_invalid_class_fails_even_on_round_one(self, repo: Path) -> None:
        write_v2_report(
            repo, "codex", result="FAIL", coverage_keys=VERIFY_KEYS,
            finding_rows=["| CX-005 | none | NEW | MADE_UP_CLASS | HIGH | z | map:5 | fix |"],
        )
        write_v2_report(repo, "antigravity", coverage_keys=VERIFY_KEYS)
        out = run_gate(repo, "aggregate", "verify", "1", "--round", "1",
                       "--expect-protocol", "continuity-v1")
        assert out["verdict"] == "FAIL"
        assert any("invalid Classification" in r for r in out["reasons"])
