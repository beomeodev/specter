/**
 * TAG System Type Definitions
 *
 * Defines core types for TAG generation, scanning, and validation.
 * Supports both basic My-Spec workflow and MoAI-style CHAIN/IMMUTABLE features.
 */

/**
 * TAG Type Categories (4-Core)
 */
export type TAGType = 'SPEC' | 'TEST' | 'CODE' | 'DOC';

/**
 * TAG Information Structure
 */
export interface TAGInfo {
  /** TAG ID (e.g., "AUTH-001") */
  id: string;

  /** TAG type */
  type: TAGType;

  /** File path where TAG is located */
  file: string;

  /** Line number in file */
  line: number;

  /** Reference to SPEC file (optional) */
  specPath?: string;

  /** Reference to TEST file (optional) */
  testPath?: string;

  /** TAG status (for MoAI compatibility) */
  status?: 'active' | 'deprecated' | 'completed';

  /** Creation date (YYYY-MM-DD) */
  created?: string;

  /** Last update date (YYYY-MM-DD) */
  updated?: string;

  /** CHAIN relationships (MoAI extension) */
  chain?: string[];

  /** Dependencies (MoAI extension) */
  depends?: string[];

  /** IMMUTABLE marker present (MoAI extension) */
  immutable?: boolean;
}

/**
 * TAG Chain Information (MoAI extension)
 */
export interface TAGChainInfo {
  /** TAG ID */
  id: string;

  /** TAG type */
  type: TAGType;

  /** Chain sequence (e.g., ["@SPEC:AUTH-001", "@TEST:AUTH-001", "@CODE:AUTH-001"]) */
  chain: string[];

  /** File path */
  file: string;

  /** Line number */
  line: number;
}

/**
 * Violation Severity Levels
 */
export type ViolationLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

/**
 * Violation Information
 */
export interface Violation {
  /** Severity level */
  level: ViolationLevel;

  /** Violation category */
  category: string;

  /** Violation message */
  message: string;

  /** File path (optional) */
  file?: string;

  /** Line number (optional) */
  line?: number;

  /** Suggested fix command (optional) */
  fixCommand?: string;
}

/**
 * Validation Result
 */
export interface ValidationResult {
  /** Overall validation passed */
  passed: boolean;

  /** Critical violations present (blocks execution) */
  blocked: boolean;

  /** List of violations */
  violations: Violation[];

  /** Summary counts by level */
  summary: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
}

/**
 * Immutability Check Result (MoAI extension)
 */
export interface ImmutabilityCheck {
  /** Immutability violated */
  violated: boolean;

  /** Modified TAG ID (if violated) */
  modifiedTag?: string;

  /** Violation details */
  violationDetails?: string;
}

/**
 * TAG Generation Options (MoAI extension)
 */
export interface TAGGenerationOptions {
  /** TAG block format */
  format?: 'inline' | 'block';

  /** Include @IMMUTABLE marker */
  immutable?: boolean;

  /** CHAIN relationships */
  chain?: string[];

  /** Dependencies */
  depends?: string[];

  /** Initial status */
  status?: 'active' | 'draft' | 'completed';
}

/**
 * Domain Extraction Result
 */
export interface DomainExtractionResult {
  /** Extracted domain (e.g., "AUTH") */
  domain: string;

  /** Confidence level (0-1) */
  confidence: number;

  /** Matched keyword (if any) */
  matchedKeyword?: string;

  /** Fallback used */
  fallback: boolean;
}
