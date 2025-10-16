/**
 * TRUST Level 1: Structure Verification
 *
 * Checks fundamental project structure requirements:
 * - Tests directory exists
 * - .env files are in .gitignore
 * - File sizes ≤500 SLOC
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { execSync } from 'child_process';
import type { Level1Result, FileSizeCheck } from './types';
import type { Violation } from '../tag/types';

/**
 * File size limit (SLOC)
 */
const MAX_FILE_SLOC = 500;

/**
 * Extensions to check for file size
 */
const CODE_EXTENSIONS = [
  '.ts',
  '.tsx',
  '.js',
  '.jsx',
  '.py',
  '.java',
  '.go',
  '.rs',
  '.c',
  '.cpp',
  '.h',
  '.hpp',
];

/**
 * Count Source Lines of Code (SLOC)
 * Excludes empty lines and comment-only lines
 *
 * @param filePath - File to count
 * @returns Number of source lines
 */
async function countSLOC(filePath: string): Promise<number> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    const lines = content.split('\n');

    let sloc = 0;
    let inBlockComment = false;

    for (let line of lines) {
      line = line.trim();

      // Skip empty lines
      if (line === '') continue;

      // Handle block comments (/* */ or """ """)
      if (line.startsWith('/*') || line.startsWith('"""') || line.startsWith("'''")) {
        inBlockComment = true;
      }

      if (inBlockComment) {
        if (line.endsWith('*/') || line.endsWith('"""') || line.endsWith("'''")) {
          inBlockComment = false;
        }
        continue;
      }

      // Skip single-line comments
      if (line.startsWith('//') || line.startsWith('#')) {
        continue;
      }

      sloc++;
    }

    return sloc;
  } catch {
    return 0;
  }
}

/**
 * Check if directory exists
 */
async function directoryExists(dirPath: string): Promise<boolean> {
  try {
    const stats = await fs.stat(dirPath);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Check if file exists
 */
async function fileExists(filePath: string): Promise<boolean> {
  try {
    const stats = await fs.stat(filePath);
    return stats.isFile();
  } catch {
    return false;
  }
}

/**
 * Find all code files in directory (recursive)
 */
async function findCodeFiles(dir: string, files: string[] = []): Promise<string[]> {
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      // Skip common directories
      if (
        entry.isDirectory() &&
        !['node_modules', '.git', 'dist', 'build', '__pycache__', '.venv', 'venv'].includes(
          entry.name
        )
      ) {
        await findCodeFiles(fullPath, files);
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name);
        if (CODE_EXTENSIONS.includes(ext)) {
          files.push(fullPath);
        }
      }
    }

    return files;
  } catch {
    return files;
  }
}

/**
 * Check if .env is in .gitignore
 */
async function checkGitignoreEnv(rootPath: string): Promise<boolean> {
  const gitignorePath = path.join(rootPath, '.gitignore');

  if (!(await fileExists(gitignorePath))) {
    return false;
  }

  try {
    const content = await fs.readFile(gitignorePath, 'utf-8');
    const lines = content.split('\n').map((l) => l.trim());

    // Check for .env patterns
    return lines.some(
      (line) => line === '.env' || line === '.env*' || line === '*.env' || line.includes('.env')
    );
  } catch {
    return false;
  }
}

/**
 * Check file sizes
 */
async function checkFileSizes(rootPath: string): Promise<FileSizeCheck[]> {
  const files = await findCodeFiles(rootPath);
  const results: FileSizeCheck[] = [];

  for (const file of files) {
    const sloc = await countSLOC(file);
    results.push({
      file: path.relative(rootPath, file),
      lines: sloc,
      exceeds: sloc > MAX_FILE_SLOC,
      limit: MAX_FILE_SLOC,
    });
  }

  return results;
}

/**
 * Run TRUST Level 1 checks (Structure)
 *
 * @param rootPath - Project root path
 * @returns Level 1 verification result
 *
 * @example
 * await runLevel1Checks('/project/root')
 * // => {
 * //   passed: false,
 * //   violations: [...],
 * //   criticalCount: 1,
 * //   checks: { testsDirectory: false, gitignoreEnv: true, fileSizes: true }
 * // }
 */
export async function runLevel1Checks(rootPath: string = '.'): Promise<Level1Result> {
  const startTime = Date.now();
  const violations: Violation[] = [];

  // Check 1: Tests directory exists (CRITICAL)
  const testsExist =
    (await directoryExists(path.join(rootPath, 'tests'))) ||
    (await directoryExists(path.join(rootPath, 'test'))) ||
    (await directoryExists(path.join(rootPath, '__tests__')));

  if (!testsExist) {
    violations.push({
      level: 'CRITICAL',
      category: 'Structure',
      message: 'Tests directory not found (tests/, test/, or __tests__/)',
      fixCommand: 'mkdir tests',
    });
  }

  // Check 2: .env in .gitignore (CRITICAL for security)
  const gitignoreEnvOk = await checkGitignoreEnv(rootPath);
  if (!gitignoreEnvOk) {
    violations.push({
      level: 'CRITICAL',
      category: 'Security',
      message: '.env files not excluded in .gitignore',
      fixCommand: 'echo ".env" >> .gitignore',
    });
  }

  // Check 3: File sizes ≤500 SLOC (MEDIUM)
  const fileSizeChecks = await checkFileSizes(rootPath);
  const oversizedFiles = fileSizeChecks.filter((f) => f.exceeds);

  for (const file of oversizedFiles) {
    violations.push({
      level: 'MEDIUM',
      category: 'File Size',
      message: `File ${file.file} exceeds ${MAX_FILE_SLOC} SLOC (${file.lines} lines)`,
      file: file.file,
      fixCommand: `Refactor ${file.file} into smaller modules`,
    });
  }

  const executionTime = Date.now() - startTime;
  const criticalCount = violations.filter((v) => v.level === 'CRITICAL').length;

  return {
    passed: violations.length === 0,
    violations,
    criticalCount,
    checks: {
      testsDirectory: testsExist,
      gitignoreEnv: gitignoreEnvOk,
      fileSizes: oversizedFiles.length === 0,
    },
    executionTime,
  };
}

/**
 * Get file size statistics
 */
export async function getFileSizeStats(
  rootPath: string = '.'
): Promise<{
  total: number;
  avgSLOC: number;
  maxSLOC: number;
  minSLOC: number;
  oversized: number;
}> {
  const fileSizeChecks = await checkFileSizes(rootPath);

  if (fileSizeChecks.length === 0) {
    return {
      total: 0,
      avgSLOC: 0,
      maxSLOC: 0,
      minSLOC: 0,
      oversized: 0,
    };
  }

  const slocs = fileSizeChecks.map((f) => f.lines);
  const total = fileSizeChecks.length;
  const avgSLOC = Math.round(slocs.reduce((a, b) => a + b, 0) / total);
  const maxSLOC = Math.max(...slocs);
  const minSLOC = Math.min(...slocs);
  const oversized = fileSizeChecks.filter((f) => f.exceeds).length;

  return {
    total,
    avgSLOC,
    maxSLOC,
    minSLOC,
    oversized,
  };
}
