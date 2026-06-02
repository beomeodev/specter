/**
 * TAG Scanner Module
 *
 * Provides ripgrep-based TAG scanning and chain analysis.
 * Supports both My-Spec basic scanning and MoAI-style chain integrity checks.
 */

import { execSync } from 'child_process';
import * as path from 'path';
import type { TAGInfo, TAGChainInfo, TAGType } from './types';

/**
 * TAG pattern for ripgrep
 * Matches: @SPEC:AUTH-001, @TEST:USER-002, etc.
 */
const TAG_PATTERN = '@([A-Z]+):([A-Z0-9-]+)';

/**
 * CHAIN pattern for ripgrep (MoAI extension)
 * Matches: CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
 * Also accepts the legacy unicode arrow.
 */
const CHAIN_PATTERN = 'CHAIN:\\s*(.+)';

/**
 * Check if ripgrep is available
 *
 * @returns True if ripgrep is installed and accessible
 */
export function isRipgrepAvailable(): boolean {
  try {
    execSync('rg --version', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Count TAGs for a specific domain
 *
 * @param domain - Domain prefix (e.g., "AUTH")
 * @param searchPath - Root path to search (defaults to current directory)
 * @returns Number of existing TAGs for this domain
 *
 * @example
 * await countTAGsForDomain("AUTH") // => 5 (AUTH-001 to AUTH-005 exist)
 */
export async function countTAGsForDomain(
  domain: string,
  searchPath: string = '.'
): Promise<number> {
  if (!isRipgrepAvailable()) {
    throw new Error('ripgrep (rg) is not installed. Install from: https://github.com/BurntSushi/ripgrep');
  }

  try {
    // Search for @SPEC:DOMAIN-, @TEST:DOMAIN-, @CODE:DOMAIN-
    // Use -o (only matching) and count unique TAG IDs
    const pattern = `@(?:SPEC|TEST|CODE|DOC):${domain}-\\d+`;
    const result = execSync(
      `rg "${pattern}" -o --no-filename --no-heading "${searchPath}" 2>/dev/null || true`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
    );

    if (!result.trim()) {
      return 0;
    }

    // Extract unique TAG IDs (remove @TYPE: prefix)
    const tagIds = new Set<string>();
    const lines = result.trim().split('\n');

    for (const line of lines) {
      const match = line.match(new RegExp(`${domain}-(\\d+)`));
      if (match) {
        tagIds.add(match[0]); // Add full TAG ID (e.g., "AUTH-001")
      }
    }

    return tagIds.size;
  } catch (error) {
    // If ripgrep fails (no matches or error), return 0
    return 0;
  }
}

/**
 * Scan all TAGs in the project
 *
 * @param searchPath - Root path to search
 * @returns Array of TAG information
 *
 * @example
 * await scanAllTAGs()
 * // => [
 * //   { id: "AUTH-001", type: "SPEC", file: "specs/auth/spec.md", line: 10, ... },
 * //   { id: "AUTH-001", type: "TEST", file: "tests/auth.test.ts", line: 5, ... }
 * // ]
 */
export async function scanAllTAGs(
  searchPath: string = '.'
): Promise<TAGInfo[]> {
  if (!isRipgrepAvailable()) {
    throw new Error('ripgrep (rg) is not installed');
  }

  try {
    // Search for all TAG patterns with line numbers and file paths
    const result = execSync(
      `rg "${TAG_PATTERN}" -n --no-heading "${searchPath}" 2>/dev/null || true`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
    );

    if (!result.trim()) {
      return [];
    }

    const tags: TAGInfo[] = [];
    const lines = result.trim().split('\n');

    for (const line of lines) {
      // Format: file/path:line:@TYPE:TAG-ID
      const match = line.match(/^(.+?):(\d+):.*?@([A-Z]+):([A-Z0-9-]+)/);
      if (!match) continue;

      const [, filePath, lineNum, type, tagId] = match;

      tags.push({
        id: tagId,
        type: type as TAGType,
        file: filePath,
        line: parseInt(lineNum, 10),
      });
    }

    return tags;
  } catch (error) {
    console.error('TAG scan failed:', error);
    return [];
  }
}

/**
 * Scan TAG chains (MoAI extension)
 *
 * @param searchPath - Root path to search
 * @returns Array of TAG chain information
 *
 * @example
 * await scanTAGChains()
 * // => [
 * //   {
 * //     id: "AUTH-001",
 * //     type: "SPEC",
 * //     chain: ["@SPEC:AUTH-001", "@TEST:AUTH-001", "@CODE:AUTH-001"],
 * //     file: "src/auth/service.ts",
 * //     line: 3
 * //   }
 * // ]
 */
export async function scanTAGChains(
  searchPath: string = '.'
): Promise<TAGChainInfo[]> {
  if (!isRipgrepAvailable()) {
    throw new Error('ripgrep (rg) is not installed');
  }

  try {
    // Search for CHAIN: lines
    const result = execSync(
      `rg "${CHAIN_PATTERN}" -n --no-heading "${searchPath}" 2>/dev/null || true`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
    );

    if (!result.trim()) {
      return [];
    }

    const chains: TAGChainInfo[] = [];
    const lines = result.trim().split('\n');

    for (const line of lines) {
      // Format: file/path:line:CHAIN: @TAG1 -> @TAG2 -> @TAG3
      const fileMatch = line.match(/^(.+?):(\d+):/);
      if (!fileMatch) continue;

      const [, filePath, lineNum] = fileMatch;

      // Extract chain string
      const chainMatch = line.match(/CHAIN:\s*(.+)$/);
      if (!chainMatch) continue;

      const chainStr = chainMatch[1].trim();
      const chainTags = chainStr
        .split(/\s*(?:->|→)\s*/)
        .map((t) => t.trim())
        .filter((t) => t.startsWith('@'));

      // Extract main TAG ID from first chain element
      const firstTag = chainTags[0];
      const tagMatch = firstTag.match(/@([A-Z]+):([A-Z0-9-]+)/);
      if (!tagMatch) continue;

      const [, type, tagId] = tagMatch;

      chains.push({
        id: tagId,
        type: type as TAGType,
        chain: chainTags,
        file: filePath,
        line: parseInt(lineNum, 10),
      });
    }

    return chains;
  } catch (error) {
    console.error('TAG chain scan failed:', error);
    return [];
  }
}

/**
 * Find orphaned TAGs (CODE/TEST without SPEC)
 *
 * @param searchPath - Root path to search
 * @returns Array of orphaned TAG IDs
 *
 * @example
 * await findOrphanedTAGs()
 * // => ["AUTH-002", "USER-005"] // These TAGs have @CODE but no @SPEC
 */
export async function findOrphanedTAGs(
  searchPath: string = '.'
): Promise<string[]> {
  const allTags = await scanAllTAGs(searchPath);

  // Group by TAG ID
  const tagMap = new Map<string, Set<TAGType>>();

  for (const tag of allTags) {
    if (!tagMap.has(tag.id)) {
      tagMap.set(tag.id, new Set());
    }
    tagMap.get(tag.id)!.add(tag.type);
  }

  // Find TAGs with CODE/TEST but no SPEC
  const orphaned: string[] = [];

  for (const [tagId, types] of tagMap.entries()) {
    const hasCode = types.has('CODE');
    const hasTest = types.has('TEST');
    const hasSpec = types.has('SPEC');

    if ((hasCode || hasTest) && !hasSpec) {
      orphaned.push(tagId);
    }
  }

  return orphaned.sort();
}

/**
 * Find duplicate SPEC TAG IDs.
 *
 * Multi-file CODE and TEST TAGs are allowed by policy. Static scanning cannot
 * prove whether repeated DOC TAGs are conflicting, so this helper reports only
 * duplicate SPEC declarations.
 *
 * @param searchPath - Root path to search
 * @returns Map of TAG ID to duplicate locations
 *
 * @example
 * await findDuplicateTAGs()
 * // => {
 * //   "AUTH-001:SPEC": [
 * //     { file: "specs/auth1.md", line: 10 },
 * //     { file: "specs/auth2.md", line: 15 }
 * //   ]
 * // }
 */
export async function findDuplicateTAGs(
  searchPath: string = '.'
): Promise<Map<string, Array<{ file: string; line: number }>>> {
  const allTags = await scanAllTAGs(searchPath);

  // Group duplicate SPEC declarations only. CODE/TEST duplicates are valid for
  // multi-file implementations and multi-file test coverage.
  const tagMap = new Map<string, Array<{ file: string; line: number }>>();

  for (const tag of allTags) {
    if (tag.type !== 'SPEC') {
      continue;
    }

    const key = `${tag.id}:${tag.type}`;
    if (!tagMap.has(key)) {
      tagMap.set(key, []);
    }
    tagMap.get(key)!.push({ file: tag.file, line: tag.line });
  }

  // Filter to only duplicates (more than 1 occurrence)
  const duplicates = new Map<string, Array<{ file: string; line: number }>>();

  for (const [key, locations] of tagMap.entries()) {
    if (locations.length > 1) {
      duplicates.set(key, locations);
    }
  }

  return duplicates;
}

/**
 * Get TAG statistics
 *
 * @param searchPath - Root path to search
 * @returns TAG statistics summary
 *
 * @example
 * await getTAGStatistics()
 * // => {
 * //   total: 150,
 * //   byType: { SPEC: 50, TEST: 50, CODE: 48, DOC: 2 },
 * //   byDomain: { AUTH: 10, USER: 15, PAY: 8 },
 * //   orphaned: 2,
 * //   duplicates: 0,
 * //   withChains: 45
 * // }
 */
export async function getTAGStatistics(searchPath: string = '.'): Promise<{
  total: number;
  byType: Record<TAGType, number>;
  byDomain: Record<string, number>;
  orphaned: number;
  duplicates: number;
  withChains: number;
}> {
  const [allTags, chains, orphaned, duplicates] = await Promise.all([
    scanAllTAGs(searchPath),
    scanTAGChains(searchPath),
    findOrphanedTAGs(searchPath),
    findDuplicateTAGs(searchPath),
  ]);

  // Count by type
  const byType: Record<TAGType, number> = {
    SPEC: 0,
    TEST: 0,
    CODE: 0,
    DOC: 0,
  };

  for (const tag of allTags) {
    byType[tag.type] = (byType[tag.type] || 0) + 1;
  }

  // Count by domain
  const byDomain: Record<string, number> = {};
  const uniqueTagIds = new Set(allTags.map((t) => t.id));

  for (const tagId of uniqueTagIds) {
    const domain = tagId.split('-')[0];
    byDomain[domain] = (byDomain[domain] || 0) + 1;
  }

  return {
    total: allTags.length,
    byType,
    byDomain,
    orphaned: orphaned.length,
    duplicates: duplicates.size,
    withChains: chains.length,
  };
}

/**
 * Search TAGs by domain
 *
 * @param domain - Domain to search
 * @param searchPath - Root path to search
 * @returns Array of TAGs in this domain
 */
export async function searchTAGsByDomain(
  domain: string,
  searchPath: string = '.'
): Promise<TAGInfo[]> {
  const allTags = await scanAllTAGs(searchPath);
  return allTags.filter((tag) => tag.id.startsWith(`${domain}-`));
}

/**
 * Find TAG by ID
 *
 * @param tagId - TAG ID to find
 * @param searchPath - Root path to search
 * @returns Array of TAG occurrences (may be multiple types)
 */
export async function findTAGById(
  tagId: string,
  searchPath: string = '.'
): Promise<TAGInfo[]> {
  const allTags = await scanAllTAGs(searchPath);
  return allTags.filter((tag) => tag.id === tagId);
}
