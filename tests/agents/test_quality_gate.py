"""
@TEST:AGENTS-005
@SPEC: specs/002-moai-adk-integration/spec.md
@CHAIN: @SPEC:AGENTS-005 → @TEST:AGENTS-005 → @CODE:AGENTS-005
@STATUS: red
@CREATED: 2025-10-26
@UPDATED: 2025-10-26

Tests for quality-gate agent

Phase 4.5 - TDD RED Phase
Implements FR-AGENTS-005: quality-gate Agent
"""

import json
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add .claude/agents to Python path for importing quality_gate module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "agents"))


class TestQualityGateCoverageCheck:
    """Test coverage validation"""

    def test_coverage_check_blocks_if_below_85_percent(self):
        """Test that quality gate blocks commit if coverage < 85%"""
        # GIVEN: Coverage report shows 70%
        coverage_data = {
            "totals": {
                "percent_covered": 70.0
            }
        }

        # WHEN: Checking coverage
        from quality_gate import check_coverage
        result = check_coverage(coverage_data)

        # THEN: Should block commit
        assert result["passed"] is False
        assert result["severity"] == "CRITICAL"
        assert "85" in result["message"]  # Check for "85" (accepts both "85%" and "85.0%")
        assert result["actual_coverage"] == 70.0

    def test_coverage_check_passes_if_above_85_percent(self):
        """Test that quality gate passes if coverage >= 85%"""
        # GIVEN: Coverage report shows 90%
        coverage_data = {
            "totals": {
                "percent_covered": 90.0
            }
        }

        # WHEN: Checking coverage
        from quality_gate import check_coverage
        result = check_coverage(coverage_data)

        # THEN: Should pass
        assert result["passed"] is True
        assert result["severity"] == "PASS"
        assert result["actual_coverage"] == 90.0

    def test_coverage_check_passes_at_exactly_85_percent(self):
        """Test boundary condition: coverage = 85% passes"""
        # GIVEN: Coverage report shows exactly 85%
        coverage_data = {
            "totals": {
                "percent_covered": 85.0
            }
        }

        # WHEN: Checking coverage
        from quality_gate import check_coverage
        result = check_coverage(coverage_data)

        # THEN: Should pass (boundary inclusive)
        assert result["passed"] is True
        assert result["actual_coverage"] == 85.0


class TestQualityGateTRUSTValidation:
    """Test TRUST 5 principles validation"""

    def test_trust_validation_calls_trust_validator_agent(self):
        """Test that TRUST validation delegates to trust-validator agent"""
        # GIVEN: Files to validate
        files_changed = ["src/auth/service.py", "tests/auth/test_service.py"]

        # WHEN: Running TRUST validation
        from quality_gate import validate_trust_principles
        with patch('quality_gate.call_agent') as mock_call:
            mock_call.return_value = {
                "test_first": {"passed": True},
                "readable": {"passed": True},
                "unified": {"passed": True},
                "secured": {"passed": True},
                "trackable": {"passed": True}
            }

            result = validate_trust_principles(files_changed)

        # THEN: Should call trust-validator agent
        mock_call.assert_called_once()
        assert "trust-validator" in str(mock_call.call_args)

    def test_trust_validation_blocks_on_critical_failure(self):
        """Test that TRUST validation blocks if any principle fails"""
        # GIVEN: TRUST validation with secured failure
        files_changed = ["src/auth/service.py"]

        # WHEN: Running TRUST validation with failure
        from quality_gate import validate_trust_principles
        with patch('quality_gate.call_agent') as mock_call:
            mock_call.return_value = {
                "test_first": {"passed": True},
                "readable": {"passed": True},
                "unified": {"passed": True},
                "secured": {"passed": False, "issues": ["SQL injection vulnerability"]},
                "trackable": {"passed": True}
            }

            result = validate_trust_principles(files_changed)

        # THEN: Should block commit
        assert result["passed"] is False
        assert result["severity"] == "CRITICAL"
        assert "secured" in result["failed_principles"]


class TestQualityGateLinterCheck:
    """Test linter validation"""

    def test_linter_check_runs_eslint_for_typescript(self):
        """Test that linter runs ESLint for TypeScript files"""
        # GIVEN: TypeScript files changed
        files_changed = ["src/auth/service.ts"]

        # WHEN: Running linter check
        from quality_gate import check_linter
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            result = check_linter(files_changed)

        # THEN: Should run ESLint
        assert mock_run.called
        assert "eslint" in str(mock_run.call_args)

    def test_linter_check_runs_pylint_for_python(self):
        """Test that linter runs Pylint for Python files"""
        # GIVEN: Python files changed
        files_changed = ["src/auth/service.py"]

        # WHEN: Running linter check
        from quality_gate import check_linter
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            result = check_linter(files_changed)

        # THEN: Should run Pylint
        assert mock_run.called
        assert "pylint" in str(mock_run.call_args) or "ruff" in str(mock_run.call_args)

    def test_linter_check_blocks_on_errors(self):
        """Test that linter check blocks if errors found"""
        # GIVEN: Python files with linter errors
        files_changed = ["src/auth/service.py"]

        # WHEN: Running linter check with errors
        from quality_gate import check_linter
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout=json.dumps([{
                    "type": "error",
                    "message": "Undefined variable",
                    "line": 42
                }])
            )
            result = check_linter(files_changed)

        # THEN: Should block commit
        assert result["passed"] is False
        assert result["severity"] == "CRITICAL"
        assert result["error_count"] > 0


