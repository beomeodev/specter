#!/usr/bin/env python3
"""
@CODE:INFRA-001
@SPEC: specs/002-moai-adk-integration/spec.md
@TEST: tests/infra/test_python_version.py
@CHAIN: @SPEC:INFRA-001 → @TEST:INFRA-001 → @CODE:INFRA-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Environment validation script for MoAI-ADK integration.

This script validates that all prerequisites are met before starting
the MoAI-ADK integration. It checks Python version, required tools,
and project prerequisites.

Requirements from spec.md Section 9.1:
- Python ≥3.13 (REQUIRED, STRICT)
- MoAI-ADK Hooks require Python 3.13+ features
- No backward compatibility for earlier versions

Usage:
    python3 scripts/validate_environment.py

Exit Codes:
    0 - All validations passed
    1 - Validation failed (missing prerequisites)

Following Constitution Section I: Test-First Development
Following Constitution Section II: Simplicity-First Architecture
"""

import sys
import subprocess
from typing import Tuple, List


def validate_python_version() -> Tuple[bool, str]:
    """
    Validate Python version is 3.13 or higher.

    Returns:
        Tuple[bool, str]: (is_valid, message)
            - is_valid: True if Python 3.13+, False otherwise
            - message: Success or error message

    Requirements:
        - Python major version MUST be 3
        - Python minor version MUST be ≥13
        - Earlier versions (3.10-3.12) are NOT supported
    """
    version_info = sys.version_info
    major = version_info.major
    minor = version_info.minor
    micro = version_info.micro

    # Validation logic: major == 3 AND minor >= 13
    is_valid = (major == 3) and (minor >= 13)

    if is_valid:
        message = (
            f"✅ Python version: {major}.{minor}.{micro} (OK)\n"
            f"   Requirement: Python ≥3.13"
        )
    else:
        message = (
            f"❌ Error: Python 3.13+ required\n"
            f"   Current version: {major}.{minor}.{micro}\n"
            f"   Minimum required: 3.13\n"
            f"   Install Python 3.13+: https://www.python.org/downloads/\n"
            f"\n"
            f"   Rationale:\n"
            f"   - MoAI-ADK Hooks require Python 3.13+ features\n"
            f"   - Improved error messages and type system enhancements\n"
            f"   - No backward compatibility burden for legacy versions"
        )

    return is_valid, message


def validate_command_available(command: str, version_flag: str = "--version") -> Tuple[bool, str]:
    """
    Validate that a command-line tool is available.

    Args:
        command: Command name to check (e.g., "pytest", "git")
        version_flag: Flag to get version (default: "--version")

    Returns:
        Tuple[bool, str]: (is_available, message)
    """
    try:
        result = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version_output = result.stdout.strip() or result.stderr.strip()
            message = f"✅ {command}: {version_output.split(chr(10))[0]}"
            return True, message
        else:
            message = (
                f"❌ {command}: Command failed\n"
                f"   Please install {command}"
            )
            return False, message

    except FileNotFoundError:
        message = (
            f"❌ {command}: Not found\n"
            f"   Please install {command}"
        )
        return False, message
    except subprocess.TimeoutExpired:
        message = f"❌ {command}: Command timed out"
        return False, message
    except Exception as e:
        message = f"❌ {command}: Error - {str(e)}"
        return False, message


def run_validations() -> Tuple[bool, List[str]]:
    """
    Run all environment validations.

    Returns:
        Tuple[bool, List[str]]: (all_passed, messages)
            - all_passed: True if all validations passed
            - messages: List of validation result messages
    """
    validations = []
    all_passed = True

    # 1. Python version (CRITICAL - blocks everything else)
    python_valid, python_msg = validate_python_version()
    validations.append(python_msg)
    if not python_valid:
        all_passed = False
        # Stop here if Python version invalid (critical blocker)
        return all_passed, validations

    # 2. pytest (required for testing)
    pytest_valid, pytest_msg = validate_command_available("pytest")
    validations.append(pytest_msg)
    if not pytest_valid:
        all_passed = False

    # 3. Git (required for checkpoints)
    git_valid, git_msg = validate_command_available("git")
    validations.append(git_msg)
    if not git_valid:
        all_passed = False

    # 4. ripgrep (required for TAG scanning)
    rg_valid, rg_msg = validate_command_available("rg")
    validations.append(rg_msg)
    if not rg_valid:
        all_passed = False
        validations.append(
            "   Installation: https://github.com/BurntSushi/ripgrep#installation"
        )

    # 5. black (required for Python formatting - PostToolUse hook)
    black_valid, black_msg = validate_command_available("black")
    validations.append(black_msg)
    if not black_valid:
        all_passed = False
        validations.append(
            "   Installation: pip install black"
        )

    return all_passed, validations


def main() -> int:
    """
    Main entry point for environment validation.

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    print("=" * 70)
    print("MoAI-ADK Integration - Environment Validation")
    print("=" * 70)
    print()

    all_passed, messages = run_validations()

    # Print all validation messages
    for message in messages:
        print(message)

    print()
    print("=" * 70)

    if all_passed:
        print("✅ All validations passed")
        print()
        print("Next steps:")
        print("  1. Run: pytest tests/infra/test_python_version.py -v")
        print("  2. Proceed to Phase 0 tasks (T002-T007)")
        print("=" * 70)
        return 0
    else:
        print("❌ Validation failed - Missing prerequisites")
        print()
        print("Action required:")
        print("  1. Install missing tools (see errors above)")
        print("  2. Re-run: python3 scripts/validate_environment.py")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
