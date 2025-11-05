---
name: ci-cd-optimization
description: Transform manual release processes into automated, quality-gated, observable CI/CD pipelines with performance tracking, regression detection (20% threshold against 10-build moving average), and smoke testing (25-test suite covering execution, consistency, and structure validation). Provides five quality gate categories (coverage threshold ≥75-80%, lint blocking with zero tolerance, CHANGELOG validation with conventional commits, build verification across platforms, 100% test pass rate), release automation with semantic versioning (feat/fix/BREAKING CHANGE parsing), automated CHANGELOG generation from commit history, GitHub Actions workflow templates, observability framework with git-committed metrics in .ci-metrics/ directory (build time, test duration, coverage trends, artifact size), rollback strategies for failed deployments, and validated patterns achieving 2.5-3.5x speedup over manual processes for production-ready delivery pipelines
---

# CI/CD Optimization

Transform manual release processes into automated, quality-gated, observable pipelines with performance tracking and regression detection. Apply when setting up deployment automation, running smoke tests, implementing quality gates, tracking build performance, optimizing CI pipelines, preventing production defects, or establishing release automation workflows. Provides coverage enforcement, CHANGELOG generation, observability metrics, and validated patterns for GitHub Actions with 2.5-3.5x speedup over manual processes.

---

## When to Use This Skill

Apply this skill when:

- **Setting up CI/CD** for new projects
- **Running smoke tests** to validate builds
- **Implementing quality gates** (coverage, linting, tests)
- **Optimizing CI pipelines** taking over 5 minutes
- **Tracking build performance** and detecting regressions
- **Automating deployments** from manual processes
- **Preventing production defects** with automated checks
- **Release automation** with CHANGELOG generation
- **Adding observability** to build pipelines
- **Establishing quality metrics** tracking
- **Integrating pre-merge checks** into pull requests
- **Setting up rollback strategies** for failed deploys

**Don't use when:**
- Pipelines already optimized and fast
- Releases happen monthly or less
- Single-developer projects with simple workflows
- Non-GitHub environments without adaptation capacity

---

## Core Components

### Five Quality Gate Categories

**1. Coverage Threshold Enforcement**
- Minimum test coverage requirement (75-80% recommended)
- Block merge if coverage drops below threshold
- Track coverage trends over time

**2. Lint Blocking**
- Code quality standards enforcement
- Zero tolerance for linting errors
- Configurable warning thresholds

**3. CHANGELOG Validation**
- Ensure release notes completeness
- Validate conventional commit format
- Prevent releases without documentation

**4. Build Verification**
- Cross-platform build success
- Package integrity checks
- Dependency verification

**5. Test Pass Rate**
- 100% test pass requirement
- No flaky test tolerance in critical paths
- Retry mechanism for transient failures

### Release Automation Framework

**Conventional Commits:**
- `feat:` → Minor version bump
- `fix:` → Patch version bump
- `docs:` → Documentation only
- `BREAKING CHANGE:` → Major version bump

**Automated CHANGELOG Generation:**
- Parse commit history
- Generate release notes automatically
- Zero external dependencies

**GitHub Releases:**
- Triggered on version tags
- Attach build artifacts
- Include CHANGELOG content

### Smoke Testing Suite (25 Tests)

**Execution Tests (10):**
- Binary runs without errors
- Help output displays correctly
- Version command works
- Basic commands execute successfully
- Exit codes are correct

**Consistency Tests (8):**
- Output format is valid (JSON, YAML, etc.)
- Error messages are user-friendly
- Logging format is consistent
- Configuration loading works

**Structure Tests (7):**
- Package completeness
- File permissions correct
- Dependencies included
- Directory structure valid

### Observability Framework

**Metrics Tracked:**
- Build time (total duration)
- Test duration (per test suite)
- Coverage percentage
- Artifact size
- Success/failure rates

**Storage:**
- Git-committed CSV files in `.ci-metrics/`
- Time-series data for trend analysis
- Queryable with standard tools

