/**
 * TRUST Level 3: Deep Analysis
 *
 * Performs comprehensive quality checks:
 * - Code coverage ≥85%
 * - Complexity ≤10 per function
 * - Circular dependency detection (madge / pydeps)
 * - Security scan (npm audit / pip-audit)
 * - TAG integrity (integrated with TAG validator)
 */

import { execSync } from 'child_process';
import type { Level3Result, ComplexityCheck, SecurityVulnerability, CoverageReport } from './types';
import type { Violation } from '../tag/types';
import { detectProjectType } from './level2';
import { validateTAGIntegrity } from '../tag/validator';

/**
 * Coverage threshold
 */
const MIN_COVERAGE = 85;

/**
 * Complexity threshold
 */
const MAX_COMPLEXITY = 10;

/**
 * Extract coverage from TypeScript/JavaScript output (Jest/c8/nyc)
 */
function extractTypescriptCoverage(output: string): CoverageReport | null {
  // Try to parse Jest/c8/nyc coverage output
  // Format: "All files | 87.5 | 82.3 | 91.2 | 87.5"
  const coverageMatch = output.match(/All files\s*\|\s*(\d+\.?\d*)/);
  if (coverageMatch) {
    return {
      overall: parseFloat(coverageMatch[1]),
    };
  }

  // Try percentage format: "Coverage: 87.5%"
  const percentMatch = output.match(/Coverage:\s*(\d+\.?\d*)%/i);
  if (percentMatch) {
    return {
      overall: parseFloat(percentMatch[1]),
    };
  }

  return null;
}

/**
 * Extract coverage from Python output (pytest-cov/coverage.py)
 */
function extractPythonCoverage(output: string): CoverageReport | null {
  // Format: "TOTAL  1234  987  80%"
  const coverageMatch = output.match(/TOTAL\s+\d+\s+\d+\s+(\d+)%/);
  if (coverageMatch) {
    return {
      overall: parseFloat(coverageMatch[1]),
    };
  }

  return null;
}

/**
 * Get code coverage
 */
async function getCoverage(rootPath: string, projectType: string): Promise<{
  success: boolean;
  coverage?: CoverageReport;
  output: string;
}> {
  try {
    let output: string;
    let coverage: CoverageReport | null = null;

    if (projectType === 'typescript') {
      // Try Jest with coverage
      try {
        output = execSync('npm test -- --coverage --coverageReporters=text', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 120000,
        });
      } catch {
        // Try c8
        output = execSync('npx c8 npm test', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 120000,
        });
      }

      coverage = extractTypescriptCoverage(output);
    } else if (projectType === 'python') {
      // Try pytest with coverage
      try {
        output = execSync('pytest --cov=. --cov-report=term', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 120000,
        });
      } catch {
        // Try coverage.py
        output = execSync('coverage run -m pytest && coverage report', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 120000,
        });
      }

      coverage = extractPythonCoverage(output);
    } else {
      return { success: true, output: 'Coverage not checked (unsupported project type)' };
    }

    return {
      success: true,
      coverage: coverage || undefined,
      output,
    };
  } catch (error: any) {
    return {
      success: false,
      output: error.stdout || error.stderr || error.message,
    };
  }
}

/**
 * Get code complexity (simplified - full implementation would use complexity tools)
 */
async function getComplexity(rootPath: string, projectType: string): Promise<{
  success: boolean;
  avgComplexity?: number;
  violations: ComplexityCheck[];
  output: string;
}> {
  try {
    let output: string;
    const violations: ComplexityCheck[] = [];

    if (projectType === 'typescript') {
      // Try eslint with complexity rules
      try {
        output = execSync('npx eslint . --rule "complexity: [error, 10]"', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });
      } catch (error: any) {
        output = error.stdout || error.stderr || error.message;
      }
    } else if (projectType === 'python') {
      // Try radon for cyclomatic complexity
      try {
        output = execSync('radon cc . -a', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });
      } catch (error: any) {
        output = error.stdout || error.stderr || error.message;
      }
    } else {
      return {
        success: true,
        violations: [],
        output: 'Complexity not checked (unsupported project type)',
      };
    }

    // Parse output for complexity violations (simplified)
    const complexityMatches = output.match(/complexity of (\d+)/gi) || [];
    let totalComplexity = 0;
    let count = 0;

    for (const match of complexityMatches) {
      const complexity = parseInt(match.match(/\d+/)![0], 10);
      totalComplexity += complexity;
      count++;

      if (complexity > MAX_COMPLEXITY) {
        violations.push({
          file: 'unknown',
          function: 'unknown',
          complexity,
          exceeds: true,
          limit: MAX_COMPLEXITY,
        });
      }
    }

    const avgComplexity = count > 0 ? Math.round(totalComplexity / count) : 0;

    return {
      success: violations.length === 0,
      avgComplexity,
      violations,
      output,
    };
  } catch (error: any) {
    return {
      success: false,
      violations: [],
      output: error.message,
    };
  }
}

