/**
 * TRUST Verification Type Definitions
 *
 * Defines types for TRUST 5 Principles verification:
 * - T: Test-First (TDD)
 * - R: Readable
 * - U: Unified (consistent)
 * - S: Secured
 * - T: Trackable (TAG system)
 */

import type { Violation } from '../tag/types';

/**
 * TRUST Verification Level Result
 */
export interface TRUSTLevelResult {
  /** Level passed all checks */
  passed: boolean;

  /** Violations found */
  violations: Violation[];

  /** CRITICAL violation count (blocks execution) */
  criticalCount: number;

  /** Execution time in ms */
  executionTime?: number;
}

/**
 * TRUST Level 1 Result (Structure)
 */
export interface Level1Result extends TRUSTLevelResult {
  /** Checks performed */
  checks: {
    testsDirectory: boolean;
    gitignoreEnv: boolean;
    fileSizes: boolean;
  };
}

/**
 * TRUST Level 2 Result (Quality)
 */
export interface Level2Result extends TRUSTLevelResult {
  /** Checks performed */
  checks: {
    testsPass: boolean;
    lintPass: boolean;
    typeCheckPass: boolean;
  };

  /** Project type detected */
  projectType: 'typescript' | 'python' | 'unknown';
}

/**
 * TRUST Level 3 Result (Deep Analysis)
 */
export interface Level3Result extends TRUSTLevelResult {
  /** Checks performed */
  checks: {
    coverage: boolean;
    complexity: boolean;
    circularDeps: boolean;
    security: boolean;
    tagIntegrity: boolean;
  };

  /** Coverage percentage (if available) */
  coveragePercent?: number;

  /** Average complexity score */
  avgComplexity?: number;

  /** Circular dependencies count */
  circularDepsCount?: number;

  /** Security vulnerabilities count */
  securityIssues?: number;

  /** TAG integrity violations */
  tagViolations?: number;
}

/**
 * Complete TRUST Verification Result
 */
export interface TRUSTVerificationResult {
  /** Overall passed */
  passed: boolean;

  /** Execution blocked (CRITICAL violations) */
  blocked: boolean;

  /** Level 1 result */
  level1: Level1Result;

  /** Level 2 result */
  level2: Level2Result;

  /** Level 3 result */
  level3: Level3Result;

  /** Total violations */
  totalViolations: number;

  /** Summary by severity */
  summary: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };

  /** Total execution time */
  totalTime: number;
}

/**
 * Project Type Detection Result
 */
export interface ProjectTypeInfo {
  /** Detected project type */
  type: 'typescript' | 'python' | 'go' | 'rust' | 'java' | 'unknown';

  /** Confidence (0-1) */
  confidence: number;

  /** Package manager detected */
  packageManager?: 'npm' | 'yarn' | 'pnpm' | 'pip' | 'poetry' | 'cargo' | 'maven' | 'gradle';

  /** Main config file found */
  configFile?: string;
}

/**
 * File Size Check Result
 */
export interface FileSizeCheck {
  /** File path */
  file: string;

  /** Lines of code */
  lines: number;

  /** Exceeds limit */
  exceeds: boolean;

  /** Limit that was checked */
  limit: number;
}

/**
 * Code Complexity Check Result
 */
export interface ComplexityCheck {
  /** File path */
  file: string;

  /** Function name */
  function: string;

  /** Complexity score */
  complexity: number;

  /** Exceeds limit */
  exceeds: boolean;

  /** Limit that was checked */
  limit: number;
}

/**
 * Security Vulnerability
 */
export interface SecurityVulnerability {
  /** Package name */
  package: string;

  /** Vulnerability severity */
  severity: 'critical' | 'high' | 'moderate' | 'low';

  /** CVE ID (if available) */
  cve?: string;

  /** Description */
  description: string;

  /** Recommended fix */
  fix?: string;
}

/**
 * Test Coverage Report
 */
export interface CoverageReport {
  /** Overall coverage percentage */
  overall: number;

  /** Line coverage */
  lines?: number;

  /** Branch coverage */
  branches?: number;

  /** Function coverage */
  functions?: number;

  /** Statement coverage */
  statements?: number;

  /** Uncovered files */
  uncoveredFiles?: string[];
}
