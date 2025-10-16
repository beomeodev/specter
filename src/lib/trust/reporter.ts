/**
 * TRUST Verification Reporter
 *
 * Generates human-readable reports for TRUST verification results.
 * Summarizes violations and provides actionable insights.
 */

import type {
  TRUSTVerificationResult,
  Level1Result,
  Level2Result,
  Level3Result,
} from './types';
import type { Violation } from '../tag/types';
import { runLevel1Checks } from './level1';
import { runLevel2Checks } from './level2';
import { runLevel3Checks } from './level3';

/**
 * Violation summary by severity
 */
export interface ViolationSummary {
  CRITICAL: Violation[];
  HIGH: Violation[];
  MEDIUM: Violation[];
  LOW: Violation[];
}

/**
 * Summarize violations from all levels
 *
 * @param level1 - Level 1 result
 * @param level2 - Level 2 result
 * @param level3 - Level 3 result
 * @returns Violation summary grouped by severity
 */
export function summarizeViolations(
  level1: Level1Result,
  level2: Level2Result,
  level3: Level3Result
): ViolationSummary {
  const allViolations = [
    ...level1.violations,
    ...level2.violations,
    ...level3.violations,
  ];

  return {
    CRITICAL: allViolations.filter((v) => v.level === 'CRITICAL'),
    HIGH: allViolations.filter((v) => v.level === 'HIGH'),
    MEDIUM: allViolations.filter((v) => v.level === 'MEDIUM'),
    LOW: allViolations.filter((v) => v.level === 'LOW'),
  };
}

/**
 * Generate human-readable report
 *
 * @param summary - Violation summary
 * @returns Formatted report string
 */
