/**
 * TAG Validator Module
 *
 * Provides TAG integrity validation and immutability checks.
 * Supports both My-Spec basic validation and MoAI-style immutability enforcement.
 */

import * as fs from 'fs/promises';
import {
  scanAllTAGs,
  scanTAGChains,
  findOrphanedTAGs,
  findDuplicateTAGs,
} from './scanner';
import type {
  Violation,
  ValidationResult,
  ImmutabilityCheck,
  TAGInfo,
  TAGChainInfo,
} from './types';

/**
 * TAG block patterns (MoAI-style)
 */
const TAG_BLOCK_PATTERN = /^\/\*\*\s*([\s\S]*?)\*\//m;
const IMMUTABLE_MARKER_PATTERN = /@IMMUTABLE/;
const MAIN_TAG_PATTERN = /@([A-Z]+):([A-Z0-9-]+)/;
const CHAIN_LINE_PATTERN = /CHAIN:\s*(.+)/;

/**
 * Extract TAG block from file content (MoAI-style, top of file only)
 *
 * @param content - File content
 * @returns TAG block content or null
 */
function extractTAGBlock(content: string): { content: string; lineNumber: number } | null {
  const lines = content.split('\n');
  let inBlock = false;
  let blockLines: string[] = [];
  let startLineNumber = 0;

  // Only scan first 30 lines
  for (let i = 0; i < Math.min(lines.length, 30); i++) {
    const line = lines[i].trim();

    // Skip empty lines and shebang
    if (!line || line.startsWith('#!')) {
      continue;
    }

    // TAG block start
    if (line.startsWith('/**') && !inBlock) {
      inBlock = true;
      blockLines = [line];
      startLineNumber = i + 1;
      continue;
    }

    // TAG block content
    if (inBlock) {
      blockLines.push(line);

      // TAG block end
      if (line.endsWith('*/')) {
        const blockContent = blockLines.join('\n');

        // Check if block contains @TAG
        if (MAIN_TAG_PATTERN.test(blockContent)) {
          return {
            content: blockContent,
            lineNumber: startLineNumber,
          };
        }

        // No @TAG, reset and continue
        inBlock = false;
        blockLines = [];
        continue;
      }
    }

    // Non-TAG code started, stop searching
    if (!inBlock && line && !line.startsWith('//') && !line.startsWith('/*')) {
      break;
    }
  }

  return null;
}

/**
 * Normalize TAG block for comparison (remove whitespace variations)
 *
 * @param blockContent - TAG block content
 * @returns Normalized content
 */
function normalizeTAGBlock(blockContent: string): string {
  return blockContent
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .join('\n');
}

/**
 * Check TAG immutability (MoAI extension)
 * Verifies that @IMMUTABLE TAG blocks are not modified
 *
 * @param filePath - File path to check
 * @param oldContent - Original file content
 * @param newContent - New file content
 * @returns Immutability check result
 *
 * @example
 * await checkImmutability("src/auth.ts", oldContent, newContent)
 * // => { violated: true, modifiedTag: "AUTH-001", violationDetails: "..." }
 */
export async function checkImmutability(
  filePath: string,
  oldContent: string,
  newContent: string
): Promise<ImmutabilityCheck> {
  // New file, no immutability check needed
  if (!oldContent || oldContent.trim() === '') {
    return { violated: false };
  }

  // Extract TAG blocks
  const oldBlock = extractTAGBlock(oldContent);
  const newBlock = extractTAGBlock(newContent);

  // No old TAG block, nothing to protect
  if (!oldBlock) {
    return { violated: false };
  }

  // Check for @IMMUTABLE marker in old block
  const wasImmutable = IMMUTABLE_MARKER_PATTERN.test(oldBlock.content);
  if (!wasImmutable) {
    return { violated: false };
  }

  // Extract TAG ID for reporting
  const tagMatch = oldBlock.content.match(MAIN_TAG_PATTERN);
  const tagId = tagMatch ? `${tagMatch[1]}:${tagMatch[2]}` : 'UNKNOWN';

  // @IMMUTABLE block was removed
  if (!newBlock) {
    return {
      violated: true,
      modifiedTag: tagId,
      violationDetails: `@IMMUTABLE TAG block was removed from ${filePath}`,
    };
  }

  // Compare normalized content
  const oldNormalized = normalizeTAGBlock(oldBlock.content);
  const newNormalized = normalizeTAGBlock(newBlock.content);

  if (oldNormalized !== newNormalized) {
    return {
      violated: true,
      modifiedTag: tagId,
      violationDetails: `@IMMUTABLE TAG block content was modified in ${filePath}`,
    };
  }

  return { violated: false };
}