/**
 * Check for circular dependencies
 */
async function checkCircularDependencies(rootPath: string, projectType: string): Promise<{
  success: boolean;
  circularDeps: Array<{ cycle: string[]; description: string }>;
  output: string;
}> {
  try {
    let output: string;
    const circularDeps: Array<{ cycle: string[]; description: string }> = [];

    if (projectType === 'typescript') {
      // Use madge to detect circular dependencies
      try {
        output = execSync('npx madge --circular --json src/', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });

        // Parse JSON output
        try {
          const cycles = JSON.parse(output);
          if (Array.isArray(cycles) && cycles.length > 0) {
            for (const cycle of cycles) {
              circularDeps.push({
                cycle: Array.isArray(cycle) ? cycle : [],
                description: Array.isArray(cycle) ? cycle.join(' → ') : String(cycle),
              });
            }
          }
        } catch {
          // If not JSON, check for text output
          if (output.includes('Circular') || output.includes('cycle')) {
            circularDeps.push({
              cycle: [],
              description: 'Circular dependencies detected (see output)',
            });
          }
        }
      } catch (error: any) {
        output = error.stdout || error.stderr || error.message;
        // Exit code 0 means no cycles, non-zero might mean cycles or error
        if (error.status !== 0 && output.includes('circular')) {
          circularDeps.push({
            cycle: [],
            description: 'Circular dependencies detected',
          });
        }
      }
    } else if (projectType === 'python') {
      // Use pydeps to detect circular dependencies
      try {
        output = execSync('pydeps --show-cycles --max-bacon=3 .', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });

        // Check for cycle indicators in output
        const cycleMatches = output.match(/\*\*\* .* \*\*\*/g);
        if (cycleMatches && cycleMatches.length > 0) {
          for (const match of cycleMatches) {
            circularDeps.push({
              cycle: [],
              description: match.replace(/\*\*\*/g, '').trim(),
            });
          }
        }
      } catch (error: any) {
        output = error.stdout || error.stderr || error.message;
        // pydeps might return non-zero on cycles
        if (output.toLowerCase().includes('cycle') || output.toLowerCase().includes('circular')) {
          circularDeps.push({
            cycle: [],
            description: 'Circular dependencies detected',
          });
        }
      }
    } else {
      return {
        success: true,
        circularDeps: [],
        output: 'Circular dependency check not run (unsupported project type)',
      };
    }

    return {
      success: circularDeps.length === 0,
      circularDeps,
      output,
    };
  } catch (error: any) {
    return {
      success: false,
      circularDeps: [],
      output: error.message,
    };
  }
}

/**
 * Run security audit
 */
async function runSecurityAudit(rootPath: string, projectType: string): Promise<{
  success: boolean;
  vulnerabilities: SecurityVulnerability[];
  output: string;
}> {
  try {
    let output: string;
    const vulnerabilities: SecurityVulnerability[] = [];

    if (projectType === 'typescript') {
      // Run npm audit
      output = execSync('npm audit --json', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 60000,
      });

      // Parse JSON output
      try {
        const auditData = JSON.parse(output);
        const vulns = auditData.vulnerabilities || {};

        for (const [pkg, data] of Object.entries(vulns)) {
          vulnerabilities.push({
            package: pkg,
            severity: (data as any).severity || 'moderate',
            description: (data as any).title || 'Security vulnerability',
          });
        }
      } catch {
        // Failed to parse, count text occurrences
        const criticalCount = (output.match(/critical/gi) || []).length;
        const highCount = (output.match(/high/gi) || []).length;

        if (criticalCount > 0 || highCount > 0) {
          vulnerabilities.push({
            package: 'multiple',
            severity: 'high',
            description: `Found ${criticalCount} critical and ${highCount} high vulnerabilities`,
          });
        }
      }
    } else if (projectType === 'python') {
      // Run pip-audit
      try {
        output = execSync('pip-audit --json', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });

        const auditData = JSON.parse(output);
        for (const vuln of auditData.vulnerabilities || []) {
          vulnerabilities.push({
            package: vuln.package || 'unknown',
            severity: vuln.severity || 'moderate',
            description: vuln.description || 'Security vulnerability',
          });
        }
      } catch (error: any) {
        output = error.stdout || error.stderr || error.message;
      }
    } else {
      return {
        success: true,
        vulnerabilities: [],
        output: 'Security audit not run (unsupported project type)',
      };
    }

    return {
      success: vulnerabilities.length === 0,
      vulnerabilities,
      output,
    };
  } catch (error: any) {
    return {
      success: false,
      vulnerabilities: [],
      output: error.message,
    };
  }
}

