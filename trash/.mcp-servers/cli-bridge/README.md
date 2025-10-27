# CLI Bridge MCP Server

Minimal MCP server that bridges Claude Code (VSCode Extension) to **Gemini CLI** and **Codex CLI**, preserving their authentication sessions.

## Features

- ✅ **Gemini CLI Integration** - Uses existing `gemini` login session
- ✅ **Codex CLI Integration** - Uses existing `codex` login session
- ✅ **Python 3.14 Background Tasks** - True parallel execution with free-threading
- ✅ **Task Management** - Start tasks in background, retrieve results later
- ✅ **Zero Configuration** - No API keys required
- ✅ **Zero Token Overhead** - Only 3 tools exposed (~400 tokens vs 4,300 for Zen MCP)

## Prerequisites

1. **Python 3.10+**
2. **MCP SDK**: `pip install mcp`
3. **Gemini CLI** (optional): `npm install -g @google/gemini-cli && gemini login`
4. **Codex CLI** (optional): Already installed (`codex login status` shows "Logged in")

## Installation

### Option 1: Direct Python Execution

```bash
# Test the server
python /workspace/my-spec/.mcp-servers/cli-bridge/server.py
```

### Option 2: Add to Claude Code Settings

Add to your Claude Code configuration:

**Global Settings** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "cli-bridge": {
      "command": "python",
      "args": ["/workspace/my-spec/.mcp-servers/cli-bridge/server.py"]
    }
  }
}
```

**Project Settings** (`.mcp.json` in project root):
```json
{
  "mcpServers": {
    "cli-bridge": {
      "command": "python",
      "args": ["${workspaceFolder}/.mcp-servers/cli-bridge/server.py"]
    }
  }
}
```

## Usage

### In Claude Code VSCode Extension

```plaintext
# Consult Gemini CLI
Use mcp__cli-bridge__gemini_cli to ask: "What are the latest React 19 features?"

# Consult Codex CLI
Use mcp__cli-bridge__codex_cli to ask: "Review this authentication code for security issues"

# With file context (Gemini only)
Use mcp__cli-bridge__gemini_cli with files ["src/auth.py"] to analyze authentication flow
```

### Tool Schemas

#### `gemini_cli`
```json
{
  "prompt": "string (required)",
  "files": ["array of file paths (optional)"],
  "background": "boolean (optional, default: false)"
}
```

**Synchronous Mode** (`background=false`):
- Blocks until CLI execution completes
- Returns full output as string
- Use for quick queries

**Background Mode** (`background=true`):
- Returns immediately with `TASK_STARTED:{task_id}`
- CLI executes independently
- Use `get_task_result` to retrieve result

#### `codex_cli`
```json
{
  "prompt": "string (required)",
  "background": "boolean (optional, default: false)"
}
```

Same behavior as `gemini_cli` for background execution.

#### `get_task_result` (NEW)
```json
{
  "task_id": "string (required)",
  "wait": "boolean (optional, default: false)",
  "timeout": "number (optional, default: 600)"
}
```

**Non-blocking Mode** (`wait=false`):
- Returns current status immediately
- Returns: result (if completed), "STATUS:RUNNING" (if running), or "ERROR:{msg}"

**Blocking Mode** (`wait=true`):
- Waits until task completes or timeout
- Returns: full CLI output or error message

## Verification

```bash
# Check CLI authentication status
gemini --version  # Should show version if installed
codex login status  # Should show "Logged in using ChatGPT"

# Test MCP server manually
python server.py
# Server should start without errors
```

## Background Execution Examples

### Example 1: Sequential vs Parallel

**❌ Sequential (30 seconds total)**:
```python
# Each task blocks until completion
result1 = mcp__cli-bridge__gemini_cli(
    prompt="Search codebase for patterns"  # Takes 10s
)
result2 = mcp__cli-bridge__gemini_cli(
    prompt="Research library docs"  # Takes 10s
)
result3 = mcp__cli-bridge__codex_cli(
    prompt="Update CHANGELOG"  # Takes 10s
)
# Total: 10 + 10 + 10 = 30 seconds
```

**✅ Parallel (10 seconds total)**:
```python
# Step 1: Launch all tasks in background (returns immediately)
task_id_1 = mcp__cli-bridge__gemini_cli(
    prompt="Search codebase for patterns",
    background=True  # Returns TASK_STARTED:{uuid}
)
task_id_2 = mcp__cli-bridge__gemini_cli(
    prompt="Research library docs",
    background=True
)
task_id_3 = mcp__cli-bridge__codex_cli(
    prompt="Update CHANGELOG",
    background=True
)

# Step 2: Do other work while tasks run in parallel
# ... (Claude Code continues working)

