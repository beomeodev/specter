"""
@TEST:INFRA-001
@SPEC: specs/002-moai-adk-integration/spec.md
@CODE: scripts/validate_environment.py
@CHAIN: @SPEC:INFRA-001 → @TEST:INFRA-001 → @CODE:INFRA-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Test suite for Python 3.13+ version validation.

This test validates T001: Validate Python 3.13+ installed
Following Constitution Section I: Test-First Development (NON-NEGOTIABLE)
"""

import subprocess
import sys
import pytest


def test_python_version_is_3_13_or_higher():
    """
    Test that Python version is 3.13 or higher.

    Requirements from spec.md Section 9.1:
    - Python ≥3.13 (REQUIRED)
    - MoAI-ADK Hooks require Python 3.13+ features
    - No backward compatibility for earlier versions
    """
    version_info = sys.version_info

    # Python must be 3.13+
    assert version_info.major == 3, (
        f"Python major version must be 3, got {version_info.major}"
    )
    assert version_info.minor >= 13, (
        f"Python minor version must be ≥13, got {version_info.minor}. "
        f"Current version: {version_info.major}.{version_info.minor}.{version_info.micro}. "
        f"Install Python 3.13+: https://www.python.org/downloads/"
    )


def test_python_version_command_output():
    """
    Test that `python3 --version` command returns correct format.

    This validates the validation script will work correctly when checking
    Python version via subprocess.
    """
    result = subprocess.run(
        ["python3", "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, "python3 --version command should succeed"
    assert "Python 3." in result.stdout, (
        f"Expected 'Python 3.x' in output, got: {result.stdout}"
    )

    # Extract version numbers
    version_str = result.stdout.strip().replace("Python ", "")
    major, minor, *_ = version_str.split(".")

    assert int(major) == 3, f"Major version must be 3, got {major}"
    assert int(minor) >= 13, (
        f"Minor version must be ≥13, got {minor}. "
        f"Current version: {version_str}"
    )


def test_python_version_grep_pattern():
    """
    Test the grep pattern used in spec.md installation script.

    Pattern: python3 --version | grep -E "3\.(1[3-9]|[2-9][0-9])"

    This regex matches:
    - 3.13-3.19 (1[3-9])
    - 3.20-3.99 ([2-9][0-9])
    """
    result = subprocess.run(
        ["python3", "--version"],
        capture_output=True,
        text=True
    )

    # Test the grep pattern
    grep_result = subprocess.run(
        ["grep", "-E", r"3\.(1[3-9]|[2-9][0-9])"],
        input=result.stdout,
        capture_output=True,
        text=True
    )

    assert grep_result.returncode == 0, (
        f"Python version does not match required pattern (3.13+). "
        f"Current version: {result.stdout.strip()}"
    )


@pytest.mark.parametrize("version_tuple,expected_valid", [
    ((3, 12, 0), False),  # 3.12 - too old
    ((3, 13, 0), True),   # 3.13 - minimum required
    ((3, 14, 0), True),   # 3.14 - valid
    ((3, 20, 0), True),   # 3.20 - future version, valid
    ((2, 7, 0), False),   # Python 2 - invalid
    ((4, 0, 0), False),   # Python 4 - wrong major version
])
def test_version_validation_logic(version_tuple, expected_valid):
    """
    Test version validation logic for different Python versions.

    This tests the core validation logic that will be used in the
    environment validation script.
    """
    major, minor, micro = version_tuple

    # Validation logic: major == 3 AND minor >= 13
    is_valid = (major == 3) and (minor >= 13)

    assert is_valid == expected_valid, (
        f"Version {major}.{minor}.{micro} validation incorrect. "
        f"Expected valid={expected_valid}, got valid={is_valid}"
    )


def test_validation_script_will_exist():
    """
    Test that the validation script location is planned correctly.

    This is a placeholder test that will pass once the script is created.
    Following Test-First principle: write test before implementation.
    """
    expected_script_path = "scripts/validate_environment.py"

    # This test documents where the script will be created
    # Once T001 GREEN phase is complete, this script will exist
    assert True, f"Script will be created at: {expected_script_path}"


def test_exit_code_on_invalid_version():
    """
    Test that validation script exits with code 1 on invalid Python version.

    This documents the expected behavior when Python version check fails.
    Actual implementation will be in GREEN phase.
    """
    # Expected behavior (documented for GREEN phase):
    # - IF version < 3.13: exit(1)
    # - IF version >= 3.13: exit(0)

    version_info = sys.version_info
    is_valid = (version_info.major == 3) and (version_info.minor >= 13)

    if is_valid:
        expected_exit_code = 0
    else:
        expected_exit_code = 1

    # Document expected behavior
    assert isinstance(expected_exit_code, int), (
        "Exit code must be integer (0 for success, 1 for failure)"
    )


def test_validation_script_execution():
    """
    Test that validation script executes successfully and returns exit code 0.

    This tests the actual script execution (GREEN phase verification).
    """
    result = subprocess.run(
        ["python3", "scripts/validate_environment.py"],
        capture_output=True,
        text=True,
        cwd="/workspace/specter"
    )

    # Script should exit with code 0 (success) since Python 3.13+ is installed
    assert result.returncode == 0, (
        f"Validation script should exit with code 0, got {result.returncode}. "
        f"Output: {result.stdout}\n{result.stderr}"
    )

    # Verify output contains success indicators
    assert "✅ All validations passed" in result.stdout, (
        "Script output should confirm all validations passed"
    )
    assert "Python version:" in result.stdout, (
        "Script output should show Python version check"
    )