/**
 * Run TRUST Level 3 checks (Deep Analysis + TAG Integration)
 *
 * @param rootPath - Project root path
 * @returns Level 3 verification result
 *
 * @example
 * await runLevel3Checks('/project/root')
 * // => {
 * //   passed: true,
 * //   violations: [],
 * //   criticalCount: 0,
 * //   checks: { coverage: true, complexity: true, circularDeps: true, security: true, tagIntegrity: true },
 * //   coveragePercent: 92.5,
 * //   avgComplexity: 6,
 * //   circularDepsCount: 0,
 * //   securityIssues: 0,
 * //   tagViolations: 0
 * // }
 */
export async function runLevel3Checks(rootPath: string = '.'): Promise<Level3Result> {
  const startTime = Date.now();
  const violations: Violation[] = [];

  // Detect project type
  const projectInfo = await detectProjectType(rootPath);
  const projectType = projectInfo.type;

  // Check 1: Code coverage ≥85% (HIGH)
  const coverageResult = await getCoverage(rootPath, projectType);
  const coveragePercent = coverageResult.coverage?.overall;

  if (coverageResult.success && coveragePercent !== undefined) {
    if (coveragePercent < MIN_COVERAGE) {
      violations.push({
        level: 'HIGH',
        category: 'Coverage',
        message: `Code coverage ${coveragePercent}% is below ${MIN_COVERAGE}%`,
        fixCommand: 'Add more tests to increase coverage',
      });
    }
  } else if (!coverageResult.success) {
    violations.push({
      level: 'MEDIUM',
      category: 'Coverage',
      message: 'Failed to measure code coverage',
    });
  }

  // Check 2: Complexity ≤10 per function (HIGH)
  const complexityResult = await getComplexity(rootPath, projectType);
  const avgComplexity = complexityResult.avgComplexity;

  for (const violation of complexityResult.violations) {
    violations.push({
      level: 'HIGH',
      category: 'Complexity',
      message: `Function "${violation.function}" in ${violation.file} has complexity ${violation.complexity} (limit: ${MAX_COMPLEXITY})`,
      file: violation.file,
      fixCommand: 'Refactor function to reduce complexity',
    });
  }

  // Check 3: Circular dependencies (HIGH)
  const circularResult = await checkCircularDependencies(rootPath, projectType);

  for (const circularDep of circularResult.circularDeps) {
    violations.push({
      level: 'HIGH',
      category: 'Architecture',
      message: `Circular dependency detected: ${circularDep.description}`,
      fixCommand: 'Refactor to remove circular dependency',
    });
  }

  // Check 4: Security audit (MEDIUM for vulnerabilities, CRITICAL for critical CVEs)
  const securityResult = await runSecurityAudit(rootPath, projectType);

  for (const vuln of securityResult.vulnerabilities) {
    const level = vuln.severity === 'critical' ? 'CRITICAL' : vuln.severity === 'high' ? 'HIGH' : 'MEDIUM';

    violations.push({
      level,
      category: 'Security',
      message: `${vuln.severity.toUpperCase()} vulnerability in ${vuln.package}: ${vuln.description}`,
      fixCommand: vuln.fix || 'Update vulnerable package',
    });
  }

  // Check 5: TAG integrity (CRITICAL for orphans/duplicates)
  const tagResult = await validateTAGIntegrity(rootPath);

  // Add TAG violations (CRITICAL and HIGH only for Level 3)
  for (const violation of tagResult.violations) {
    if (violation.level === 'CRITICAL' || violation.level === 'HIGH') {
      violations.push(violation);
    }
  }

  const executionTime = Date.now() - startTime;
  const criticalCount = violations.filter((v) => v.level === 'CRITICAL').length;

  return {
    passed: violations.length === 0,
    violations,
    criticalCount,
    checks: {
      coverage: coveragePercent !== undefined && coveragePercent >= MIN_COVERAGE,
      complexity: complexityResult.violations.length === 0,
      circularDeps: circularResult.circularDeps.length === 0,
      security: securityResult.vulnerabilities.length === 0,
      tagIntegrity: tagResult.passed,
    },
    coveragePercent,
    avgComplexity,
    circularDepsCount: circularResult.circularDeps.length,
    securityIssues: securityResult.vulnerabilities.length,
    tagViolations: tagResult.violations.length,
    executionTime,
  };
}
