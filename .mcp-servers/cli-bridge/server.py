#!/usr/bin/env python3
"""
CLI Bridge MCP Server - Minimal Gemini/Codex CLI Integration
Executes Gemini CLI and Codex CLI preserving their authentication sessions
"""

import asyncio
import json
import logging
import sys
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool, ListToolsResult, CallToolResult
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cli-bridge")

# Create MCP server
app = Server("cli-bridge")


@app.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """Expose gemini-cli and codex-cli tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="gemini_cli",
                description="Execute Gemini CLI with preserved authentication (uses 'gemini' command)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Prompt to send to Gemini CLI",
                        },
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional file paths to include",
                        },
                    },
                    "required": ["prompt"],
                },
            ),
            Tool(
                name="codex_cli",
                description="Execute Codex CLI with preserved authentication (uses 'codex exec' command)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Prompt to send to Codex CLI",
                        }
                    },
                    "required": ["prompt"],
                },
            ),
        ]
    )


async def execute_gemini_cli(prompt: str, files: list[str] | None = None) -> str:
    """Execute Gemini CLI command"""
    cmd = ["gemini", "--yolo", "--telemetry", "false"]

    # Add file arguments if provided
    if files:
        for file in files:
            cmd.extend(["--file", file])

    logger.info(f"Executing: {' '.join(cmd[:3])}... (with prompt)")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(prompt.encode("utf-8")),
            timeout=600,  # 10 minute timeout
        )

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            logger.error(f"Gemini CLI failed: {error_msg}")
            return (
                f"ERROR: Gemini CLI returned exit code {proc.returncode}\n\n{error_msg}"
            )

        return stdout.decode("utf-8", errors="replace")

    except asyncio.TimeoutError:
        logger.error("Gemini CLI timed out")
        return "ERROR: Gemini CLI execution timed out after 10 minutes"
    except FileNotFoundError:
        logger.error("Gemini CLI not found in PATH")
        return "ERROR: 'gemini' command not found. Install: npm install -g @google/gemini-cli"
    except Exception as e:
        logger.error(f"Gemini CLI execution failed: {e}")
        return f"ERROR: {str(e)}"


async def execute_codex_cli(prompt: str) -> str:
    """Execute Codex CLI command"""
    cmd = ["codex", "exec", "--full-auto"]

    logger.info("Executing: codex exec --full-auto (with prompt)")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(prompt.encode("utf-8")),
            timeout=600,  # 10 minute timeout
        )

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            logger.error(f"Codex CLI failed: {error_msg}")
            return (
                f"ERROR: Codex CLI returned exit code {proc.returncode}\n\n{error_msg}"
            )

        # Return raw output (not JSON in full-auto mode)
        output = stdout.decode("utf-8", errors="replace")
        return output

    except asyncio.TimeoutError:
        logger.error("Codex CLI timed out")
        return "ERROR: Codex CLI execution timed out after 10 minutes"
    except FileNotFoundError:
        logger.error("Codex CLI not found in PATH")
        return "ERROR: 'codex' command not found. Check installation and login status"
    except Exception as e:
        logger.error(f"Codex CLI execution failed: {e}")
        return f"ERROR: {str(e)}"


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    logger.info(f"Tool called: {name}")

    if name == "gemini_cli":
        prompt = arguments.get("prompt", "")
        files = arguments.get("files", [])
        result = await execute_gemini_cli(prompt, files)
        return [TextContent(type="text", text=result)]

    elif name == "codex_cli":
        prompt = arguments.get("prompt", "")
        result = await execute_codex_cli(prompt)
        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    logger.info("Starting CLI Bridge MCP Server...")
    logger.info("Exposing tools: gemini_cli, codex_cli")

    async with stdio_server() as (read_stream, write_stream):
        init_options = app.create_initialization_options()
        await app.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
