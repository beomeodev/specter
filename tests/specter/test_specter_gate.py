"""Tests for the lean, state-free SPECTER gate."""

# @TEST:FIX-GATE-SCOPE-001

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "docs" / "templates" / "scripts" / "specter-gate.sh"

MAP_TEXT = (
    "# Feature Map\n\n"
    "| C-ID | Commitment | Owning Feature |\n"
    "|---|---|---|\n"
    "| C001 | Store items | Feature 006 |\n"
    "| C002 | Report items | Feature 012 |\n\n"
    "## Feature 006: Storage\n\n"
    "### In scope\n- Store items\n\n"
    "### Done criteria\n- Items persist\n- CI passes green\n\n"
    "## Feature 012: Reporting\n\n"
    "### In scope\n- Report items\n\n"
    "### Done criteria\n- Reports render\n- CI passes green\n"
)

FEATURE_HEADING = re.compile(r"^## Feature (\d+):")


def _tagged_lines(text: str):
    """Yield (owning feature or None, line). A Feature heading is global: it
    belongs to the map's decomposition, not to the section body it opens.
    Text inside a fenced block is content, never structure."""
    current: str | None = None
    fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip(" \t").startswith(("```", "~~~")):
            fence = not fence
            yield current, line
            continue
        if not fence:
            match = FEATURE_HEADING.match(line)
            if match:
                current = str(int(match.group(1)))
                yield None, line
                continue
            if line.startswith("## "):
                current = None
        yield current, line


def expected_global_sha(text: str) -> str:
    """Oracle: everything except Feature section bodies."""
    kept = "".join(line for owner, line in _tagged_lines(text) if owner is None)
    return hashlib.sha256(kept.encode()).hexdigest()


def expected_scope_sha(text: str, feature: str) -> str:
    """Oracle: the global skeleton plus this Feature's own body."""
    want = str(int(feature))
    kept = "".join(
        line for owner, line in _tagged_lines(text) if owner is None or owner == want
    )
    return hashlib.sha256(kept.encode()).hexdigest()


