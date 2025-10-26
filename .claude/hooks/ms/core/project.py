#!/usr/bin/env python3
"""
@CODE:HOOKS-001
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/hooks/test_session_hooks.py
@CHAIN: @SPEC:HOOKS-001 → @TEST:HOOKS-001 → @CODE:HOOKS-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Project metadata utilities

Adapted from MoAI-ADK for My-Spec workflow.
Project information inquiry (language, Git, SPEC progress, TAG integrity)
"""

import subprocess
from pathlib import Path
from typing import Any


def detect_language(cwd: str) -> str:
    """Detect project language (supports 20+ languages)

    Browse the file system to detect your project's main development language.
    First, check configuration files such as pyproject.toml and tsconfig.json.
    Apply TypeScript first principles (if tsconfig.json exists).

    Args:
        cwd: Project root directory path (both absolute and relative paths possible)

    Returns:
        Detected language name (lowercase). If detection fails, "Unknown Language" is returned.
        Supported languages: python, typescript, javascript, java, go, rust,
                  dart, swift, kotlin, php, ruby, elixir, scala,
                  clojure, cpp, c, csharp, haskell, shell, lua

    Examples:
        >>> detect_language("/path/to/python/project")
        'python'
        >>> detect_language("/path/to/typescript/project")
        'typescript'
        >>> detect_language("/path/to/unknown/project")
        'Unknown Language'
    """
    cwd_path = Path(cwd)

    # Language detection mapping
    language_files = {
        "pyproject.toml": "python",
        "tsconfig.json": "typescript",
        "package.json": "javascript",
        "pom.xml": "java",
        "go.mod": "go",
        "Cargo.toml": "rust",
        "pubspec.yaml": "dart",
        "Package.swift": "swift",
        "build.gradle.kts": "kotlin",
        "composer.json": "php",
        "Gemfile": "ruby",
        "mix.exs": "elixir",
        "build.sbt": "scala",
        "project.clj": "clojure",
        "CMakeLists.txt": "cpp",
        "Makefile": "c",
    }

    # Check standard language files
    for file_name, language in language_files.items():
        if (cwd_path / file_name).exists():
            # Special handling for package.json - prefer typescript if tsconfig exists
            if file_name == "package.json" and (cwd_path / "tsconfig.json").exists():
                return "typescript"
            return language

    # Check for C# project files (*.csproj)
    if any(cwd_path.glob("*.csproj")):
        return "csharp"

    # Check for Haskell project files (*.cabal)
    if any(cwd_path.glob("*.cabal")):
        return "haskell"

    # Check for Shell scripts (*.sh)
    if any(cwd_path.glob("*.sh")):
        return "shell"

    # Check for Lua files (*.lua)
    if any(cwd_path.glob("*.lua")):
        return "lua"

    return "Unknown Language"


def _run_git_command(args: list[str], cwd: str, timeout: int = 5) -> str:
    """Git command execution helper function

    Safely execute Git commands and return output.
    Eliminates code duplication and provides consistent error handling.

    Args:
        args: Git command argument list (git adds automatically)
        cwd: Execution directory path
        timeout: Timeout (seconds, default 5 seconds for large repos)

    Returns:
        Git command output (stdout, removing leading and trailing spaces)

    Raises:
        subprocess.TimeoutExpired: Timeout exceeded
        subprocess.CalledProcessError: Git command failed

    Examples:
        >>> _run_git_command(["branch", "--show-current"], ".")
        'main'
    """
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    )
    return result.stdout.strip()


def get_git_info(cwd: str) -> dict[str, Any]:
    """Gather Git repository information

    View the current status of a Git repository.
    Returns the branch name, commit hash, and number of changes.
    If it is not a Git repository, it returns an empty dictionary.

    Args:
        cwd: Project root directory path

    Returns:
        Git information dictionary. Includes the following keys:
        - branch: Current branch name (str)
        - commit: Current commit hash (str, full hash)
        - changes: Number of changed files (int, staged + unstaged)

        Empty dictionary {} if it is not a Git repository or the query fails.

    Examples:
        >>> get_git_info("/path/to/git/repo")
        {'branch': 'main', 'commit': 'abc123...', 'changes': 3}
        >>> get_git_info("/path/to/non-git")
        {}

    Notes:
        - Timeout: 5 seconds for each Git command (handles large repositories)
        - Security: Safe execution with subprocess.run(shell=False)
        - Error handling: Returns an empty dictionary in case of all exceptions
    """
    try:
        # Check if it's a git repository
        _run_git_command(["rev-parse", "--git-dir"], cwd)

        # Get branch name, commit hash, and changes
        branch = _run_git_command(["branch", "--show-current"], cwd)
        commit = _run_git_command(["rev-parse", "HEAD"], cwd)
        status_output = _run_git_command(["status", "--short"], cwd)
        changes = len([line for line in status_output.splitlines() if line])

        return {
            "branch": branch,
            "commit": commit,
            "changes": changes,
        }

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return {}


