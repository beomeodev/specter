# CLI Bridge MCP Server

Minimal MCP server that bridges Claude Code (VSCode Extension) to **Gemini CLI** and **Codex CLI**, preserving their authentication sessions.

## Features

- ✅ **Gemini CLI Integration** - Uses existing `gemini` login session
- ✅ **Codex CLI Integration** - Uses existing `codex` login session
- ✅ **Zero Configuration** - No API keys required
- ✅ **Lightweight** - ~150 lines, single file
- ✅ **Zero Token Overhead** - Only 2 tools exposed (~300 tokens vs 4,300 for Zen MCP)

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
  "files": ["array of file paths (optional)"]
}
```

#### `codex_cli`
```json
{
  "prompt": "string (required)"
}
```

## Verification

```bash
# Check CLI authentication status
gemini --version  # Should show version if installed
codex login status  # Should show "Logged in using ChatGPT"

# Test MCP server manually
python server.py
# Server should start without errors
```

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