# Step 3: Retrieve results when needed
result1 = mcp__cli-bridge__get_task_result(task_id=task_id_1, wait=True)
result2 = mcp__cli-bridge__get_task_result(task_id=task_id_2, wait=True)
result3 = mcp__cli-bridge__get_task_result(task_id=task_id_3, wait=True)
# Total: max(10, 10, 10) = 10 seconds
```

### Example 2: Fire-and-Forget with Polling

```python
# Launch long-running task
task_id = mcp__cli-bridge__gemini_cli(
    prompt="Deep codebase analysis (may take 5 minutes)",
    background=True
)

# Continue with other work...
# (Claude Code does other tasks)

# Check status periodically
status = mcp__cli-bridge__get_task_result(
    task_id=task_id,
    wait=False  # Non-blocking check
)

if "STATUS:RUNNING" in status:
    # Task still running, continue other work
    pass
elif "ERROR:" in status:
    # Handle error
    pass
else:
    # Task completed, use result
    pass
```

### Example 3: Real-World Workflow (ms.implement)

```python
# Step 1.5: Library research (background)
task_id = mcp__cli-bridge__gemini_cli(
    prompt="""Research latest API documentation for:
    - Library: fastapi
    - Topic: background tasks
    - Return: API usage examples and best practices
    """,
    background=True
)

# Step 2: Claude Code reads spec.md, plan.md, tasks.md
# (works in parallel while Gemini researches)

# Step 3: Retrieve library docs when needed for implementation
library_docs = mcp__cli-bridge__get_task_result(
    task_id=task_id,
    wait=True
)

# Step 4: Implement using latest library patterns

# Step 3.5: Update CHANGELOG in background (while Claude inserts TAG blocks)
changelog_task_id = mcp__cli-bridge__codex_cli(
    prompt="Update docs/CHANGELOG.md with implementation details",
    background=True
)

# Claude continues with TAG block insertion...

# Wait for CHANGELOG update before finishing
changelog_result = mcp__cli-bridge__get_task_result(
    task_id=changelog_task_id,
    wait=True
)
```

## Python 3.14 Free-Threading

### Enable Free-Threading Mode

```bash
# Check current GIL status
python -c "import sys; print(f'GIL enabled: {sys._is_gil_enabled()}')"

# Disable GIL for true parallelism
export PYTHON_GIL=0
python .mcp-servers/cli-bridge/server.py

# Or use command-line flag
python -X gil=0 .mcp-servers/cli-bridge/server.py
```

### Performance Impact

| Mode | Behavior | Performance |
|------|----------|-------------|
| **GIL Enabled** (default) | Concurrent I/O-bound tasks | Good for network requests |
| **GIL Disabled** | True parallel execution | Excellent for CPU + I/O mix |

**Recommendation**: Enable free-threading (`PYTHON_GIL=0`) for maximum performance.

### Implementation Pattern (from Python 3.14 docs)

```python
# Official Python 3.14 pattern used in this server
background_tasks = set()

task = asyncio.create_task(some_coro(param=i))

# Add task to the set. This creates a strong reference.
background_tasks.add(task)

# To prevent keeping references to finished tasks forever,
# make each task remove its own reference from the set after
# completion:
task.add_done_callback(background_tasks.discard)
```

**Reference**: [Python 3.14 asyncio-task documentation](https://docs.python.org/3.14/library/asyncio-task.html#managing-background-tasks)

## Troubleshooting

### "gemini command not found"
```bash
npm install -g @google/gemini-cli
gemini login
```

### "codex command not found"
Already installed in your system. Check:
```bash
which codex
codex login status
```

### MCP Server Not Appearing in `/mcp`
1. Check `.mcp.json` syntax
2. Restart VSCode Extension
3. Check logs: `~/.claude/logs/`

## Token Overhead Comparison

| MCP Server | Tools | Schema Tokens/msg | Conversation (20 msgs) |
|------------|-------|-------------------|------------------------|
| CLI Bridge | 2 | ~300 | 6,000 |
| Zen MCP | 18 | ~4,300 | 86,000 |
| **Savings** | **-16** | **-4,000 (93%)** | **-80,000** |

## Architecture

```
Claude Code VSCode Extension
    ↓
CLI Bridge MCP Server (server.py)
    ↓
subprocess.exec()
    ├─ gemini --yolo --telemetry false
    │  └─ Uses ~/.gemini/auth (login session)
    │
    └─ codex exec --json
       └─ Uses ~/.codex/config.toml (login session)
```

**Key Design:**
- No API keys stored/transmitted
- CLI authentication preserved (login sessions)
- Direct subprocess execution
- JSON parsing for Codex output
- File attachment support for Gemini

## License

MIT - Based on analysis of Zen MCP's clink tool architecture