export function generateReport(summary: ViolationSummary): string {
  const lines: string[] = [];

  lines.push('# TRUST Verification Report');
  lines.push('');

  // Overall status
  const totalViolations =
    summary.CRITICAL.length +
    summary.HIGH.length +
    summary.MEDIUM.length +
    summary.LOW.length;

  const blocked = summary.CRITICAL.length > 0;

  lines.push(`**Status**: ${totalViolations === 0 ? '✅ PASSED' : '❌ FAILED'}`);
  lines.push(`**Blocked**: ${blocked ? '🚫 YES - Cannot proceed' : '✅ NO'}`);
  lines.push('');

  // Summary counts
  lines.push('## Summary');
  lines.push('');
  lines.push(`- 🔴 CRITICAL: ${summary.CRITICAL.length}`);
  lines.push(`- 🟠 HIGH: ${summary.HIGH.length}`);
  lines.push(`- 🟡 MEDIUM: ${summary.MEDIUM.length}`);
  lines.push(`- 🟢 LOW: ${summary.LOW.length}`);
  lines.push('');

  // Violations by level
  if (summary.CRITICAL.length > 0) {
    lines.push('## 🔴 CRITICAL Violations (Blocking)');
    lines.push('');
    lines.push('**These must be fixed before proceeding.**');
    lines.push('');

    for (const violation of summary.CRITICAL) {
      lines.push(`### ${violation.category}`);
      lines.push('');
      lines.push(`- **Issue**: ${violation.message}`);

      if (violation.file) {
        lines.push(`- **File**: \`${violation.file}\`${violation.line ? `:${violation.line}` : ''}`);
      }

      if (violation.fixCommand) {
        lines.push(`- **Fix**: \`${violation.fixCommand}\``);
      }

      lines.push('');
    }
  }

  if (summary.HIGH.length > 0) {
    lines.push('## 🟠 HIGH Violations');
    lines.push('');
    lines.push('**Strongly recommended to fix.**');
    lines.push('');

    for (const violation of summary.HIGH) {
      lines.push(`- **${violation.category}**: ${violation.message}`);

      if (violation.file) {
        lines.push(`  - File: \`${violation.file}\`${violation.line ? `:${violation.line}` : ''}`);
      }

      if (violation.fixCommand) {
        lines.push(`  - Fix: \`${violation.fixCommand}\``);
      }
    }

    lines.push('');
  }

  if (summary.MEDIUM.length > 0) {
    lines.push('## 🟡 MEDIUM Violations');
    lines.push('');
    lines.push('**Should be addressed soon.**');
    lines.push('');

    for (const violation of summary.MEDIUM) {
      lines.push(`- **${violation.category}**: ${violation.message}`);
    }

    lines.push('');
  }

  if (summary.LOW.length > 0) {
    lines.push('## 🟢 LOW Violations');
    lines.push('');
    lines.push('**Nice to fix when possible.**');
    lines.push('');

    for (const violation of summary.LOW) {
      lines.push(`- ${violation.message}`);
    }

    lines.push('');
  }

  if (totalViolations === 0) {
    lines.push('## ✅ All Checks Passed!');
    lines.push('');
    lines.push('Your project meets all TRUST 5 Principles:');
    lines.push('');
    lines.push('- **T**est-First: All tests pass');
    lines.push('- **R**eadable: Code quality checks pass');
    lines.push('- **U**nified: Consistent structure and style');
    lines.push('- **S**ecured: No security vulnerabilities');
    lines.push('- **T**rackable: TAG integrity maintained');
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Generate compact summary (for CLI output)
 *
 * @param summary - Violation summary
 * @returns Compact summary string
 */
export function generateCompactSummary(summary: ViolationSummary): string {
  const lines: string[] = [];

  const totalViolations =
    summary.CRITICAL.length +
    summary.HIGH.length +
    summary.MEDIUM.length +
    summary.LOW.length;

  if (totalViolations === 0) {
    lines.push('✅ TRUST Verification: PASSED');
  } else {
    lines.push('❌ TRUST Verification: FAILED');
    lines.push(
      `   🔴 ${summary.CRITICAL.length} CRITICAL | 🟠 ${summary.HIGH.length} HIGH | 🟡 ${summary.MEDIUM.length} MEDIUM | 🟢 ${summary.LOW.length} LOW`
    );

    if (summary.CRITICAL.length > 0) {
      lines.push('');
      lines.push('🚫 CRITICAL issues block execution:');
      for (const violation of summary.CRITICAL) {
        lines.push(`   - ${violation.category}: ${violation.message}`);
      }
    }
  }

  return lines.join('\n');
}

/**
 * Run complete TRUST verification and generate report
 *
 * @param rootPath - Project root path
 * @param verbose - Generate verbose report (default: true)
 * @returns Complete TRUST verification result
 *
 * @example
 * const result = await runTRUSTVerification('/project/root');
 * console.log(result.report);
 * // => Full TRUST verification report with all violations
 */
export async function runTRUSTVerification(
  rootPath: string = '.',
  verbose: boolean = true
): Promise<TRUSTVerificationResult & { report: string }> {
  const startTime = Date.now();

  // Run all levels
  const level1 = await runLevel1Checks(rootPath);
  const level2 = await runLevel2Checks(rootPath);
  const level3 = await runLevel3Checks(rootPath);

  // Summarize violations
  const violationSummary = summarizeViolations(level1, level2, level3);

  const totalViolations =
    violationSummary.CRITICAL.length +
    violationSummary.HIGH.length +
    violationSummary.MEDIUM.length +
    violationSummary.LOW.length;

  const summary = {
    CRITICAL: violationSummary.CRITICAL.length,
    HIGH: violationSummary.HIGH.length,
    MEDIUM: violationSummary.MEDIUM.length,
    LOW: violationSummary.LOW.length,
  };

  const totalTime = Date.now() - startTime;
  const blocked = summary.CRITICAL > 0;

  // Generate report
  const report = verbose
    ? generateReport(violationSummary)
    : generateCompactSummary(violationSummary);

  return {
    passed: totalViolations === 0,
    blocked,
    level1,
    level2,
    level3,
    totalViolations,
    summary,
    totalTime,
    report,
  };
}

/**
 * Generate JSON report (for machine consumption)
 *
 * @param result - TRUST verification result
 * @returns JSON string
 */
export function generateJSONReport(
  result: TRUSTVerificationResult
): string {
  return JSON.stringify(
    {
      passed: result.passed,
      blocked: result.blocked,
      totalViolations: result.totalViolations,
      summary: result.summary,
      totalTime: result.totalTime,
      levels: {
        level1: {
          passed: result.level1.passed,
          checks: result.level1.checks,
          criticalCount: result.level1.criticalCount,
          violationCount: result.level1.violations.length,
        },
        level2: {
          passed: result.level2.passed,
          checks: result.level2.checks,
          projectType: result.level2.projectType,
          criticalCount: result.level2.criticalCount,
          violationCount: result.level2.violations.length,
        },
        level3: {
          passed: result.level3.passed,
          checks: result.level3.checks,
          coveragePercent: result.level3.coveragePercent,
          avgComplexity: result.level3.avgComplexity,
          securityIssues: result.level3.securityIssues,
          tagViolations: result.level3.tagViolations,
          criticalCount: result.level3.criticalCount,
          violationCount: result.level3.violations.length,
        },
      },
      violations: {
        CRITICAL: result.level1.violations
          .concat(result.level2.violations, result.level3.violations)
          .filter((v) => v.level === 'CRITICAL')
          .map((v) => ({
            level: v.level,
            category: v.category,
            message: v.message,
            file: v.file,
            line: v.line,
            fixCommand: v.fixCommand,
          })),
        HIGH: result.level1.violations
          .concat(result.level2.violations, result.level3.violations)
          .filter((v) => v.level === 'HIGH')
          .map((v) => ({
            level: v.level,
            category: v.category,
            message: v.message,
            file: v.file,
            line: v.line,
            fixCommand: v.fixCommand,
          })),
      },
    },
    null,
    2
  );
}

/**
 * Generate markdown report file
 *
 * @param result - TRUST verification result
 * @param outputPath - Output file path
 */
export async function saveReportToFile(
  result: TRUSTVerificationResult & { report: string },
  outputPath: string
): Promise<void> {
  const fs = await import('fs/promises');
  await fs.writeFile(outputPath, result.report, 'utf-8');
}
