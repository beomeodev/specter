"""End-to-end tests for scripts/specter/specter_sync.py (/ms.sync engine).

Each test builds a throwaway SPECTER source repo and bare target repos on
disk, then drives the real sync flow (clone -> 3-way decide -> commit -> push)
and asserts on the target's committed state.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts"
    / "specter"
    / "specter_sync.py"
)
_spec = importlib.util.spec_from_file_location("specter_sync", MODULE_PATH)
assert _spec and _spec.loader
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)

CMD_RELPATH = ".claude/commands/ms.plan.md"
AGENTS_RELPATH = "AGENTS.md"
MANIFEST = {
    "include": [".claude/commands/ms.*.md", "AGENTS.md"],
    "exclude": [".claude/commands/ms.sync.md"],
}


def test_default_root_resolves_to_repo_root() -> None:
    # Regression: after relocating the engine under scripts/specter/, the
    # --root default kept climbing only two levels and built the doubled path
    # <repo>/scripts/scripts/specter/... , crashing manifest loading. Tests
    # always inject --root, so pin the untested default here.
    root = sync.default_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / sync.MANIFEST_RELPATH).is_file()


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@local", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def make_source(tmp_path: Path) -> Path:
    src = tmp_path / "specter-src"
    src.mkdir()
    git(src, "init", "-b", "main")
    (src / ".claude/commands").mkdir(parents=True)
    (src / CMD_RELPATH).write_text(
        "plan v1\n" + "".join(f"line{i}\n" for i in range(1, 11))
    )
    (src / ".claude/commands/ms.sync.md").write_text("must not sync\n")
    (src / AGENTS_RELPATH).write_text("agents v1\n")
    (src / sync.MANIFEST_RELPATH).parent.mkdir(parents=True, exist_ok=True)
    (src / sync.MANIFEST_RELPATH).write_text(json.dumps(MANIFEST))
    commit_all(src, "source v1")
    return src


def make_target(tmp_path: Path, name: str, files: dict[str, str] | None = None) -> Path:
    """Create a bare origin (what GitHub is) seeded with an initial commit."""
    bare = tmp_path / f"{name}.git"
    bare.mkdir()
    git(bare, "init", "--bare", "-b", "main")
    seed = tmp_path / f"{name}-seed"
    git(tmp_path, "clone", str(bare), str(seed))
    git(seed, "checkout", "-b", "main")
    (seed / "README.md").write_text(f"# {name}\n")
    for relpath, content in (files or {}).items():
        path = seed / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    commit_all(seed, "target init")
    git(seed, "push", "origin", "main")
    return bare


def write_registry(
    tmp_path: Path, src: Path, bare: Path, exclude: list[str] | None = None
) -> Path:
    registry_path = tmp_path / "registry.json"
    target: dict = {"name": "proj", "repo": str(bare)}
    if exclude:
        target["exclude"] = exclude
    registry_path.write_text(json.dumps({"source": str(src), "targets": [target]}))
    return registry_path


_run_counter = 0


def run_sync(tmp_path: Path, src: Path, registry: Path, *extra: str) -> int:
    global _run_counter
    _run_counter += 1
    work = tmp_path / f"work-{_run_counter}"
    return sync.main(
        [
            "--registry",
            str(registry),
            "--root",
            str(src),
            "--work-dir",
            str(work),
            *extra,
        ]
    )


def bare_file(bare: Path, relpath: str) -> str | None:
    result = subprocess.run(
        ["git", "--git-dir", str(bare), "show", f"main:{relpath}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def update_source(src: Path, relpath: str, content: str, message: str) -> None:
    (src / relpath).write_text(content)
    commit_all(src, message)


def customize_target(tmp_path: Path, bare: Path, relpath: str, content: str) -> None:
    global _run_counter
    _run_counter += 1
    clone = tmp_path / f"customize-{_run_counter}"
    git(tmp_path, "clone", str(bare), str(clone))
    path = clone / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    commit_all(clone, f"customize {relpath}")
    git(clone, "push", "origin", "main")


def test_fresh_sync_copies_manifest_files_and_state(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)

    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, CMD_RELPATH) == (src / CMD_RELPATH).read_text()
    assert bare_file(bare, AGENTS_RELPATH) == "agents v1\n"
    assert bare_file(bare, ".claude/commands/ms.sync.md") is None  # manifest exclude
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    head = git(src, "rev-parse", "HEAD")
    assert state["files"][CMD_RELPATH] == head


def test_temp_work_dir_is_removed_after_sync(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    tmp_root = tmp_path / "tmpdir"
    tmp_root.mkdir()
    # tempfile caches gettempdir(), so TMPDIR alone would not redirect mkdtemp.
    monkeypatch.setattr(sync.tempfile, "tempdir", str(tmp_root))

    code = sync.main(["--registry", str(registry), "--root", str(src)])

    assert code == 0
    assert list(tmp_root.iterdir()) == []


def test_explicit_work_dir_is_kept_after_sync(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    work = tmp_path / "explicit-work"

    code = sync.main(
        ["--registry", str(registry), "--root", str(src), "--work-dir", str(work)]
    )

    assert code == 0
    assert (work / "proj").is_dir()


def test_source_update_overwrites_untouched_target(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    update_source(src, AGENTS_RELPATH, "agents v2\n", "source v2")
    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, AGENTS_RELPATH) == "agents v2\n"


def test_local_specialization_kept_when_source_unchanged(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    customize_target(tmp_path, bare, AGENTS_RELPATH, "agents custom\n")
    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, AGENTS_RELPATH) == "agents custom\n"
    assert bare_file(bare, AGENTS_RELPATH + sync.CONFLICT_SUFFIX) is None


def test_non_overlapping_changes_merge_cleanly(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    original = (src / CMD_RELPATH).read_text()
    customize_target(
        tmp_path, bare, CMD_RELPATH, original.replace("line1\n", "line1 CUSTOM\n")
    )
    update_source(
        src, CMD_RELPATH, original.replace("line10\n", "line10 UPSTREAM\n"), "source v2"
    )
    assert run_sync(tmp_path, src, registry) == 0

    merged = bare_file(bare, CMD_RELPATH) or ""
    assert "line1 CUSTOM" in merged
    assert "line10 UPSTREAM" in merged


def test_overlapping_changes_conflict_without_overwrite(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    original = (src / CMD_RELPATH).read_text()
    local = original.replace("line5\n", "line5 CUSTOM\n")
    upstream = original.replace("line5\n", "line5 UPSTREAM\n")
    customize_target(tmp_path, bare, CMD_RELPATH, local)
    update_source(src, CMD_RELPATH, upstream, "source v2")
    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, CMD_RELPATH) == local  # local content untouched
    assert bare_file(bare, CMD_RELPATH + sync.CONFLICT_SUFFIX) == upstream


def test_first_sync_over_diverged_file_is_conservative_conflict(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(
        tmp_path, "proj", files={AGENTS_RELPATH: "pre-existing custom\n"}
    )
    registry = write_registry(tmp_path, src, bare)

    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, AGENTS_RELPATH) == "pre-existing custom\n"
    assert bare_file(bare, AGENTS_RELPATH + sync.CONFLICT_SUFFIX) == "agents v1\n"


def test_target_exclude_skips_file(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare, exclude=[AGENTS_RELPATH])

    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, AGENTS_RELPATH) is None
    assert bare_file(bare, CMD_RELPATH) is not None


def test_missing_registry_is_a_friendly_noop(tmp_path: Path, capsys) -> None:
    src = make_source(tmp_path)

    assert run_sync(tmp_path, src, tmp_path / "absent.json") == 0

    assert "nothing to do" in capsys.readouterr().out


def test_source_mismatch_refuses_to_broadcast(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "source": "git@github.com:someone-else/other.git",
                "targets": [{"name": "proj", "repo": str(bare)}],
            }
        )
    )

    assert run_sync(tmp_path, src, registry) == 1
    assert bare_file(bare, AGENTS_RELPATH) is None


def test_dirty_manifest_file_aborts(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    (src / AGENTS_RELPATH).write_text("uncommitted edit\n")

    assert run_sync(tmp_path, src, registry) == 1
    assert bare_file(bare, AGENTS_RELPATH) is None


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)

    assert run_sync(tmp_path, src, registry, "--dry-run") == 0

    assert bare_file(bare, AGENTS_RELPATH) is None
    assert bare_file(bare, sync.STATE_FILENAME) is None


def test_symlinked_target_path_is_refused(tmp_path: Path) -> None:
    """2026-07-18 audit #20: a target repo committing a symlink at a managed
    path must not let sync read or write through it outside the clone."""
    src = make_source(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("untouched\n")

    bare = tmp_path / "proj.git"
    bare.mkdir()
    git(bare, "init", "--bare", "-b", "main")
    seed = tmp_path / "proj-seed"
    git(tmp_path, "clone", str(bare), str(seed))
    git(seed, "checkout", "-b", "main")
    (seed / "README.md").write_text("# proj\n")
    link = seed / CMD_RELPATH
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)
    commit_all(seed, "target init with symlinked managed path")
    git(seed, "push", "origin", "main")

    registry = write_registry(tmp_path, src, bare)
    run_sync(tmp_path, src, registry)

    assert outside.read_text() == "untouched\n"
    synced = bare_file(bare, AGENTS_RELPATH)
    assert synced is not None  # safe managed files still sync
    linked = bare_file(bare, CMD_RELPATH)
    assert linked != (src / CMD_RELPATH).read_text()  # symlink path untouched


def test_register_creates_and_appends_registry(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    registry = tmp_path / "registry.json"

    code = sync.main(
        [
            "register",
            "git@github.com:me/proj-a.git",
            "--registry",
            str(registry),
            "--root",
            str(src),
        ]
    )
    assert code == 0
    data = json.loads(registry.read_text())
    assert data["targets"] == [
        {"name": "proj-a", "repo": "git@github.com:me/proj-a.git"}
    ]

    # duplicate registration (https form of the same repo) is a no-op
    code = sync.main(
        [
            "register",
            "https://github.com/me/proj-a",
            "--registry",
            str(registry),
            "--root",
            str(src),
        ]
    )
    assert code == 0
    assert len(json.loads(registry.read_text())["targets"]) == 1


def delete_source(src: Path, relpath: str, message: str) -> None:
    git(src, "rm", "-q", relpath)
    git(src, "commit", "-m", message)


def test_upstream_deletion_removes_unmodified_target_file(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0
    assert bare_file(bare, CMD_RELPATH) is not None

    delete_source(src, CMD_RELPATH, "retire ms.plan")
    assert run_sync(tmp_path, src, registry) == 0

    assert bare_file(bare, CMD_RELPATH) is None
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    assert CMD_RELPATH not in state["files"]


def test_upstream_deletion_keeps_customized_target_file(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    customize_target(tmp_path, bare, CMD_RELPATH, "customized plan\n")
    delete_source(src, CMD_RELPATH, "retire ms.plan")
    assert run_sync(tmp_path, src, registry) == 0

    # Specialization wins: the fork survives, but it is no longer managed.
    assert bare_file(bare, CMD_RELPATH) == "customized plan\n"
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    assert CMD_RELPATH not in state["files"]

    # And it must not resurface on the next sync.
    assert run_sync(tmp_path, src, registry) == 0
    assert bare_file(bare, CMD_RELPATH) == "customized plan\n"


def test_manifest_narrowing_does_not_delete(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    narrowed = {"include": ["AGENTS.md"], "exclude": []}
    (src / sync.MANIFEST_RELPATH).write_text(json.dumps(narrowed))
    commit_all(src, "narrow manifest (ms.plan still tracked)")
    assert run_sync(tmp_path, src, registry) == 0

    # The file left the manifest but still exists upstream: never delete,
    # and keep the baseline so a re-widened manifest can still 3-way merge.
    assert bare_file(bare, CMD_RELPATH) is not None
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    assert CMD_RELPATH in state["files"]


def test_dry_run_reports_deletion_without_writing(tmp_path: Path) -> None:
    src = make_source(tmp_path)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)
    assert run_sync(tmp_path, src, registry) == 0

    delete_source(src, CMD_RELPATH, "retire ms.plan")
    assert run_sync(tmp_path, src, registry, "--dry-run") == 0

    assert bare_file(bare, CMD_RELPATH) is not None
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    assert CMD_RELPATH in state["files"]


def make_symlink_source(tmp_path: Path, agents_body: str) -> Path:
    """Source where CLAUDE.md is a symlink to AGENTS.md (SPECTER's real layout),
    both in the manifest."""
    src = tmp_path / "specter-src-symlink"
    src.mkdir()
    git(src, "init", "-b", "main")
    (src / ".claude/commands").mkdir(parents=True)
    (src / CMD_RELPATH).write_text("plan v1\n")
    (src / ".claude/commands/ms.sync.md").write_text("must not sync\n")
    (src / AGENTS_RELPATH).write_text(agents_body)
    (src / "CLAUDE.md").symlink_to(AGENTS_RELPATH)
    (src / sync.MANIFEST_RELPATH).parent.mkdir(parents=True, exist_ok=True)
    (src / sync.MANIFEST_RELPATH).write_text(
        json.dumps(
            {
                "include": [".claude/commands/ms.*.md", "AGENTS.md", "CLAUDE.md"],
                "exclude": [".claude/commands/ms.sync.md"],
            }
        )
    )
    commit_all(src, "source v1")
    return src


def test_symlinked_manifest_file_resolves_to_target_content(tmp_path: Path) -> None:
    """git_show follows an in-tree symlink so CLAUDE.md -> AGENTS.md compares by
    target content, not the 9-byte symlink blob."""
    agents_v1 = "agents header\n" + "".join(f"line{i}\n" for i in range(1, 11))
    src = make_symlink_source(tmp_path, agents_v1)

    head = git(src, "rev-parse", "HEAD")
    resolved = sync.git_show(src, head, "CLAUDE.md")
    assert resolved == agents_v1.encode()  # followed the symlink, not "AGENTS.md"
    assert sync.tree_mode(src, head, "CLAUDE.md") == sync.SYMLINK_MODE


def test_symlinked_file_merges_upstream_body_onto_customized_target(
    tmp_path: Path,
) -> None:
    """A target that turned CLAUDE.md into a regular file with an extra project
    tail must 3-way merge upstream AGENTS.md body changes onto its content
    (MERGED, baseline advances) instead of conflicting forever."""
    agents_v1 = "agents header\n" + "".join(f"line{i}\n" for i in range(1, 11))
    src = make_symlink_source(tmp_path, agents_v1)
    bare = make_target(tmp_path, "proj")
    registry = write_registry(tmp_path, src, bare)

    # First sync seeds the target CLAUDE.md as AGENTS.md content + baseline.
    assert run_sync(tmp_path, src, registry) == 0
    assert bare_file(bare, "CLAUDE.md") == agents_v1

    # Target keeps the body and appends a project-specific tail.
    tail = "\n## Project-Specific\nlocal rule\n"
    customize_target(tmp_path, bare, "CLAUDE.md", agents_v1 + tail)

    # Upstream changes the AGENTS.md body that CLAUDE.md points at.
    agents_v2 = agents_v1.replace("agents header\n", "agents header v2\n")
    update_source(src, AGENTS_RELPATH, agents_v2, "source v2")

    assert run_sync(tmp_path, src, registry) == 0

    merged = bare_file(bare, "CLAUDE.md")
    assert "agents header v2" in merged  # upstream body change flowed in
    assert "local rule" in merged  # project tail preserved
    assert bare_file(bare, "CLAUDE.md" + sync.CONFLICT_SUFFIX) is None  # no conflict
    state = json.loads(bare_file(bare, sync.STATE_FILENAME) or "{}")
    assert state["files"]["CLAUDE.md"] == git(src, "rev-parse", "HEAD")
