#!/usr/bin/env python3
"""SPECTER workflow broadcast sync (/ms.sync engine).

Pushes the manifest-listed workflow files (``scripts/specter_sync_manifest.json``:
``.claude`` commands/skills/agents, gate scripts, doc templates, AGENTS.md /
CLAUDE.md) from this SPECTER checkout to every repo registered in the
machine-local registry (``~/.claude/specter-sync.json``).

Safety model for a public template repo: the registry lives OUTSIDE the repo,
so a stranger cloning SPECTER has no registry and /ms.sync no-ops for them.
Additionally the registry's ``source`` must match this checkout (path or
normalized origin URL), so a fork never broadcasts from the wrong source.

Per-target conflict model: ``.specter-sync-state.json`` in each target records,
per file, the SPECTER commit whose content was *last actually applied*. That
commit's content is the 3-way merge base:

  target file  | SPECTER file | action
  -------------+--------------+---------------------------------------------
  == base      | changed      | UPDATE (safe overwrite)
  changed      | == base      | KEPT-LOCAL (local specialization wins)
  changed      | changed      | git merge-file 3-way; clean -> MERGED,
               |              | overlapping -> CONFLICT (+ <file>.specter-new)
  no base yet  | differs      | CONFLICT (conservative first-sync stance)

CONFLICT never advances the baseline, so an unresolved conflict resurfaces on
every sync until the target either adopts the upstream hunks (then a later
3-way merges clean) or excludes the file in its registry entry.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REGISTRY_DEFAULT = Path.home() / ".claude" / "specter-sync.json"
MANIFEST_RELPATH = "scripts/specter_sync_manifest.json"
STATE_FILENAME = ".specter-sync-state.json"
CONFLICT_SUFFIX = ".specter-new"
# Identity for the sync commits pushed into target repos. Uses the template
# owner's real GitHub identity so sync commits attribute to their account.
COMMIT_IDENTITY = [
    "-c",
    "user.name=beomeodev",
    "-c",
    "user.email=66253976+beomeodev@users.noreply.github.com",
]

NEW = "NEW"
SAME = "SAME"
UPDATE = "UPDATE"
MERGED = "MERGED"
KEPT_LOCAL = "KEPT-LOCAL"
CONFLICT = "CONFLICT"
EXCLUDED = "EXCLUDED"
DELETED_LOCAL = "DELETED-LOCAL"
BASELINE_ADVANCING = {NEW, SAME, UPDATE, MERGED}


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)


def git_out(args: list[str], cwd: Path) -> str:
    result = run_git(args, cwd)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.decode(errors='replace')}")
    return result.stdout.decode().strip()


def normalize_repo_url(url: str) -> str:
    normalized = url.strip()
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized[len("git@github.com:"):]
    if normalized.endswith(".git"):
        normalized = normalized[: -len(".git")]
    return normalized.rstrip("/")


def origin_url(root: Path) -> str:
    result = run_git(["remote", "get-url", "origin"], root)
    return result.stdout.decode().strip() if result.returncode == 0 else ""


def source_matches(registry_source: str, root: Path) -> bool:
    try:
        if Path(registry_source).expanduser().resolve() == root.resolve():
            return True
    except OSError:
        pass
    origin = origin_url(root)
    return bool(origin) and normalize_repo_url(registry_source) == normalize_repo_url(origin)


def load_manifest(root: Path) -> tuple[list[str], list[str]]:
    manifest = json.loads((root / MANIFEST_RELPATH).read_text(encoding="utf-8"))
    return manifest["include"], manifest.get("exclude", [])


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def manifest_files(root: Path) -> list[str]:
    include, exclude = load_manifest(root)
    tracked = git_out(["ls-tree", "-r", "--name-only", "HEAD"], root).splitlines()
    return sorted(p for p in tracked if matches_any(p, include) and not matches_any(p, exclude))


def dirty_manifest_files(root: Path, files: list[str]) -> list[str]:
    if not files:
        return []
    out = git_out(["status", "--porcelain", "--", *files], root)
    return [line[3:] for line in out.splitlines()]


def git_show(root: Path, commit: str, relpath: str) -> bytes | None:
    result = run_git(["show", f"{commit}:{relpath}"], root)
    return result.stdout if result.returncode == 0 else None


def three_way_merge(current: bytes, base: bytes, other: bytes) -> bytes | None:
    """Return merged content, or None when the changes overlap (conflict)."""
    with tempfile.TemporaryDirectory(prefix="specter-merge-") as tmp:
        paths = []
        for name, content in (("current", current), ("base", base), ("other", other)):
            path = Path(tmp) / name
            path.write_bytes(content)
            paths.append(str(path))
        result = subprocess.run(["git", "merge-file", "-p", *paths], capture_output=True, check=False)
        return result.stdout if result.returncode == 0 else None


def decide_file(src: bytes, base: bytes | None, dst: bytes | None) -> tuple[str, bytes | None]:
    """Classify one file; return (status, content to write into the target or None)."""
    if dst is None:
        if base is None:
            return NEW, src
        return DELETED_LOCAL, None
    if dst == src:
        return SAME, None
    if base is None:
        return CONFLICT, None
    if dst == base:
        return UPDATE, src
    if src == base:
        return KEPT_LOCAL, None
    merged = three_way_merge(dst, base, src)
    if merged is None:
        return CONFLICT, None
    return MERGED, merged


def load_state(clone_dir: Path) -> dict[str, str]:
    state_path = clone_dir / STATE_FILENAME
    if not state_path.exists():
        return {}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    files = state.get("files", {})
    return {str(k): str(v) for k, v in files.items()}


def apply_file(clone_dir: Path, relpath: str, status: str, content: bytes | None, src: bytes) -> list[str]:
    """Write the decided outcome for one file into the clone; return paths to stage."""
    staged: list[str] = []
    conflict_path = clone_dir / (relpath + CONFLICT_SUFFIX)
    if status == CONFLICT:
        conflict_path.parent.mkdir(parents=True, exist_ok=True)
        conflict_path.write_bytes(src)
        staged.append(relpath + CONFLICT_SUFFIX)
    elif conflict_path.exists():
        conflict_path.unlink()  # stale marker from a previously resolved conflict
        staged.append(relpath + CONFLICT_SUFFIX)
    if content is not None:
        target_path = clone_dir / relpath
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
        staged.append(relpath)
    return staged


def commit_and_push(clone_dir: Path, staged: list[str], source_head: str) -> tuple[str | None, str | None]:
    """Stage, commit, push. Return (commit subject or None, error or None)."""
    run_git(["add", "--", *staged], clone_dir)
    if run_git(["diff", "--cached", "--quiet"], clone_dir).returncode == 0:
        return None, None
    subject = f"chore(specter-sync): apply SPECTER workflow @ {source_head[:10]}"
    commit = run_git([*COMMIT_IDENTITY, "commit", "-m", subject], clone_dir)
    if commit.returncode != 0:
        return None, f"commit failed: {commit.stderr.decode(errors='replace')}"
    push = run_git(["push", "origin", "HEAD"], clone_dir)
    if push.returncode != 0:
        return subject, f"push failed: {push.stderr.decode(errors='replace')}"
    return subject, None


def sync_target(
    source_root: Path,
    source_head: str,
    files: list[str],
    target: dict,
    work_dir: Path,
    dry_run: bool,
) -> dict:
    repo = target["repo"]
    name = target.get("name") or normalize_repo_url(repo).rsplit("/", 1)[-1]
    report: dict = {"name": name, "repo": repo, "results": [], "commit": None, "error": None}
    clone_dir = work_dir / name
    clone = run_git(["clone", repo, str(clone_dir)], work_dir)
    if clone.returncode != 0:
        report["error"] = f"clone failed: {clone.stderr.decode(errors='replace')}"
        return report

    baselines = load_state(clone_dir)
    excludes = target.get("exclude", [])
    staged: list[str] = []
    for relpath in files:
        if matches_any(relpath, excludes):
            report["results"].append((relpath, EXCLUDED))
            continue
        src = (source_root / relpath).read_bytes()
        base_commit = baselines.get(relpath)
        base = git_show(source_root, base_commit, relpath) if base_commit else None
        dst_path = clone_dir / relpath
        dst = dst_path.read_bytes() if dst_path.exists() else None
        status, content = decide_file(src, base, dst)
        if status in BASELINE_ADVANCING:
            baselines[relpath] = source_head
        if not dry_run:
            staged.extend(apply_file(clone_dir, relpath, status, content, src))
        report["results"].append((relpath, status))

    if dry_run:
        return report
    state = {"source": origin_url(source_root) or str(source_root), "files": baselines}
    (clone_dir / STATE_FILENAME).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    staged.append(STATE_FILENAME)
    report["commit"], report["error"] = commit_and_push(clone_dir, staged, source_head)
    return report


def print_report(report: dict, dry_run: bool) -> None:
    print(f"\n=== {report['name']} ({report['repo']}) ===")
    if report["error"] and not report["results"]:
        print(f"  ERROR: {report['error']}")
        return
    counts: dict[str, int] = {}
    for relpath, status in report["results"]:
        counts[status] = counts.get(status, 0) + 1
        if status != SAME:
            print(f"  {status:<13} {relpath}")
    summary = ", ".join(f"{status}={n}" for status, n in sorted(counts.items()))
    print(f"  -- {summary or 'no files'}")
    if report["error"]:
        print(f"  ERROR: {report['error']}")
    elif dry_run:
        print("  (dry-run: nothing written)")
    elif report["commit"]:
        print(f"  pushed: {report['commit']}")
    else:
        print("  already up to date (no commit)")


def cmd_sync(args: argparse.Namespace) -> int:
    root = args.root
    registry_path = args.registry
    if not registry_path.exists():
        print(f"No sync registry at {registry_path} — nothing to do.")
        print("This is expected unless you registered target repos (see /ms.sync docs).")
        return 0
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    targets = registry.get("targets", [])
    if not targets:
        print(f"Sync registry {registry_path} has no targets — nothing to do.")
        return 0
    if not source_matches(str(registry.get("source", "")), root):
        print(f"❌ Registry source '{registry.get('source')}' does not match this checkout ({root}).")
        print("Refusing to broadcast from an unregistered source (fork/clone protection).")
        return 1

    files = manifest_files(root)
    if not files:
        print("❌ Manifest matched no tracked files — check scripts/specter_sync_manifest.json.")
        return 1
    dirty = dirty_manifest_files(root, files)
    if dirty:
        print("❌ Manifest files have uncommitted changes; commit them first (sync baselines are git commits):")
        for path in dirty:
            print(f"  - {path}")
        return 1

    source_head = git_out(["rev-parse", "HEAD"], root)
    work_dir = args.work_dir or Path(tempfile.mkdtemp(prefix="specter-sync-"))
    work_dir.mkdir(parents=True, exist_ok=True)
    selected = [t for t in targets if args.target in (None, t.get("name"))]
    if args.target and not selected:
        print(f"❌ No registered target named '{args.target}'.")
        return 1

    print(f"Broadcasting {len(files)} files @ {source_head[:10]} to {len(selected)} target(s)"
          + (" [dry-run]" if args.dry_run else ""))
    conflicts = 0
    errors = 0
    for target in selected:
        report = sync_target(root, source_head, files, target, work_dir, args.dry_run)
        print_report(report, args.dry_run)
        conflicts += sum(1 for _, status in report["results"] if status == CONFLICT)
        errors += 1 if report["error"] else 0
    if conflicts:
        print(f"\n⚠️  {conflicts} CONFLICT file(s): resolve in each target project"
              f" (compare with the pushed *{CONFLICT_SUFFIX} file, merge, delete the marker).")
    if errors:
        print(f"\n❌ {errors} target(s) had errors.")
        return 1
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    registry_path = args.registry
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"source": origin_url(args.root) or str(args.root), "targets": []}
    repo_key = normalize_repo_url(args.repo)
    for target in registry["targets"]:
        if normalize_repo_url(target["repo"]) == repo_key:
            print(f"Already registered: {target['repo']} (name={target.get('name')})")
            return 0
    name = args.name or repo_key.rsplit("/", 1)[-1]
    registry["targets"].append({"name": name, "repo": args.repo})
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Registered sync target '{name}' -> {args.repo} in {registry_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=["sync", "register"], default="sync")
    parser.add_argument("repo", nargs="?", help="repo URL to add (register mode only)")
    parser.add_argument("--name", help="target name for register mode (default: repo basename)")
    parser.add_argument("--registry", type=Path, default=REGISTRY_DEFAULT, help="registry JSON path")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="SPECTER checkout root (tests only)")
    parser.add_argument("--work-dir", type=Path, default=None, help="clone workspace (default: temp dir)")
    parser.add_argument("--target", help="sync only the target with this registered name")
    parser.add_argument("--dry-run", action="store_true", help="report decisions without writing/pushing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "register":
        if not args.repo:
            print("❌ register mode needs a repo URL: specter_sync.py register <repo-url> [--name NAME]")
            return 1
        return cmd_register(args)
    return cmd_sync(args)


if __name__ == "__main__":
    sys.exit(main())
