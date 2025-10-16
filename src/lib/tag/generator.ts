/**
 * TAG Generator Module
 *
 * Provides TAG ID generation with automatic domain extraction.
 * Supports both My-Spec basic format and MoAI-style TAG blocks.
 */

import type {
  TAGType,
  TAGGenerationOptions,
  DomainExtractionResult,
} from './types';

/**
 * Domain keyword mappings
 * Maps common feature names to domain prefixes
 */
const DOMAIN_KEYWORDS: Record<string, string[]> = {
  AUTH: ['auth', 'authentication', 'login', 'signup', 'password', 'session', 'jwt', 'token'],
  USER: ['user', 'account', 'profile', 'member'],
  PAY: ['payment', 'pay', 'checkout', 'billing', 'invoice'],
  CART: ['cart', 'shopping', 'basket'],
  ORDER: ['order', 'purchase'],
  PRODUCT: ['product', 'item', 'goods', 'catalog'],
  API: ['api', 'endpoint', 'rest', 'graphql'],
  DB: ['database', 'db', 'schema', 'migration'],
  UI: ['ui', 'interface', 'component', 'layout'],
  TEST: ['test', 'testing', 'spec', 'qa'],
  PERF: ['performance', 'optimization', 'cache', 'speed'],
  SEC: ['security', 'vulnerability', 'encryption'],
  DOC: ['documentation', 'docs', 'readme'],
  CONFIG: ['config', 'configuration', 'settings'],
  DEPLOY: ['deploy', 'deployment', 'release', 'ci', 'cd'],
  MONITOR: ['monitor', 'logging', 'metrics', 'analytics'],
};

/**
 * Extract domain from FR title with keyword matching
 *
 * @param frTitle - Functional Requirement title (e.g., "User Authentication")
 * @param frNumber - FR number as fallback (e.g., "FR-1")
 * @returns Domain extraction result with confidence score
 *
 * @example
 * extractDomain("User Authentication", "FR-1")
 * // => { domain: "AUTH", confidence: 1, matchedKeyword: "authentication", fallback: false }
 *
 * extractDomain("Random Feature", "FR-9")
 * // => { domain: "FR9", confidence: 0.5, fallback: true }
 */
export function extractDomain(
  frTitle: string,
  frNumber: string
): DomainExtractionResult {
  const normalizedTitle = frTitle.toLowerCase();

  // Try keyword matching
  for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
    for (const keyword of keywords) {
      if (normalizedTitle.includes(keyword)) {
        return {
          domain,
          confidence: 1.0,
          matchedKeyword: keyword,
          fallback: false,
        };
      }
    }
  }

  // Fallback: Use FR number (remove non-alphanumeric)
  const fallbackDomain = frNumber.replace(/[^A-Z0-9]/gi, '').toUpperCase();

  return {
    domain: fallbackDomain,
    confidence: 0.5,
    fallback: true,
  };
}

/**
 * Generate next TAG ID with zero-padded counter
 *
 * @param domain - Domain prefix (e.g., "AUTH")
 * @param count - Current TAG count for this domain
 * @returns Next TAG ID (e.g., "AUTH-001")
 *
 * @example
 * generateNextTAGID("AUTH", 0) // => "AUTH-001"
 * generateNextTAGID("AUTH", 5) // => "AUTH-006"
 * generateNextTAGID("PAY", 99) // => "PAY-100"
 */
export function generateNextTAGID(domain: string, count: number): string {
  const nextId = count + 1;
  const paddedId = String(nextId).padStart(3, '0');
  return `${domain}-${paddedId}`;
}

/**
 * Generate inline TAG reference
 *
 * @param id - TAG ID (e.g., "AUTH-001")
 * @param type - TAG type
 * @returns Inline TAG string (e.g., "@SPEC:AUTH-001")
 *
 * @example
 * generateInlineTAG("AUTH-001", "SPEC") // => "@SPEC:AUTH-001"
 */
export function generateInlineTAG(id: string, type: TAGType): string {
  return `@${type}:${id}`;
}

/**
 * Generate TAG chain string (My-Spec format)
 *
 * @param id - TAG ID
 * @returns TAG chain (e.g., "@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001")
 *
 * @example
 * generateTAGChain("AUTH-001")
 * // => "@SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001"
 */
export function generateTAGChain(id: string): string {
  return `@SPEC:${id} → @TEST:${id} → @CODE:${id}`;
}

/**
 * Generate MoAI-style TAG block (JSDoc format)
 *
 * @param id - TAG ID
 * @param type - TAG type
 * @param options - Generation options
 * @returns Complete TAG block with metadata
 *
 * @example
 * generateTAGBlock("AUTH-001", "SPEC", {
 *   immutable: true,
 *   chain: ["@SPEC:AUTH-001", "@TEST:AUTH-001", "@CODE:AUTH-001"]
 * })
 * // =>
 * // /**
 * //  * @SPEC:AUTH-001
 * //  * CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
 * //  * DEPENDS: NONE
 * //  * STATUS: active
 * //  * CREATED: 2025-10-16
 * //  * @IMMUTABLE
 * //  *\/
 */
