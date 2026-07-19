"""Tests for specter-release.sh and specter-publish.sh (read-only publish helpers).

Covers the 2026-07-19 phase-1 adoption (Codex sol review, ADOPT-WITH-CHANGES):
deterministic semver with unclassified-commit exposure, and evidence-rich
end-state verification with true/false/not_applicable/unknown states.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent.parent / "docs" / "templates" / "scripts"
RELEASE = SCRIPTS / "specter-release.sh"
PUBLISH = SCRIPTS / "specter-publish.sh"

ENV = {"PATH": "/usr/bin:/bin", "HOME": "/tmp", "GIT_CONFIG_NOSYSTEM": "1"}


def run_script(script: Path, cwd: Path, *args: str) -> dict:
    result = subprocess.run(
        ["bash", str(script), *args],
        cwd=cwd,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"git {args}: {result.stderr}"
    return result.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Work repo with a local bare origin, one pushed commit, upstream set."""
    origin = tmp_path / "origin.git"
    origin.mkdir()
    git(origin, "init", "--bare", "-q")
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init", "-q", "-b", "master")
    git(work, "remote", "add", "origin", str(origin))
    git(work, "commit", "--allow-empty", "-q", "-m", "feat: initial engine")
    git(work, "push", "-q", "-u", "origin", "master")
    return work


