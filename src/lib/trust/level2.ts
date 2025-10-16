/**
 * TRUST Level 2: Quality Verification
 *
 * Checks code quality requirements:
 * - Tests pass successfully
 * - Linting zero warnings
 * - Type checking passes
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { execSync } from 'child_process';
import type { Level2Result, ProjectTypeInfo } from './types';
import type { Violation } from '../tag/types';

/**
 * Detect project type from config files
 *
 * @param rootPath - Project root path
 * @returns Project type information
 */
export async function detectProjectType(rootPath: string = '.'): Promise<ProjectTypeInfo> {
  const checks = [
    {
      type: 'typescript' as const,
      files: ['package.json', 'tsconfig.json'],
      packageManagers: ['npm', 'yarn', 'pnpm'] as const,
    },
    {
      type: 'python' as const,
      files: ['setup.py', 'pyproject.toml', 'requirements.txt'],
      packageManagers: ['pip', 'poetry'] as const,
    },
    {
      type: 'go' as const,
      files: ['go.mod'],
      packageManagers: [] as const,
    },
    {
      type: 'rust' as const,
      files: ['Cargo.toml'],
      packageManagers: ['cargo'] as const,
    },
    {
      type: 'java' as const,
      files: ['pom.xml', 'build.gradle', 'build.gradle.kts'],
      packageManagers: ['maven', 'gradle'] as const,
    },
  ];

  for (const check of checks) {
    for (const file of check.files) {
      try {
        const filePath = path.join(rootPath, file);
        await fs.stat(filePath);

        // File exists, determine package manager
        let packageManager: typeof check.packageManagers[number] | undefined;

        if (check.type === 'typescript') {
          if (await fileExists(path.join(rootPath, 'yarn.lock'))) {
            packageManager = 'yarn';
          } else if (await fileExists(path.join(rootPath, 'pnpm-lock.yaml'))) {
            packageManager = 'pnpm';
          } else {
            packageManager = 'npm';
          }
        } else if (check.type === 'python') {
          if (await fileExists(path.join(rootPath, 'poetry.lock'))) {
            packageManager = 'poetry';
          } else {
            packageManager = 'pip';
          }
        } else if (check.type === 'rust') {
          packageManager = 'cargo';
        } else if (check.type === 'java') {
          if (file.includes('gradle')) {
            packageManager = 'gradle';
          } else {
            packageManager = 'maven';
          }
        }

        return {
          type: check.type,
          confidence: 1.0,
          packageManager,
          configFile: file,
        };
      } catch {
        // File doesn't exist, continue
      }
    }
  }

  return {
    type: 'unknown',
    confidence: 0,
  };
}

/**
 * Check if file exists
 */
async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.stat(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Run TypeScript project tests
 */
async function runTypescriptTests(rootPath: string): Promise<{
  success: boolean;
  output: string;
}> {
  try {
    // Try npm test first
    const output = execSync('npm test', {
      cwd: rootPath,
      encoding: 'utf-8',
      stdio: 'pipe',
      timeout: 120000, // 2 minutes timeout
    });

    return { success: true, output };
  } catch (error: any) {
    return {
      success: false,
      output: error.stdout || error.stderr || error.message,
    };
  }
}

/**
 * Run Python project tests
 */
async function runPythonTests(rootPath: string): Promise<{
  success: boolean;
  output: string;
}> {
  try {
    // Try pytest first, then unittest
    let output: string;
    try {
      output = execSync('pytest', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 120000,
      });
    } catch {
      output = execSync('python -m unittest discover', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 120000,
      });
    }

    return { success: true, output };
  } catch (error: any) {
    return {
      success: false,
      output: error.stdout || error.stderr || error.message,
    };
  }
}

/**
 * Run linting checks
 */
async function runLintChecks(
  rootPath: string,
  projectType: ProjectTypeInfo
): Promise<{
  success: boolean;
  warnings: number;
  output: string;
}> {
  try {
    let output: string;

    if (projectType.type === 'typescript') {
      // Try ESLint
      output = execSync('npx eslint . --max-warnings=0', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 60000,
      });
    } else if (projectType.type === 'python') {
      // Try flake8 or pylint
      try {
        output = execSync('flake8 .', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });
      } catch {
        output = execSync('pylint **/*.py', {
          cwd: rootPath,
          encoding: 'utf-8',
          stdio: 'pipe',
          timeout: 60000,
        });
      }
    } else {
      return { success: true, warnings: 0, output: 'No linter configured' };
    }

    // Count warnings in output
    const warnings = (output.match(/warning/gi) || []).length;

    return {
      success: warnings === 0,
      warnings,
      output,
    };
  } catch (error: any) {
    const output = error.stdout || error.stderr || error.message;
    const warnings = (output.match(/warning/gi) || []).length;

    return {
      success: false,
      warnings,
      output,
    };
  }
}