export function generateTAGBlock(
  id: string,
  type: TAGType,
  options: TAGGenerationOptions = {}
): string {
  const lines: string[] = ['/**'];

  // Main TAG line
  lines.push(` * @${type}:${id}`);

  // CHAIN (MoAI extension)
  if (options.chain && options.chain.length > 0) {
    const chainStr = options.chain.join(' -> ');
    lines.push(` * CHAIN: ${chainStr}`);
  }

  // DEPENDS (MoAI extension)
  if (options.depends && options.depends.length > 0) {
    const dependsStr = options.depends.join(', ');
    lines.push(` * DEPENDS: ${dependsStr}`);
  } else {
    lines.push(' * DEPENDS: NONE');
  }

  // STATUS
  const status = options.status || 'active';
  lines.push(` * STATUS: ${status}`);

  // CREATED
  const today = new Date().toISOString().split('T')[0];
  lines.push(` * CREATED: ${today}`);

  // @IMMUTABLE marker (MoAI extension)
  if (options.immutable) {
    lines.push(' * @IMMUTABLE');
  }

  lines.push(' */');

  return lines.join('\n');
}

/**
 * Parse TAG ID into components
 *
 * @param tagId - TAG ID (e.g., "AUTH-001")
 * @returns Parsed components or null if invalid
 *
 * @example
 * parseTAGID("AUTH-001") // => { domain: "AUTH", number: 1 }
 * parseTAGID("UPDATE-REFACTOR-001") // => { domain: "UPDATE-REFACTOR", number: 1 }
 * parseTAGID("INVALID") // => null
 */
export function parseTAGID(tagId: string): {
  domain: string;
  number: number;
} | null {
  // Pattern: DOMAIN-NNN or DOMAIN-DOMAIN-NNN (composite domains)
  const match = tagId.match(/^([A-Z]+(?:-[A-Z]+)*)-(\d+)$/);

  if (!match) {
    return null;
  }

  return {
    domain: match[1],
    number: parseInt(match[2], 10),
  };
}

/**
 * Validate TAG ID format
 *
 * @param tagId - TAG ID to validate
 * @returns True if valid format
 *
 * @example
 * isValidTAGID("AUTH-001") // => true
 * isValidTAGID("AUTH-1") // => false (needs 3 digits)
 * isValidTAGID("auth-001") // => false (must be uppercase)
 */
export function isValidTAGID(tagId: string): boolean {
  // Must match: DOMAIN-NNN (3 digits minimum)
  return /^[A-Z]+(?:-[A-Z]+)*-\d{3,}$/.test(tagId);
}

/**
 * Generate complete TAG metadata for tasks.md
 *
 * @param id - TAG ID
 * @param frTitle - Functional Requirement title
 * @param frGoal - FR goal description
 * @returns Formatted TAG metadata block
 *
 * @example
 * generateTaskTAGMetadata("AUTH-001", "User Authentication", "Implement login")
 * // =>
 * // **TAG**: @SPEC:AUTH-001 → @TEST:AUTH-001 → @CODE:AUTH-001
 * //
 * // **Goal**: Implement login
 * // **Independent Test**: User Authentication
 */
export function generateTaskTAGMetadata(
  id: string,
  frTitle: string,
  frGoal: string
): string {
  const chain = generateTAGChain(id);

  return [
    `**TAG**: ${chain}`,
    '',
    `**Goal**: ${frGoal}`,
    `**Independent Test**: ${frTitle}`,
  ].join('\n');
}

/**
 * Extract domain suggestions from FR title
 * Returns multiple possible domains with confidence scores
 *
 * @param frTitle - FR title
 * @returns Array of domain suggestions sorted by confidence
 *
 * @example
 * suggestDomains("User authentication and profile management")
 * // => [
 * //   { domain: "AUTH", confidence: 1.0, keyword: "authentication" },
 * //   { domain: "USER", confidence: 0.8, keyword: "user" }
 * // ]
 */
export function suggestDomains(frTitle: string): Array<{
  domain: string;
  confidence: number;
  keyword: string;
}> {
  const normalizedTitle = frTitle.toLowerCase();
  const suggestions: Array<{ domain: string; confidence: number; keyword: string }> = [];

  for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
    for (const keyword of keywords) {
      if (normalizedTitle.includes(keyword)) {
        // Higher confidence for longer keywords
        const confidence = Math.min(1.0, keyword.length / 10);
        suggestions.push({ domain, confidence, keyword });
        break; // One match per domain
      }
    }
  }

  // Sort by confidence descending
  return suggestions.sort((a, b) => b.confidence - a.confidence);
}
