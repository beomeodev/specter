# Pre-commit Hook Logs

This directory contains logs from pre-commit hooks when errors or warnings occur.

## Log Format

Each log file follows this naming convention:
```
pre-commit-YYYYMMDD-HHMMSS.log
```

Example: `pre-commit-20251027-143025.log`

## Log Content

Each log file includes:
- **Date & Time**: When the pre-commit hook ran
- **Exit Code**: The exit code from pre-commit (0 = success, non-zero = error)
- **Command**: Which command triggered the hook (`/fin` or `/finq`)
- **Output**: Full stdout and stderr from pre-commit hooks
- **Environment**: Git branch and commit context

## When Logs Are Created

Logs are **only** created when:
- Pre-commit exits with non-zero exit code (errors)
- Output contains "error", "warning", or "fail" keywords

**No logs are created for successful runs** - this keeps the directory clean.

## Example Log File

```markdown
# Pre-commit Hook Log
Date: 2025-10-27 14:30:25
Exit Code: 1
Command: /finq

## Output:
ruff....................................................................Failed
- hook id: ruff
- exit code: 1

src/example.py:15:1: F401 'os' imported but unused

## Environment:
Branch: feature/new-feature
Commit: a1b2c3d
```

## Troubleshooting

If you see repeated errors in these logs:
1. Review the specific error message in the log
2. Fix the issue in your code
3. Run `/fin` or `/finq` again to verify the fix

## Log Retention

These logs are kept for manual review and troubleshooting. You can safely delete old logs after reviewing them.
