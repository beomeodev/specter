"""Tests for docs/templates/scripts/specter-gate.sh under verification-v2.

Contract: docs/design/verification-v2.md. This suite is the seeded-defect
corpus from that design's §6 replay plan, expressed as fixtures: stale input
digest, wrong station Mode/Scope, malformed report, degrade placeholders,
over-budget rounds, false prose triggers that must NOT escalate, and the
deterministic diff facts that MUST.

Replaces the retired v1 suites (test_specter_gate.py,
test_specter_gate_subcommands.py, test_specter_gate_continuity.py,
test_audit_tier.py); still-live v1 behaviors (octal Feature numbers,
split-slate map pinning) are ported here.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "docs" / "templates" / "scripts" / "specter-gate.sh"
CONFIG = ROOT / "docs" / "templates" / "verification-v2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_gate(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(repo),
            "GIT_CONFIG_NOSYSTEM": "1",
        },
        capture_output=True,
        text=True,
        timeout=30,
    )


def gate_json(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=repo,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(repo),
            "GIT_CONFIG_NOSYSTEM": "1",
        },
        capture_output=True,
        check=True,
        timeout=30,
    )


SIGNAL_ROWS_ALL_NO = "\n".join(
    f"| {sig} | no | docs/PRD.md:12 |"
    for sig in (
        "authorization",
        "secrets",
        "data-migration",
        "destructive-data",
        "irreversible-operation",
        "public-contract",
        "financial-or-regulated",
        "gate-or-policy-change",
    )
)


def feature_section(feature: str, signal_rows: str | None) -> str:
    signals = ""
    if signal_rows is not None:
        signals = (
            "### Verification signals\n\n"
            "| Signal | Value | Evidence |\n"
            "| --- | --- | --- |\n"
            f"{signal_rows}\n\n"
        )
    return (
        f"## Feature {feature}: Storage\n\n"
        "### Source PRDs\n- docs/PRD.md\n\n"
        "### PRD references\n- C-001\n\n"
        "### In scope\n- Storage layer\n\n"
        "### Explicitly out of scope\n- None\n\n"
        "### Key decisions\n- JSON file store\n\n"
        f"{signals}"
        "### Done criteria\n- Store works\n- CI passes green\n"
    )


def make_repo(
    tmp_path: Path,
    feature: str = "006",
    signal_rows: str | None = SIGNAL_ROWS_ALL_NO,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "prd" / "checklists").mkdir(parents=True)
    (repo / "docs" / "templates").mkdir(parents=True)
    shutil.copy(CONFIG, repo / "docs" / "templates" / "verification-v2.json")
    (repo / "docs" / "prd" / "feature-map.md").write_text(
        "# Feature Map\n\n"
        "## PRD Commitment Index\n\n"
        "| # | Source PRD | Commitment | Evidence | ID | Owning Feature |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| 1 | docs/PRD.md | Store todos | docs/PRD.md:10 | C-001 | Feature {feature} |\n\n"
        + feature_section(feature, signal_rows)
    )
    (repo / "docs" / "prd" / "featuremap-checklist.md").write_text(
        "**Mode**: prd-only\nC-001 store todos\n"
    )
    (repo / "docs" / "prd" / f"checklists/feature-{feature}.checklist.md").write_text(
        "**Mode**: per-feature\n"
        f"**Feature**: Feature {feature}\n"
        "**Result**: PASS\n"
    )
    return repo


def digest_of(repo: Path, station: str, arg: str) -> str:
    data = gate_json(run_gate(repo, "digest", station, arg))
    assert data["verdict"] == "PASS", data["reasons"]
    return data["input_digest"]


VERIFY_MODES = ("codex-per-feature-verify", "antigravity-per-feature-verify")


def report_body(
    mode: str,
    scope: str,
    digest: str,
    result: str = "PASS",
    *,
    contract: str = "verification-v2",
    availability: str | None = None,
    findings: str = "",
    checked: str = "commitments C-001 (docs/prd/feature-map.md:8)",
    not_checked: str = "none - all owned commitments examined",
) -> str:
    avail = f"**Availability**: {availability}\n" if availability else ""
    return (
        "# Report\n\n"
        f"**Contract**: {contract}\n"
        f"**Mode**: {mode}\n"
        f"**Scope**: {scope}\n"
        f"**Input Digest**: {digest}\n"
        f"**Result**: {result}\n"
        f"{avail}\n"
        "## Scope and evidence\n"
        f"**Checked**: {checked}\n"
        f"**Not checked**: {not_checked}\n\n"
        "## Findings\n"
        "| ID | Severity | State | Finding | Evidence | Required Fix |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"{findings}"
        "\n## Verdict\n"
        "Done.\n"
    )


def write_verify_reports(
    repo: Path,
    feature: str,
    digest: str,
    *,
    round_no: int = 1,
    results: tuple[str, str] = ("PASS", "PASS"),
    findings: tuple[str, str] = ("", ""),
) -> None:
    base = repo / "docs" / "prd" / "checklists"
    for lane, mode, result, rows in zip(
        ("codex", "antigravity"), VERIFY_MODES, results, findings, strict=True
    ):
        (base / f"feature-{feature}.{lane}-verify.r{round_no}.md").write_text(
            report_body(mode, f"Feature {feature}", digest, result, findings=rows)
        )


# ---------------------------------------------------------------- version


def test_version_reports_v2_contract(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    data = gate_json(run_gate(repo, "version"))
    assert data["contract"] == "verification-v2"
    assert "aggregate" in data["subcommands"]
    assert "decide" in data["subcommands"]
    assert "manifest" not in data["subcommands"]
    assert "continuity" not in data["subcommands"]


# ---------------------------------------------------------------- digest


def test_digest_is_stable_and_tracks_artifact_changes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    d1 = digest_of(repo, "verify", "006")
    assert d1 == digest_of(repo, "verify", "006")
    checklist = repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md"
    checklist.write_text(checklist.read_text() + "\nedited\n")
    assert digest_of(repo, "verify", "006") != d1


def test_digest_missing_artifact_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md").unlink()
    data = gate_json(run_gate(repo, "digest", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("missing digest artifact" in r for r in data["reasons"])


# ---------------------------------------------------------------- validate-report


def test_validate_report_accepts_a_valid_report(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(
        run_gate(
            repo,
            "validate-report",
            "docs/prd/checklists/feature-006.codex-verify.r1.md",
            "verify",
            "006",
        )
    )
    assert data["valid"] is True, data["errors"]


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda t: t.replace("**Contract**: verification-v2\n", ""), "Contract"),
        (lambda t: t.replace("codex-per-feature-verify", "wrong-mode"), "Mode"),
        (lambda t: t + "**Result**: PASS\n", "exactly one Result"),
        (lambda t: t.replace("**Result**: PASS", "**Result**: MAYBE"), "invalid Result"),
        (lambda t: t.replace("**Checked**:", "**Chekked**:"), "Checked"),
        (lambda t: t.replace("**Not checked**:", "**Not chekked**:"), "Not checked"),
        (lambda t: t.replace("**Input Digest**", "**Digest**"), "Input Digest"),
    ],
)
def test_validate_report_rejects_format_defects(
    tmp_path: Path, mutation, expected_error: str
) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    rpt = repo / "docs" / "prd" / "checklists" / "feature-006.codex-verify.r1.md"
    rpt.write_text(mutation(rpt.read_text()))
    data = gate_json(
        run_gate(
            repo,
            "validate-report",
            "docs/prd/checklists/feature-006.codex-verify.r1.md",
            "verify",
            "006",
        )
    )
    assert data["valid"] is False
    assert any(expected_error in e for e in data["errors"]), data["errors"]


def test_validate_report_placeholder_skips_body_sections(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    rpt = repo / "docs" / "prd" / "checklists" / "feature-006.codex-verify.r1.md"
    rpt.write_text(
        "# Placeholder\n\n"
        "**Contract**: verification-v2\n"
        "**Mode**: codex-per-feature-verify\n"
        "**Scope**: Feature 006\n"
        f"**Input Digest**: {digest}\n"
        "**Result**: WARN\n"
        "**Availability**: UNAVAILABLE (binary not on PATH)\n"
    )
    data = gate_json(
        run_gate(
            repo,
            "validate-report",
            "docs/prd/checklists/feature-006.codex-verify.r1.md",
            "verify",
            "006",
        )
    )
    assert data["valid"] is True, data["errors"]


def test_validate_report_rejects_malformed_findings_row(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(
        repo,
        "006",
        digest,
        findings=("| CX-1 | HIGH | broken row |\n", ""),
    )
    data = gate_json(
        run_gate(
            repo,
            "validate-report",
            "docs/prd/checklists/feature-006.codex-verify.r1.md",
            "verify",
            "006",
        )
    )
    assert data["valid"] is False
    assert any("6 columns" in e for e in data["errors"])


# ---------------------------------------------------------------- aggregate: grading


def test_aggregate_both_pass(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--ledger"))
    assert data["verdict"] == "PASS"
    assert data["risk_profile"] == "ordinary"
    assert data["receipt_written"] is True
    assert data["ledger_written"] is True
    receipt = json.loads(
        (repo / ".specify" / "verification-v2" / "verify-006.json").read_text()
    )
    assert receipt["verdict"] == "PASS"
    assert receipt["input_digest"] == digest
    ledger = (repo / ".specify" / "specter-run.jsonl").read_text().strip().splitlines()
    line = json.loads(ledger[-1])
    assert line["contract"] == "verification-v2"
    assert line["step"] == "verify"
    assert line["round"] == 1


def test_aggregate_worst_of_wins_and_catches_verbatim(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    row = "| AG-V-001 | HIGH | NEW | missing C-001 | map:12 | restore C-001 row |\n"
    write_verify_reports(
        repo, "006", digest, results=("PASS", "FAIL"), findings=("", row)
    )
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--ledger"))
    assert data["verdict"] == "FAIL"
    assert any("AG-V-001" in c for c in data["caught"])
    line = json.loads(
        (repo / ".specify" / "specter-run.jsonl").read_text().strip().splitlines()[-1]
    )
    assert any("AG-V-001" in c for c in line["caught"])


def test_aggregate_missing_report_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    (repo / "docs/prd/checklists/feature-006.antigravity-verify.r1.md").unlink()
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("missing or empty report" in r for r in data["reasons"])


def test_aggregate_rejects_stale_digest(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    checklist = repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md"
    checklist.write_text(checklist.read_text() + "\nedited after review\n")
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("stale Input Digest" in r for r in data["reasons"])


def test_aggregate_rejects_wrong_scope_and_wrong_contract(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    base = repo / "docs" / "prd" / "checklists"
    codex = base / "feature-006.codex-verify.r1.md"
    codex.write_text(codex.read_text().replace("Feature 006", "Feature 007"))
    agy = base / "feature-006.antigravity-verify.r1.md"
    agy.write_text(agy.read_text().replace("verification-v2", "continuity-v1"))
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("Scope" in r and "007" in r for r in data["reasons"])
    assert any("Contract" in r for r in data["reasons"])


def test_aggregate_host_cannot_select_inputs(tmp_path: Path) -> None:
    """The station name fixes the report set; an extra positional is not a path."""
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(
        run_gate(repo, "aggregate", "verify", "006", "some/other/report.md")
    )
    # The stray argument is ignored (first positional wins); inputs stay fixed.
    assert [i["path"] for i in data["inputs"]] == [
        "docs/prd/checklists/feature-006.codex-verify.r1.md",
        "docs/prd/checklists/feature-006.antigravity-verify.r1.md",
    ]


# ---------------------------------------------------------------- aggregate: degrade


def test_single_placeholder_caps_at_warn(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    agy = repo / "docs/prd/checklists/feature-006.antigravity-verify.r1.md"
    agy.write_text(
        report_body(
            VERIFY_MODES[1],
            "Feature 006",
            digest,
            "WARN",
            availability="UNAVAILABLE (auth token expired)",
        )
    )
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "WARN"
    assert data["cap"] == "single-agent-degrade"


def test_both_placeholders_fail_no_host_only_verdict(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    for lane, mode in zip(("codex", "antigravity"), VERIFY_MODES, strict=True):
        (repo / f"docs/prd/checklists/feature-006.{lane}-verify.r1.md").write_text(
            report_body(
                mode,
                "Feature 006",
                digest,
                "WARN",
                availability="UNAVAILABLE (down)",
            )
        )
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("no independent verifier" in r for r in data["reasons"])


def test_placeholder_with_pass_result_is_agent_authored_failure(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    agy = repo / "docs/prd/checklists/feature-006.antigravity-verify.r1.md"
    agy.write_text(
        report_body(
            VERIFY_MODES[1],
            "Feature 006",
            digest,
            "PASS",
            availability="UNAVAILABLE (down)",
        )
    )
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("malformed Availability" in r for r in data["reasons"])


# ---------------------------------------------------------------- round budget


def test_round_2_needs_no_decision(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest, round_no=2)
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--round", "2"))
    assert data["verdict"] == "PASS"
    assert data.get("over_budget") is not True


@pytest.mark.parametrize("round_no", ["3", "28"])
def test_over_budget_rounds_are_refused_before_reading_reports(
    tmp_path: Path, round_no: str
) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest, round_no=int(round_no))
    data = gate_json(
        run_gate(repo, "aggregate", "verify", "006", "--round", round_no)
    )
    assert data["verdict"] == "FAIL"
    assert data["over_budget"] is True
    # Refused BEFORE grading: no inputs array in the over-budget receipt.
    assert "inputs" not in data


def test_authorized_round_3_proceeds(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest, round_no=3)
    decide = gate_json(
        run_gate(
            repo,
            "decide",
            "authorize-round",
            "verify",
            "006",
            "--round",
            "3",
            "--reason",
            "doctrine dispute round",
        )
    )
    assert decide["event_written"] is True
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--round", "3"))
    assert data.get("over_budget") is not True
    assert data["verdict"] == "PASS"


def test_authorization_is_round_specific(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest, round_no=4)
    gate_json(
        run_gate(
            repo,
            "decide",
            "authorize-round",
            "verify",
            "006",
            "--round",
            "3",
            "--reason",
            "round 3 only",
        )
    )
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--round", "4"))
    assert data["over_budget"] is True


# ---------------------------------------------------------------- decide


def test_decide_rejects_unknown_type_and_missing_reason(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    data = gate_json(run_gate(repo, "decide", "lower-verdict", "verify", "006",
                              "--reason", "nope"))
    assert data["verdict"] == "FAIL"
    assert data["event_written"] is False
    data = gate_json(run_gate(repo, "decide", "accept-warn", "verify", "006"))
    assert data["verdict"] == "FAIL"
    assert any("--reason" in r for r in data["reasons"])


# ---------------------------------------------------------------- risk profile


def test_declared_yes_signal_is_high_risk(tmp_path: Path) -> None:
    rows = SIGNAL_ROWS_ALL_NO.replace(
        "| authorization | no |", "| authorization | yes |"
    )
    repo = make_repo(tmp_path, signal_rows=rows)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["risk_profile"] == "high-risk"
    assert {"signal": "authorization", "source": "docs/PRD.md:12"} in data[
        "risk_evidence"
    ]


def test_missing_signals_table_is_high_risk_legacy(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, signal_rows=None)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(run_gate(repo, "aggregate", "verify", "006"))
    assert data["risk_profile"] == "high-risk"
    assert any(
        e["signal"] == "legacy-missing-signals-table" for e in data["risk_evidence"]
    )


def test_manual_raise_is_upward_only_flag(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    data = gate_json(run_gate(repo, "aggregate", "verify", "006", "--raise-risk"))
    assert data["risk_profile"] == "high-risk"
    assert any(e["signal"] == "manual-raise" for e in data["risk_evidence"])


def test_structural_rejects_malformed_signals(tmp_path: Path) -> None:
    rows = SIGNAL_ROWS_ALL_NO.replace(
        "| data-migration | no |", "| data-migration | maybe |"
    )
    repo = make_repo(tmp_path, signal_rows=rows)
    data = gate_json(run_gate(repo, "structural", "006"))
    assert data["verdict"] == "FAIL"
    assert data["checks"]["verification_signals_ok"] is False


def test_structural_rejects_unknown_signal_name(tmp_path: Path) -> None:
    rows = SIGNAL_ROWS_ALL_NO + "\n| state-machine | yes | docs/PRD.md:9 |"
    repo = make_repo(tmp_path, signal_rows=rows)
    data = gate_json(run_gate(repo, "structural", "006"))
    assert data["verdict"] == "FAIL"
    assert any("unknown Verification signal" in r for r in data["reasons"])


# ---------------------------------------------------------------- review: diff facts


def make_review_repo(tmp_path: Path, signal_rows: str | None = SIGNAL_ROWS_ALL_NO) -> Path:
    repo = make_repo(tmp_path, signal_rows=signal_rows)
    (repo / "docs" / "review").mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "baseline")
    return repo


def write_review_reports(repo: Path, spec_id: str, digest: str) -> None:
    modes = ("codex-adversarial-code-review", "antigravity-adversarial-code-review")
    feature = f"Feature {spec_id[:3]}"
    for lane, mode in zip(("codex", "antigravity"), modes, strict=True):
        (repo / "docs" / "review" / f"{spec_id}.{lane}-review.r1.md").write_text(
            report_body(mode, feature, digest)
        )


def test_review_clean_diff_is_ordinary(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src" / "store.py").write_text("def load():\n    return []\n")
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["verdict"] == "PASS"
    assert data["risk_profile"] == "ordinary"


def test_review_false_prose_triggers_do_not_escalate(tmp_path: Path) -> None:
    """The v1 killers — 'CI', 'retry', 'source of truth' in prose — stay ordinary."""
    repo = make_review_repo(tmp_path)
    (repo / "notes.md").write_text(
        "CI passes green. We retry on failure. This file is the source of truth.\n"
        "Concurrency, queue, lease, state machine, reconciliation, permission.\n"
    )
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["risk_profile"] == "ordinary", data["risk_evidence"]


def test_review_migration_path_fact_is_high_risk(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    mig = repo / "db" / "migrations"
    mig.mkdir(parents=True)
    (mig / "001_init.sql").write_text("CREATE TABLE todos (id INTEGER);\n")
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["risk_profile"] == "high-risk"
    classes = {e["signal"] for e in data["risk_evidence"]}
    assert "data-migration" in classes


def test_review_ddl_content_fact_is_high_risk(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    (repo / "setup.py").write_text('SQL = "DROP TABLE users"\n')
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["risk_profile"] == "high-risk"
    classes = {e["signal"] for e in data["risk_evidence"]}
    assert "destructive-data" in classes


def test_review_gate_machinery_diff_is_high_risk(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    hook_dir = repo / ".claude" / "commands"
    hook_dir.mkdir(parents=True)
    (hook_dir / "ms.verify.md").write_text("edited gate command\n")
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["risk_profile"] == "high-risk"
    classes = {e["signal"] for e in data["risk_evidence"]}
    assert "gate-or-policy-change" in classes


def test_review_diff_change_stales_reports(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    (repo / "sneaky.py").write_text("added after review\n")
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    assert data["verdict"] == "FAIL"
    assert any("stale Input Digest" in r for r in data["reasons"])


def test_review_required_acks_roundtrip(tmp_path: Path) -> None:
    repo = make_review_repo(tmp_path)
    mig = repo / "db" / "migrations"
    mig.mkdir(parents=True)
    (mig / "001_init.sql").write_text("CREATE TABLE todos (id INTEGER);\n")
    digest = digest_of(repo, "review", "006-storage")
    write_review_reports(repo, "006-storage", digest)
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    acks = {a["class"]: a for a in data["required_acks"]}
    assert acks["data-migration"]["satisfied"] is False
    assert data["acks_satisfied"] is False
    gate_json(
        run_gate(
            repo,
            "decide",
            "ack-migration",
            "review",
            "006",
            "--reason",
            "rollback story reviewed",
        )
    )
    data = gate_json(run_gate(repo, "aggregate", "review", "006-storage"))
    acks = {a["class"]: a for a in data["required_acks"]}
    assert acks["data-migration"]["satisfied"] is True
    assert data["acks_satisfied"] is True


# ---------------------------------------------------------------- expand


def test_expand_missing_baseline_is_warn_cap(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "expand", "2")
    (repo / "docs/prd/feature-map.delta-2.antigravity-verify.r1.md").write_text(
        report_body("antigravity-delta-verify", "Amendment 2", digest)
    )
    data = gate_json(run_gate(repo, "aggregate", "expand", "2"))
    assert data["verdict"] == "WARN"
    assert data["cap"] == "missing-baseline"


# ---------------------------------------------------------------- legacy gate probe


def add_global_pass_fixture(repo: Path) -> None:
    map_sha = sha256(repo / "docs" / "prd" / "feature-map.md")
    (repo / "docs" / "prd" / "feature-map.checklist.md").write_text(
        "**Mode**: global\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\n"
    )
    memory = repo / ".specify" / "memory"
    memory.mkdir(parents=True, exist_ok=True)
    (memory / "constitution.md").write_text(
        "## IX. Project-Specific Constraints\n\nestablished content\n"
    )
    checklist = repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md"
    checklist.write_text(
        "**Mode**: per-feature\n"
        "**Feature**: Feature 006\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\n"
    )


def test_legacy_gate_requires_verify_receipt(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    add_global_pass_fixture(repo)
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "MISSING"
    assert data["checks"]["verify_receipt_exists"] is False


def test_legacy_gate_passes_with_fresh_pass_receipt(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    add_global_pass_fixture(repo)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    gate_json(run_gate(repo, "aggregate", "verify", "006"))
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "PASS", data["reasons"]
    assert data["checks"]["verify_receipt_verdict_ok"] is True
    assert data["checks"]["verify_receipt_fresh"] is True


def test_legacy_gate_detects_stale_receipt(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    add_global_pass_fixture(repo)
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    gate_json(run_gate(repo, "aggregate", "verify", "006"))
    checklist = repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md"
    map_sha = sha256(repo / "docs" / "prd" / "feature-map.md")
    checklist.write_text(
        "**Mode**: per-feature\n"
        "**Feature**: Feature 006\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\nedited after verify\n"
    )
    data = gate_json(run_gate(repo, "006"))
    assert data["overall"] == "FAIL"
    assert data["checks"]["verify_receipt_fresh"] is False


def test_legacy_gate_octal_feature_number(tmp_path: Path) -> None:
    """Ported v1 regression: '069' must not be parsed as octal."""
    repo = make_repo(tmp_path, feature="069")
    add_global_pass_fixture(repo)
    checklist = repo / "docs" / "prd" / "checklists" / "feature-069.checklist.md"
    map_sha = sha256(repo / "docs" / "prd" / "feature-map.md")
    checklist.write_text(
        "**Mode**: per-feature\n"
        "**Feature**: Feature 069\n"
        f"**Feature Map SHA256**: {map_sha}\n"
        "**Result**: PASS\n"
    )
    # Fixture helper wrote feature-006 files; 069 needs its own checklist only.
    digest = digest_of(repo, "verify", "69")
    base = repo / "docs" / "prd" / "checklists"
    for lane, mode in zip(("codex", "antigravity"), VERIFY_MODES, strict=True):
        (base / f"feature-069.{lane}-verify.r1.md").write_text(
            report_body(mode, "Feature 069", digest)
        )
    agg = gate_json(run_gate(repo, "aggregate", "verify", "69"))
    assert agg["verdict"] == "PASS"
    data = gate_json(run_gate(repo, "69"))
    assert data["checks"]["verify_receipt_verdict_ok"] is True


def test_legacy_gate_split_slate_map_pinning(tmp_path: Path) -> None:
    """Ported v1 regression: a checklist pinning its own map file is hashed
    against that file, not the master map."""
    repo = make_repo(tmp_path)
    add_global_pass_fixture(repo)
    slate = repo / "docs" / "prd" / "feature-map_006_frozen.md"
    slate.write_text("frozen slate content\n")
    checklist = repo / "docs" / "prd" / "checklists" / "feature-006.checklist.md"
    checklist.write_text(
        "**Mode**: per-feature\n"
        "**Feature**: Feature 006\n"
        f"**Feature Map**: docs/prd/feature-map_006_frozen.md\n"
        f"**Feature Map SHA256**: {sha256(slate)}\n"
        "**Result**: PASS\n"
    )
    digest = digest_of(repo, "verify", "006")
    write_verify_reports(repo, "006", digest)
    gate_json(run_gate(repo, "aggregate", "verify", "006"))
    data = gate_json(run_gate(repo, "006"))
    assert data["checks"]["feature_checklist_sha_ok"] is True
    assert data["overall"] == "PASS", data["reasons"]


# ---------------------------------------------------------------- pre-verify


def test_pre_verify_global_station(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    digest = digest_of(repo, "pre-verify", "")
    modes = ("codex-global-verify", "antigravity-global-verify")
    for lane, mode in zip(("codex", "antigravity"), modes, strict=True):
        (repo / f"docs/prd/feature-map.{lane}-verify.r1.md").write_text(
            report_body(mode, "global", digest)
        )
    data = gate_json(run_gate(repo, "aggregate", "pre-verify"))
    assert data["verdict"] == "PASS"
    assert data["scope"] == "global"