/**
 * Validate TAG chain format (MoAI extension)
 *
 * @param chainString - CHAIN line content (e.g., "@SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001")
 * @returns True if valid chain format
 */
export function validateTAGChainFormat(chainString: string): boolean {
  const tags = chainString.split(/\s*(?:->|→)\s*/).map((t) => t.trim());

  // Must have at least 2 tags
  if (tags.length < 2) {
    return false;
  }

  // Each tag must match @TYPE:ID format
  for (const tag of tags) {
    if (!MAIN_TAG_PATTERN.test(tag)) {
      return false;
    }
  }

  return true;
}

/**
 * Detect circular dependencies in TAG chains (MoAI extension)
 *
 * @param chains - Array of TAG chain info
 * @returns Array of circular dependency violations
 */
export function detectCircularDependencies(
  chains: TAGChainInfo[]
): Violation[] {
  const violations: Violation[] = [];
  const graph = new Map<string, Set<string>>();

  // Build dependency graph
  for (const chain of chains) {
    for (let i = 0; i < chain.chain.length - 1; i++) {
      const from = chain.chain[i];
      const to = chain.chain[i + 1];

      if (!graph.has(from)) {
        graph.set(from, new Set());
      }
      graph.get(from)!.add(to);
    }
  }

  // DFS cycle detection
  const visited = new Set<string>();
  const recStack = new Set<string>();

  function hasCycle(node: string, path: string[]): boolean {
    visited.add(node);
    recStack.add(node);
    path.push(node);

    const neighbors = graph.get(node);
    if (neighbors) {
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          if (hasCycle(neighbor, path)) {
            return true;
          }
        } else if (recStack.has(neighbor)) {
          // Cycle detected
          violations.push({
            level: 'HIGH',
            category: 'TAG Chain',
            message: `Circular dependency detected: ${path.join(' -> ')} -> ${neighbor}`,
          });
          return true;
        }
      }
    }

    path.pop();
    recStack.delete(node);
    return false;
  }

  for (const node of graph.keys()) {
    if (!visited.has(node)) {
      hasCycle(node, []);
    }
  }

  return violations;
}

/**
 * Validate TAG integrity
 * Checks for orphaned TAGs, duplicates, and chain integrity
 *
 * @param searchPath - Root path to search
 * @returns Validation result with violations
 *
 * @example
 * await validateTAGIntegrity()
 * // => {
 * //   passed: false,
 * //   blocked: false,
 * //   violations: [
 * //     { level: "MEDIUM", category: "Orphaned TAG", message: "..." }
 * //   ],
 * //   summary: { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 0 }
 * // }
 */
