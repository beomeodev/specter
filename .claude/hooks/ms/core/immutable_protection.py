#!/usr/bin/env python3
"""
@CODE:IMMUTABLE-001
@SPEC: specs/001-moai-adk-fixes/spec.md
@TEST: tests/hooks/test_immutable_protection.py
@CHAIN: @SPEC:IMMUTABLE-001 → @TEST:IMMUTABLE-001 → @CODE:IMMUTABLE-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

@IMMUTABLE file protection system

Provides:
- UnlockRegistry: Session-scoped state tracking unlocked files
- scan_immutable_marker: Detect @IMMUTABLE marker via ripgrep
- is_file_unlocked: Check if file is in unlock registry
- unlock_file: Create checkpoint, validate justification, log audit entry

Requirements:
- ripgrep ≥13.0 (for @IMMUTABLE detection)
- Git ≥2.30 (for checkpoint creation)
- Python 3.13+ (for type hints)
"""

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class UnlockResult:
    """Result of unlock_file operation

    Attributes:
        success: Whether unlock succeeded
        checkpoint_ref: Git checkpoint reference (branch name)
        error_message: Error message if failed
    """

    success: bool
    checkpoint_ref: Optional[str] = None
    error_message: Optional[str] = None


class UnlockRegistry:
    """Session-scoped singleton tracking unlocked @IMMUTABLE files

    Usage:
        registry = UnlockRegistry.get_instance()
        registry.add("/path/to/file.py", "Bug fix justification")
        if registry.is_unlocked("/path/to/file.py"):
            # Allow edit
            pass

    Session lifecycle:
        - SessionStart: Registry is empty
        - During session: Files added via /ms.unlock command
        - SessionEnd: Registry.clear() called
    """

    _instance: Optional["UnlockRegistry"] = None
    _unlocked_files: dict[str, str] = {}  # {file_path: justification}

    @classmethod
    def get_instance(cls) -> "UnlockRegistry":
        """Get singleton instance

        Returns:
            UnlockRegistry: Singleton instance
        """
        if cls._instance is None:
            cls._instance = UnlockRegistry()
        return cls._instance

    def add(self, file_path: str, justification: str) -> None:
        """Add file to unlock registry

        Args:
            file_path: Absolute path to unlocked file
            justification: Unlock justification (≥10 chars)
        """
        self._unlocked_files[file_path] = justification

    def is_unlocked(self, file_path: str) -> bool:
        """Check if file is unlocked in current session

        Args:
            file_path: Absolute path to check

        Returns:
            bool: True if file is unlocked
        """
        return file_path in self._unlocked_files

    def clear(self) -> None:
        """Clear all unlocked files (called on SessionEnd)"""
        self._unlocked_files.clear()


def scan_immutable_marker(file_path: str) -> bool:
    """Scan file for @IMMUTABLE marker using ripgrep

    Args:
        file_path: Path to file to scan

    Returns:
        bool: True if @IMMUTABLE marker found, False otherwise

    Fail-open behavior:
        - Returns False if ripgrep not available
        - Returns False if file doesn't exist
        - Returns False on any scan error

    Example:
        >>> if scan_immutable_marker("config.json"):
        ...     print("File is protected")
    """
    try:
        # Use ripgrep for fast pattern matching
        result = subprocess.run(
            ["rg", "@IMMUTABLE", file_path, "--quiet"],
            capture_output=True,
            check=False,
        )

        # Exit code 0 = match found, 1 = no match, 2+ = error
        return result.returncode == 0

    except FileNotFoundError:
        # ripgrep not installed - fail-open
        return False
    except Exception:
        # Any other error - fail-open
        return False


def is_file_unlocked(file_path: str) -> bool:
    """Check if file is unlocked in current session

    Args:
        file_path: Path to check

    Returns:
        bool: True if file is in unlock registry

    Example:
        >>> if not is_file_unlocked("constitution.md"):
        ...     print("File is still protected")
    """
    registry = UnlockRegistry.get_instance()
    return registry.is_unlocked(file_path)


def unlock_file(
    file_path: str,
    justification: str,
    cwd: str,
) -> UnlockResult:
    """Unlock @IMMUTABLE file with Git checkpoint and audit logging

    Workflow:
        1. Validate justification (≥10 chars)
        2. Check Git repository exists
        3. Create Git checkpoint branch (immutable-unlock-YYYYMMDD-HHMMSS)
        4. Log to .specify/immutable_changes.log
        5. Add file to unlock registry

    Args:
        file_path: Absolute path to file to unlock
        justification: Reason for unlock (must be ≥10 chars)
        cwd: Current working directory (Git repo root)

    Returns:
        UnlockResult: Success status, checkpoint ref, or error message

    Example:
        >>> result = unlock_file(
        ...     file_path="/workspace/project/config.json",
        ...     justification="Emergency production bug fix - auth bypass",
        ...     cwd="/workspace/project"
        ... )
        >>> if result.success:
        ...     print(f"Unlocked with checkpoint: {result.checkpoint_ref}")
    """
    # Step 1: Validate justification
    if len(justification) < 10:
        return UnlockResult(
            success=False,
            error_message="Justification must be at least 10 characters",
        )

    # Step 2: Check Git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return UnlockResult(
            success=False,
            error_message="Not a Git repository - checkpoint creation requires Git",
        )
    except FileNotFoundError:
        return UnlockResult(
            success=False,
            error_message="Git not found - please install Git ≥2.30",
        )

    # Step 3: Create Git checkpoint branch
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    checkpoint_ref = f"immutable-unlock-{timestamp}"

    try:
        # Get current branch before creating checkpoint
        current_branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        original_branch = current_branch_result.stdout.strip()

        # Create checkpoint branch
        subprocess.run(
            ["git", "checkout", "-b", checkpoint_ref],
            cwd=cwd,
            check=True,
            capture_output=True,
        )

        # Commit current state
        subprocess.run(
            ["git", "add", "-A"],
            cwd=cwd,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Checkpoint before @IMMUTABLE unlock: {Path(file_path).name}",
                "--allow-empty",
            ],
            cwd=cwd,
            check=True,
            capture_output=True,
        )

        # Return to original branch
        subprocess.run(
            ["git", "checkout", original_branch],
            cwd=cwd,
            check=True,
            capture_output=True,
        )

    except subprocess.CalledProcessError as e:
        return UnlockResult(
            success=False,
            error_message=f"Git checkpoint failed: {e}",
        )

    # Step 4: Log to audit file
    audit_dir = Path(cwd) / ".specify"
    audit_dir.mkdir(exist_ok=True)
    audit_file = audit_dir / "immutable_changes.log"

    audit_entry = f"""
[{datetime.now().isoformat()}] UNLOCK
File: {file_path}
Justification: {justification}
Checkpoint: {checkpoint_ref}
Session: {os.getenv('CLAUDE_SESSION_ID', 'unknown')}
---
"""

    with open(audit_file, "a") as f:
        f.write(audit_entry)

    # Step 5: Add to unlock registry
    registry = UnlockRegistry.get_instance()
    registry.add(file_path, justification)

    return UnlockResult(
        success=True,
        checkpoint_ref=checkpoint_ref,
    )
