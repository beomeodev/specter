#!/usr/bin/env python3
"""
CLI Bridge MCP Server - Streaming version for large responses
"""

import asyncio
import json
import logging
import sys
from typing import Any, AsyncGenerator

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool, ListToolsResult
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cli-bridge-streaming")

app = Server("cli-bridge-streaming")

# Token limit per chunk
CHUNK_SIZE = 20000  # Stay under 25000 limit


@app.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """Expose streaming versions of CLI tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="codex_cli_summary",
                description="Execute Codex CLI with automatic summarization for large responses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Prompt to send to Codex CLI",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Maximum tokens in response (default: 20000)",
                            "default": 20000,
                        },
                    },
                    "required": ["prompt"],
                },
            ),
            Tool(
                name="codex_cli_stream",
                description="Execute Codex CLI and return only first part of response",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Prompt with explicit length constraint",
                        }
                    },
                    "required": ["prompt"],
                },
            ),
        ]
    )


async def execute_codex_with_limit(prompt: str, max_tokens: int = 20000) -> str:
    """Execute Codex with response size control"""

    # Add length constraint to prompt
    enhanced_prompt = f"""{prompt}

IMPORTANT: Keep your response under {max_tokens // 4} words (approximately {max_tokens} tokens).
Focus on the most critical issues only."""

    cmd = ["codex", "exec", "--json"]
    logger.info(f"Executing Codex with token limit: {max_tokens}")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(enhanced_prompt.encode("utf-8")),
            timeout=300,  # 5 minute timeout
        )

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            return f"ERROR: Codex CLI failed with: {error_msg[:1000]}"

        output = stdout.decode("utf-8", errors="replace")

        # Parse JSON and extract response
        try:
            result = json.loads(output)
            response = result.get("response", output)
        except json.JSONDecodeError:
            response = output

        # Truncate if still too large
        if len(response) > max_tokens:
            logger.warning(
                f"Response truncated from {len(response)} to {max_tokens} chars"
            )
            response = (
                response[:max_tokens] + "\n\n... [Response truncated due to size limit]"
            )

        return response

    except asyncio.TimeoutError:
        return "ERROR: Codex execution timed out after 5 minutes"
    except FileNotFoundError:
        return "ERROR: 'codex' command not found"
    except Exception as e:
        return f"ERROR: {str(e)}"


async def execute_codex_first_chunk(prompt: str) -> str:
    """Execute Codex and return only the first chunk"""

    # Modify prompt to request concise response
    concise_prompt = f"""{prompt}

CRITICAL: Provide a VERY CONCISE response (under 5000 tokens).
List only the TOP 3-5 most important points."""

    return await execute_codex_with_limit(concise_prompt, max_tokens=20000)


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls with size limits"""
    logger.info(f"Tool called: {name}")

    if name == "codex_cli_summary":
        prompt = arguments.get("prompt", "")
        max_tokens = arguments.get("max_tokens", 20000)
        result = await execute_codex_with_limit(prompt, max_tokens)
        return [TextContent(type="text", text=result)]

    elif name == "codex_cli_stream":
        prompt = arguments.get("prompt", "")
        result = await execute_codex_first_chunk(prompt)
        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    logger.info("Starting CLI Bridge Streaming MCP Server...")
    logger.info("Features: Automatic response size control")

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