def edit_feature_body(
    repo: Path, feature: str, marker: str = "- refined detail\n"
) -> None:
    """Append a line inside one Feature's section, leaving every other byte alone."""
    path = repo / "docs/prd/feature-map.md"
    out = []
    for owner, line in _tagged_lines(path.read_text()):
        out.append(line)
        if owner == str(int(feature)) and line.startswith("### In scope"):
            out.append(marker)
    path.write_text("".join(out))


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
    feature_map.write_text(MAP_TEXT)
    map_sha = hashlib.sha256(feature_map.read_bytes()).hexdigest()
    (tmp_path / "docs/prd/feature-map.checklist.md").write_text(
        f"**Mode**: global\n**Feature Map SHA256**: {map_sha}\n**Result**: PASS\n"
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


def test_version_is_lean_with_round_log(repo: Path) -> None:
    data = output(run_gate(repo, "version"))
    assert data == {
        "contract": "lean-verification-v1",
        "rev": 3,
        "subcommands": ["hash", "reduce", "rounds", "map-sha"],
        "stateful": False,
        "round_log": ".specify/gate-rounds.log",
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


def touch_inputs(repo: Path) -> None:
    checklist = repo / "docs/prd/checklists/feature-006.checklist.md"
    checklist.write_text(checklist.read_text() + "touched\n")


def fail_round(repo: Path) -> subprocess.CompletedProcess[str]:
    write_reports(repo, digest(repo), "FAIL", "PASS")
    return run_gate(repo, "reduce", "verify", "006")


def test_round_cap_refuses_third_fail_round(repo: Path) -> None:
    assert output(fail_round(repo))["verdict"] == "FAIL"
    touch_inputs(repo)
    assert output(fail_round(repo))["verdict"] == "FAIL"
    touch_inputs(repo)
    result = fail_round(repo)
    assert result.returncode != 0
    assert "round cap reached" in result.stdout
    rounds = output(run_gate(repo, "rounds", "verify", "006"))
    assert rounds["fail_rounds"] == 2
    assert rounds["blocked"] is True


def test_same_hash_reread_is_not_a_new_round(repo: Path) -> None:
    fail_round(repo)
    fail_round(repo)
    assert output(run_gate(repo, "rounds", "verify", "006"))["fail_rounds"] == 1


def test_override_runs_reduction_and_records_reason(repo: Path) -> None:
    fail_round(repo)
    touch_inputs(repo)
    fail_round(repo)
    touch_inputs(repo)
    write_reports(repo, digest(repo), "PASS", "PASS")
    result = run_gate(
        repo, "reduce", "verify", "006", "--override", "owner authorized round 3"
    )
    assert result.returncode == 0
    assert output(result)["verdict"] == "PASS"
    assert output(result)["override"] == "owner authorized round 3"
    log = (repo / ".specify/gate-rounds.log").read_text()
    assert "owner authorized round 3" in log
    assert output(run_gate(repo, "rounds", "verify", "006"))["blocked"] is False


def test_override_requires_reason(repo: Path) -> None:
    result = run_gate(repo, "reduce", "verify", "006", "--override", "")
    assert result.returncode == 2


def test_structural_failure_consumes_no_budget(repo: Path) -> None:
    write_reports(repo, "0" * 64)
    for _ in range(3):
        result = run_gate(repo, "reduce", "verify", "006")
        assert output(result)["verdict"] == "FAIL"
        assert "stale" in result.stdout
    assert output(run_gate(repo, "rounds", "verify", "006"))["fail_rounds"] == 0


def test_pass_resets_the_streak(repo: Path) -> None:
    fail_round(repo)
    touch_inputs(repo)
    write_reports(repo, digest(repo), "PASS", "PASS")
    assert run_gate(repo, "reduce", "verify", "006").returncode == 0
    assert output(run_gate(repo, "rounds", "verify", "006"))["fail_rounds"] == 0


def test_composite_gate_does_not_log_or_block(repo: Path) -> None:
    fail_round(repo)
    touch_inputs(repo)
    fail_round(repo)
    write_reports(repo, digest(repo), "PASS", "PASS")
    result = run_gate(repo, "006")
    assert result.returncode == 0
    log_lines = (repo / ".specify/gate-rounds.log").read_text().splitlines()
    assert len(log_lines) == 2


def rebind_checklists(repo: Path) -> None:
    """Rebind both checklists to the scoped digests the gate now records."""
    text = (repo / "docs/prd/feature-map.md").read_text()
    global_checklist = repo / "docs/prd/feature-map.checklist.md"
    global_checklist.write_text(
        re.sub(
            r"\*\*Feature Map SHA256\*\*: \S+",
            f"**Feature Map SHA256**: {expected_global_sha(text)}",
            global_checklist.read_text(),
        )
    )
    feature_checklist = repo / "docs/prd/checklists/feature-006.checklist.md"
    feature_checklist.write_text(
        re.sub(
            r"\*\*Feature Map SHA256\*\*: \S+",
            f"**Feature Map SHA256**: {expected_scope_sha(text, '006')}",
            feature_checklist.read_text(),
        )
    )


def test_map_sha_subcommand_reports_both_scoped_digests(repo: Path) -> None:
    text = (repo / "docs/prd/feature-map.md").read_text()
    data = output(run_gate(repo, "map-sha", "006"))
    assert data["scope_sha256"] == expected_scope_sha(text, "006")
    assert data["global_sha256"] == expected_global_sha(text)


def test_unrelated_feature_section_edit_keeps_the_cycle_alive(repo: Path) -> None:
    """The reported symptom: refining Feature 012 must not stall Feature 006."""
    rebind_checklists(repo)
    write_reports(repo, digest(repo))
    edit_feature_body(repo, "012")
    result = run_gate(repo, "006")
    assert result.returncode == 0, result.stdout
    assert output(result)["overall"] == "PASS"


def test_unrelated_feature_section_edit_preserves_the_station_digest(
    repo: Path,
) -> None:
    rebind_checklists(repo)
    before = digest(repo)
    edit_feature_body(repo, "012")
    assert digest(repo) == before


def test_own_feature_section_edit_still_stales_the_checklist(repo: Path) -> None:
    rebind_checklists(repo)
    write_reports(repo, digest(repo))
    edit_feature_body(repo, "006")
    result = run_gate(repo, "006")
    assert result.returncode != 0
    assert output(result)["overall"] == "FAIL"
    assert any(
        "Feature Map SHA256 is stale" in str(r) for r in output(result)["reasons"]
    )


def test_own_feature_section_edit_changes_the_station_digest(repo: Path) -> None:
    rebind_checklists(repo)
    before = digest(repo)
    edit_feature_body(repo, "006")
    assert digest(repo) != before


def test_shared_map_content_edit_still_stales_every_checklist(repo: Path) -> None:
    """Commitment rows, ordering, and the DAG stay globally binding."""
    rebind_checklists(repo)
    write_reports(repo, digest(repo))
    path = repo / "docs/prd/feature-map.md"
    path.write_text(
        path.read_text().replace("| C002 | Report items", "| C002 | Render items")
    )
    result = run_gate(repo, "006")
    assert result.returncode != 0
    assert output(result)["overall"] == "FAIL"


def test_adding_a_feature_still_stales_the_global_checklist(repo: Path) -> None:
    rebind_checklists(repo)
    write_reports(repo, digest(repo))
    path = repo / "docs/prd/feature-map.md"
    path.write_text(
        path.read_text() + "\n## Feature 020: Exporting\n\n### In scope\n- Export\n"
    )
    result = run_gate(repo, "006")
    assert result.returncode != 0
    assert output(result)["overall"] == "FAIL"


def test_fenced_heading_does_not_leak_a_feature_body_into_the_skeleton(
    repo: Path,
) -> None:
    """A "## ..." line inside a fenced block is sample text, not a section end.

    Treating it as structure pushes the rest of that Feature's body into the
    global skeleton, so editing that Feature re-stales every other Feature —
    exactly the coupling this scoping removes.
    """
    path = repo / "docs/prd/feature-map.md"
    path.write_text(
        path.read_text().replace(
            "### In scope\n- Store items\n",
            "### In scope\n```bash\n## not a heading\n```\n- Store items\n",
        )
    )
    rebind_checklists(repo)
    write_reports(repo, digest(repo))
    before_global = run_gate(repo, "map-sha", "006")
    path.write_text(path.read_text().replace("- Store items\n", "- Store items fast\n"))
    after_global = run_gate(repo, "map-sha", "006")
    assert (
        output(before_global)["global_sha256"] == output(after_global)["global_sha256"]
    )
    assert output(before_global)["scope_sha256"] != output(after_global)["scope_sha256"]


def test_legacy_whole_map_binding_is_still_accepted(repo: Path) -> None:
    """Checklists written before scoping keep working until regenerated."""
    write_reports(repo, digest(repo))
    result = run_gate(repo, "006")
    assert result.returncode == 0, result.stdout
    assert output(result)["overall"] == "PASS"


def write_feature_override(
    repo: Path, reason: str = "owner accepts the refinement", feature: str = "006"
) -> None:
    checklist = repo / f"docs/prd/checklists/feature-{feature}.checklist.md"
    (repo / f"docs/prd/checklists/feature-{feature}.checklist.override.md").write_text(
        "**Mode**: feature-override\n"
        f"**Feature Checklist SHA256**: {hashlib.sha256(checklist.read_bytes()).hexdigest()}\n"
        f"**Reason**: {reason}\n"
    )


def test_feature_override_downgrades_stale_map_binding_to_warn(repo: Path) -> None:
    rebind_checklists(repo)
    edit_feature_body(repo, "006")
    write_feature_override(repo)
    write_reports(repo, digest(repo))
    result = run_gate(repo, "006")
    assert result.returncode == 0, result.stdout
    data = output(result)
    assert data["overall"] == "WARN"
    assert any("overridden to WARN" in str(r) for r in data["reasons"])


def test_feature_override_invalidated_by_checklist_change(repo: Path) -> None:
    rebind_checklists(repo)
    edit_feature_body(repo, "006")
    write_feature_override(repo)
    checklist = repo / "docs/prd/checklists/feature-006.checklist.md"
    checklist.write_text(checklist.read_text() + "regenerated\n")
    write_reports(repo, digest(repo))
    assert run_gate(repo, "006").returncode != 0


def test_feature_override_requires_reason(repo: Path) -> None:
    rebind_checklists(repo)
    edit_feature_body(repo, "006")
    write_feature_override(repo, reason="")
    write_reports(repo, digest(repo))
    assert run_gate(repo, "006").returncode != 0


def write_global_override(
    repo: Path, reason: str = "owner accepts standing findings"
) -> None:
    checklist_sha = hashlib.sha256(
        (repo / "docs/prd/feature-map.checklist.md").read_bytes()
    ).hexdigest()
    (repo / "docs/prd/feature-map.checklist.override.md").write_text(
        "**Mode**: global-override\n"
        f"**Global Checklist SHA256**: {checklist_sha}\n"
        f"**Reason**: {reason}\n"
    )


def test_global_override_downgrades_standing_fail_to_warn(repo: Path) -> None:
    checklist = repo / "docs/prd/feature-map.checklist.md"
    checklist.write_text(
        checklist.read_text().replace("**Result**: PASS", "**Result**: FAIL")
    )
    write_global_override(repo)
    write_reports(repo, digest(repo))
    result = run_gate(repo, "006")
    assert result.returncode == 0
    data = output(result)
    assert data["overall"] == "WARN"
    assert any("overridden to WARN" in str(r) for r in data["reasons"])


def test_global_override_invalidated_by_checklist_change(repo: Path) -> None:
    checklist = repo / "docs/prd/feature-map.checklist.md"
    checklist.write_text(
        checklist.read_text().replace("**Result**: PASS", "**Result**: FAIL")
    )
    write_global_override(repo)
    checklist.write_text(checklist.read_text() + "regenerated\n")
    write_reports(repo, digest(repo))
    result = run_gate(repo, "006")
    assert result.returncode != 0
    assert output(result)["overall"] == "FAIL"


def test_global_override_requires_reason(repo: Path) -> None:
    checklist = repo / "docs/prd/feature-map.checklist.md"
    checklist.write_text(
        checklist.read_text().replace("**Result**: PASS", "**Result**: FAIL")
    )
    write_global_override(repo, reason="")
    write_reports(repo, digest(repo))
    assert run_gate(repo, "006").returncode != 0


def test_replay_shakedown_round_sequences(repo: Path) -> None:
    """Replay the 2026-08 shakedown drift sequences (suseonglm 089/090/091).

    Observed under rev 1: analyze ran 3 rounds in Features 090 and 091 and
    review ran 4 rounds in Feature 089 against a prose cap of 2, while clean
    stations (090 verify: WARN/WARN) never exceeded budget. rev 2 must block
    the third FAIL round and leave the clean path untouched.
    """
    # 090/091 analyze drift shape: FAIL, FAIL, then round 3 must be refused.
    fail_round(repo)
    touch_inputs(repo)
    fail_round(repo)
    touch_inputs(repo)
    blocked = fail_round(repo)
    assert blocked.returncode != 0 and "round cap reached" in blocked.stdout
    # Owner override (as recorded in the 090 dispute file) still works once.
    write_reports(repo, digest(repo), "FAIL", "PASS")
    overridden = run_gate(
        repo, "reduce", "verify", "006", "--override", "dispute: owner authorized"
    )
    assert output(overridden)["verdict"] == "FAIL"
    # A failed override round does not reopen the budget: round 4 needs its
    # own authorization (089 review round 4 was individually user-authorized).
    touch_inputs(repo)
    write_reports(repo, digest(repo), "WARN", "WARN")
    blocked_again = run_gate(repo, "reduce", "verify", "006")
    assert blocked_again.returncode != 0
    assert "round cap reached" in blocked_again.stdout
    clean = run_gate(
        repo, "reduce", "verify", "006", "--override", "dispute: owner authorized r4"
    )
    assert clean.returncode == 0
    assert output(clean)["verdict"] == "WARN"
    # The advancing verdict resets the streak: the next station visit is clean.
    assert output(run_gate(repo, "rounds", "verify", "006"))["blocked"] is False


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
