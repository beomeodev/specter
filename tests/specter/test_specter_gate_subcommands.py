"""Tests for the specter-gate.sh v3 subcommands (three-layer + audit tiers).

Covers the 2026-07-19 three-layer adoption (Codex-reviewed): `version`
capability probe, `structural` Layer-1 deterministic checks, and `aggregate`
Layer-3 verdict aggregation with the typed degrade contract and mechanical
ledger emission (specter-agent-protocols §7).
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

GOOD_MAP = """# Feature Map

## PRD Commitment Index

| Source PRD | PRD Ref | Commitment Type | Short Label | Owning Feature | Handling |
|------------|---------|-----------------|-------------|----------------|----------|
| Product PRD | §3.1 | Functional | User login | Feature 001 | Implemented |
| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |

> Progress Ledger: docs/prd/feature-map.progress.md

---
## Feature 001: Auth engine

### One-line summary
Auth.

### Source PRDs
- Product PRD: docs/prd/PRD.md

### PRD references
- Product PRD §3.1 login

### In scope
**Core**
- login endpoint
**Tests**
- login test

### Explicitly out of scope
- logout UI → 002

### Key decisions
- JWT

### Done criteria
- login works
- CI passes green
---
## Feature 002: Logout

### One-line summary
Logout.

### Source PRDs
- Product PRD: docs/prd/PRD.md

### PRD references
- Product PRD §3.2 logout

### In scope
**Core**
- logout endpoint
**Tests**
- logout test

### Explicitly out of scope
- None

### Key decisions
- reuse JWT

### Done criteria
- logout works
- CI passes green
---
"""

GOOD_PROGRESS = """# Feature Map Progress Ledger

