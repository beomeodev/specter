# My-Spec Hooks Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-26
**Status**: Active

---

## Table of Contents

1. [Introduction](#introduction)
2. [Hook System Architecture](#hook-system-architecture)
3. [The Four Hook Events](#the-four-hook-events)
4. [Hook Implementation Details](#hook-implementation-details)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

My-Spec's Hook system provides automated safety infrastructure based on MoAI-ADK's proven architecture. Hooks are Python 3.13+ scripts that intercept key events in the Claude Code session lifecycle to provide:

- **Automatic safety checkpoints** before risky operations
- **Constitution context injection** for sub-agent delegation
- **Auto-formatting** for code consistency
- **Project status display** at session start

**Key Benefits:**
- 🔒 **Safety**: Automatic Git checkpoints before critical file edits
- 🤖 **Intelligence**: Constitution-aware sub-agents
- 🎨 **Consistency**: Auto-formatting with Prettier and Black
- 📊 **Visibility**: Real-time project status tracking

---

## Hook System Architecture

### Components

```
.claude/hooks/ms/
├── ms_hooks.py              # Entry point (CLI args router)
├── core/
│   ├── __init__.py          # HookPayload, HookResult classes
│   ├── project.py           # Language detect, Git info, TAG integrity
│   ├── checkpoint.py        # Auto checkpoints
│   └── tags.py              # TAG scan, validation (future)
└── handlers/
    ├── session.py           # SessionStart, SessionEnd
    ├── user.py              # UserPromptSubmit
    └── tool.py              # PreToolUse, PostToolUse
```

### Data Flow

```
Claude Code Event
       ↓
.claude/settings.local.json (hook configuration)
       ↓
ms_hooks.py (entry point)
       ↓
Event Router (SessionStart/PreToolUse/PostToolUse/UserPromptSubmit)
       ↓
Specific Handler (session.py/tool.py/user.py)
       ↓
Core Functions (project.py/checkpoint.py)
       ↓
HookResult (continue_execution, system_message)
       ↓
Claude Code (continues or blocks based on result)
```

---

## The Four Hook Events

### 1. SessionStart

**When**: Claude Code session begins
**Purpose**: Display project status card
**Performance**: Target <100ms (current: 2-5s, optimization pending)

**What It Does:**
- Detects primary programming language (20+ languages supported)
- Extracts Git branch, commit hash, and change count
- Counts SPEC files and calculates completion percentage
- Calculates TAG integrity score (@SPEC → @TEST → @CODE chains)

**Example Output:**
```
🚀 My-Spec Session Started

📊 Project Status:
  Language: Python
  Git Branch: master ✓ (2 changes)
  SPEC Progress: 2/2 completed (100%)
  TAG Integrity: 0% (139 @SPEC tags, 0 complete chains)

📁 Working Directory: /workspace/specter
```

**Files Involved:**
- `.claude/hooks/ms/handlers/session.py`
- `.claude/hooks/ms/core/project.py`

---

### 2. PreToolUse

**When**: Before any tool (Read, Write, Edit, Bash, etc.) executes
**Purpose**: Create Git checkpoints before risky operations
**Performance**: <100ms ✅

**What It Does:**
- Detects risky operations:
  - Editing `.specify/memory/constitution.md`
  - Editing ≥5 files simultaneously
  - Dangerous Bash commands (`rm -rf`, `git reset --hard`, etc.)
- Creates Git checkpoint branch: `checkpoint/before-{operation}-{timestamp}`
- Logs checkpoint to `.specify/checkpoints.log`
- Uses **Fail-open**: Continues execution even if checkpoint fails

**Risky Operations Detected:**

| Tool | Condition | Checkpoint Name |
|------|-----------|-----------------|
| Edit/Write | `.specify/memory/constitution.md` | `before-critical-file-{timestamp}` |
| MultiEdit | ≥5 files | `before-bulk-edit-{timestamp}` |
| Bash | `rm -rf`, `git merge`, `git reset --hard` | `before-dangerous-command-{timestamp}` |

**Checkpoint Log Format:**
```
2025-10-26T10:30:00Z | CHECKPOINT | before-critical-file | branch: checkpoint/before-critical-file-20251026103000
```

**Files Involved:**
- `.claude/hooks/ms/handlers/tool.py`
- `.claude/hooks/ms/core/checkpoint.py`

---

### 3. PostToolUse

**When**: After tool execution completes
**Purpose**: Auto-format code files
**Performance**: <100ms ✅ (trigger only, formatting runs async)

**What It Does:**
- Detects file type by extension:
  - TypeScript/JavaScript: `.ts`, `.tsx`, `.js`, `.jsx` → `npx prettier --write {file}`
  - Python: `.py` → `black {file}`
- Runs formatter asynchronously (non-blocking via subprocess.Popen)
- Uses **Fail-open**: Ignores formatter errors

**Supported Formatters:**

| Language | Extension | Formatter | Command |
|----------|-----------|-----------|---------|
| TypeScript | .ts, .tsx | Prettier | `npx prettier --write {file}` |
| JavaScript | .js, .jsx | Prettier | `npx prettier --write {file}` |
| Python | .py | Black | `black {file}` |

**Files Involved:**
- `.claude/hooks/ms/handlers/tool.py`

---

### 4. UserPromptSubmit

**When**: User submits a prompt
**Purpose**: Inject Constitution context for sub-agent delegation
**Performance**: <100ms ✅

**What It Does:**
- Detects Task tool invocation (sub-agent delegation):
  - Prompt contains `Task(` or `subagent_type=`
- Reads and injects Constitution context:
  - `.specify/memory/constitution.md` (first 16000 tokens)
  - `AGENTS.md` (if exists, first 16000 tokens)
  - Project structure docs (if exists, first 16000 tokens)
- Prepends context to agent prompt with marker: `# Constitution Context (Auto-Injected)`

**Injection Format:**
```markdown
# Constitution Context (Auto-Injected)

## Constitution

[Constitution content...]

## AI Coding Standards (AGENTS.md)

[AGENTS.md content...]

---

[Original user prompt...]
```

**Files Involved:**
- `.claude/hooks/ms/handlers/user.py`

---

## Hook Implementation Details

### HookPayload Class

```python
class HookPayload:
    """Standard payload format for all hooks"""
    def __init__(self, cwd: str, tool_name: str = None, tool_input: dict = None):
        self.cwd = cwd              # Working directory
        self.tool_name = tool_name  # Tool being invoked (PreToolUse/PostToolUse)
        self.tool_input = tool_input  # Tool arguments
```

### HookResult Class

```python
class HookResult:
    """Standard result format for all hooks"""
    def __init__(self, continue_execution=True, system_message=None):
        self.continue_execution = continue_execution  # Allow/block operation
        self.system_message = system_message  # Message to display
        self.start_time = time.time()  # For performance logging

    def finalize(self) -> dict:
        """Convert to Claude Code format"""
        return {
            "continue": self.continue_execution,
            "systemMessage": self.system_message
        }
```

### Fail-Open Error Handling

All hooks use **Fail-open** principle:
- If hook encounters error, execution continues (doesn't block user)
- Errors logged to stderr for debugging
- Graceful degradation (e.g., "Language: Unknown" if detection fails)

**Example:**
```python
def detect_language(cwd: str) -> str:
    try:
        # Language detection logic...
        return detected_language
    except Exception as e:
        print(f"Language detection failed: {e}", file=sys.stderr)
        return "Unknown"  # Fail-open: return default value
```

---

## Usage Examples

### Example 1: Manual Hook Testing

```bash
# Test SessionStart hook
echo '{"cwd": "."}' | python .claude/hooks/ms/ms_hooks.py SessionStart

# Test PreToolUse hook (Constitution edit)
echo '{"cwd": ".", "tool_name": "Edit", "tool_input": {"file_path": ".specify/memory/constitution.md"}}' | python .claude/hooks/ms/ms_hooks.py PreToolUse

# Test PostToolUse hook (Python file formatting)
echo '{"cwd": ".", "tool_name": "Write", "tool_input": {"file_path": "test.py"}}' | python .claude/hooks/ms/ms_hooks.py PostToolUse

# Test UserPromptSubmit hook (Task tool detection)
echo '{"cwd": ".", "prompt": "Task(subagent_type=\"spec-builder\")"}' | python .claude/hooks/ms/ms_hooks.py UserPromptSubmit
```

### Example 2: Checkpoint Restoration

```bash
# List all checkpoints
cat .specify/checkpoints.log

# Restore from checkpoint
git checkout checkpoint/before-critical-file-20251026103000

# Review changes
git diff master

# Return to master
git checkout master
```

### Example 3: Custom Language Detection

```python
# Add new language to .claude/hooks/ms/core/project.py

def detect_language(cwd: str) -> str:
    """Detect primary language"""
    # Add your custom language detection
    if Path(f"{cwd}/Gemfile").exists():
        return "ruby"

    if Path(f"{cwd}/build.gradle").exists():
        return "java"

    # ... existing logic ...
```

---

## Configuration

### .claude/settings.local.json

```json
{
  "hooks": [
    {
      "event": "SessionStart",
      "command": "python",
      "args": [".claude/hooks/ms/ms_hooks.py", "SessionStart"]
    },
    {
      "event": "SessionEnd",
      "command": "python",
      "args": [".claude/hooks/ms/ms_hooks.py", "SessionEnd"]
    },
    {
      "event": "UserPromptSubmit",
      "command": "python",
      "args": [".claude/hooks/ms/ms_hooks.py", "UserPromptSubmit"]
    },
    {
      "event": "PreToolUse",
      "command": "python",
      "args": [".claude/hooks/ms/ms_hooks.py", "PreToolUse"]
    },
    {
      "event": "PostToolUse",
      "command": "python",
      "args": [".claude/hooks/ms/ms_hooks.py", "PostToolUse"]
    }
  ]
}
```

### Environment Variables

No environment variables currently required.

### Dependencies

- Python ≥3.13 (REQUIRED)
- Git ≥2.30
- Prettier (for TypeScript/JavaScript formatting)
- Black (for Python formatting)

---

## Best Practices

### 1. Keep Hooks Fast

**Guideline**: Hooks should execute in <100ms
**Current Status**:
- SessionStart: 2-5s (optimization pending)
- PreToolUse: <100ms ✅
- PostToolUse: <100ms ✅
- UserPromptSubmit: <100ms ✅

**Optimization Strategies:**
- Cache expensive operations (language detection, TAG scanning)
- Use parallel execution (ThreadPoolExecutor)
- Defer non-critical operations to background

### 2. Always Use Fail-Open

**Guideline**: Never block user due to hook errors

**Example:**
```python
# ❌ Bad: Blocks user if error
def risky_operation():
    result = subprocess.run(["git", "branch"], check=True)  # Raises on error
    return result.stdout

# ✅ Good: Fail-open
def safe_operation():
    try:
        result = subprocess.run(["git", "branch"], check=True, timeout=5)
        return result.stdout
    except Exception as e:
        print(f"Git operation failed: {e}", file=sys.stderr)
        return "git-info-unavailable"  # Graceful degradation
```

### 3. Log Performance Metrics

**Guideline**: Track hook performance for optimization

**Implementation** (future):
```python
# .specify/hooks_performance.log (JSON lines)
{"hook": "SessionStart", "duration_ms": 2547, "exceeded_limit": true, "timestamp": "2025-10-26T10:30:00Z"}
{"hook": "PreToolUse", "duration_ms": 42, "exceeded_limit": false, "timestamp": "2025-10-26T10:31:00Z"}
```

### 4. Test Hooks Independently

**Guideline**: Each hook should have comprehensive unit tests

**Example**:
```python
# tests/hooks/test_session_hooks.py
def test_session_start_displays_project_status():
    result = run_hook("SessionStart", {"cwd": "."})
    assert "🚀 My-Spec Session Started" in result["message"]
    assert "Language" in result["message"]
```

**Current Test Coverage**:
- SessionStart: 18 tests ✅
- PreToolUse: 21 tests ✅
- PostToolUse: Manual testing ✅
- UserPromptSubmit: Manual testing ✅

### 5. Document Risky Operations

**Guideline**: Clearly document what triggers checkpoints

**Current Risky Operations:**
- Constitution file edit
- Bulk edits (≥5 files)
- Dangerous Bash commands

**How to Add New Risky Operation:**
```python
# .claude/hooks/ms/core/checkpoint.py

def detect_risky_operation(tool_name: str, tool_args: dict, cwd: str) -> tuple[bool, str]:
    """Detect risky operations"""

    # Add your custom risky operation
    if tool_name == "Edit":
        file_path = tool_args.get("file_path", "")

        # Example: Protect package.json
        if "package.json" in file_path:
            return (True, "package-json-edit")

    # ... existing logic ...
```

---

## Troubleshooting

### Issue 1: Hooks Not Triggering

**Symptom**: SessionStart hook doesn't display project status

**Diagnosis:**
```bash
# Verify hooks configuration
cat .claude/settings.local.json

# Test hook manually
echo '{"cwd": "."}' | python .claude/hooks/ms/ms_hooks.py SessionStart

# Check Python version
python3 --version  # Must be ≥3.13
```

**Solution:**
1. Ensure Python 3.13+ installed
2. Verify `.claude/settings.local.json` has correct hook configuration
3. Check permissions: `chmod +x .claude/hooks/ms/ms_hooks.py`
4. Restart Claude Code session

---

### Issue 2: SessionStart Hook Slow (>5 seconds)

**Symptom**: Project status card takes 2-5 seconds to display

**Diagnosis:**
```bash
# Measure hook performance
time echo '{"cwd": "."}' | python .claude/hooks/ms/ms_hooks.py SessionStart
```

**Solution** (optimization pending):
1. **Caching**: Implement project info cache (1-minute TTL)
2. **Parallel Execution**: Use ThreadPoolExecutor for concurrent operations
3. **Lazy Loading**: Display basic info first, update TAG integrity later

**Workaround**: Disable TAG integrity calculation temporarily:
```python
# .claude/hooks/ms/handlers/session.py
def handle_session_start(payload: dict) -> HookResult:
    # ... existing code ...

    # Comment out TAG integrity calculation
    # tag_integrity = calculate_tag_integrity(cwd)
    tag_integrity = "disabled for performance"

    # ... rest of code ...
```

---

### Issue 3: Git Checkpoint Creation Fails

**Symptom**: PreToolUse hook shows "checkpoint-failed" in log

**Diagnosis:**
```bash
# Verify Git repository
git status

# Check .specify/ directory exists
ls -la .specify/

# Check checkpoints log
cat .specify/checkpoints.log

# Test checkpoint manually
python -c "from .claude.hooks.ms.core.checkpoint import create_checkpoint; print(create_checkpoint('test', '.'))"
```

**Solution:**
1. Ensure Git repository initialized: `git init`
2. Create `.specify/` directory: `mkdir -p .specify && touch .specify/checkpoints.log`
3. Check Git permissions
4. Verify no Git lock files: `rm -f .git/index.lock`

---

### Issue 4: Auto-Formatting Not Working

**Symptom**: Python/TypeScript files not auto-formatted after edit

**Diagnosis:**
```bash
# Verify Prettier installed
npx prettier --version

# Verify Black installed
black --version

# Test formatting manually
npx prettier --write test.ts
black test.py
```

**Solution:**
1. Install Prettier: `npm install -D prettier`
2. Install Black: `pip install black`
3. Verify PostToolUse hook configured in settings.local.json
4. Check hook logs for formatter errors

---

### Issue 5: Constitution Not Injected for Sub-Agents

**Symptom**: Sub-agent doesn't have Constitution context

**Diagnosis:**
```bash
# Test UserPromptSubmit hook
echo '{"cwd": ".", "prompt": "Task(subagent_type=\"test\")"}' | python .claude/hooks/ms/ms_hooks.py UserPromptSubmit

# Verify Constitution exists
ls -la .specify/memory/constitution.md
```

**Solution:**
1. Ensure Constitution file exists at `.specify/memory/constitution.md`
2. Verify UserPromptSubmit hook configured
3. Check prompt contains Task tool invocation
4. Test hook manually (command above)

---

## Performance Tuning

### Current Performance Metrics

| Hook | Current | Target | Status |
|------|---------|--------|--------|
| SessionStart | 2-5s | <100ms | ⚠️ NEEDS OPTIMIZATION |
| PreToolUse | <100ms | <100ms | ✅ PASS |
| PostToolUse | <100ms | <100ms | ✅ PASS |
| UserPromptSubmit | <100ms | <100ms | ✅ PASS |

### Optimization Roadmap

**Phase 1 (Immediate - Week 1-2):**
- Implement project info caching (1-minute TTL)
- Disable TAG integrity calculation temporarily
- Add performance logging

**Phase 2 (Short-term - Week 3-4):**
- Parallel execution for `detect_language()` and `get_git_info()`
- Lazy loading for TAG integrity (display "calculating..." first)
- Optimize language detection (reduce file I/O)

**Phase 3 (Long-term - Week 5-6):**
- Background TAG integrity calculation (async)
- Redis/file-based cache for expensive operations
- Performance profiling and bottleneck analysis

---

## References

### My-Spec Documentation
- [Migration Guide](../migration/moai-integration-guide.md)
- [Existing Hooks Analysis](../migration/existing-hooks-analysis.md)
- [Constitution Template](../../.specify/memory/constitution.md)

### MoAI-ADK Documentation
- [MoAI-ADK Hooks Implementation](https://github.com/modu-ai/moai-adk)
- [MoAI Hooks Analysis](/workspace/specter/docs/references/moai-adk-hooks-analysis.md)

### Claude Code Documentation
- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Hook Configuration Guide](https://docs.claude.com/en/docs/claude-code/hooks#configuration)

---

## Changelog

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-26 | 1.0.0 | Initial Hooks guide created | Claude Code (MoAI Integration) |

---

**END OF HOOKS GUIDE**

For questions or issues, please refer to the troubleshooting section or consult the MoAI-ADK reference documentation.
