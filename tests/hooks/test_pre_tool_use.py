#!/usr/bin/env python3
"""
@TEST:HOOKS-002
@SPEC: specs/002-moai-adk-integration/spec.md
@CHAIN: @SPEC:HOOKS-002 → @TEST:HOOKS-002 → @CODE:HOOKS-002
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Tests for PreToolUse Hook (Event-Driven Checkpoint)

Adapted from MoAI-ADK for My-Spec workflow.
Tests risky operation detection and Git checkpoint creation.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


def _load_checkpoint_module():
    """Dynamically load checkpoint.py module for testing"""
    repo_root = Path(__file__).resolve().parents[2]
    hooks_dir = repo_root / ".claude" / "hooks" / "ms"
    sys.path.insert(0, str(hooks_dir))

    module_path = hooks_dir / "core" / "checkpoint.py"
    spec = importlib.util.spec_from_file_location("checkpoint", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load checkpoint module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_tool_handler_module():
    """Dynamically load handlers/tool.py module for testing"""
    repo_root = Path(__file__).resolve().parents[2]
    hooks_dir = repo_root / ".claude" / "hooks" / "ms"
    sys.path.insert(0, str(hooks_dir))

    module_path = hooks_dir / "handlers" / "tool.py"
    spec = importlib.util.spec_from_file_location("tool_handler", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load tool handler module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRiskyOperationDetection:
    """Tests for detect_risky_operation() function

    Verifies that dangerous operations are correctly detected across:
    - Bash tool: rm -rf, git merge, git reset --hard, git rebase, script execution
    - Edit/Write tool: Constitution, config files
    - MultiEdit tool: ≥5 files (My-Spec threshold, stricter than MoAI's 10)
    """

    def test_bash_rm_rf_detected(self):
        """Test: Bash rm -rf is detected as risky delete operation"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "rm -rf src/"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "delete"

    def test_bash_git_rm_detected(self):
        """Test: Bash git rm is detected as risky delete operation"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "git rm .claude/hooks/old-hook.sh"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "delete"

    def test_bash_git_merge_detected(self):
        """Test: Bash git merge is detected as risky merge operation"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "git merge feature-branch"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "merge"

    def test_bash_git_reset_hard_detected(self):
        """Test: Bash git reset --hard is detected as risky merge operation"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "git reset --hard HEAD~1"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "merge"

    def test_bash_git_rebase_detected(self):
        """Test: Bash git rebase is detected as risky merge operation"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "git rebase main"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "merge"

    def test_bash_script_execution_detected(self):
        """Test: Bash script execution (python, node, bash) is detected as risky"""
        checkpoint = _load_checkpoint_module()

        # Python script
        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "python scripts/migrate.py"},
            cwd="."
        )
        assert is_risky is True
        assert operation_type == "script"

        # Node script
        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "node build.js"},
            cwd="."
        )
        assert is_risky is True
        assert operation_type == "script"

        # Bash script
        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "bash deploy.sh"},
            cwd="."
        )
        assert is_risky is True
        assert operation_type == "script"

    def test_edit_constitution_detected(self):
        """Test: Edit .specify/memory/constitution.md is detected as risky"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Edit",
            tool_args={"file_path": ".specify/memory/constitution.md"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "critical-file"

    def test_write_config_json_detected(self):
        """Test: Write .specify/config.json is detected as risky"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Write",
            tool_args={"file_path": ".specify/config.json"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "critical-file"

    def test_edit_claude_md_detected(self):
        """Test: Edit CLAUDE.md is detected as risky"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Edit",
            tool_args={"file_path": "CLAUDE.md"},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "critical-file"

    def test_multiedit_5_files_detected(self):
        """Test: MultiEdit with ≥5 files is detected as risky refactor

        My-Spec uses stricter threshold (5 files) than MoAI-ADK (10 files)
        to minimize risk of breaking changes.
        """
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="MultiEdit",
            tool_args={"edits": [{"file": f"file{i}.py"} for i in range(5)]},
            cwd="."
        )

        assert is_risky is True
        assert operation_type == "refactor"

    def test_read_tool_not_risky(self):
        """Test: Read tool is NOT detected as risky (safe operation)"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Read",
            tool_args={"file_path": "src/main.py"},
            cwd="."
        )

        assert is_risky is False
        assert operation_type == ""

    def test_bash_safe_commands_not_risky(self):
        """Test: Safe Bash commands (ls, git status) are NOT risky"""
        checkpoint = _load_checkpoint_module()

        # ls command
        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "ls -la"},
            cwd="."
        )
        assert is_risky is False
        assert operation_type == ""

        # git status
        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Bash",
            tool_args={"command": "git status"},
            cwd="."
        )
        assert is_risky is False
        assert operation_type == ""

    def test_edit_normal_file_not_risky(self):
        """Test: Editing normal source files is NOT risky"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="Edit",
            tool_args={"file_path": "src/services/auth.py"},
            cwd="."
        )

        assert is_risky is False
        assert operation_type == ""

    def test_multiedit_4_files_not_risky(self):
        """Test: MultiEdit with <5 files is NOT risky (below threshold)"""
        checkpoint = _load_checkpoint_module()

        is_risky, operation_type = checkpoint.detect_risky_operation(
            tool_name="MultiEdit",
            tool_args={"edits": [{"file": f"file{i}.py"} for i in range(4)]},
            cwd="."
        )

        assert is_risky is False
        assert operation_type == ""


class TestCheckpointCreation:
    """Tests for create_checkpoint() function

    Verifies Git branch creation and checkpoint logging.
    """

    def test_checkpoint_creates_git_branch(self):
        """Test: Checkpoint creates Git local branch with correct naming format"""
        checkpoint = _load_checkpoint_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize Git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)

            # Create initial commit
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

            # Create checkpoint
            branch_name = checkpoint.create_checkpoint(tmpdir, "delete")

            # Verify branch exists and follows naming convention
            assert branch_name.startswith("before-delete-")
            assert len(branch_name.split("-")) >= 3  # before-{operation}-{timestamp}

            # Verify branch exists in Git
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            assert branch_name in result.stdout

    def test_checkpoint_logs_to_file(self):
        """Test: Checkpoint creation is logged to .specify/checkpoints.log"""
        checkpoint = _load_checkpoint_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize Git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)

            # Create initial commit
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

            # Create checkpoint
            branch_name = checkpoint.create_checkpoint(tmpdir, "merge")

            # Verify log file exists
            log_file = Path(tmpdir) / ".specify" / "checkpoints.log"
            assert log_file.exists()

            # Verify log format (JSON Lines)
            log_content = log_file.read_text()
            log_entry = json.loads(log_content.strip())

            assert "timestamp" in log_entry
            assert log_entry["branch"] == branch_name
            assert log_entry["operation"] == "merge"

    def test_checkpoint_handles_git_error_gracefully(self):
        """Test: Checkpoint fails gracefully if Git is unavailable (fail-open)"""
        checkpoint = _load_checkpoint_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # No Git repo initialized - should fail gracefully
            branch_name = checkpoint.create_checkpoint(tmpdir, "delete")

            # Should return error marker but not crash
            assert branch_name == "checkpoint-failed"


class TestPreToolUseHandler:
    """Tests for handle_pre_tool_use() handler

    Verifies that PreToolUse hook creates checkpoints when risky operations detected.
    """

    def test_pretooluse_creates_checkpoint_for_risky_bash(self):
        """Test: PreToolUse creates checkpoint for risky Bash command"""
        tool_handler = _load_tool_handler_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize Git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)

            # Create initial commit
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

            # Trigger PreToolUse with risky command
            payload = {
                "cwd": tmpdir,
                "tool": "Bash",
                "arguments": {"command": "rm -rf src/"}
            }

            result = tool_handler.handle_pre_tool_use(payload)

            # Verify checkpoint created
            assert result.continue_execution is True
            assert "🛡️ Checkpoint created:" in result.system_message
            assert "delete" in result.system_message

    def test_pretooluse_creates_checkpoint_for_constitution_edit(self):
        """Test: PreToolUse creates checkpoint for Constitution edit"""
        tool_handler = _load_tool_handler_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize Git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)

            # Create initial commit
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

            # Trigger PreToolUse with Constitution edit
            payload = {
                "cwd": tmpdir,
                "tool": "Edit",
                "arguments": {"file_path": ".specify/memory/constitution.md"}
            }

            result = tool_handler.handle_pre_tool_use(payload)

            # Verify checkpoint created
            assert result.continue_execution is True
            assert "🛡️ Checkpoint created:" in result.system_message
            assert "critical-file" in result.system_message

    def test_pretooluse_no_checkpoint_for_safe_operation(self):
        """Test: PreToolUse does NOT create checkpoint for safe operations"""
        tool_handler = _load_tool_handler_module()

        # Trigger PreToolUse with safe Read command
        payload = {
            "cwd": ".",
            "tool": "Read",
            "arguments": {"file_path": "src/main.py"}
        }

        result = tool_handler.handle_pre_tool_use(payload)

        # Verify no checkpoint created (no system_message)
        assert result.continue_execution is True
        assert result.system_message is None or result.system_message == ""

    def test_pretooluse_continues_execution_even_if_checkpoint_fails(self):
        """Test: PreToolUse continues execution even if checkpoint creation fails (fail-open)"""
        tool_handler = _load_tool_handler_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            # No Git repo - checkpoint will fail
            payload = {
                "cwd": tmpdir,
                "tool": "Bash",
                "arguments": {"command": "rm -rf src/"}
            }

            result = tool_handler.handle_pre_tool_use(payload)

            # Verify execution continues despite checkpoint failure
            assert result.continue_execution is True
