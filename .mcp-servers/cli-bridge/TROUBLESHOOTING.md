# CLI Bridge MCP Server - Troubleshooting Guide

## ✅ Fixed Issues

### 1. **mcp package not installed**
**Problem**: `ImportError: No module named 'mcp'`
**Solution**:
```bash
pip install mcp
```
**Status**: ✅ FIXED - Package installed successfully

### 2. **Server Status**
**Current Status**: ✅ Working
- Server starts correctly
- Codex CLI integration working
- Authentication preserved

---

## 🔧 How to Use in VSCode

### Method 1: Restart VSCode
1. Close VSCode completely
2. Reopen VSCode
3. The MCP servers should auto-start

### Method 2: Reload Window
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Developer: Reload Window"
3. Press Enter

### Method 3: Manual Test
Test if the server is recognized:
```
/mcp
```

Expected output should include:
```
Available MCP Servers:
- cli-bridge (2 tools)
  - gemini_cli
  - codex_cli
```

---

## 📝 Usage Examples

### Using Codex CLI through MCP

Since I don't have direct access to the `mcp__cli-bridge__codex_cli` function (it needs to be exposed through VSCode Extension), you would use it like:

```
Use mcp__cli-bridge__codex_cli with prompt "Analyze this code for security issues"
```

Or for code review:
```
Use mcp__cli-bridge__codex_cli with prompt "Review the ms.review.md file for improvements"
```

---

## 🚨 Common Issues and Solutions

### Issue 1: "mcp__cli-bridge__codex_cli not found"
**Cause**: VSCode Extension hasn't loaded the MCP server
**Solutions**:
1. Restart VSCode completely
2. Check if `.mcp.json` exists in workspace root
3. Verify Python path: `which python3`

### Issue 2: "Codex CLI timeout"
**Cause**: Codex API is slow or network issues
**Solutions**:
1. Check Codex login: `codex login status`
2. Re-login if needed: `codex login`
3. Test directly: `echo "test" | codex exec`

### Issue 3: "Permission denied"
**Cause**: Server script not executable
**Solution**:
```bash
chmod +x /workspace/my-spec/.mcp-servers/cli-bridge/server.py
```

---

## 🧪 Testing the Server

### Direct Python Test
```bash
cd /workspace/my-spec/.mcp-servers/cli-bridge
python3 test_direct.py
```

### Manual Server Start (for debugging)
```bash
python3 /workspace/my-spec/.mcp-servers/cli-bridge/server.py
# Should see: "Starting CLI Bridge MCP Server..."
# Press Ctrl+C to stop
```

### Test Codex CLI Directly
```bash
echo "What is 2+2?" | codex exec --json
```

---

## 📊 Current Configuration

**File**: `/workspace/my-spec/.mcp.json`
```json
{
  "mcpServers": {
    "cli-bridge": {
      "command": "python3",
      "args": [
        "/workspace/my-spec/.mcp-servers/cli-bridge/server.py"
      ],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {}
    }
  }
}
```

---

## ✅ Verification Checklist

- [x] Python 3 installed: `Python 3.12.11`
- [x] mcp package installed: `pip show mcp`
- [x] Codex CLI installed: `/usr/bin/codex`
- [x] Codex logged in: `Logged in using ChatGPT`
- [x] Server starts without errors
- [x] Direct test passes
- [x] Configuration files in place

---

## 🎯 Next Steps

1. **Restart VSCode** to load the MCP servers
2. **Run `/mcp`** command to verify servers are loaded
3. **Try using** the codex_cli tool with a simple prompt

If VSCode still doesn't recognize the server after restart, the issue is likely with the VSCode Extension's MCP loader, not with our server implementation.