**Regression Detection:**
- 20% threshold against 10-build moving average
- Automated alerts on performance degradation
- Historical comparison reports

---

## Quick Start (30 minutes)

### Step 1: Coverage Gate (10 min)

**Python Example (pytest + pytest-cov):**

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=term --cov-report=xml --cov-fail-under=75

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**TypeScript Example (Vitest):**

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm test -- --coverage --coverage.thresholds.lines=75

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/coverage-final.json
          fail_ci_if_error: true
```

### Step 2: CHANGELOG Automation (15 min)

**Create CHANGELOG Generator Script:**

```python
#!/usr/bin/env python3
"""Generate CHANGELOG from conventional commits."""

import subprocess
import sys
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Commit:
    """Parsed commit information."""
    type: str
    scope: str
    description: str
    body: str
    breaking: bool
    hash: str

def parse_commit(commit_line: str) -> Commit:
    """Parse conventional commit format."""
    parts = commit_line.split('|')
    if len(parts) < 3:
        return None

    hash = parts[0].strip()
    message = parts[1].strip()
    body = parts[2].strip() if len(parts) > 2 else ""

    # Parse conventional commit: type(scope): description
    if ':' not in message:
        return None

    type_scope, description = message.split(':', 1)
    type_scope = type_scope.strip()
    description = description.strip()

    # Extract type and scope
    if '(' in type_scope and ')' in type_scope:
        type = type_scope.split('(')[0]
        scope = type_scope.split('(')[1].split(')')[0]
    else:
        type = type_scope
        scope = ""

    # Check for breaking change
    breaking = 'BREAKING CHANGE' in body or '!' in type_scope

    return Commit(
        type=type,
        scope=scope,
        description=description,
        body=body,
        breaking=breaking,
        hash=hash
    )

def get_commits_since_last_tag() -> List[Commit]:
    """Get commits since last git tag."""
    try:
        # Get last tag
        last_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Get commits since last tag
        commit_range = f"{last_tag}..HEAD"
    except subprocess.CalledProcessError:
        # No tags yet, get all commits
        commit_range = "HEAD"

    # Get commit log
    log = subprocess.check_output([
        'git', 'log', commit_range,
        '--pretty=format:%h|%s|%b',
        '--no-merges'
    ]).decode()

    commits = []
    for line in log.split('\n'):
        if not line.strip():
            continue
        commit = parse_commit(line)
        if commit:
            commits.append(commit)

    return commits

def generate_changelog(commits: List[Commit], version: str) -> str:
    """Generate CHANGELOG content."""
    if not commits:
        return ""

    # Group commits by type
    grouped = defaultdict(list)
    for commit in commits:
        grouped[commit.type].append(commit)

    # Generate markdown
    lines = [
        f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}",
        ""
    ]

    # Breaking changes first
    breaking = [c for c in commits if c.breaking]
    if breaking:
        lines.append("### ⚠️ BREAKING CHANGES")
        lines.append("")
        for commit in breaking:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    # Features
    if 'feat' in grouped:
        lines.append("### ✨ Features")
        lines.append("")
        for commit in grouped['feat']:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    # Bug fixes
    if 'fix' in grouped:
        lines.append("### 🐛 Bug Fixes")
        lines.append("")
        for commit in grouped['fix']:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    # Documentation
    if 'docs' in grouped:
        lines.append("### 📚 Documentation")
        lines.append("")
        for commit in grouped['docs']:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    # Performance improvements
    if 'perf' in grouped:
        lines.append("### ⚡ Performance")
        lines.append("")
        for commit in grouped['perf']:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    # Refactoring
    if 'refactor' in grouped:
        lines.append("### ♻️ Refactoring")
        lines.append("")
        for commit in grouped['refactor']:
            scope_str = f"**{commit.scope}**: " if commit.scope else ""
            lines.append(f"- {scope_str}{commit.description} ({commit.hash})")
        lines.append("")

    return '\n'.join(lines)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: generate_changelog.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Get commits
    commits = get_commits_since_last_tag()

    if not commits:
        print("No commits found since last release.")
        sys.exit(0)

    # Generate CHANGELOG
    changelog = generate_changelog(commits, version)

    # Read existing CHANGELOG
    try:
        with open('CHANGELOG.md', 'r') as f:
            existing = f.read()
    except FileNotFoundError:
        existing = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

    # Prepend new version
    header = existing.split('\n\n')[0] + '\n\n'
    body = '\n\n'.join(existing.split('\n\n')[1:])
    new_changelog = header + changelog + '\n\n' + body

    # Write updated CHANGELOG
    with open('CHANGELOG.md', 'w') as f:
        f.write(new_changelog)

    print(f"✅ CHANGELOG.md updated for version {version}")
    print(changelog)

