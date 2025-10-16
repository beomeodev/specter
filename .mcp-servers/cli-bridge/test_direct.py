#!/usr/bin/env python3
"""Test script to verify CLI Bridge functionality directly"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions directly
from server import execute_codex_cli, execute_gemini_cli

async def test_codex():
    """Test Codex CLI"""
    print("Testing Codex CLI...")
    result = await execute_codex_cli("What is 2+2?")
    print(f"Codex result: {result[:200]}...")
    return "ERROR" not in result

async def test_gemini():
    """Test Gemini CLI"""
    print("\nTesting Gemini CLI...")
    result = await execute_gemini_cli("What is 2+2?")
    print(f"Gemini result: {result[:200]}...")
    return "ERROR" not in result

async def main():
    """Run tests"""
    codex_ok = await test_codex()
    # gemini_ok = await test_gemini()  # Skip if not installed

    print("\n" + "="*50)
    print("Test Results:")
    print(f"  Codex CLI: {'✅ Working' if codex_ok else '❌ Failed'}")
    # print(f"  Gemini CLI: {'✅ Working' if gemini_ok else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(main())