class TestQualityGateTAGChainValidation:
    """Test TAG chain completeness validation"""

    def test_tag_chain_validation_calls_tag_auditor(self):
        """Test that TAG validation delegates to tag-auditor agent"""
        # GIVEN: Files with TAG blocks
        files_changed = ["src/auth/service.py"]

        # WHEN: Validating TAG chains
        from quality_gate import validate_tag_chains
        with patch('quality_gate.call_agent') as mock_call:
            mock_call.return_value = {
                "complete_chains": 45,
                "orphaned_tags": [],
                "integrity_score": 100.0
            }

            result = validate_tag_chains(files_changed)

        # THEN: Should call tag-auditor agent
        mock_call.assert_called_once()
        assert "tag-auditor" in str(mock_call.call_args)

    def test_tag_chain_validation_warns_on_orphaned_tags(self):
        """Test that TAG validation warns if orphaned TAGs found"""
        # GIVEN: Files with orphaned TAGs
        files_changed = ["src/auth/service.py"]

        # WHEN: Validating TAG chains with orphans
        from quality_gate import validate_tag_chains
        with patch('quality_gate.call_agent') as mock_call:
            mock_call.return_value = {
                "complete_chains": 43,
                "orphaned_tags": ["AUTH-001", "AUTH-003"],
                "integrity_score": 95.5
            }

            result = validate_tag_chains(files_changed)

        # THEN: Should warn (not block, but warn)
        assert result["passed"] is True  # Orphans are warnings, not blockers
        assert result["severity"] == "WARNING"
        assert len(result["orphaned_tags"]) == 2


class TestQualityGateIntegration:
    """Integration tests for quality-gate agent"""

    def test_quality_gate_returns_pass_when_all_checks_pass(self):
        """Test that quality gate returns PASS when all checks pass"""
        # GIVEN: All quality checks pass
        files_changed = ["src/auth/service.py", "tests/auth/test_service.py"]

        # WHEN: Running full quality gate
        from quality_gate import run_quality_gate
        with patch.multiple('quality_gate',
            check_coverage=Mock(return_value={"passed": True, "severity": "PASS"}),
            validate_trust_principles=Mock(return_value={"passed": True, "severity": "PASS"}),
            check_linter=Mock(return_value={"passed": True, "severity": "PASS"}),
            validate_tag_chains=Mock(return_value={"passed": True, "severity": "PASS"}),
        ):
            result = run_quality_gate(files_changed)

        # THEN: Should return PASS
        assert result["final_evaluation"] == "PASS"
        assert result["can_commit"] is True

    def test_quality_gate_returns_critical_when_coverage_fails(self):
        """Test that quality gate returns CRITICAL when coverage < 85%"""
        # GIVEN: Coverage check fails
        files_changed = ["src/auth/service.py"]

        # WHEN: Running quality gate with coverage failure
        from quality_gate import run_quality_gate
        with patch.multiple('quality_gate',
            check_coverage=Mock(return_value={"passed": False, "severity": "CRITICAL"}),
            validate_trust_principles=Mock(return_value={"passed": True, "severity": "PASS"}),
            check_linter=Mock(return_value={"passed": True, "severity": "PASS"}),
            validate_tag_chains=Mock(return_value={"passed": True, "severity": "PASS"}),
        ):
            result = run_quality_gate(files_changed)

        # THEN: Should return CRITICAL and block commit
        assert result["final_evaluation"] == "CRITICAL"
        assert result["can_commit"] is False

    def test_quality_gate_returns_warning_when_tag_chains_have_orphans(self):
        """Test that quality gate returns WARNING for orphaned TAGs"""
        # GIVEN: TAG chain validation has warnings
        files_changed = ["src/auth/service.py"]

        # WHEN: Running quality gate with TAG warnings
        from quality_gate import run_quality_gate
        with patch.multiple('quality_gate',
            check_coverage=Mock(return_value={"passed": True, "severity": "PASS"}),
            validate_trust_principles=Mock(return_value={"passed": True, "severity": "PASS"}),
            check_linter=Mock(return_value={"passed": True, "severity": "PASS"}),
            validate_tag_chains=Mock(return_value={"passed": True, "severity": "WARNING"}),
        ):
            result = run_quality_gate(files_changed)

        # THEN: Should return WARNING but allow commit
        assert result["final_evaluation"] == "WARNING"
        assert result["can_commit"] is True  # Warnings don't block


class TestQualityGateReportGeneration:
    """Test quality gate report generation"""

    def test_report_generation_includes_all_sections(self):
        """Test that quality gate report includes all required sections"""
        # GIVEN: Quality gate results
        results = {
            "coverage": {"passed": True, "severity": "PASS", "actual_coverage": 90.0},
            "trust": {"passed": True, "severity": "PASS"},
            "linter": {"passed": True, "severity": "PASS", "error_count": 0},
            "tags": {"passed": True, "severity": "PASS", "orphaned_tags": []}
        }

        # WHEN: Generating report
        from quality_gate import generate_report
        report = generate_report(results)

        # THEN: Should include all sections
        assert "Final Evaluation" in report
        assert "Verification Summary" in report
        assert "TRUST Principles" in report
        assert "Code Style" in report
        assert "Test Coverage" in report
        assert "TAG Chains" in report

    def test_report_highlights_critical_items(self):
        """Test that report highlights critical failures"""
        # GIVEN: Quality gate results with critical failure
        results = {
            "coverage": {"passed": False, "severity": "CRITICAL", "actual_coverage": 70.0},
            "trust": {"passed": True, "severity": "PASS"},
            "linter": {"passed": True, "severity": "PASS"},
            "tags": {"passed": True, "severity": "PASS"}
        }

        # WHEN: Generating report
        from quality_gate import generate_report
        report = generate_report(results)

        # THEN: Should highlight critical items
        assert "❌ CRITICAL" in report
        assert "coverage" in report.lower()
        assert "70" in report  # Shows actual coverage
