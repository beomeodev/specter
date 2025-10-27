#!/usr/bin/env python3
"""
CLI Bridge MCP Server - Minimal Gemini/Codex CLI Integration
Executes Gemini CLI and Codex CLI preserving their authentication sessions

Python 3.14 Free-Threading Support:
- Background task execution using asyncio.create_task()
- Task lifecycle management with set() + add_done_callback() pattern
- Safe concurrent execution without GIL blocking

Security Features (Personal Use):
- Input validation for file paths and prompts
- LRU cache for task metadata (prevents memory leaks)
- Forced process termination on timeout
"""

import asyncio
import json
import logging
import re
import sys
import uuid
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
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
# Security Configuration (Personal Use)
# ============================================================================

# Maximum prompt length (5MB - allows large code context)
MAX_PROMPT_LENGTH = 5_000_000

# Maximum task metadata history (LRU cache to prevent memory leaks)
MAX_TASK_HISTORY = 50

# Allowed base directories for file access (workspace + home)
ALLOWED_BASE_DIRS = [
    Path("/workspace"),
    Path.home(),
]

# Process execution timeout (30 minutes for long tasks)
PROCESS_TIMEOUT = 1800


# ============================================================================
# Input Validation Functions
# ============================================================================


def validate_file_path(file_path: str) -> str:
    """
    Validate file path for security.

    Security checks:
    1. Resolve to absolute path (handle symlinks, .., .)
    2. Verify path is within allowed directories
    3. Block shell metacharacters

    Args:
        file_path: Path to validate

    Returns:
        Validated absolute path string

    Raises:
        ValueError: If path is invalid or outside allowed directories
    """
    try:
        # Resolve to absolute path (handles symlinks, .., .)
        resolved_path = Path(file_path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")

    # Check if path is within allowed directories
    is_allowed = any(
        resolved_path.is_relative_to(base_dir) for base_dir in ALLOWED_BASE_DIRS
    )

    if not is_allowed:
        allowed_str = ", ".join(str(d) for d in ALLOWED_BASE_DIRS)
        raise ValueError(
            f"File path outside allowed directories: {resolved_path}\n"
            f"Allowed: {allowed_str}"
        )

    # Block shell metacharacters to prevent injection
    dangerous_chars = r'[;&|`$()<>]'
    if re.search(dangerous_chars, str(resolved_path)):
        raise ValueError(
            f"File path contains dangerous characters: {resolved_path}"
        )

    return str(resolved_path)


def validate_prompt(prompt: str) -> str:
    """
    Validate prompt for security.

    Security checks:
    1. Length limit to prevent resource exhaustion

    Args:
        prompt: Prompt to validate

    Returns:
        Validated prompt

    Raises:
        ValueError: If prompt is invalid
    """
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError(
            f"Prompt too long: {len(prompt)} bytes > {MAX_PROMPT_LENGTH} bytes"
        )

    return prompt


# ============================================================================
# Background Task Management (Python 3.14 Official Pattern)
# Reference: https://docs.python.org/3.14/library/asyncio-task.html
# ============================================================================

# Strong references to prevent garbage collection
# Pattern: background_tasks.add(task) + task.add_done_callback(background_tasks.discard)
background_tasks: set[asyncio.Task] = set()

# Task metadata storage with LRU cache (prevents memory leaks)
# task_id -> {status, started_at, completed_at, cli, result, error}
task_metadata: OrderedDict[str, dict[str, Any]] = OrderedDict()


def store_task_metadata(task_id: str, metadata: dict[str, Any]) -> None:
    """
    Store task metadata with automatic LRU eviction.

    Args:
        task_id: Unique task identifier
        metadata: Task metadata dictionary
    """
    task_metadata[task_id] = metadata

    # Evict oldest entries if cache exceeds limit
    while len(task_metadata) > MAX_TASK_HISTORY:
        oldest_id = next(iter(task_metadata))
        logger.info(f"Evicting old task metadata: {oldest_id}")
        task_metadata.pop(oldest_id)


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
    """
    Execute Gemini CLI command with security validation.

    Args:
        prompt: User prompt (validated for length)
        files: Optional file paths (validated for safety)

    Returns:
        CLI output or error message

    Security:
        - Validates prompt length
        - Validates file paths
        - Enforces process timeout with forced termination
    """
    # Validate prompt
    prompt = validate_prompt(prompt)

    cmd = ["gemini", "--yolo"]

    # Add file arguments if provided (with validation)
    if files:
        for file in files:
            validated_file = validate_file_path(file)
            cmd.extend(["--file", validated_file])

    logger.info(f"Executing: {' '.join(cmd[:3])}... (with prompt)")

    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(prompt.encode("utf-8")),
            timeout=PROCESS_TIMEOUT,
        )

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            logger.error(f"Gemini CLI failed: {error_msg}")
            return (
                f"ERROR: Gemini CLI returned exit code {proc.returncode}\n\n{error_msg}"
            )

        return stdout.decode("utf-8", errors="replace")

    except asyncio.TimeoutError:
        # Force kill process on timeout
        if proc:
            logger.warning(f"Gemini CLI timed out, killing process (PID: {proc.pid})")
            proc.kill()
            await proc.wait()
        logger.error(f"Gemini CLI timed out after {PROCESS_TIMEOUT}s")
        return f"ERROR: Gemini CLI execution timed out after {PROCESS_TIMEOUT}s"
    except FileNotFoundError:
        logger.error("Gemini CLI not found in PATH")
        return "ERROR: 'gemini' command not found. Install: npm install -g @google/gemini-cli"
    except ValueError as e:
        # Validation errors (file path, prompt length)
        logger.error(f"Validation error: {e}")
        return f"ERROR: {str(e)}"
    except Exception as e:
        logger.error(f"Gemini CLI execution failed: {e}")
        return f"ERROR: {str(e)}"


async def execute_codex_cli(prompt: str) -> str:
    """
    Execute Codex CLI command with security validation.

    Args:
        prompt: User prompt (validated for length)

    Returns:
        CLI output or error message

    Security:
        - Validates prompt length
        - Enforces process timeout with forced termination
    """
    # Validate prompt
    prompt = validate_prompt(prompt)

    cmd = ["codex", "exec", "--full-auto"]

    logger.info("Executing: codex exec --full-auto (with prompt)")

    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(prompt.encode("utf-8")),
            timeout=PROCESS_TIMEOUT,
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
        # Force kill process on timeout
        if proc:
            logger.warning(f"Codex CLI timed out, killing process (PID: {proc.pid})")
            proc.kill()
            await proc.wait()
        logger.error(f"Codex CLI timed out after {PROCESS_TIMEOUT}s")
        return f"ERROR: Codex CLI execution timed out after {PROCESS_TIMEOUT}s"
    except FileNotFoundError:
        logger.error("Codex CLI not found in PATH")
        return "ERROR: 'codex' command not found. Check installation and login status"
    except ValueError as e:
        # Validation errors (prompt length)
        logger.error(f"Validation error: {e}")
        return f"ERROR: {str(e)}"
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

            # Store metadata with LRU eviction
            store_task_metadata(
                task_id,
                {
                    "status": "RUNNING",
                    "started_at": datetime.now().isoformat(),
                    "cli": "gemini",
                    "prompt_length": len(prompt),
                    "files_count": len(files) if files else 0,
                },
            )

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

            # Store metadata with LRU eviction
            store_task_metadata(
                task_id,
                {
                    "status": "RUNNING",
                    "started_at": datetime.now().isoformat(),
                    "cli": "codex",
                    "prompt_length": len(prompt),
                },
            )

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