class TestSemver:
    def test_no_tag_feat_is_minor_against_zero(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "semver")
        assert data["computed_bump"] == "minor"
        assert data["computed_version"] == "0.1.0"
        assert data["last_tag"] is None
        assert any("no_prior_tag" in n for n in data["notes"])

    def test_breaking_bang_is_major_with_v_prefix_kept(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v0.2.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "feat!: breaking cut")
        data = run_script(RELEASE, repo, "semver")
        assert data["computed_bump"] == "major"
        assert data["computed_version"] == "v1.0.0"
        assert len(data["drivers"]["major"]) == 1

    def test_breaking_change_footer_is_major(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v0.2.0", "-m", "r")
        git(
            repo, "commit", "--allow-empty", "-q",
            "-m", "fix: tighten parser", "-m", "BREAKING CHANGE: drops legacy input",
        )
        data = run_script(RELEASE, repo, "semver")
        assert data["computed_bump"] == "major"

    def test_fix_only_is_patch(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.2.3", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: null guard")
        data = run_script(RELEASE, repo, "semver")
        assert data["computed_bump"] == "patch"
        assert data["computed_version"] == "v1.2.4"

    def test_unclassified_commits_are_exposed_not_hidden(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "random message no type")
        data = run_script(RELEASE, repo, "semver")
        assert data["computed_bump"] == "patch"
        assert len(data["unclassified"]) == 1
        assert "random message no type" in data["unclassified"][0]
        assert any("non-conventional" in n for n in data["notes"])

    def test_explicit_version_overrides_with_note(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v2.5.0")
        assert data["chosen_version"] == "v2.5.0"
        assert data["computed_version"] == "v1.0.1"
        assert any("overrides computed" in n for n in data["notes"])

    def test_invalid_explicit_version_refuses_to_choose(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "semver", "banana")
        assert data["chosen_version"] == ""
        assert any("not semver" in n for n in data["notes"])

    def test_version_probe(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "version")
        assert data["contract"] == "publish-helpers-v1"
        assert "semver" in data["subcommands"]

    def test_malformed_last_tag_withholds_version(self, repo: Path) -> None:
        git(repo, "tag", "-a", "release-abc", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver")
        assert data["tag_malformed"] is True
        assert data["computed_version"] == ""
        assert data["chosen_version"] == ""
        assert any("explicit version is required" in n for n in data["notes"])

    def test_malformed_tag_with_valid_explicit_still_chooses(self, repo: Path) -> None:
        git(repo, "tag", "-a", "release-abc", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v3.0.0")
        assert data["chosen_version"] == "v3.0.0"

    def test_zero_commits_withholds_version(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        data = run_script(RELEASE, repo, "semver")
        assert data["commits_total"] == 0
        assert data["computed_version"] == ""
        assert data["chosen_version"] == ""
        assert any("nothing to release" in n for n in data["notes"])

    def test_driver_oids_are_full_length(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver")
        oid = data["drivers"]["patch"][0].split(" ")[0]
        assert len(oid) == 40

    def test_collision_with_existing_tag_is_refused(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v1.0.0")
        assert any("collision" in n for n in data["notes"])
        assert data["chosen_version"] == ""

    def test_remote_only_collision_is_refused(self, repo: Path) -> None:
        # Tag exists on origin but not locally (e.g. tagged from another clone).
        git(repo, "tag", "-a", "v9.0.0", "-m", "r")
        git(repo, "push", "-q", "origin", "v9.0.0")
        git(repo, "tag", "-d", "v9.0.0")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v9.0.0")
        assert any("exists on origin" in n for n in data["notes"])
        assert data["chosen_version"] == ""

    def test_non_monotonic_explicit_is_refused(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v2.0.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v0.5.0")
        assert any("not monotonic" in n for n in data["notes"])
        assert data["chosen_version"] == ""

    def test_monotonic_compare_is_componentwise(self, repo: Path) -> None:
        # 1.2000.0 > 1.3.0 must hold — no weighted-sum encoding.
        git(repo, "tag", "-a", "v1.3.0", "-m", "r")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: x")
        data = run_script(RELEASE, repo, "semver", "v1.2000.0")
        assert not any("not monotonic" in n for n in data["notes"])
        assert data["chosen_version"] == "v1.2000.0"

    def test_merge_commits_excluded_from_classification(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "checkout", "-q", "-b", "side")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: side work")
        git(repo, "checkout", "-q", "master")
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: main work")
        git(repo, "merge", "--no-ff", "-q", "-m", "merge side", "side")
        data = run_script(RELEASE, repo, "semver")
        assert any("merge commit" in n for n in data["notes"])
        merged_subjects = " ".join(
            data["drivers"]["major"] + data["drivers"]["minor"]
            + data["drivers"]["patch"] + data["unclassified"]
        )
        assert "merge side" not in merged_subjects


class TestPublishEndstate:
    def test_clean_pushed_tree(self, repo: Path) -> None:
        data = run_script(PUBLISH, repo, "verify-endstate")
        checks = data["checks"]
        assert checks["tree_clean"]["status"] == "true"
        assert checks["pushed"]["status"] == "true"
        # no gh in the test PATH: unknown, never false
        assert checks["pr_open"]["status"] == "unknown"

    def test_unpushed_commit_is_false_with_count(self, repo: Path) -> None:
        git(repo, "commit", "--allow-empty", "-q", "-m", "fix: local only")
        data = run_script(PUBLISH, repo, "verify-endstate")
        assert data["checks"]["pushed"]["status"] == "false"
        assert "1 commit" in data["checks"]["pushed"]["evidence"]

    def test_dirty_tree_is_false(self, repo: Path) -> None:
        (repo / "stray.txt").write_text("uncommitted\n")
        data = run_script(PUBLISH, repo, "verify-endstate")
        assert data["checks"]["tree_clean"]["status"] == "false"

    def test_upstream_resolved_not_hardcoded(self, repo: Path) -> None:
        data = run_script(PUBLISH, repo, "verify-endstate")
        assert data["upstream"] == "origin/master"
        assert data["branch"] == "master"

    def test_outside_work_tree_is_all_unknown(self, tmp_path: Path) -> None:
        bare = tmp_path / "not-a-repo"
        bare.mkdir()
        data = run_script(PUBLISH, bare, "verify-endstate")
        assert data["checks"]["tree_clean"]["status"] == "unknown"
        assert data["checks"]["pushed"]["status"] == "unknown"
        assert data["checks"]["pr_open"]["status"] == "unknown"


class TestReleaseEndstate:
    def test_tag_local_and_remote(self, repo: Path) -> None:
        git(repo, "tag", "-a", "v1.0.0", "-m", "release")
        git(repo, "push", "-q", "origin", "v1.0.0")
        data = run_script(RELEASE, repo, "verify-endstate", "1", "v1.0.0")
        checks = data["checks"]
        assert checks["tag_local"]["status"] == "true"
        assert checks["tag_remote"]["status"] == "true"
        # gh unavailable: unknown, never false
        assert checks["pr_merged"]["status"] == "unknown"
        assert checks["release_exists"]["status"] == "unknown"
        assert checks["wip_marker_cleared"]["status"] == "true"

    def test_missing_tag_is_false_locally(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "verify-endstate", "1", "v9.9.9")
        assert data["checks"]["tag_local"]["status"] == "false"

    def test_absent_remote_tag_is_false_not_unknown(self, repo: Path) -> None:
        # Regression: the ls-remote result branch must report a reachable
        # remote that simply lacks the tag as `false` (prior $? bug made it
        # unreachable).
        git(repo, "tag", "-a", "v5.0.0", "-m", "local only")
        data = run_script(RELEASE, repo, "verify-endstate", "1", "v5.0.0")
        assert data["checks"]["tag_local"]["status"] == "true"
        assert data["checks"]["tag_remote"]["status"] == "false"

    def test_verifier_never_fetches(self, repo: Path) -> None:
        # Read-only contract: remote-tracking refs must not appear/advance.
        before = git(repo, "for-each-ref", "refs/remotes")
        git(repo, "tag", "-a", "v1.0.0", "-m", "r")
        git(repo, "push", "-q", "origin", "v1.0.0")
        run_script(RELEASE, repo, "verify-endstate", "1", "v1.0.0")
        after = git(repo, "for-each-ref", "refs/remotes")
        assert before == after

    def test_no_release_flag_marks_not_applicable(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "verify-endstate", "1", "--no-release")
        checks = data["checks"]
        assert checks["tag_local"]["status"] == "not_applicable"
        assert checks["release_exists"]["status"] == "not_applicable"

    def test_wip_marker_present_is_false(self, repo: Path) -> None:
        marker = repo / ".specify"
        marker.mkdir()
        (marker / ".ms-wip-publish").write_text("reason=--no-ci publish\n")
        data = run_script(RELEASE, repo, "verify-endstate", "1", "--no-release")
        assert data["checks"]["wip_marker_cleared"]["status"] == "false"

    def test_ledger_not_applicable_without_flag(self, repo: Path) -> None:
        data = run_script(RELEASE, repo, "verify-endstate", "1", "--no-release")
        assert data["checks"]["ledger_shipped"]["status"] == "not_applicable"

    def _push_ledger(self, repo: Path, status: str) -> None:
        docs = repo / "docs" / "prd"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "feature-map.progress.md").write_text(
            "# Ledger\n\n| Feature | Depends on | Status |\n"
            "|---------|------------|--------|\n"
            f"| 006 shipped-widgets | — | {status} |\n"
        )
        git(repo, "add", "docs")
        git(repo, "commit", "-q", "-m", "chore: ledger")
        git(repo, "push", "-q", "origin", "master")
        git(repo, "remote", "set-head", "origin", "master")

    def test_ledger_status_column_shipped_is_true(self, repo: Path) -> None:
        self._push_ledger(repo, "✅ shipped")
        data = run_script(
            RELEASE, repo, "verify-endstate", "1", "--no-release", "--ledger-feature", "6"
        )
        assert data["checks"]["ledger_shipped"]["status"] == "true"

    def test_ledger_shipped_in_name_column_does_not_count(self, repo: Path) -> None:
        # The Feature name contains "shipped" but the Status column is planned.
        self._push_ledger(repo, "⬜ planned")
        data = run_script(
            RELEASE, repo, "verify-endstate", "1", "--no-release", "--ledger-feature", "6"
        )
        assert data["checks"]["ledger_shipped"]["status"] == "false"

    def test_repository_url_credentials_are_stripped(self, repo: Path) -> None:
        git(repo, "remote", "set-url", "origin", "https://user:secret@example.com/x.git")
        data = run_script(RELEASE, repo, "verify-endstate", "1", "--no-release")
        assert data["repository"] == "https://example.com/x.git"
        assert "secret" not in json.dumps(data)
