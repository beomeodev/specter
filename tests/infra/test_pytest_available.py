"""
@TEST:INFRA-001
@SPEC: specs/002-moai-adk-integration/spec.md
@CODE: scripts/validate_environment.py
@CHAIN: @SPEC:INFRA-001 → @TEST:INFRA-001 → @CODE:INFRA-001
@STATUS: implemented
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Test suite for pytest and pytest-cov availability.

This test validates T002: Install pytest and pytest-cov
Following Constitution Section I: Test-First Development (NON-NEGOTIABLE)
"""

import subprocess
import sys
import pytest
import importlib.util


def test_pytest_module_importable():
    """
    Test that pytest module can be imported.

    Requirements from spec.md Section 9.1:
    - pytest ≥7.0 (required for test framework)
    """
    # Try to import pytest
    import pytest as pytest_module

    assert pytest_module is not None, "pytest module should be importable"

    # Check version is ≥7.0
    version_parts = pytest_module.__version__.split(".")
    major_version = int(version_parts[0])

    assert major_version >= 7, (
        f"pytest version must be ≥7.0, got {pytest_module.__version__}"
    )


def test_pytest_command_available():
    """
    Test that pytest command is available in PATH.

    This validates the CLI tool can be executed.
    """
    result = subprocess.run(
        ["pytest", "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, (
        "pytest command should be available and return exit code 0"
    )
    assert "pytest" in result.stdout, (
        f"Expected 'pytest' in output, got: {result.stdout}"
    )


def test_pytest_cov_plugin_available():
    """
    Test that pytest-cov plugin is installed and available.

    Requirements from spec.md Section 9.1:
    - pytest-cov (Latest) for coverage reporting
    """
    result = subprocess.run(
        ["pytest", "--cov", "--version"],
        capture_output=True,
        text=True
    )

    # Should not fail when --cov flag is used
    assert result.returncode == 0, (
        "pytest --cov command should work if pytest-cov is installed"
    )


def test_pytest_cov_module_importable():
    """
    Test that pytest_cov module can be imported.
    """
    spec = importlib.util.find_spec("pytest_cov")

    assert spec is not None, (
        "pytest_cov module should be importable. "
        "Install with: pip install pytest-cov"
    )


def test_black_formatter_available():
    """
    Test that black formatter is installed.

    Requirements from spec.md Section 9.1:
    - Black (Latest) for Python formatting
    """
    result = subprocess.run(
        ["black", "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, (
        "black command should be available. "
        "Install with: pip install black"
    )
    assert "black" in result.stdout.lower(), (
        f"Expected 'black' in output, got: {result.stdout}"
    )


def test_pytest_runs_tests_successfully():
    """
    Test that pytest can actually run tests.

    This validates the complete testing workflow works.
    """
    # Run pytest on this test file itself
    result = subprocess.run(
        ["pytest", "tests/infra/test_python_version.py", "-v"],
        capture_output=True,
        text=True,
        cwd="/workspace/specter"
    )

    assert result.returncode == 0, (
        f"pytest should successfully run tests. "
        f"Exit code: {result.returncode}\n"
        f"Stdout: {result.stdout}\n"
        f"Stderr: {result.stderr}"
    )
    assert "passed" in result.stdout, (
        "Test output should show passed tests"
    )


def test_pytest_coverage_measurement():
    """
    Test that pytest can measure code coverage.

    This validates pytest-cov integration works correctly.
    """
    # Run pytest with coverage on a test file
    result = subprocess.run(
        [
            "pytest",
            "tests/infra/test_python_version.py",
            "--cov=scripts",
            "--cov-report=term"
        ],
        capture_output=True,
        text=True,
        cwd="/workspace/specter"
    )

    # Should complete without error
    assert result.returncode == 0, (
        f"pytest with coverage should succeed. "
        f"Exit code: {result.returncode}"
    )

    # Output should contain coverage information
    # (Note: May show 0% coverage if script not executed by tests)
    output = result.stdout + result.stderr
    assert "coverage" in output.lower() or "TOTAL" in output, (
        "Coverage report should be generated"
    )


def test_pytest_config_file_exists():
    """
    Test that pytest configuration file exists.

    My-Spec uses pyproject.toml for pytest configuration.
    """
    import os

    config_path = "/workspace/specter/pyproject.toml"
    assert os.path.exists(config_path), (
        f"pytest config should exist at {config_path}"
    )

    # Verify it contains pytest configuration
    with open(config_path, "r") as f:
        content = f.read()

    assert "[tool.pytest" in content or "pytest" in content, (
        "pyproject.toml should contain pytest configuration"
    )


@pytest.mark.parametrize("package", [
    "pytest",
    "pytest-cov",
    "black"
])
def test_required_packages_installed(package):
    """
    Test that all required packages from spec.md are installed.

    Requirements from spec.md Section 9.1:
    - pytest ≥7.0
    - pytest-cov (Latest)
    - black (Latest)
    """
    # Replace hyphens with underscores for module names
    module_name = package.replace("-", "_")

    spec = importlib.util.find_spec(module_name)

    assert spec is not None, (
        f"Package '{package}' should be installed. "
        f"Install with: pip install {package}"
    )


def test_installation_script_commands():
    """
    Test the exact commands from spec.md installation script.

    This validates the documented installation process.

    From spec.md Section 9.1:
    ```bash
    pip install pytest pytest-cov black
    ```
    """
    # Verify all three packages are importable
    packages_to_check = ["pytest", "pytest_cov", "black"]

    for package in packages_to_check:
        spec = importlib.util.find_spec(package)
        assert spec is not None, (
            f"Package '{package}' should be installed via: "
            f"pip install pytest pytest-cov black"
        )


def test_pytest_operational_definition():
    """
    Test that "pytest operational" is satisfied.

    Operational means:
    1. pytest command works
    2. Can run tests
    3. Can measure coverage
    4. All dependencies installed

    This is the deliverable for T002.
    """
    # 1. pytest command works
    pytest_result = subprocess.run(
        ["pytest", "--version"],
        capture_output=True
    )
    assert pytest_result.returncode == 0, "pytest command should work"

    # 2. Can run tests (use a simple passing test)
    test_result = subprocess.run(
        ["pytest", "tests/infra/test_python_version.py", "-q"],
        capture_output=True,
        cwd="/workspace/specter"
    )
    assert test_result.returncode == 0, "pytest should run tests successfully"

    # 3. Can measure coverage
    cov_result = subprocess.run(
        ["pytest", "--cov", "--version"],
        capture_output=True
    )
    assert cov_result.returncode == 0, "pytest-cov should be available"

    # 4. All dependencies installed
    for module in ["pytest", "pytest_cov", "black"]:
        spec = importlib.util.find_spec(module)
        assert spec is not None, f"{module} should be installed"

    # If all checks pass, pytest is operational ✅
    assert True, "pytest is operational - all checks passed"
