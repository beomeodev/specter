#!/usr/bin/env python3
"""
CLI Bridge MCP Server - Minimal Gemini/Codex CLI Integration
Executes Gemini CLI and Codex CLI preserving their authentication sessions

Python 3.14 Free-Threading Support:
- Background task execution using asyncio.create_task()
- Task lifecycle management with set() + add_done_callback() pattern
- Safe concurrent execution without GIL blocking
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import ListToolsResult, TextContent, Tool
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cli-bridge")

# Create MCP server
app = Server("cli-bridge")

# ============================================================================
# Background Task Management (Python 3.14 Official Pattern)
# Reference: https://docs.python.org/3.14/library/asyncio-task.html
# ============================================================================

# Strong references to prevent garbage collection
# Pattern: background_tasks.add(task) + task.add_done_callback(background_tasks.discard)
background_tasks: set[asyncio.Task] = set()

# Task metadata storage
# task_id -> {status, started_at, completed_at, cli, result, error}
task_metadata: dict[str, dict[str, Any]] = {}


@app.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """Expose gemini-cli, codex-cli, and task management tools"""
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
                        "background": {
                            "type": "boolean",
                            "description": "Run in background (returns task_id immediately, default: false)",
                            "default": False,
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
                        },
                        "background": {
                            "type": "boolean",
                            "description": "Run in background (returns task_id immediately, default: false)",
                            "default": False,
                        },
                    },
                    "required": ["prompt"],
                },
            ),
            Tool(
                name="get_task_result",
                description="Get result of a background task by task_id",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID returned by background execution",
                        },
                        "wait": {
                            "type": "boolean",
                            "description": "Wait for task completion (blocks until done, default: false)",
                            "default": False,
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Timeout in seconds when wait=true (default: 600)",
                            "default": 600,
                        },
                    },
                    "required": ["task_id"],
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
    """
    Handle tool calls with background task support.

    Background Execution Pattern (Python 3.14):
    1. Create task with asyncio.create_task()
    2. Add to set for strong reference: background_tasks.add(task)
    3. Auto-cleanup on completion: task.add_done_callback(background_tasks.discard)
    4. Store metadata for result retrieval

    Reference: https://docs.python.org/3.14/library/asyncio-task.html#managing-background-tasks
    """
    logger.info(f"Tool called: {name}")

    if name == "gemini_cli":
        prompt = arguments.get("prompt", "")
        files = arguments.get("files", [])
        background = arguments.get("background", False)

        if background:
            # Background execution with Python 3.14 pattern
            task_id = str(uuid.uuid4())

            async def execute_and_store():
                """Wrapper to execute CLI and store result"""
                try:
                    result = await execute_gemini_cli(prompt, files)
                    task_metadata[task_id]["status"] = "COMPLETED"
                    task_metadata[task_id]["result"] = result
                    task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
                    logger.info(f"Task {task_id} completed (Gemini)")
                except Exception as e:
                    task_metadata[task_id]["status"] = "ERROR"
                    task_metadata[task_id]["error"] = str(e)
                    task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
                    logger.error(f"Task {task_id} failed: {e}")

            # Create task
            task = asyncio.create_task(execute_and_store())

            # Python 3.14 Official Pattern: Strong reference + auto-cleanup
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

            # Store metadata
            task_metadata[task_id] = {
                "status": "RUNNING",
                "started_at": datetime.now().isoformat(),
                "cli": "gemini",
                "prompt_length": len(prompt),
                "files_count": len(files) if files else 0,
            }

            logger.info(f"Background task started: {task_id} (Gemini)")
            return [TextContent(type="text", text=f"TASK_STARTED:{task_id}")]
        else:
            # Synchronous execution (blocking)
            result = await execute_gemini_cli(prompt, files)
            return [TextContent(type="text", text=result)]

    elif name == "codex_cli":
        prompt = arguments.get("prompt", "")
        background = arguments.get("background", False)

        if background:
            # Background execution with Python 3.14 pattern
            task_id = str(uuid.uuid4())

            async def execute_and_store():
                """Wrapper to execute CLI and store result"""
                try:
                    result = await execute_codex_cli(prompt)
                    task_metadata[task_id]["status"] = "COMPLETED"
                    task_metadata[task_id]["result"] = result
                    task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
                    logger.info(f"Task {task_id} completed (Codex)")
                except Exception as e:
                    task_metadata[task_id]["status"] = "ERROR"
                    task_metadata[task_id]["error"] = str(e)
                    task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
                    logger.error(f"Task {task_id} failed: {e}")

            # Create task
            task = asyncio.create_task(execute_and_store())

            # Python 3.14 Official Pattern: Strong reference + auto-cleanup
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

            # Store metadata
            task_metadata[task_id] = {
                "status": "RUNNING",
                "started_at": datetime.now().isoformat(),
                "cli": "codex",
                "prompt_length": len(prompt),
            }

            logger.info(f"Background task started: {task_id} (Codex)")
            return [TextContent(type="text", text=f"TASK_STARTED:{task_id}")]
        else:
            # Synchronous execution (blocking)
            result = await execute_codex_cli(prompt)
            return [TextContent(type="text", text=result)]

    elif name == "get_task_result":
        result_task_id: str = arguments.get("task_id", "")
        wait = arguments.get("wait", False)
        timeout = arguments.get("timeout", 600)

        if result_task_id not in task_metadata:
            error_msg = (
                f"ERROR:TASK_NOT_FOUND - Task ID '{result_task_id}' does not exist"
            )
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

        meta = task_metadata[result_task_id]

        if wait:
            # Polling with timeout
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < timeout:
                if meta["status"] in ["COMPLETED", "ERROR"]:
                    break
                await asyncio.sleep(0.1)  # Poll every 100ms

            # Check final status
            if meta["status"] == "COMPLETED":
                logger.info(f"Task {result_task_id} result retrieved (waited)")
                return [TextContent(type="text", text=meta["result"])]
            elif meta["status"] == "ERROR":
                error_msg = f"ERROR:{meta['error']}"
                logger.error(f"Task {result_task_id} failed: {meta['error']}")
                return [TextContent(type="text", text=error_msg)]
            else:
                timeout_msg = f"TIMEOUT:Task still running after {timeout}s"
                logger.warning(f"Task {result_task_id} timed out")
                return [TextContent(type="text", text=timeout_msg)]
        else:
            # Non-blocking status check
            if meta["status"] == "COMPLETED":
                return [TextContent(type="text", text=meta["result"])]
            elif meta["status"] == "ERROR":
                return [TextContent(type="text", text=f"ERROR:{meta['error']}")]
            else:
                # Return current status with metadata
                status_info = json.dumps(
                    {
                        "status": meta["status"],
                        "started_at": meta["started_at"],
                        "cli": meta["cli"],
                        "elapsed_seconds": (
                            datetime.now() - datetime.fromisoformat(meta["started_at"])
                        ).total_seconds(),
                    },
                    indent=2,
                )
                return [TextContent(type="text", text=f"STATUS:RUNNING\n{status_info}")]

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
