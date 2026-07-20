"""Deterministic Feature Audit Tier policy, receipt, and adversarial tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "specter" / "classify_audit_tier.py"
POLICY = ROOT / "docs" / "templates" / "audit-tier-policy.json"
GATE = ROOT / "docs" / "templates" / "scripts" / "specter-gate.sh"


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--policy", str(POLICY), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    if check:
        assert result.returncode == 0, result.stderr
    return result


def payload(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


BOOL_SIGNALS = [
    "auth_or_authorization",
    "tenant_or_resource_ownership",
    "money_billing_or_financial",
    "secrets_crypto_or_credentials",
    "personal_sensitive_or_destructive_data",
    "schema_or_data_migration",
    "public_api_or_external_integration",
    "state_machine_or_multi_store_state",
    "concurrency_background_jobs_or_distributed_work",
    "build_release_ci_hooks_permissions_or_sandbox",
    "cross_layer_or_cross_feature_contract",
    "new_runtime_dependency",
    "persistence_change",
    "irreversible_operations",
    "policy_or_gate_change",
    "unresolved_clarification",
]


def feature_map(
    overrides: dict[str, str] | None = None,
    *,
    include_signals: bool = True,
    extra_rows: list[tuple[str, str, str]] | None = None,
) -> str:
    values = {key: "no" for key in BOOL_SIGNALS}
    values.update(
        {
            "behavioral_fr_count": "2",
            "estimated_domains": "1",
            "estimated_touched_files": "4",
        }
    )
    values.update(overrides or {})
    section = ""
    if include_signals:
        rows = [
            f"| {key} | {value} | PRD §1 / Feature scope evidence |"
            for key, value in values.items()
        ]
        rows.extend(f"| {k} | {v} | {e} |" for k, v, e in (extra_rows or []))
        section = (
            "\n### Audit signals\n\n"
            "| Signal | Value | Evidence |\n"
            "| --- | --- | --- |\n" + "\n".join(rows) + "\n"
        )
    return (
        "# Feature Map\n\n"
        "## Feature 001: Sample\n\n"
        "### Source PRDs\n- Product: docs/prd/PRD.md\n"
        "### PRD references\n- Product §1\n"
        f"{section}"
        "### In scope\n- sample\n"
        "### Done criteria\n- sample works\n- CI passes green\n"
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "prd").mkdir(parents=True)
    (tmp_path / "docs" / "prd" / "feature-map.md").write_text(feature_map())
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=tmp_path, check=True)
    return tmp_path


def classify(repo: Path, phase: str = "feature-map", *extra: str) -> dict:
    return payload(
        run(
            repo,
            "classify",
            "--feature",
            "1",
            "--phase",
            phase,
            "--feature-map",
            "docs/prd/feature-map.md",
            *extra,
        )
    )


def prepare_tiered_verify_station(repo: Path, *, hard_risk: bool) -> None:
    classifier_target = repo / "scripts" / "specter" / "classify_audit_tier.py"
    policy_target = repo / "docs" / "templates" / "audit-tier-policy.json"
    classifier_target.parent.mkdir(parents=True, exist_ok=True)
    policy_target.parent.mkdir(parents=True, exist_ok=True)
    classifier_target.write_bytes(SCRIPT.read_bytes())
    policy_target.write_bytes(POLICY.read_bytes())
    if hard_risk:
        (repo / "docs/prd/feature-map.md").write_text(
            feature_map({"auth_or_authorization": "yes"})
        )
    classify(repo)

    checklists = repo / "docs" / "prd" / "checklists"
    checklists.mkdir(parents=True, exist_ok=True)
    checklist = checklists / "feature-001.checklist.md"
    checklist.write_text(
        "# Feature 001 Checklist\n\n"
        "**Mode**: per-feature\n"
        "**Feature**: Feature 001: sample\n"
        "**Result**: PASS\n"
    )
    checklist_sha = hashlib.sha256(checklist.read_bytes()).hexdigest()
    (checklists / "feature-001.codex-verify.md").write_text(
        "# Codex\n\n"
        "**Mode**: codex-per-feature-verify\n"
        "**Feature**: Feature 001\n"
        f"**Checklist SHA256**: {checklist_sha}\n"
        "**Result**: WARN\n"
        "**Availability**: UNAVAILABLE (binary not on PATH)\n"
    )
    (checklists / "feature-001.antigravity-verify.md").write_text(
        "# Antigravity\n\n"
        "**Mode**: antigravity-per-feature-verify\n"
        "**Feature**: Feature 001\n"
        f"**Checklist SHA256**: {checklist_sha}\n"
        "**Result**: PASS\n"
    )


def run_gate(repo: Path, *args: str) -> dict:
    result = subprocess.run(
        ["bash", str(GATE), *args],
        cwd=repo,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "signal",
    json.loads(POLICY.read_text())["t3_hard_risk_signals"],
)
def test_every_t3_signal_forces_t3(repo: Path, signal: str) -> None:
    (repo / "docs/prd/feature-map.md").write_text(feature_map({signal: "yes"}))
    assert classify(repo)["effective_tier"] == "T3"


@pytest.mark.parametrize(
    ("override", "reason_fragment"),
    [
        ({"estimated_domains": "2"}, "estimated_domains"),
        ({"behavioral_fr_count": "4"}, "behavioral_fr_count"),
        ({"estimated_touched_files": "9"}, "estimated_touched_files"),
        ({"cross_layer_or_cross_feature_contract": "yes"}, "cross_layer"),
        ({"new_runtime_dependency": "yes"}, "new_runtime_dependency"),
        ({"persistence_change": "yes"}, "persistence_change"),
        ({"unresolved_clarification": "yes"}, "unresolved_clarification"),
    ],
)
def test_every_t1_eligibility_boundary_falls_to_t2(
    repo: Path, override: dict[str, str], reason_fragment: str
) -> None:
    (repo / "docs/prd/feature-map.md").write_text(feature_map(override))
    data = classify(repo)
    assert data["newly_computed_tier"] == "T2"
    assert any(reason_fragment in reason for reason in data["reasons"])


def test_all_t1_predicates_affirmed_produces_t1(repo: Path) -> None:
    assert classify(repo)["effective_tier"] == "T1"


def test_legacy_feature_is_t2(repo: Path) -> None:
    (repo / "docs/prd/feature-map.md").write_text(feature_map(include_signals=False))
    data = classify(repo)
    assert data["effective_tier"] == "T2"
    assert "legacy-unclassified" in data["reasons"]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda: feature_map(extra_rows=[("audit_tier", "T1", "agent chose it")]),
        lambda: feature_map({"estimated_touched_files": "-2"}),
        lambda: feature_map({"estimated_domains": "many"}),
        lambda: feature_map({"auth_or_authorization": "false"}),
        lambda: feature_map({"auth_or_authorization": "yes"}).replace(
            "PRD §1 / Feature scope evidence", "", 1
        ),
    ],
)
def test_malformed_signals_fail_safe_to_t3(repo: Path, mutation) -> None:
    (repo / "docs/prd/feature-map.md").write_text(mutation())
    data = classify(repo)
    assert data["effective_tier"] == "T3"
    assert data["classification_status"] == "fail-safe"


def test_unknown_cannot_produce_t1(repo: Path) -> None:
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"estimated_touched_files": "unknown"})
    )
    assert classify(repo)["effective_tier"] == "T2"


@pytest.mark.parametrize("signal", BOOL_SIGNALS)
def test_unknown_boolean_signal_cannot_produce_t1(repo: Path, signal: str) -> None:
    (repo / "docs/prd/feature-map.md").write_text(feature_map({signal: "unknown"}))
    assert classify(repo)["effective_tier"] != "T1"


def test_omitted_hard_risk_signal_is_fail_safe_not_t1(repo: Path) -> None:
    fmap = feature_map().replace(
        "| auth_or_authorization | no | PRD §1 / Feature scope evidence |\n", ""
    )
    (repo / "docs/prd/feature-map.md").write_text(fmap)
    data = classify(repo)
    assert data["effective_tier"] == "T3"
    assert data["classification_status"] == "fail-safe"


def test_manual_override_can_raise_only(repo: Path) -> None:
    raised = classify(repo, "feature-map", "--raise-tier", "T3")
    assert raised["effective_tier"] == "T3"
    persisted = classify(repo)
    assert persisted["manual_upward_override"] == "T3"
    assert persisted["effective_tier"] == "T3"
    result = run(
        repo,
        "classify",
        "--feature",
        "1",
        "--phase",
        "feature-map",
        "--feature-map",
        "docs/prd/feature-map.md",
        "--raise-tier",
        "T1",
        check=False,
    )
    assert result.returncode != 0
    assert "cannot lower" in result.stderr


def test_unknown_cli_tier_lowering_flag_is_rejected(repo: Path) -> None:
    result = run(
        repo,
        "classify",
        "--feature",
        "1",
        "--phase",
        "feature-map",
        "--feature-map",
        "docs/prd/feature-map.md",
        "--audit-tier",
        "T1",
        check=False,
    )
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr


def test_spec_phase_escalates_from_content(repo: Path) -> None:
    spec = repo / "specs" / "001-sample" / "spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("The auth service shall enforce resource ownership.\n")
    data = classify(repo, "spec", "--spec", str(spec.relative_to(repo)))
    assert data["effective_tier"] == "T3"


def test_plan_phase_new_dependency_escalates_to_t2(repo: Path) -> None:
    spec = repo / "specs" / "001-sample" / "spec.md"
    plan = repo / "specs" / "001-sample" / "plan.md"
    plan.parent.mkdir(parents=True)
    spec.write_text("Routine rendering behavior.\n")
    plan.write_text("Add new runtime dependency for rendering.\n")
    data = classify(
        repo,
        "plan",
        "--spec",
        str(spec.relative_to(repo)),
        "--plan",
        str(plan.relative_to(repo)),
    )
    assert data["effective_tier"] == "T2"


@pytest.mark.parametrize(
    ("phase", "args", "missing"),
    [
        ("spec", (), "spec"),
        ("plan", ("--spec", "docs/prd/feature-map.md"), "plan"),
        (
            "pre-implement",
            (
                "--spec",
                "docs/prd/feature-map.md",
                "--plan",
                "docs/prd/feature-map.md",
            ),
            "tasks",
        ),
    ],
)
def test_phase_inputs_cannot_be_omitted(
    repo: Path, phase: str, args: tuple[str, ...], missing: str
) -> None:
    result = run(
        repo,
        "classify",
        "--feature",
        "1",
        "--phase",
        phase,
        "--feature-map",
        "docs/prd/feature-map.md",
        *args,
        check=False,
    )
    assert result.returncode != 0
    assert f"requires: {missing}" in result.stderr


def test_phase_artifact_role_cannot_be_rebound_to_benign_file(repo: Path) -> None:
    benign = repo / "docs" / "benign.md"
    benign.write_text("routine")
    result = run(
        repo,
        "classify",
        "--feature",
        "1",
        "--phase",
        "spec",
        "--feature-map",
        "docs/prd/feature-map.md",
        "--spec",
        "docs/benign.md",
        check=False,
    )
    assert result.returncode != 0
    assert "expected spec.md" in result.stderr


@pytest.mark.parametrize(
    "path",
    [
        "backend/auth/service.py",
        "db/migrations/0002.sql",
        "docs/templates/scripts/specter-gate.sh",
    ],
)
def test_real_diff_hard_risk_paths_force_t3(repo: Path, path: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("changed\n")
    data = classify(repo, "diff", "--diff-base", "HEAD")
    assert data["effective_tier"] == "T3"


def test_effective_tier_is_monotonic(repo: Path) -> None:
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"auth_or_authorization": "yes"})
    )
    assert classify(repo)["effective_tier"] == "T3"
    (repo / "docs/prd/feature-map.md").write_text(feature_map())
    data = classify(repo)
    assert data["newly_computed_tier"] == "T1"
    assert data["effective_tier"] == "T3"


def test_policy_and_artifact_hash_freshness(repo: Path) -> None:
    data = classify(repo)
    assert data["policy_hash"] == hashlib.sha256(POLICY.read_bytes()).hexdigest()
    assert len(data["input_artifacts"][0]["sha256"]) == 64
    valid = payload(run(repo, "validate-receipt", "--feature", "1"))
    assert valid["valid"] is True
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"estimated_domains": "2"})
    )
    invalid = run(repo, "validate-receipt", "--feature", "1", check=False)
    assert invalid.returncode != 0
    assert payload(invalid)["valid"] is False


def test_direct_receipt_t1_tampering_is_rejected_by_replay(repo: Path) -> None:
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"auth_or_authorization": "yes"})
    )
    receipt = classify(repo)
    assert receipt["effective_tier"] == "T3"
    path = Path(receipt["receipt_path"])
    tampered = json.loads(path.read_text())
    tampered["newly_computed_tier"] = "T1"
    tampered["effective_tier"] = "T1"
    tampered["tier_settings"] = json.loads(POLICY.read_text())["tiers"]["T1"]
    path.write_text(json.dumps(tampered))

    result = run(repo, "validate-receipt", "--feature", "1", check=False)
    assert result.returncode != 0
    data = payload(result)
    assert data["valid"] is False
    assert any("deterministic replay" in reason for reason in data["reasons"])


def test_historical_floor_survives_deleted_current_receipt(repo: Path) -> None:
    classify(repo, "feature-map", "--ledger")
    risky = repo / "backend" / "auth" / "service.py"
    risky.parent.mkdir(parents=True)
    risky.write_text("changed\n")
    escalated = classify(repo, "diff", "--diff-base", "HEAD", "--ledger")
    assert escalated["effective_tier"] == "T3"

    risky.unlink()
    Path(escalated["receipt_path"]).unlink()
    replayed = classify(repo, "feature-map", "--ledger")
    assert replayed["newly_computed_tier"] == "T1"
    assert replayed["prior_effective_tier"] == "T3"
    assert replayed["effective_tier"] == "T3"


def test_partial_sync_policy_contract_mismatch_fails(
    repo: Path, tmp_path: Path
) -> None:
    bad_policy = tmp_path / "bad-policy.json"
    data = json.loads(POLICY.read_text())
    data["contract"] = "audit-tier-v0"
    bad_policy.write_text(json.dumps(data))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--policy", str(bad_policy), "version"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "contract mismatch" in result.stderr


def test_malformed_policy_numeric_threshold_fails(repo: Path, tmp_path: Path) -> None:
    bad_policy = tmp_path / "bad-threshold-policy.json"
    data = json.loads(POLICY.read_text())
    data["t1_eligibility"]["estimated_touched_files_max"] = "eight"
    bad_policy.write_text(json.dumps(data))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--policy", str(bad_policy), "version"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must be a non-negative integer" in result.stderr


def test_t3_warn_ack_is_bound_to_receipt(repo: Path) -> None:
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"auth_or_authorization": "yes"})
    )
    receipt = classify(repo)
    status = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert status["required"] is True
    assert status["satisfied"] is False
    premature = run(
        repo,
        "acknowledge-warn",
        "--feature",
        "1",
        "--station",
        "verify",
        "--actor",
        "human",
        check=False,
    )
    assert premature.returncode != 0
    assert "mechanical station WARN receipt" in premature.stderr

    reports = repo / "docs" / "prd" / "checklists"
    reports.mkdir(parents=True, exist_ok=True)
    report_paths = [
        reports / "feature-001.codex-verify.md",
        reports / "feature-001.antigravity-verify.md",
    ]
    for path in report_paths:
        path.write_text("**Result**: WARN\n")
    tier_receipt_sha = hashlib.sha256(
        Path(receipt["receipt_path"]).read_bytes()
    ).hexdigest()
    ledger_entry = {
        "ts": "2026-07-20T00:00:00Z",
        "cycle": "feature",
        "feature": "001",
        "step": "verify",
        "verdict": "WARN",
        "round": 1,
        "artifacts": [str(path.relative_to(repo)) for path in report_paths],
        "report_shas": [
            hashlib.sha256(path.read_bytes()).hexdigest() for path in report_paths
        ],
        "audit_tier": "T3",
        "tier_receipt_sha256": tier_receipt_sha,
        "policy_hash": receipt["policy_hash"],
        "caught": ["high-risk warning"],
    }
    ledger = repo / ".specify" / "specter-run.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps(ledger_entry, sort_keys=True) + "\n")
    payload(
        run(
            repo,
            "acknowledge-warn",
            "--feature",
            "1",
            "--station",
            "verify",
            "--actor",
            "human",
        )
    )
    status = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert status["satisfied"] is True
    assert (
        status["tier_receipt_sha256"]
        == hashlib.sha256(Path(receipt["receipt_path"]).read_bytes()).hexdigest()
    )
    report_paths[0].write_text("**Result**: PASS\n")
    status = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert status["satisfied"] is False
    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"schema_or_data_migration": "yes"})
    )
    classify(repo)
    status = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert status["satisfied"] is False


def test_t1_and_t2_warns_do_not_require_t3_ack(repo: Path) -> None:
    classify(repo)
    t1 = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert t1["required"] is False

    (repo / "docs/prd/feature-map.md").write_text(
        feature_map({"estimated_domains": "2"})
    )
    classify(repo)
    t2 = payload(run(repo, "ack-status", "--feature", "1", "--station", "verify"))
    assert t2["required"] is False


def test_one_agent_degrade_behavior_is_tier_bound(repo: Path) -> None:
    prepare_tiered_verify_station(repo, hard_risk=False)
    t1 = run_gate(repo, "aggregate", "verify", "1", "--ledger")
    assert t1["audit_tier"] == "T1", (t1["verdict"], t1["reasons"])
    assert t1["verdict"] == "WARN"
    assert t1["cap"] == "single-agent-degrade"
    assert t1["warn_ack_required"] is False


def test_t3_degrade_requires_fresh_mechanical_warn_ack(repo: Path) -> None:
    prepare_tiered_verify_station(repo, hard_risk=True)
    first = run_gate(repo, "aggregate", "verify", "1", "--ledger")
    assert first["audit_tier"] == "T3", (first["verdict"], first["reasons"])
    assert first["verdict"] == "WARN"
    assert first["warn_ack_required"] is True
    assert first["warn_ack_satisfied"] is False

    payload(
        run(
            repo,
            "acknowledge-warn",
            "--feature",
            "1",
            "--station",
            "verify",
            "--actor",
            "human",
        )
    )
    second = run_gate(repo, "aggregate", "verify", "1")
    assert second["verdict"] == "WARN"
    assert second["warn_ack_required"] is True
    assert second["warn_ack_satisfied"] is True


def test_policy_keeps_two_reviewers_and_executable_gates_for_t1() -> None:
    policy = json.loads(POLICY.read_text())
    t1 = policy["tiers"]["T1"]
    assert t1["independent_reviewers"] == 2
    assert t1["executable_gates_required"] is True
    assert t1["done_criteria_execution_required"] is True


def test_zero_reviewer_and_station_fixed_invariants_remain_in_gate_script() -> None:
    gate = (ROOT / "docs/templates/scripts/specter-gate.sh").read_text()
    assert "no independent verifier ran" in gate
    assert (
        'INPUTS=("docs/prd/checklists/feature-${agg_feature}.codex-verify.md"' in gate
    )


def test_bypass_and_stop_hooks_remain_unconditional() -> None:
    specify_hook = (
        ROOT / "docs/templates/scripts/speckit-specify-gate-hook.sh"
    ).read_text()
    stop_hook = (ROOT / "docs/templates/scripts/specter-stop-gate.sh").read_text()
    assert "audit_tier" not in specify_hook
    assert "audit_tier" not in stop_hook
    assert "permissionDecision" in specify_hook
    assert "MAX_BLOCKS=3" in stop_hook


def test_tiering_cannot_disable_executable_migration_or_publish_backstops() -> None:
    review = (ROOT / ".claude" / "commands" / "ms.review.md").read_text()
    fin = (ROOT / ".claude" / "commands" / "ms.fin.md").read_text()
    precommit = (ROOT / ".pre-commit-config.yaml").read_text()
    assert "Executable Code Gates" in review
    assert "Done Criteria Execution" in review
    assert "Migration Rollback & Failure Analysis" in review
    assert "explicit ack" in review
    assert "High-Stakes Diff" in fin
    assert "check_tag_chain.py" in precommit
    assert "check_feature_map_gate.py" in precommit


def test_commands_reject_reviewer_and_tier_lowering_paths() -> None:
    for name in ("ms.verify.md", "ms.analyze.md", "ms.review.md"):
        command = (ROOT / ".claude" / "commands" / name).read_text()
        assert "Reject" in command
        assert "--raise-audit-tier T2|T3" in command
        assert "skip" in command.lower()
        assert "two" in command.lower() or "both" in command.lower()


def test_global_preverify_is_explicitly_not_tiered() -> None:
    command = (ROOT / ".claude" / "commands" / "ms.pre-verify.md").read_text()
    assert "always full strength" in command
    assert "never Feature-tiered" in command


def test_init_and_sync_propagate_policy_classifier_pair() -> None:
    init = (ROOT / ".claude" / "commands" / "ms.init.md").read_text()
    manifest = json.loads(
        (ROOT / "scripts" / "specter" / "specter_sync_manifest.json").read_text()
    )
    assert "docs/templates/audit-tier-policy.json" in init
    assert "scripts/specter/classify_audit_tier.py" in init
    assert "docs/templates/*" in manifest["include"]
    assert "scripts/specter/classify_audit_tier.py" in manifest["include"]


def test_gate_capability_probe_rejects_partial_sync(repo: Path) -> None:
    partial_policy = repo / "docs" / "templates" / "audit-tier-policy.json"
    partial_policy.parent.mkdir(parents=True, exist_ok=True)
    partial_policy.write_bytes(POLICY.read_bytes())
    version = run_gate(repo, "version")
    assert version["audit_tier_capability"] == "partial-sync"
