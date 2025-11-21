#!/usr/bin/env python3
"""
@CODE:HOOKS-SKILL-001
@SPEC: specs/003-skill-auto-activation/spec.md
@TEST: tests/hooks/test_skill_activator.py
@CHAIN: @SPEC:HOOKS-SKILL-001 → @TEST:HOOKS-SKILL-001 → @CODE:HOOKS-SKILL-001
@STATUS: implemented
@CREATED: 2025-10-30
@UPDATED: 2025-10-30

Skill Auto-Activation Engine for SPECTER

Adapted from diet103/claude-code-infrastructure-showcase for My-Spec workflow.
Automatically detects user intent and suggests relevant skills based on:
- Keyword matching in user prompts
- Regex pattern matching for intent detection
- File path pattern matching
- File content pattern matching

🎯 Design Principles:
- Project-agnostic (no hardcoded paths like 'blog-api/')
- Fast matching (regex compilation cached)
- Priority-based suggestions (critical → high → medium → low)
- Fail-open (JSON parse errors don't block execution)

🔧 Usage:
    activator = SkillActivator(cwd="/workspace/specter")
    matches = activator.suggest(
        prompt="How do I write pytest fixtures?",
        open_files=["tests/test_auth.py"]
    )
    print(activator.format_suggestions(matches))
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MatchedSkill:
    """Skill matching result with metadata.

    Attributes:
        name: Skill identifier (e.g., 'ms-lang-python')
        priority: Importance level ('critical', 'high', 'medium', 'low')
        enforcement: Action type ('suggest', 'warn', 'block')
        match_reasons: List of why this skill matched
                       (e.g., ["keyword: pytest", "file: tests/test_auth.py"])
        description: Brief skill description for display
    """

    name: str
    priority: str
    enforcement: str
    match_reasons: list[str]
    description: str


class SkillActivator:
    """Skill auto-activation engine for SPECTER.

    Loads skill-rules.json and matches user prompts/files against
    trigger patterns to suggest relevant skills automatically.

    Design:
        - Lazy-load rules (only once)
        - Cache compiled regex patterns (performance)
        - Project-agnostic path patterns (use **/*.py, not blog-api/src/**/*.py)
        - Fail-open on errors (return empty list, don't crash)

    Example:
        >>> activator = SkillActivator(cwd=".")
        >>> matches = activator.suggest("How to write pytest?", [])
        >>> len(matches) > 0
        True
        >>> matches[0].name
        'ms-lang-python'
    """

    def __init__(self, cwd: str):
        """Initialize skill activator.

        Args:
            cwd: Current working directory (project root)
        """
        self.cwd = Path(cwd)
        self.rules: dict[str, Any] | None = None
        self._compiled_patterns: dict[str, list[re.Pattern]] = {}

    def _load_rules(self) -> dict[str, Any]:
        """Load skill-rules.json from .claude/skills/.

        Returns:
            Parsed JSON dict with 'skills' key, or empty dict on error.

        Notes:
            - Caches result in self.rules (only loads once)
            - Fails open: returns empty dict if file missing or invalid JSON
            - Prints error to stderr but doesn't raise exception
        """
        if self.rules is not None:
            return self.rules

        rules_path = self.cwd / ".claude" / "skills" / "skill-rules.json"

        if not rules_path.exists():
            print(f"⚠️ Warning: {rules_path} not found", file=__import__("sys").stderr)
            self.rules = {"skills": {}}
            return self.rules

        try:
            with open(rules_path, encoding="utf-8") as f:
                self.rules = json.load(f)
            return self.rules
        except json.JSONDecodeError as e:
            print(
                f"⚠️ Warning: Invalid JSON in {rules_path}: {e}",
                file=__import__("sys").stderr,
            )
            self.rules = {"skills": {}}
            return self.rules

    def _compile_patterns(
        self, skill_name: str, patterns: list[str]
    ) -> list[re.Pattern]:
        """Compile and cache regex patterns for a skill.

        Args:
            skill_name: Skill identifier (for cache key)
            patterns: List of regex pattern strings

        Returns:
            List of compiled re.Pattern objects

        Notes:
            - Caches compiled patterns in self._compiled_patterns
            - Ignores invalid patterns (prints warning)
        """
        cache_key = f"{skill_name}_patterns"
        if cache_key in self._compiled_patterns:
            return self._compiled_patterns[cache_key]

        compiled = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                print(
                    f"⚠️ Warning: Invalid regex '{pattern}' in {skill_name}: {e}",
                    file=__import__("sys").stderr,
                )

        self._compiled_patterns[cache_key] = compiled
        return compiled

    def suggest(
        self, prompt: str, open_files: list[str] | None = None
    ) -> list[MatchedSkill]:
        """Suggest relevant skills based on user prompt and open files.

        Args:
            prompt: User's input prompt to analyze
            open_files: List of currently open file paths (optional)

        Returns:
            List of MatchedSkill objects, sorted by priority (critical first)

        Algorithm:
            1. Load skill rules from JSON
            2. For each skill, check:
               - Keyword matching in prompt (case-insensitive)
               - Intent pattern matching in prompt (regex)
               - File path pattern matching (glob-style)
               - File content pattern matching (requires file read)
            3. Collect match reasons for each skill
            4. Sort by priority (critical → high → medium → low)
            5. Return sorted list

        Examples:
            >>> activator = SkillActivator(".")
            >>> matches = activator.suggest("How to write pytest?")
            >>> matches[0].name
            'ms-lang-python'

            >>> matches = activator.suggest("Fix bug", ["tests/test_auth.py"])
            >>> any(m.name == 'ms-essentials-debug' for m in matches)
            True
        """
        rules = self._load_rules()
        matches: list[MatchedSkill] = []
        open_files = open_files or []

        for skill_name, skill_config in rules.get("skills", {}).items():
            match_reasons = self._check_match(
                prompt, open_files, skill_name, skill_config
            )

            if match_reasons:
                matches.append(
                    MatchedSkill(
                        name=skill_name,
                        priority=skill_config.get("priority", "low"),
                        enforcement=skill_config.get("enforcement", "suggest"),
                        match_reasons=match_reasons,
                        description=skill_config.get("description", ""),
                    )
                )

        # Sort by priority: critical → high → medium → low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        matches.sort(key=lambda m: priority_order.get(m.priority, 99))

        return matches

    def _check_match(
        self, prompt: str, open_files: list[str], skill_name: str, config: dict
    ) -> list[str]:
        """Check if prompt/files match skill triggers.

        Args:
            prompt: User prompt text
            open_files: List of open file paths
            skill_name: Skill identifier (for caching)
            config: Skill configuration from skill-rules.json

        Returns:
            List of match reasons (e.g., ["keyword: pytest", "pattern: write.*python"])
            Empty list if no matches.

        Matching Logic:
            1. Keyword matching: Case-insensitive substring search
            2. Intent patterns: Regex matching with compiled patterns
            3. File path patterns: Glob-style matching (**/*.py)
            4. File content patterns: Regex search in file contents (NOT implemented yet)
        """
        reasons = []

        # 1. Keyword matching in prompt
        keywords = config.get("promptTriggers", {}).get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt.lower():
                reasons.append(f"keyword: {kw}")

        # 2. Intent pattern matching (regex)
        intent_patterns = config.get("promptTriggers", {}).get("intentPatterns", [])
        compiled_patterns = self._compile_patterns(skill_name, intent_patterns)

        for i, pattern_obj in enumerate(compiled_patterns):
            if pattern_obj.search(prompt):
                # Use original pattern string for display
                original_pattern = intent_patterns[i]
                reasons.append(f"pattern: {original_pattern}")

        # 3. File path pattern matching
        path_patterns = config.get("fileTriggers", {}).get("pathPatterns", [])
        for file_path in open_files:
            for pattern in path_patterns:
                if self._match_glob(file_path, pattern):
                    reasons.append(f"file: {file_path}")
                    break  # Only count each file once

        # 4. File content pattern matching (TODO: Implement if needed)
        # For now, skipping content matching to avoid expensive file I/O
        # Content matching should be opt-in or done only for small files

        return reasons

    def _match_glob(self, path: str, pattern: str) -> bool:
        """Match file path against glob-style pattern.

        Args:
            path: File path to test (e.g., "tests/test_auth.py")
            pattern: Glob pattern (e.g., "**/*.py", "tests/**/*.py")

        Returns:
            True if path matches pattern, False otherwise

        Pattern Syntax:
            - ** matches zero or more directories
            - * matches any characters except /
            - Literal dots must match exactly

        Examples:
            >>> activator = SkillActivator(".")
            >>> activator._match_glob("tests/test_auth.py", "**/*.py")
            True
            >>> activator._match_glob("src/main.py", "tests/**/*.py")
            False
            >>> activator._match_glob("config.json", "*.json")
            True
        """
        # Use pathlib's match() which handles glob patterns correctly
        try:
            return Path(path).match(pattern)
        except (ValueError, re.error):
            # Invalid pattern or path
            return False

    def format_suggestions(self, matches: list[MatchedSkill]) -> str:
        """Format matched skills into user-friendly message.

        Args:
            matches: List of MatchedSkill objects (should be pre-sorted by priority)

        Returns:
            Formatted string with skill suggestions, grouped by priority.
            Empty string if no matches.

        Format:
            💡 **Suggested Skills for this Task**

            ⚠️ **CRITICAL** (Required):
              - `skill-name` - Brief description

            📚 **RECOMMENDED**:
              - `skill-name` - Brief description

            💡 Tip: Use Skill tool to load skill documentation

        Notes:
            - Only shows critical and high priority skills (prevent spam)
            - Limits high priority to top 3 (prevent clutter)
            - Includes brief description for each skill
        """
        if not matches:
            return ""

        lines = ["", "💡 **Suggested Skills for this Task**", ""]

        # Group by priority
        by_priority: dict[str, list[MatchedSkill]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for match in matches:
            by_priority[match.priority].append(match)

        # Show CRITICAL skills (if any)
        if by_priority["critical"]:
            lines.append("⚠️ **CRITICAL** (Required):")
            for m in by_priority["critical"]:
                lines.append(f"  - `{m.name}` - {m.description}")
            lines.append("")

        # Show HIGH priority skills (limit to 3)
        if by_priority["high"]:
            lines.append("📚 **RECOMMENDED**:")
            for m in by_priority["high"][:3]:  # Limit to top 3
                lines.append(f"  - `{m.name}` - {m.description}")
            lines.append("")

        # Show MEDIUM priority skills (limit to 2, only if no high priority)
        if not by_priority["high"] and by_priority["medium"]:
            lines.append("💡 **SUGGESTED**:")
            for m in by_priority["medium"][:2]:  # Limit to top 2
                lines.append(f"  - `{m.name}` - {m.description}")
            lines.append("")

        # Add usage tip
        lines.append("💡 **Tip**: Use `Skill` tool to load skill documentation")
        lines.append("")

        return "\n".join(lines)


# Export public interface
__all__ = ["SkillActivator", "MatchedSkill"]
