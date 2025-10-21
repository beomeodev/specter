#!/usr/bin/env python3
"""
MCP Client for testing cli-bridge server
Direct test without Claude Code Extension
"""

import asyncio
import sys
from pathlib import Path

# Add mcp to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp")
    sys.exit(1)


async def test_background_execution():
    """Test background execution feature"""
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent / ".mcp-servers/cli-bridge/server.py")],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            print("=== Available Tools ===")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\n=== Test 1: Synchronous Execution ===")
            # Test synchronous execution
            sync_result = await session.call_tool(
                "gemini_cli",
                arguments={"prompt": "What is 2+2?", "background": False},
            )
            print(
                f"Sync result (first 200 chars):\n{str(sync_result.content[0].text)[:200]}..."
            )

            print("\n=== Test 2: Background Execution ===")
            # Test background execution
            bg_result = await session.call_tool(
                "gemini_cli",
                arguments={"prompt": "Count from 1 to 5", "background": True},
            )
            task_response = bg_result.content[0].text
            print(f"Background task started: {task_response}")

            if task_response.startswith("TASK_STARTED:"):
                task_id = task_response.split("TASK_STARTED:")[1]
                print(f"Task ID: {task_id}")

                # Wait a bit
                print("Waiting 2 seconds...")
                await asyncio.sleep(2)

                # Get result (non-blocking check)
                print("\n=== Test 3: Get Task Result (non-blocking) ===")
                status_result = await session.call_tool(
                    "get_task_result",
                    arguments={"task_id": task_id, "wait": False},
                )
                print(f"Status: {status_result.content[0].text[:100]}...")

                # Get result (blocking wait)
                print("\n=== Test 4: Get Task Result (blocking wait) ===")
                final_result = await session.call_tool(
                    "get_task_result",
                    arguments={"task_id": task_id, "wait": True, "timeout": 60},
                )
                print(
                    f"Final result (first 200 chars):\n{str(final_result.content[0].text)[:200]}..."
                )

            print("\n✅ All tests passed!")


if __name__ == "__main__":
    try:
        asyncio.run(test_background_execution())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