export async function validateTAGIntegrity(
  searchPath: string = '.'
): Promise<ValidationResult> {
  const violations: Violation[] = [];

  try {
    // 1. Find orphaned TAGs (warning by default)
    const orphaned = await findOrphanedTAGs(searchPath);
    for (const tagId of orphaned) {
      violations.push({
        level: 'MEDIUM',
        category: 'Orphaned TAG',
        message: `TAG ${tagId} has @CODE or @TEST but no @SPEC`,
        fixCommand: `Create SPEC for TAG ${tagId}`,
      });
    }

    // 2. Find duplicate SPEC TAGs. CODE/TEST multi-file TAGs are allowed.
    const duplicates = await findDuplicateTAGs(searchPath);
    for (const [key, locations] of duplicates.entries()) {
      const [tagId, type] = key.split(':');
      violations.push({
        level: 'HIGH',
        category: 'Duplicate TAG',
        message: `SPEC TAG ${tagId} (${type}) appears in ${locations.length} files`,
        file: locations[0].file,
        line: locations[0].line,
      });
    }

    // 3. Validate TAG chains (HIGH)
    const chains = await scanTAGChains(searchPath);
    for (const chain of chains) {
      const chainStr = chain.chain.join(' -> ');
      if (!validateTAGChainFormat(chainStr)) {
        violations.push({
          level: 'HIGH',
          category: 'Invalid TAG Chain',
          message: `Invalid chain format in ${chain.file}:${chain.line}`,
          file: chain.file,
          line: chain.line,
        });
      }
    }

    // 4. Detect circular dependencies (HIGH)
    const circularViolations = detectCircularDependencies(chains);
    violations.push(...circularViolations);

    // 5. Check broken chain references (MEDIUM)
    const allTags = await scanAllTAGs(searchPath);
    const existingTagIds = new Set(allTags.map((t) => t.id));

    for (const chain of chains) {
      for (const tagRef of chain.chain) {
        const match = tagRef.match(/@[A-Z]+:([A-Z0-9-]+)/);
        if (match) {
          const refId = match[1];
          if (!existingTagIds.has(refId)) {
            violations.push({
              level: 'MEDIUM',
              category: 'Broken Chain Reference',
              message: `Chain references non-existent TAG: ${refId}`,
              file: chain.file,
              line: chain.line,
            });
          }
        }
      }
    }
  } catch (error) {
    violations.push({
      level: 'HIGH',
      category: 'Validation Error',
      message: `TAG integrity validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    });
  }

  // Summarize violations
  const summary = {
    CRITICAL: violations.filter((v) => v.level === 'CRITICAL').length,
    HIGH: violations.filter((v) => v.level === 'HIGH').length,
    MEDIUM: violations.filter((v) => v.level === 'MEDIUM').length,
    LOW: violations.filter((v) => v.level === 'LOW').length,
  };

  return {
    passed: violations.length === 0,
    blocked: false, // TAG integrity is best-effort unless promoted by project policy or CI
    violations,
    summary,
  };
}

/**
 * Validate TAG format
 *
 * @param tagId - TAG ID to validate
 * @returns Violation if invalid, null if valid
 */
export function validateTAGFormat(tagId: string): Violation | null {
  // Must match: DOMAIN-NNN (3+ digits)
  if (!/^[A-Z]+(?:-[A-Z]+)*-\d{3,}$/.test(tagId)) {
    return {
      level: 'MEDIUM',
      category: 'TAG Format',
      message: `Invalid TAG format: ${tagId} (expected: DOMAIN-NNN with 3+ digits)`,
    };
  }

  return null;
}

/**
 * Check TAG consistency across spec/test/code files
 *
 * @param tagId - TAG ID to check
 * @param searchPath - Root path to search
 * @returns Violations if inconsistent
 */
export async function checkTAGConsistency(
  tagId: string,
  searchPath: string = '.'
): Promise<Violation[]> {
  const violations: Violation[] = [];
  const tags = await scanAllTAGs(searchPath);
  const matchingTags = tags.filter((t) => t.id === tagId);

  if (matchingTags.length === 0) {
    violations.push({
      level: 'HIGH',
      category: 'TAG Not Found',
      message: `TAG ${tagId} not found in project`,
    });
    return violations;
  }

  const types = new Set(matchingTags.map((t) => t.type));

  // Report chain coverage. TAG integrity is warning-only by default.
  if (!types.has('SPEC')) {
    violations.push({
      level: 'HIGH',
      category: 'Incomplete TAG Chain',
      message: `TAG ${tagId} missing @SPEC`,
    });
  }

  if (!types.has('TEST')) {
    violations.push({
      level: 'MEDIUM',
      category: 'Incomplete TAG Chain',
      message: `TAG ${tagId} missing @TEST`,
    });
  }

  if (!types.has('CODE')) {
    violations.push({
      level: 'LOW',
      category: 'Incomplete TAG Chain',
      message: `TAG ${tagId} missing @CODE (may not be implemented yet)`,
    });
  }

  return violations;
}

/**
 * Generate TAG integrity report
 *
 * @param searchPath - Root path to search
 * @returns Human-readable report
 */
export async function generateTAGIntegrityReport(
  searchPath: string = '.'
): Promise<string> {
  const result = await validateTAGIntegrity(searchPath);
  const lines: string[] = [];

  lines.push('# TAG Integrity Report');
  lines.push('');
  lines.push(`**Status**: ${result.passed ? '✅ PASSED' : '❌ FAILED'}`);
  lines.push(`**Blocked**: ${result.blocked ? '🚫 YES' : '✅ NO'}`);
  lines.push('');

  lines.push('## Summary');
  lines.push('');
  lines.push(`- CRITICAL: ${result.summary.CRITICAL}`);
  lines.push(`- HIGH: ${result.summary.HIGH}`);
  lines.push(`- MEDIUM: ${result.summary.MEDIUM}`);
  lines.push(`- LOW: ${result.summary.LOW}`);
  lines.push('');

  if (result.violations.length > 0) {
    lines.push('## Violations');
    lines.push('');

    // Group by level
    for (const level of ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const) {
      const levelViolations = result.violations.filter((v) => v.level === level);
      if (levelViolations.length === 0) continue;

      lines.push(`### ${level} (${levelViolations.length})`);
      lines.push('');

      for (const violation of levelViolations) {
        lines.push(`- **${violation.category}**: ${violation.message}`);
        if (violation.file) {
          lines.push(`  - File: ${violation.file}:${violation.line || '?'}`);
        }
        if (violation.fixCommand) {
          lines.push(`  - Fix: \`${violation.fixCommand}\``);
        }
      }
      lines.push('');
    }
  } else {
    lines.push('## ✅ No violations found');
    lines.push('');
    lines.push('No TAG integrity warnings found.');
  }

  return lines.join('\n');
}