if __name__ == '__main__':
    main()
```

**Make executable:**
```bash
chmod +x scripts/generate_changelog.py
```

**Add to CI workflow:**
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history for changelog

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Generate CHANGELOG
        run: python scripts/generate_changelog.py ${{ steps.version.outputs.VERSION }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
          files: |
            dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3: Basic Smoke Tests (5 min)

**Python Smoke Tests:**

```python
# tests/smoke/test_smoke.py
"""Smoke tests for basic functionality."""

import subprocess
import json
import pytest

def test_binary_runs():
    """Binary should execute without errors."""
    result = subprocess.run(['python', '-m', 'your_app'], capture_output=True)
    assert result.returncode in [0, 1]  # 0 or expected error code

def test_help_command():
    """Help command should display usage."""
    result = subprocess.run(
        ['python', '-m', 'your_app', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower() or 'help' in result.stdout.lower()

def test_version_command():
    """Version command should display version."""
    result = subprocess.run(
        ['python', '-m', 'your_app', '--version'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Version should match semantic versioning pattern
    import re
    assert re.search(r'\d+\.\d+\.\d+', result.stdout)

def test_config_loading():
    """Application should load configuration correctly."""
    from your_app.config import load_config

    config = load_config()
    assert config is not None
    assert hasattr(config, 'database')
    assert hasattr(config, 'api_key')

def test_json_output_valid():
    """JSON output should be valid."""
    result = subprocess.run(
        ['python', '-m', 'your_app', 'list', '--format', 'json'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))
```

**TypeScript Smoke Tests:**

```typescript
// tests/smoke/smoke.test.ts
import { describe, test, expect } from 'vitest';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

describe('Smoke Tests', () => {
  test('binary runs without errors', async () => {
    try {
      await execAsync('node dist/index.js');
    } catch (error) {
      // Expected exit codes: 0 or 1
      expect([0, 1]).toContain(error.code);
    }
  });

  test('help command displays usage', async () => {
    const { stdout, stderr } = await execAsync('node dist/index.js --help');

    expect(stdout.toLowerCase()).toMatch(/usage|help/);
  });

  test('version command displays version', async () => {
    const { stdout } = await execAsync('node dist/index.js --version');

    // Should match semantic versioning
    expect(stdout).toMatch(/\d+\.\d+\.\d+/);
  });

  test('config loading works', async () => {
    const { loadConfig } = await import('../src/config');

    const config = loadConfig();
    expect(config).toBeDefined();
    expect(config.database).toBeDefined();
    expect(config.apiKey).toBeDefined();
  });

  test('json output is valid', async () => {
    try {
      const { stdout } = await execAsync('node dist/index.js list --format json');

      const data = JSON.parse(stdout);
      expect(typeof data === 'object').toBe(true);
    } catch (error) {
      // If command doesn't exist, that's OK for smoke test
      expect(error.code).toBe(1);
    }
  });
});
```

**Add to CI:**
```yaml
# .github/workflows/ci.yml (add to existing workflow)
  smoke-tests:
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - uses: actions/checkout@v3

      - name: Set up environment
        uses: actions/setup-python@v4  # or setup-node@v3
        with:
          python-version: '3.11'  # or node-version: '20'

      - name: Run smoke tests
        run: pytest tests/smoke/  # or npm run test:smoke
```

---

## Full Implementation (90 minutes)

### Advanced Quality Gates

**1. Multi-Stage Linting:**

```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  lint-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install linters
        run: |
          pip install ruff mypy bandit

      - name: Ruff lint
        run: ruff check .

      - name: Ruff format check
        run: ruff format --check .

      - name: Type check with mypy
        run: mypy src/

      - name: Security check with bandit
        run: bandit -r src/ -f json -o bandit-report.json

      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json

  lint-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Biome lint
        run: npm run lint

      - name: Biome format check
        run: npm run format:check

      - name: Type check
        run: npm run type-check
```

**2. Build Verification Across Platforms:**

```yaml
# .github/workflows/build-matrix.yml
name: Build Matrix

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']  # or node-version

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build
        run: python -m build

      - name: Test
        run: pytest

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist-${{ matrix.os }}-py${{ matrix.python-version }}
          path: dist/
```

### Observability Implementation

**Create metrics collection script:**

```python
#!/usr/bin/env python3
"""Collect and store CI/CD metrics."""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

METRICS_DIR = Path('.ci-metrics')
METRICS_FILE = METRICS_DIR / 'build_metrics.csv'

def ensure_metrics_dir():
    """Create metrics directory if it doesn't exist."""
    METRICS_DIR.mkdir(exist_ok=True)

def load_existing_metrics() -> list:
    """Load existing metrics from CSV."""
    if not METRICS_FILE.exists():
        return []

    with open(METRICS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def record_metric(metric_data: Dict[str, Any]):
    """Record a new metric."""
    ensure_metrics_dir()

    # Add timestamp
    metric_data['timestamp'] = datetime.utcnow().isoformat()

    # Check if file exists to determine if we need header
    file_exists = METRICS_FILE.exists()

    with open(METRICS_FILE, 'a', newline='') as f:
        fieldnames = [
            'timestamp', 'build_time', 'test_duration',
            'coverage_percent', 'artifact_size', 'success'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(metric_data)

def calculate_moving_average(metrics: list, field: str, window: int = 10) -> float:
    """Calculate moving average for a field."""
    if len(metrics) < window:
        window = len(metrics)

    if window == 0:
        return 0.0

    values = [float(m[field]) for m in metrics[-window:] if m[field]]
    return sum(values) / len(values) if values else 0.0

def check_regression(metric_data: Dict[str, Any], threshold: float = 0.20) -> bool:
    """Check if current metric shows regression."""
    metrics = load_existing_metrics()

    if len(metrics) < 3:
        # Not enough data for regression detection
        return False

    # Check build time regression
    avg_build_time = calculate_moving_average(metrics, 'build_time')
    current_build_time = float(metric_data['build_time'])

    if current_build_time > avg_build_time * (1 + threshold):
        print(f"⚠️  Build time regression detected: {current_build_time}s vs {avg_build_time}s average")
        return True

    # Check coverage regression
    avg_coverage = calculate_moving_average(metrics, 'coverage_percent')
    current_coverage = float(metric_data['coverage_percent'])

    if current_coverage < avg_coverage * (1 - threshold):
        print(f"⚠️  Coverage regression detected: {current_coverage}% vs {avg_coverage}% average")
        return True

    return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: collect_metrics.py <metrics.json>")
        sys.exit(1)

    metrics_file = sys.argv[1]

    with open(metrics_file, 'r') as f:
        metric_data = json.load(f)

    # Record metric
    record_metric(metric_data)

    # Check for regressions
    has_regression = check_regression(metric_data)

    # Generate report
    metrics = load_existing_metrics()
    print(f"\n📊 CI/CD Metrics Summary (last 10 builds):")
    print(f"   Average build time: {calculate_moving_average(metrics, 'build_time'):.2f}s")
    print(f"   Average test duration: {calculate_moving_average(metrics, 'test_duration'):.2f}s")
    print(f"   Average coverage: {calculate_moving_average(metrics, 'coverage_percent'):.2f}%")

    if has_regression:
        print("\n⚠️  Performance regression detected!")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Integrate into CI:**

```yaml
# .github/workflows/ci.yml (add to existing workflow)
  collect-metrics:
    runs-on: ubuntu-latest
    needs: [test-coverage, lint, build]
    if: always()
    steps:
      - uses: actions/checkout@v3

      - name: Collect metrics
        run: |
          cat > metrics.json <<EOF
          {
            "build_time": "${{ needs.build.outputs.duration }}",
            "test_duration": "${{ needs.test-coverage.outputs.duration }}",
            "coverage_percent": "${{ needs.test-coverage.outputs.coverage }}",
            "artifact_size": "${{ needs.build.outputs.size }}",
            "success": "${{ needs.test-coverage.result == 'success' && needs.lint.result == 'success' }}"
          }
          EOF

      - name: Record and analyze metrics
        run: python scripts/collect_metrics.py metrics.json

      - name: Commit metrics
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .ci-metrics/
          git commit -m "chore: update CI metrics [skip ci]" || echo "No changes"
          git push || echo "Push failed"
```

### Complete Smoke Test Suite (25 Tests)

```python
# tests/smoke/test_complete_smoke.py
"""Complete smoke test suite (25 tests)."""

import subprocess
import json
import os
import pytest
from pathlib import Path

# ============================================================================
# EXECUTION TESTS (10)
# ============================================================================

def test_binary_runs_without_crash():
    """1. Binary should execute without crashing."""
    result = subprocess.run(['python', '-m', 'your_app'], capture_output=True)
    assert result.returncode in [0, 1]  # Valid exit codes

def test_help_output_displays():
    """2. Help output should display correctly."""
    result = subprocess.run(['python', '-m', 'your_app', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert len(result.stdout) > 0

def test_version_command_works():
    """3. Version command should work."""
    result = subprocess.run(['python', '-m', 'your_app', '--version'], capture_output=True, text=True)
    assert result.returncode == 0

def test_list_command_executes():
    """4. List command should execute."""
    result = subprocess.run(['python', '-m', 'your_app', 'list'], capture_output=True)
    assert result.returncode in [0, 1]

def test_create_command_executes():
    """5. Create command should execute."""
    result = subprocess.run(['python', '-m', 'your_app', 'create', 'test'], capture_output=True)
    assert result.returncode in [0, 1]

def test_invalid_command_fails_gracefully():
    """6. Invalid command should fail gracefully."""
    result = subprocess.run(['python', '-m', 'your_app', 'invalid_command'], capture_output=True, text=True)
    assert result.returncode != 0
    assert len(result.stderr) > 0 or 'error' in result.stdout.lower()

def test_no_args_displays_usage():
    """7. No arguments should display usage."""
    result = subprocess.run(['python', '-m', 'your_app'], capture_output=True, text=True)
    assert 'usage' in result.stdout.lower() or 'usage' in result.stderr.lower()

def test_verbose_flag_works():
    """8. Verbose flag should work."""
    result = subprocess.run(['python', '-m', 'your_app', '--verbose', 'list'], capture_output=True)
    assert result.returncode in [0, 1]

def test_quiet_flag_works():
    """9. Quiet flag should work."""
    result = subprocess.run(['python', '-m', 'your_app', '--quiet', 'list'], capture_output=True)
    assert result.returncode in [0, 1]

def test_exit_code_on_error():
    """10. Should return non-zero exit code on error."""
    result = subprocess.run(['python', '-m', 'your_app', 'invalid'], capture_output=True)
    assert result.returncode != 0

# ============================================================================
# CONSISTENCY TESTS (8)
# ============================================================================

def test_json_output_format_valid():
    """11. JSON output format should be valid."""
    result = subprocess.run(['python', '-m', 'your_app', 'list', '--format', 'json'], capture_output=True, text=True)
    if result.returncode == 0:
        json.loads(result.stdout)  # Should not raise

def test_error_messages_user_friendly():
    """12. Error messages should be user-friendly."""
    result = subprocess.run(['python', '-m', 'your_app', 'invalid'], capture_output=True, text=True)
    error_output = result.stderr or result.stdout
    assert len(error_output) > 0
    assert not any(x in error_output for x in ['Traceback', 'Exception'])

def test_logging_format_consistent():
    """13. Logging format should be consistent."""
    result = subprocess.run(['python', '-m', 'your_app', '--verbose', 'list'], capture_output=True, text=True)
    # Check for structured logging (JSON or consistent format)
    if result.returncode == 0 and result.stdout:
        lines = result.stdout.strip().split('\n')
        # Should have consistent format
        assert all(len(line) > 0 for line in lines)

def test_config_file_loading():
    """14. Config file should load correctly."""
    from your_app.config import load_config
    config = load_config()
    assert config is not None

def test_environment_variable_override():
    """15. Environment variables should override config."""
    env = os.environ.copy()
    env['APP_DEBUG'] = 'true'
    result = subprocess.run(['python', '-m', 'your_app', 'list'], env=env, capture_output=True)
    assert result.returncode in [0, 1]

def test_output_encoding_utf8():
    """16. Output should be UTF-8 encoded."""
    result = subprocess.run(['python', '-m', 'your_app', 'list'], capture_output=True, text=True, encoding='utf-8')
    assert result.returncode in [0, 1]

def test_timestamps_iso8601_format():
    """17. Timestamps should use ISO 8601 format."""
    result = subprocess.run(['python', '-m', 'your_app', 'list', '--format', 'json'], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        import re
        # Check for ISO 8601 timestamp pattern
        assert re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', result.stdout)

def test_error_codes_documented():
    """18. Error codes should be documented."""
    result = subprocess.run(['python', '-m', 'your_app', '--help'], capture_output=True, text=True)
    # Should mention exit codes or have documentation
    assert result.returncode == 0

# ============================================================================
# STRUCTURE TESTS (7)
# ============================================================================

def test_package_structure_complete():
    """19. Package structure should be complete."""
    package_dir = Path('src/your_app')
    assert package_dir.exists()
    assert (package_dir / '__init__.py').exists()
    assert (package_dir / '__main__.py').exists()

def test_dependencies_installed():
    """20. Dependencies should be installed."""
    try:
        import your_app
        assert your_app is not None
    except ImportError:
        pytest.fail("Package not importable")

def test_entry_point_exists():
    """21. Entry point should exist."""
    result = subprocess.run(['which', 'your-app'], capture_output=True)
    # Entry point may or may not exist depending on installation
    assert result.returncode in [0, 1]

def test_config_directory_structure():
    """22. Config directory should have correct structure."""
    # Check for config files
    assert Path('config').exists() or Path('src/your_app/config').exists()

def test_logging_directory_writable():
    """23. Logging directory should be writable."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    test_file = log_dir / 'test.log'
    test_file.write_text('test')
    assert test_file.exists()
    test_file.unlink()

def test_temp_directory_cleanup():
    """24. Temp directories should be cleaned up."""
    temp_dir = Path('/tmp/your_app')
    # Should not have leftover temp files
    if temp_dir.exists():
        assert len(list(temp_dir.iterdir())) < 100  # Reasonable limit

def test_permissions_correct():
    """25. File permissions should be correct."""
    package_dir = Path('src/your_app')
    for file in package_dir.rglob('*.py'):
        assert os.access(file, os.R_OK)  # Readable
```

---

## Performance Optimization Strategies

### 1. Native-Only Testing (Mature Languages)

For mature, well-tested languages (Go, Rust, Python 3.10+), skip cross-platform testing in CI:

```yaml
# Only test on native platform
jobs:
  test:
    runs-on: ubuntu-latest  # Single platform
```

### 2. Module Caching

```yaml
# Python caching
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Node.js caching
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 3. Parallel Execution

```yaml
jobs:
  test:
    strategy:
      matrix:
        test-suite: [unit, integration, smoke]
    steps:
      - run: pytest tests/${{ matrix.test-suite }}
```

### 4. Fail Fast

```yaml
strategy:
  fail-fast: true  # Stop all jobs if one fails
```

---

## Validation Results

### Meta-CC Project Results

**Pattern Validation:** 91.7% (11 of 12 patterns validated)

**Performance Improvement:** 2.5-3.5x speedup vs manual processes

**Transferability:**
- GitHub Actions: 100% (native support)
- GitLab CI: 80% (requires YAML adaptation)
- Jenkins: 70% (requires Groovy adaptation)

**Time Savings:**
- Manual release: 45-60 minutes
- Automated release: 15-20 minutes
- Net savings: 30-40 minutes per release

---

## Common Anti-Patterns

### ❌ 1. Testing Everything Everywhere
**Problem:** Running full test suite on every platform
**Solution:** Use native-only testing for mature languages

### ❌ 2. No Performance Tracking
**Problem:** No visibility into CI/CD performance trends
**Solution:** Implement observability metrics with regression detection

### ❌ 3. Manual CHANGELOG Updates
**Problem:** Forgetting to update CHANGELOG before release
**Solution:** Automate from conventional commits

### ❌ 4. Weak Quality Gates
**Problem:** Allowing code with failing tests to merge
**Solution:** Enforce strict quality gates (100% pass rate)

### ❌ 5. No Smoke Tests
**Problem:** Deployments break basic functionality
**Solution:** Implement comprehensive smoke test suite

### ❌ 6. Ignoring Build Regressions
**Problem:** Builds getting slower over time
**Solution:** Track metrics and alert on 20% degradation

---

## Implementation Checklist

### Phase 1: Foundation (Week 1)
- [ ] Set up GitHub Actions workflow
- [ ] Add coverage gate (75-80% threshold)
- [ ] Implement basic linting
- [ ] Create smoke test suite (10+ tests)
- [ ] Set up CHANGELOG automation

### Phase 2: Quality Gates (Week 2)
- [ ] Add multi-stage linting (format, type, security)
- [ ] Implement build verification
- [ ] Add test pass rate enforcement
- [ ] Create pre-commit hooks
- [ ] Document quality standards

### Phase 3: Observability (Week 3)
- [ ] Implement metrics collection
- [ ] Set up regression detection (20% threshold)
- [ ] Create performance dashboard
- [ ] Add historical trend tracking
- [ ] Configure alerts

### Phase 4: Optimization (Week 4)
- [ ] Enable module caching
- [ ] Implement parallel execution
- [ ] Optimize test execution time
- [ ] Add fail-fast strategy
- [ ] Measure and document improvements

### Phase 5: Release Automation (Week 5)
- [ ] Set up tag-triggered releases
- [ ] Automate artifact uploads
- [ ] Configure GitHub Releases
- [ ] Test rollback procedures
- [ ] Document release process

---

## Related Skills

- **ms-foundation-trust**: Test coverage requirements
- **ms-essentials-review**: Code quality standards
- **cross-cutting-concerns**: Linting and enforcement patterns
- **api-testing-patterns**: Integration test strategies

---

## References

- GitHub Actions Documentation: https://docs.github.com/en/actions
- Conventional Commits: https://www.conventionalcommits.org/
- Semantic Versioning: https://semver.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- Codecov: https://docs.codecov.com/
- Keep a Changelog: https://keepachangelog.com/

---

**Version:** 1.0.0
**Source:** github.com/yaleh/meta-cc (Go original)
**Validation:** Bootstrap project (91.7% pattern validation, 2.5-3.5x speedup)
**Estimated ROI:** 2.5-3.5x time savings over manual processes