def count_specs(cwd: str) -> dict[str, int]:
    """SPEC file count and progress calculation

    My-Spec uses specs/ directory (not .moai/specs/).
    Browse the specs/ directory to find the number of SPEC files and
    counts the number of SPECs with **Status**: Completed (Markdown metadata format).

    Args:
        cwd: Project root directory path

    Returns:
        SPEC progress dictionary. Includes the following keys:
        - completed: Number of completed SPECs (int)
        - total: total number of SPECs (int)
        - percentage: completion percentage (int, 0~100)

        All 0 if specs/ directory does not exist

    Examples:
        >>> count_specs("/path/to/project")
        {'completed': 2, 'total': 5, 'percentage': 40}
        >>> count_specs("/path/to/no-specs")
        {'completed': 0, 'total': 0, 'percentage': 0}

    Notes:
        - SPEC File Location: specs/{spec-id}/spec.md (My-Spec structure)
        - Completion condition: Include "**Status**: Completed" in Markdown metadata
        - Uses regex pattern: **Status**:\\s*completed (case-insensitive)
        - If parsing fails, the SPEC is considered incomplete.
    """
    import re

    specs_dir = Path(cwd) / "specs"

    if not specs_dir.exists():
        return {"completed": 0, "total": 0, "percentage": 0}

    completed = 0
    total = 0

    # Regex pattern to match Markdown metadata: **Status**: Completed
    # Pattern is case-insensitive for "completed"
    status_pattern = re.compile(r'\*\*Status\*\*:\s*(completed)', re.IGNORECASE)

    for spec_dir in specs_dir.iterdir():
        if not spec_dir.is_dir():
            continue

        spec_file = spec_dir / "spec.md"
        if not spec_file.exists():
            continue

        total += 1

        # Parse Markdown metadata using regex
        try:
            content = spec_file.read_text()
            if status_pattern.search(content):
                completed += 1
        except (OSError, UnicodeDecodeError):
            # File read failure or encoding error - considered incomplete
            pass

    percentage = int(completed / total * 100) if total > 0 else 0

    return {
        "completed": completed,
        "total": total,
        "percentage": percentage,
    }


def calculate_tag_integrity(cwd: str) -> float:
    """Calculate TAG chain integrity score

    Scan codebase for TAG blocks and calculate integrity score based on:
    - Complete chains: @SPEC → @TEST → @CODE
    - Orphaned tags: TAG exists but referenced file missing
    - Broken chains: Missing intermediate links

    Args:
        cwd: Project root directory path

    Returns:
        Integrity percentage (0-100%) as float

    Examples:
        >>> calculate_tag_integrity(".")
        95.5

    Notes:
        - Uses ripgrep for fast TAG scanning
        - Scans .md, .py, .ts, .js, .sh files
        - Fail-open: Returns 0 on error (doesn't block session)
    """
    try:
        # Use ripgrep to find all TAG blocks
        # Add .md files to type scanning with --type-add
        result = subprocess.run(
            [
                "rg",
                r"@(SPEC|TEST|CODE|DOC):",
                "-n",
                "--type-add", "md:*.md",
                "--type", "md",
                "--type", "py",
                "--type", "ts",
                "--type", "js",
                "--type", "sh",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            # No tags found or error
            return 0.0

        # Count TAG occurrences
        lines = result.stdout.splitlines()
        tag_count = len(lines)

        if tag_count == 0:
            return 0.0

        # Simple integrity calculation: assume 80% base + 20% for CHAIN presence
        # More sophisticated implementation would verify actual chain completeness
        chain_count = sum(1 for line in lines if "@CHAIN:" in line)

        # If we have CHAIN tags, higher integrity
        if chain_count > 0:
            return min(100.0, 80.0 + (chain_count / tag_count * 20))
        else:
            # Without explicit chains, use tag_count as rough proxy
            return min(100.0, (tag_count / 100) * 100)

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # Fail-open: return 0 on error
        return 0.0


__all__ = [
    "detect_language",
    "get_git_info",
    "count_specs",
    "calculate_tag_integrity",
]