/**
 * Run type checking
 */
async function runTypeChecks(
  rootPath: string,
  projectType: ProjectTypeInfo
): Promise<{
  success: boolean;
  errors: number;
  output: string;
}> {
  try {
    let output: string;

    if (projectType.type === 'typescript') {
      // Run tsc --noEmit
      output = execSync('npx tsc --noEmit', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 60000,
      });
    } else if (projectType.type === 'python') {
      // Try mypy
      output = execSync('mypy .', {
        cwd: rootPath,
        encoding: 'utf-8',
        stdio: 'pipe',
        timeout: 60000,
      });
    } else {
      return { success: true, errors: 0, output: 'No type checker configured' };
    }

    return { success: true, errors: 0, output };
  } catch (error: any) {
    const output = error.stdout || error.stderr || error.message;
    const errors = (output.match(/error/gi) || []).length;

    return {
      success: false,
      errors,
      output,
    };
  }
}

/**
 * Run TRUST Level 2 checks (Quality)
 *
 * @param rootPath - Project root path
 * @returns Level 2 verification result
 *
 * @example
 * await runLevel2Checks('/project/root')
 * // => {
 * //   passed: true,
 * //   violations: [],
 * //   criticalCount: 0,
 * //   checks: { testsPass: true, lintPass: true, typeCheckPass: true },
 * //   projectType: 'typescript'
 * // }
 */
export async function runLevel2Checks(rootPath: string = '.'): Promise<Level2Result> {
  const startTime = Date.now();
  const violations: Violation[] = [];

  // Detect project type
  const projectInfo = await detectProjectType(rootPath);

  if (projectInfo.type === 'unknown') {
    violations.push({
      level: 'HIGH',
      category: 'Project Type',
      message: 'Unable to detect project type (no package.json, setup.py, etc.)',
    });

    return {
      passed: false,
      violations,
      criticalCount: 0,
      checks: {
        testsPass: false,
        lintPass: false,
        typeCheckPass: false,
      },
      projectType: 'unknown',
      executionTime: Date.now() - startTime,
    };
  }

  // Check 1: Tests pass (CRITICAL)
  let testsPass = false;
  if (projectInfo.type === 'typescript') {
    const testResult = await runTypescriptTests(rootPath);
    testsPass = testResult.success;

    if (!testsPass) {
      violations.push({
        level: 'CRITICAL',
        category: 'Tests',
        message: 'Tests failed to pass',
        fixCommand: 'npm test',
      });
    }
  } else if (projectInfo.type === 'python') {
    const testResult = await runPythonTests(rootPath);
    testsPass = testResult.success;

    if (!testsPass) {
      violations.push({
        level: 'CRITICAL',
        category: 'Tests',
        message: 'Tests failed to pass',
        fixCommand: 'pytest',
      });
    }
  }

  // Check 2: Linting zero warnings (CRITICAL)
  const lintResult = await runLintChecks(rootPath, projectInfo);
  if (!lintResult.success || lintResult.warnings > 0) {
    violations.push({
      level: 'CRITICAL',
      category: 'Linting',
      message: `Linting failed with ${lintResult.warnings} warnings`,
      fixCommand: projectInfo.type === 'typescript' ? 'npx eslint . --fix' : 'flake8 .',
    });
  }

  // Check 3: Type checking passes (CRITICAL)
  const typeResult = await runTypeChecks(rootPath, projectInfo);
  if (!typeResult.success) {
    violations.push({
      level: 'CRITICAL',
      category: 'Type Checking',
      message: `Type checking failed with ${typeResult.errors} errors`,
      fixCommand: projectInfo.type === 'typescript' ? 'npx tsc --noEmit' : 'mypy .',
    });
  }

  const executionTime = Date.now() - startTime;
  const criticalCount = violations.filter((v) => v.level === 'CRITICAL').length;

  return {
    passed: violations.length === 0,
    violations,
    criticalCount,
    checks: {
      testsPass,
      lintPass: lintResult.success && lintResult.warnings === 0,
      typeCheckPass: typeResult.success,
    },
    projectType: projectInfo.type,
    executionTime,
  };
}