| Feature | Depends on | Status |
|---------|------------|--------|
| 001 Auth engine | — | ⬜ planned |
| 002 Logout | 001 | ⬜ planned |
"""


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
    (prd / "codex").mkdir(parents=True)
    (prd / "feature-map.md").write_text(GOOD_MAP)
    (prd / "feature-map.progress.md").write_text(GOOD_PROGRESS)
    return tmp_path


def write_report(
    path: Path,
    *,
    mode: str,
    feature: str | None = "006",
    sha_field: str | None = None,
    sha_value: str = "",
    result: str = "PASS",
    availability: str | None = None,
    findings: list[str] | None = None,
    extra_result_line: bool = False,
) -> None:
    lines = ["# Report\n", f"**Mode**: {mode}"]
    if feature is not None:
        lines.append(f"**Feature**: Feature {feature}: sample")
    if sha_field is not None:
        lines.append(f"**{sha_field}**: {sha_value}")
    lines.append(f"**Result**: {result}")
    if extra_result_line:
        lines.append(f"**Result**: {result}")
    if availability is not None:
        lines.append(f"**Availability**: {availability}")
    if findings:
        lines.append("\n## Findings\n")
        lines.append("| Severity | Finding | Evidence | Required Fix |")
        lines.append("| --- | --- | --- | --- |")
        lines.extend(findings)
    path.write_text("\n".join(lines) + "\n")


def write_agent_verify_pair(
    repo: Path,
    *,
    codex_result: str = "PASS",
    anti_result: str = "PASS",
    codex_availability: str | None = None,
    anti_availability: str | None = None,
    anti_findings: list[str] | None = None,
) -> Path:
    checklists = repo / "docs" / "prd" / "checklists"
    checklist = checklists / "feature-006.checklist.md"
    checklist.write_text(
        "# Feature 006 Checklist\n\n"
        "**Mode**: per-feature\n"
        "**Feature**: Feature 006: sample\n"
        "**Result**: PASS\n"
    )
    csha = sha256(checklist)
    write_report(
        checklists / "feature-006.codex-verify.md",
        mode="codex-per-feature-verify",
        sha_field="Checklist SHA256",
        sha_value=csha,
        result=codex_result,
        availability=codex_availability,
    )
    write_report(
        checklists / "feature-006.antigravity-verify.md",
        mode="antigravity-per-feature-verify",
        sha_field="Checklist SHA256",
        sha_value=csha,
        result=anti_result,
        availability=anti_availability,
        findings=anti_findings,
    )
    return checklist


class TestVersion:
    def test_version_probe(self, repo: Path) -> None:
        data = run_gate(repo, "version")
        assert data["contract"] == "three-layer-v2-audit-tier"
        assert data["audit_tier_contract"] == "audit-tier-v1"
        assert "aggregate" in data["subcommands"]
        assert "structural" in data["subcommands"]


class TestStructural:
    def test_well_formed_map_passes(self, repo: Path) -> None:
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["reasons"] == []

    def test_dag_cycle_fails(self, repo: Path) -> None:
        progress = repo / "docs" / "prd" / "feature-map.progress.md"
        progress.write_text(
            GOOD_PROGRESS.replace(
                "| 001 Auth engine | — |", "| 001 Auth engine | 002 |"
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["dag_acyclic"] is False
        assert any("cycle" in r for r in data["reasons"])

    def test_placeholder_in_done_criteria_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- login works", "- login works TODO"))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["placeholders_clean"] is False

    def test_placeholder_outside_done_criteria_warns(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- login endpoint", "- login endpoint TBD"))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "WARN"
        assert data["checks"]["placeholders_clean"] is False

    def test_missing_ci_green_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace("- login works\n- CI passes green", "- login works")
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("CI passes green" in r for r in data["reasons"])

    def test_commitment_row_without_owner_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace("| Feature 002 | Implemented |", "|  | Implemented |")
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["commitment_index_ok"] is False

    def test_out_of_scope_without_destination_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- logout UI → 002", "- logout UI"))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("destination" in r for r in data["reasons"])

    def test_exclusion_row_with_non_goal_owner_passes(self, repo: Path) -> None:
        # 2026-07-23 spade-ace false positive: Exclusion rows legitimately have
        # no owning Feature — the established convention marks them "— (non-goal)".
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |",
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |\n"
                "| Product PRD | §8 | Exclusion | Live trading | — (non-goal) | Out — successor PRD (§8) |",
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS", data["reasons"]
        assert data["checks"]["commitment_index_ok"] is True

    def test_exclusion_row_with_empty_owner_still_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |",
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |\n"
                "| Product PRD | §8 | Exclusion | Live trading |  | Out — successor PRD (§8) |",
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["commitment_index_ok"] is False

    def test_non_exclusion_row_with_non_goal_owner_still_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |",
                "| Product PRD | §3.2 | Functional | Logout | — (non-goal) | Implemented |",
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["commitment_index_ok"] is False

    def test_out_of_scope_prose_destination_passes(self, repo: Path) -> None:
        # 2026-07-23 spade-ace false positive: a destination may be non-Feature
        # prose (successor PRD, backlog, frozen branch). The deterministic layer
        # checks only the arrow-and-named-destination form; destination validity
        # is Layer-2 semantics.
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "- logout UI → 002",
                "- logout UI → successor auto-trading PRD (§8 non-goal)",
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS", data["reasons"]

    def test_out_of_scope_empty_destination_still_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- logout UI → 002", "- logout UI →"))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("destination" in r for r in data["reasons"])

    def test_feature_scope_ignores_other_sections(self, repo: Path) -> None:
        # A placeholder in Feature 001 must not fail a Feature-002-scoped run.
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- login endpoint", "- login endpoint TBD"))
        data = run_gate(repo, "structural", "2")
        assert data["scope"] == "feature"
        assert data["feature"] == "002"
        assert not any("Feature 001" in r for r in data["reasons"])

    def test_cited_cid_missing_from_baseline_checklist_fails(self, repo: Path) -> None:
        checklists = repo / "docs" / "prd" / "checklists"
        (checklists / "feature-002.checklist.md").write_text(
            "# Feature 002 Checklist\n\n**Mode**: per-feature\n"
            "**Feature**: Feature 002: sample\n**Result**: PASS\n\n"
            "| C101 | §3.2 | owned | covered |\n"
        )
        (repo / "docs" / "prd" / "featuremap-checklist.md").write_text(
            "# PRD Checklist\n\n**Mode**: prd-only\n\n| C100 | §3.1 | login |\n"
        )
        data = run_gate(repo, "structural", "2")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["checklist_refs_ok"] is False
        assert any("C101" in r for r in data["reasons"])

    def test_cid_crossref_falls_back_to_legacy_codex_path(self, repo: Path) -> None:
        # Established consumer projects still have docs/prd/codex/checklist.md.
        checklists = repo / "docs" / "prd" / "checklists"
        (checklists / "feature-002.checklist.md").write_text(
            "# Feature 002 Checklist\n\n**Mode**: per-feature\n"
            "**Feature**: Feature 002: sample\n**Result**: PASS\n\n"
            "| C100 | §3.2 | owned | covered |\n"
        )
        (repo / "docs" / "prd" / "codex" / "checklist.md").write_text(
            "# Codex PRD Checklist\n\n**Mode**: prd-only\n\n| C100 | §3.1 | login |\n"
        )
        data = run_gate(repo, "structural", "2")
        assert data["checks"]["checklist_refs_ok"] is True

    def test_product_word_todo_is_not_a_placeholder(self, repo: Path) -> None:
        # 2026-07-22 doit-n-live false positive: a product named "Todo" (and
        # identifiers like TODOS_TABLE) must not trip the TODO placeholder scan.
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "- login endpoint", "- Todo list endpoint (TODOS_TABLE)"
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["checks"]["placeholders_clean"] is True

    def test_standalone_todo_token_still_flagged(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(GOOD_MAP.replace("- login endpoint", "- login endpoint (TODO)"))
        data = run_gate(repo, "structural")
        assert data["checks"]["placeholders_clean"] is False

    def test_index_owner_column_located_by_header(self, repo: Path) -> None:
        # 2026-07-22 doit-n-live false positive: an extra leading column moved
        # the owner out of position 6; the header names the column instead.
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            GOOD_MAP.replace(
                "| Source PRD | PRD Ref | Commitment Type | Short Label | Owning Feature | Handling |",
                "| C-ID | Source PRD | PRD Ref | Commitment Type | Short Label | Owning Feature | Handling |",
            )
            .replace(
                "|------------|---------|-----------------|-------------|----------------|----------|",
                "|------|------------|---------|-----------------|-------------|----------------|----------|",
            )
            .replace(
                "| Product PRD | §3.1 | Functional | User login | Feature 001 | Implemented |",
                "| C001 | Product PRD | §3.1 | Functional | User login | Feature 001 | Implemented |",
            )
            .replace(
                "| Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |",
                "| C002 | Product PRD | §3.2 | Functional | Logout | Feature 002 | Implemented |",
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["checks"]["commitment_index_ok"] is True


OBLIGATIONS_HEADER = (
    "\n## Implementation Obligations\n\n"
    "| D-ID | Supports | Kind | Obligation | Why necessary | Impact | Owning Feature |\n"
    "|------|----------|------|------------|---------------|--------|----------------|\n"
)
OBLIGATIONS_ROW = (
    "| D-001 | C100 | logical-enablement | Reachable login surface "
    "| No compliant design works without one | user-visible | Feature 001 |\n"
)
OBLIGATIONS_ANCHOR = "\n> Progress Ledger:"


def map_with_obligations(rows: str) -> str:
    return GOOD_MAP.replace(
        OBLIGATIONS_ANCHOR, OBLIGATIONS_HEADER + rows + OBLIGATIONS_ANCHOR
    )


class TestStructuralObligations:
    def test_legacy_map_without_section_is_valid(self, repo: Path) -> None:
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["checks"]["implementation_obligations_ok"] is True

    def test_valid_table_passes(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(map_with_obligations(OBLIGATIONS_ROW))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["checks"]["implementation_obligations_ok"] is True

    def test_unknown_kind_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            map_with_obligations(
                OBLIGATIONS_ROW.replace("logical-enablement", "nice-to-have")
            )
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["implementation_obligations_ok"] is False
        assert any("unknown Kind" in r for r in data["reasons"])

    def test_unknown_impact_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            map_with_obligations(OBLIGATIONS_ROW.replace("user-visible", "huge"))
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("unknown Impact" in r for r in data["reasons"])

    def test_d_to_d_chain_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(
            map_with_obligations(OBLIGATIONS_ROW.replace("| C100 |", "| C100, D-002 |"))
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("D-to-D" in r for r in data["reasons"])

    def test_duplicate_did_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(map_with_obligations(OBLIGATIONS_ROW + OBLIGATIONS_ROW))
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert any("duplicate D-ID" in r for r in data["reasons"])

    def test_supports_cid_missing_from_baseline_fails(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(map_with_obligations(OBLIGATIONS_ROW))
        (repo / "docs" / "prd" / "featuremap-checklist.md").write_text(
            "# PRD Checklist\n\n**Mode**: prd-only\n\n| C099 | §3.1 | login |\n"
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "FAIL"
        assert data["checks"]["implementation_obligations_ok"] is False
        assert any("C100" in r for r in data["reasons"])

    def test_supports_cid_present_in_baseline_passes(self, repo: Path) -> None:
        fmap = repo / "docs" / "prd" / "feature-map.md"
        fmap.write_text(map_with_obligations(OBLIGATIONS_ROW))
        (repo / "docs" / "prd" / "featuremap-checklist.md").write_text(
            "# PRD Checklist\n\n**Mode**: prd-only\n\n| C100 | §3.1 | login |\n"
        )
        data = run_gate(repo, "structural")
        assert data["verdict"] == "PASS"
        assert data["checks"]["implementation_obligations_ok"] is True


class TestAggregate:
    def test_worse_of_two_with_verbatim_caught(self, repo: Path) -> None:
        row = "| MEDIUM | done criterion (d) lacks PRD evidence | L12 | add row |"
        write_agent_verify_pair(repo, anti_result="WARN", anti_findings=[row])
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "WARN"
        assert data["caught"] == [row]
        assert data["cap"] is None

    def test_stale_checklist_sha_fails(self, repo: Path) -> None:
        checklist = write_agent_verify_pair(repo)
        checklist.write_text(checklist.read_text() + "\nedited after verify\n")
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("stale" in r for r in data["reasons"])

    def test_single_degrade_placeholder_warns_with_cap(self, repo: Path) -> None:
        write_agent_verify_pair(
            repo,
            codex_result="WARN",
            codex_availability="UNAVAILABLE (binary not on PATH)",
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "WARN"
        assert data["cap"] == "single-agent-degrade"

    def test_recused_placeholder_warns_with_cap(self, repo: Path) -> None:
        write_agent_verify_pair(
            repo,
            codex_result="WARN",
            codex_availability="RECUSED (implemented this Feature)",
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "WARN"
        assert data["cap"] == "single-agent-degrade"

    def test_all_degraded_fails(self, repo: Path) -> None:
        write_agent_verify_pair(
            repo,
            codex_result="WARN",
            codex_availability="UNAVAILABLE (binary not on PATH)",
            anti_result="WARN",
            anti_availability="UNAVAILABLE (auth expired)",
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("no independent verifier" in r for r in data["reasons"])

    def test_availability_with_non_warn_result_fails(self, repo: Path) -> None:
        # An agent-authored failure must not be relabeled environmental.
        write_agent_verify_pair(
            repo, codex_result="PASS", codex_availability="UNAVAILABLE (host said so)"
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"

    def test_duplicate_result_lines_fail(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        checklists = repo / "docs" / "prd" / "checklists"
        checklist_sha = sha256(checklists / "feature-006.checklist.md")
        write_report(
            checklists / "feature-006.codex-verify.md",
            mode="codex-per-feature-verify",
            sha_field="Checklist SHA256",
            sha_value=checklist_sha,
            extra_result_line=True,
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("exactly one Result" in r for r in data["reasons"])

    def test_missing_report_fails(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        (repo / "docs" / "prd" / "checklists" / "feature-006.codex-verify.md").unlink()
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("missing or empty" in r for r in data["reasons"])

    def test_feature_mismatch_fails(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        checklists = repo / "docs" / "prd" / "checklists"
        checklist_sha = sha256(checklists / "feature-006.checklist.md")
        write_report(
            checklists / "feature-006.codex-verify.md",
            mode="codex-per-feature-verify",
            feature="005",
            sha_field="Checklist SHA256",
            sha_value=checklist_sha,
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("does not match" in r for r in data["reasons"])

    def test_ledger_emission_is_mechanical(self, repo: Path) -> None:
        row = "| HIGH | invented behavior in scope | L4 | remove |"
        write_agent_verify_pair(repo, anti_result="FAIL", anti_findings=[row])
        data = run_gate(repo, "aggregate", "verify", "6", "--ledger")
        assert data["verdict"] == "FAIL"
        assert data["ledger_written"] is True
        ledger = (
            (repo / ".specify" / "specter-run.jsonl").read_text().strip().splitlines()
        )
        entry = json.loads(ledger[-1])
        assert entry["step"] == "verify"
        assert entry["feature"] == "006"
        assert entry["verdict"] == "FAIL"
        assert entry["caught"] == [row]

    def test_pass_ledger_line_stays_minimal(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        data = run_gate(repo, "aggregate", "verify", "6", "--ledger")
        assert data["verdict"] == "PASS"
        entry = json.loads(
            (repo / ".specify" / "specter-run.jsonl")
            .read_text()
            .strip()
            .splitlines()[-1]
        )
        assert "caught" not in entry
        assert "cap" not in entry

    def test_pre_verify_station_binds_to_feature_map_sha(self, repo: Path) -> None:
        prd = repo / "docs" / "prd"
        map_sha = sha256(prd / "feature-map.md")
        write_report(
            prd / "feature-map.codex-verify.md",
            mode="codex-global-verify",
            feature=None,
            sha_field="Feature Map SHA256",
            sha_value=map_sha,
        )
        write_report(
            prd / "feature-map.antigravity-checklist.md",
            mode="antigravity-global-verify",
            feature=None,
            sha_field="Feature Map SHA256",
            sha_value=map_sha,
        )
        data = run_gate(repo, "aggregate", "pre-verify")
        assert data["verdict"] == "PASS"
        # Editing the map invalidates both reports.
        (prd / "feature-map.md").write_text(GOOD_MAP + "\nedited\n")
        data = run_gate(repo, "aggregate", "pre-verify")
        assert data["verdict"] == "FAIL"

    def test_legacy_agent_verify_station_alias(self, repo: Path) -> None:
        # Pre-rename callers passing "agent-verify" must hit the per-Feature
        # station (and fail loudly on bad args, never silently hit pre-verify).
        write_agent_verify_pair(repo)
        data = run_gate(repo, "aggregate", "agent-verify", "6")
        assert data["station"] == "verify"
        assert data["verdict"] == "PASS"

    def test_expand_station_binds_to_extended_map(self, repo: Path) -> None:
        prd = repo / "docs" / "prd"
        row = "| MEDIUM | new Feature 003 overlaps 001 scope | Amendment 2 | re-cut |"
        write_report(
            prd / "feature-map.delta-2.antigravity-verify.md",
            mode="antigravity-delta-verify",
            feature=None,
            sha_field="Feature Map SHA256",
            sha_value=sha256(prd / "feature-map.md"),
            result="WARN",
            findings=[row],
        )
        data = run_gate(repo, "aggregate", "expand", "2")
        assert data["verdict"] == "WARN"
        assert data["caught"] == [row]
        # extending the map again invalidates the delta report
        (prd / "feature-map.md").write_text(GOOD_MAP + "\n## PRD Amendment edit\n")
        data = run_gate(repo, "aggregate", "expand", "2")
        assert data["verdict"] == "FAIL"

    def test_unknown_station_fails(self, repo: Path) -> None:
        data = run_gate(repo, "aggregate", "nonsense")
        assert data["verdict"] == "FAIL"
        assert any("unknown station" in r for r in data["reasons"])

    def test_wrong_station_mode_fails(self, repo: Path) -> None:
        # A report from another station at the right path must not grade this
        # station (2026-07-19 re-verification finding).
        write_agent_verify_pair(repo)
        checklists = repo / "docs" / "prd" / "checklists"
        checklist_sha = sha256(checklists / "feature-006.checklist.md")
        write_report(
            checklists / "feature-006.codex-verify.md",
            mode="codex-adversarial-code-review",
            sha_field="Checklist SHA256",
            sha_value=checklist_sha,
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("does not match station mode" in r for r in data["reasons"])

    def test_non_numeric_agent_verify_arg_fails(self, repo: Path) -> None:
        data = run_gate(repo, "aggregate", "verify", "../../etc")
        assert data["verdict"] == "FAIL"
        assert any("numeric Feature number" in r for r in data["reasons"])

    def test_invalid_review_spec_id_fails(self, repo: Path) -> None:
        data = run_gate(repo, "aggregate", "review", "006/../../evil")
        assert data["verdict"] == "FAIL"
        assert any("NNN-name" in r for r in data["reasons"])

    def test_analyze_traversal_and_nonconventional_dirs_fail(self, repo: Path) -> None:
        for bad in ("specs/..", "specs/foo", "specs/../..", "docs/prd"):
            data = run_gate(repo, "aggregate", "analyze", bad)
            assert data["verdict"] == "FAIL", bad
            assert any("specs/NNN-name" in r for r in data["reasons"]), bad

    def test_feature_match_is_boundary_not_substring(self, repo: Path) -> None:
        # "Feature 0061" must not satisfy a Feature-006 station.
        write_agent_verify_pair(repo)
        checklists = repo / "docs" / "prd" / "checklists"
        checklist_sha = sha256(checklists / "feature-006.checklist.md")
        write_report(
            checklists / "feature-006.codex-verify.md",
            mode="codex-per-feature-verify",
            feature="0061",
            sha_field="Checklist SHA256",
            sha_value=checklist_sha,
        )
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("does not match Feature 006" in r for r in data["reasons"])

    def test_degrade_placeholder_with_stale_sha_fails(self, repo: Path) -> None:
        # A stale or mis-scoped placeholder must not become an accepted cap.
        write_agent_verify_pair(
            repo,
            codex_result="WARN",
            codex_availability="UNAVAILABLE (binary not on PATH)",
        )
        checklists = repo / "docs" / "prd" / "checklists"
        checklist = checklists / "feature-006.checklist.md"
        checklist.write_text(checklist.read_text() + "\nedited after the placeholder\n")
        data = run_gate(repo, "aggregate", "verify", "6")
        assert data["verdict"] == "FAIL"
        assert any("stale" in r for r in data["reasons"])

    def test_report_shas_align_with_artifacts_when_missing(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        (repo / "docs" / "prd" / "checklists" / "feature-006.codex-verify.md").unlink()
        run_gate(repo, "aggregate", "verify", "6", "--ledger")
        entry = json.loads(
            (repo / ".specify" / "specter-run.jsonl")
            .read_text()
            .strip()
            .splitlines()[-1]
        )
        assert len(entry["report_shas"]) == len(entry["artifacts"]) == 2
        assert entry["report_shas"][0] == ""
        assert len(entry["report_shas"][1]) == 64

    def test_ledger_receipt_carries_round_and_report_shas(self, repo: Path) -> None:
        write_agent_verify_pair(repo)
        data = run_gate(repo, "aggregate", "verify", "6", "--ledger", "--round", "2")
        assert data["round"] == 2
        entry = json.loads(
            (repo / ".specify" / "specter-run.jsonl")
            .read_text()
            .strip()
            .splitlines()[-1]
        )
        assert entry["round"] == 2
        assert len(entry["report_shas"]) == 2
        assert all(len(s) == 64 for s in entry["report_shas"])

    def test_analyze_station_binds_to_tasks_sha(self, repo: Path) -> None:
        spec_dir = repo / "specs" / "006-sample"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text("# Tasks\n\n- T001 @SPEC:X\n")
        tasks_sha = sha256(spec_dir / "tasks.md")
        for agent in ("codex", "antigravity"):
            write_report(
                spec_dir / f"analyze.{agent}.md",
                mode="agent-document-consistency",
                sha_field="Tasks SHA256",
                sha_value=tasks_sha,
            )
        data = run_gate(repo, "aggregate", "analyze", "specs/006-sample")
        assert data["verdict"] == "PASS"
        assert data["feature"] == "006"
        # editing tasks.md invalidates both reports
        (spec_dir / "tasks.md").write_text(
            "# Tasks\n\n- T001 @SPEC:X\n- T002 @SPEC:Y\n"
        )
        data = run_gate(repo, "aggregate", "analyze", "specs/006-sample")
        assert data["verdict"] == "FAIL"
        assert any("stale Tasks SHA256" in r for r in data["reasons"])

    def test_expand_missing_codex_baseline_caps_warn(self, repo: Path) -> None:
        prd = repo / "docs" / "prd"
        write_report(
            prd / "feature-map.delta-3.antigravity-verify.md",
            mode="antigravity-delta-verify",
            feature=None,
            sha_field="Feature Map SHA256",
            sha_value=sha256(prd / "feature-map.md"),
            result="PASS",
        )
        data = run_gate(repo, "aggregate", "expand", "3")
        assert data["verdict"] == "WARN"
        assert data["cap"] == "missing-baseline"
        # with the baseline present, the same PASS report aggregates to PASS
        (prd / "codex" / "checklist-delta-3.md").write_text(
            "# Codex Delta Checklist\n\n**Mode**: prd-only\n\n| C200 | §A1 | new |\n"
        )
        data = run_gate(repo, "aggregate", "expand", "3")
        assert data["verdict"] == "PASS"
        assert data["cap"] is None
