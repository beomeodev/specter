#!/usr/bin/env node
/**
 * TAG Enforcer Hook (Claude Code PreToolUse)
 *
 * Enforces TAG integrity and @IMMUTABLE protection.
 * Blocks file writes that violate TAG rules.
 *
 * Triggered on: Edit, Write, MultiEdit tools
 */

import * as fs from 'fs/promises';
import * as path from 'path';

// Import helpers (must be compiled to JS first)
import { checkImmutability } from '../../src/lib/tag/validator';
import { validateTAGChainFormat } from '../../src/lib/tag/validator';

/**
 * Hook input from Claude Code
 */
interface HookInput {
  tool_name?: string;
  tool_input?: Record<string, any>;
}

/**
 * Hook result to return
 */
interface HookResult {
  success: boolean;
  blocked?: boolean;
  message?: string;
  exitCode?: number;
}

/**
 * Extract file path from tool input
 */
function extractFilePath(toolInput: Record<string, any>): string | null {
  return (
    toolInput.file_path ||
    toolInput.filePath ||
    toolInput.notebook_path ||
    null
  );
}

/**
 * Extract file content from tool input
 */
function extractFileContent(toolInput: Record<string, any>): string {
  if (toolInput.content) return toolInput.content;
  if (toolInput.new_string) return toolInput.new_string;
  if (toolInput.new_source) return toolInput.new_source;
  if (toolInput.edits && Array.isArray(toolInput.edits)) {
    return toolInput.edits.map((edit: any) => edit.new_string).join('\n');
  }
  return '';
}

/**
 * Check if file should be enforced
 */
function shouldEnforceTags(filePath: string): boolean {
  const enforceExtensions = [
    '.ts',
    '.tsx',
    '.js',
    '.jsx',
    '.py',
    '.md',
    '.go',
    '.rs',
    '.java',
    '.cpp',
    '.hpp',
  ];

  const ext = path.extname(filePath);

  // Skip test files (different TAG rules)
  if (
    filePath.includes('test') ||
    filePath.includes('spec') ||
    filePath.includes('__test__')
  ) {
    return false;
  }

  // Skip node_modules, .git, dist, build
  if (
    filePath.includes('node_modules') ||
    filePath.includes('.git') ||
    filePath.includes('dist') ||
    filePath.includes('build')
  ) {
    return false;
  }

  return enforceExtensions.includes(ext);
}

/**
 * Read original file content
 */
async function getOriginalFileContent(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, 'utf-8');
  } catch {
    // New file
    return '';
  }
}

/**
 * Generate immutability help message
 */
function generateImmutabilityHelp(modifiedTag: string): string {
  return `
🚫 @IMMUTABLE TAG Modification Detected

TAG ${modifiedTag} is marked as @IMMUTABLE and cannot be modified.

📋 TAG Immutability Rules:
• @IMMUTABLE TAG blocks cannot be edited once created
• TAG metadata is permanent and immutable
• To make changes, create a NEW TAG with a different ID

✅ Recommended Actions:
1. Create a new TAG ID for the modified functionality
   Example: @SPEC:AUTH-002 (if AUTH-001 was modified)

2. Add @DOC marker to deprecated TAG
   Example: /** @DOC:AUTH-001 (replaced by AUTH-002) */

3. Reference the old TAG in the new one
   Example: REPLACES: AUTH-001

🔍 Modified TAG: ${modifiedTag}
`.trim();
}

/**
 * Main hook execution
 */
async function main(): Promise<void> {
  try {
    // Parse stdin input from Claude Code
    const input: HookInput = JSON.parse(
      await fs.readFile(process.stdin.fd, 'utf-8')
    );

    // 1. Check if this is a write operation
    const toolName = input.tool_name || '';
    if (!['Write', 'Edit', 'MultiEdit', 'NotebookEdit'].includes(toolName)) {
      console.log(JSON.stringify({ success: true }));
      process.exit(0);
    }

    const toolInput = input.tool_input || {};
    const filePath = extractFilePath(toolInput);

    // 2. Check if file should be enforced
    if (!filePath || !shouldEnforceTags(filePath)) {
      console.log(JSON.stringify({ success: true }));
      process.exit(0);
    }

    // 3. Get old and new content
    const oldContent = await getOriginalFileContent(filePath);
    const newContent = extractFileContent(toolInput);

    // 4. Check @IMMUTABLE TAG block modification
    const immutabilityCheck = await checkImmutability(
      filePath,
      oldContent,
      newContent
    );

    if (immutabilityCheck.violated) {
      const message = generateImmutabilityHelp(
        immutabilityCheck.modifiedTag || 'UNKNOWN'
      );

      console.error('BLOCKED:', immutabilityCheck.violationDetails);
      console.error('');
      console.error(message);

      const result: HookResult = {
        success: false,
        blocked: true,
        message: `@IMMUTABLE TAG modification blocked: ${immutabilityCheck.modifiedTag}`,
        exitCode: 2,
      };

      console.log(JSON.stringify(result));
      process.exit(2);
    }

    // 5. Validate TAG chain format (warning only, not blocking)
    const chainPattern = /CHAIN:\s*(.+)/;
    const chainMatch = newContent.match(chainPattern);

    if (chainMatch) {
      const chainStr = chainMatch[1].trim();
      if (!validateTAGChainFormat(chainStr)) {
        console.warn('⚠️  TAG chain format warning:', chainStr);
        console.warn('    Expected: @TYPE:ID -> @TYPE:ID -> @TYPE:ID');
      }
    }

    // 6. All checks passed
    const result: HookResult = {
      success: true,
      message: 'TAG integrity verified',
    };

    console.log(JSON.stringify(result));
    process.exit(0);
  } catch (error) {
    // On error, don't block (fail-open for safety)
    console.error('TAG Enforcer error:', error instanceof Error ? error.message : 'Unknown error');

    const result: HookResult = {
      success: true,
      message: 'TAG Enforcer error (non-blocking)',
    };

    console.log(JSON.stringify(result));
    process.exit(0);
  }
}

// Execute if run directly
if (require.main === module) {
  main();
}
