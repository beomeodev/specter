# My-Spec Helper Libraries

TypeScript helper libraries for TAG system management and TRUST verification.

## 📦 Installation

```bash
# Install dependencies
npm install

# Build TypeScript to JavaScript
npm run build
```

This compiles TypeScript files from `src/` to `dist/`.

## 🏷️ TAG System

### Features

- **Automatic TAG ID generation** with domain extraction
- **ripgrep-based TAG scanning** (blazing fast)
- **TAG integrity validation** (orphaned TAGs, duplicates, broken chains)
- **MoAI-style TAG blocks** with CHAIN and @IMMUTABLE support
- **@IMMUTABLE protection** via Claude Code hooks

### Usage Examples

#### Generate TAG IDs

```typescript
import { TAG } from './index';

// Extract domain from FR title
const domainResult = TAG.extractDomain('User Authentication', 'FR-1');
// => { domain: 'AUTH', confidence: 1.0, matchedKeyword: 'authentication', fallback: false }

// Count existing TAGs for this domain
const count = await TAG.countTAGsForDomain('AUTH');
// => 5 (AUTH-001 to AUTH-005 exist)

// Generate next TAG ID
const newTagId = TAG.generateNextTAGID('AUTH', count);
// => 'AUTH-006'

// Generate TAG chain
const chain = TAG.generateTAGChain('AUTH-006');
// => '@SPEC:AUTH-006 → @TEST:AUTH-006 → @CODE:AUTH-006'
```

#### Generate MoAI-style TAG Blocks

```typescript
const tagBlock = TAG.generateTAGBlock('AUTH-001', 'SPEC', {
  immutable: true,
  chain: ['@SPEC:AUTH-001', '@TEST:AUTH-001', '@CODE:AUTH-001'],
  status: 'active',
});

console.log(tagBlock);
// /**
//  * @SPEC:AUTH-001
//  * CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
//  * DEPENDS: NONE
//  * STATUS: active
//  * CREATED: 2025-10-16
//  * @IMMUTABLE
//  */
```

#### Scan and Validate TAGs

```typescript
// Scan all TAGs in project
const allTags = await TAG.scanAllTAGs();
// => [
//   { id: 'AUTH-001', type: 'SPEC', file: 'specs/auth.md', line: 10 },
//   { id: 'AUTH-001', type: 'TEST', file: 'tests/auth.test.ts', line: 5 },
//   ...
// ]

// Find orphaned TAGs (CODE/TEST without SPEC)
const orphaned = await TAG.findOrphanedTAGs();
// => ['USER-005', 'PAY-003']

// Find duplicate TAGs
const duplicates = await TAG.findDuplicateTAGs();
// => Map { 'AUTH-001:SPEC' => [{ file: 'specs/a.md', line: 10 }, { file: 'specs/b.md', line: 15 }] }

// Validate complete TAG integrity
const validation = await TAG.validateTAGIntegrity();
// => {
//   passed: false,
//   blocked: true,
//   violations: [{ level: 'CRITICAL', category: 'Orphaned TAG', message: '...' }],
//   summary: { CRITICAL: 2, HIGH: 1, MEDIUM: 0, LOW: 0 }
// }

// Generate TAG integrity report
const report = await TAG.generateTAGIntegrityReport();
console.log(report);
// => Markdown report with all violations
```

#### Check Immutability (MoAI Extension)

```typescript
const oldContent = await fs.readFile('src/auth.ts', 'utf-8');
const newContent = '...'; // Modified content

const immutabilityCheck = await TAG.checkImmutability(
  'src/auth.ts',
  oldContent,
  newContent
);

if (immutabilityCheck.violated) {
  console.error('❌ @IMMUTABLE TAG was modified:', immutabilityCheck.modifiedTag);
  console.error('Details:', immutabilityCheck.violationDetails);
}
```

## ✅ TRUST Verification

### TRUST 5 Principles

- **T**est-First: TDD with passing tests
- **R**eadable: Clean, maintainable code
- **U**nified: Consistent structure and style
- **S**ecured: No security vulnerabilities
- **T**rackable: Complete TAG traceability

### Usage Examples

#### Run Complete TRUST Verification

```typescript
import { TRUST } from './index';

// Run all TRUST levels and generate report
const result = await TRUST.runTRUSTVerification('/project/root');

console.log(result.report);
// => Full markdown report

console.log('Passed:', result.passed);
console.log('Blocked:', result.blocked);
console.log('Summary:', result.summary);
// => { CRITICAL: 2, HIGH: 3, MEDIUM: 1, LOW: 0 }
```

#### Run Individual Levels

```typescript
// Level 1: Structure verification
const level1 = await TRUST.runLevel1Checks('/project/root');
// Checks:
// - tests/ directory exists
// - .env in .gitignore
// - File sizes ≤500 SLOC

// Level 2: Quality verification
const level2 = await TRUST.runLevel2Checks('/project/root');
// Checks:
// - Tests pass
// - Linting zero warnings
// - Type checking passes

// Level 3: Deep analysis
const level3 = await TRUST.runLevel3Checks('/project/root');
// Checks:
// - Coverage ≥85%
// - Complexity ≤10 per function
// - Security scan (npm audit / pip-audit)
// - TAG integrity (calls TAG validator)
```

#### Custom Reporting

```typescript
// Summarize violations
const summary = TRUST.summarizeViolations(level1, level2, level3);

// Generate full report
const fullReport = TRUST.generateReport(summary);

// Generate compact summary
const compactSummary = TRUST.generateCompactSummary(summary);

// Generate JSON report
const jsonReport = TRUST.generateJSONReport(result);

// Save to file
await TRUST.saveReportToFile(result, 'trust-report.md');
```

## 🛡️ Claude Code Hook (Optional)

### @IMMUTABLE TAG Protection

The TAG enforcer hook prevents modification of @IMMUTABLE TAG blocks.

#### Setup

1. Build TypeScript to JavaScript:
```bash
npm run build
```

2. The hook is already configured in `.claude/settings.local.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "node $CLAUDE_PROJECT_DIR/.claude/hooks/tag-enforcer.js"
          }
        ]
      }
    ]
  }
}
```

3. Restart Claude Code or reload the project.

#### How It Works

- **PreToolUse hook** runs before Write/Edit/MultiEdit operations
- Checks if @IMMUTABLE TAG blocks are modified
- **Blocks file write** if violation detected
- Shows helpful error message with fix suggestions

#### Example

```typescript
// Original file (src/auth.ts)
/**
 * @SPEC:AUTH-001
 * CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-001
 * STATUS: active
 * CREATED: 2025-10-15
 * @IMMUTABLE
 */
export function authenticate() { ... }

// Try to modify @IMMUTABLE block → BLOCKED! ❌
/**
 * @SPEC:AUTH-001
 * CHAIN: @SPEC:AUTH-001 -> @TEST:AUTH-001 -> @CODE:AUTH-002  // Changed!
 * STATUS: active
 * CREATED: 2025-10-15
 * @IMMUTABLE
 */

// Error message:
// 🚫 @IMMUTABLE TAG Modification Detected
// TAG AUTH-001 is marked as @IMMUTABLE and cannot be modified.
// ...
```

## 📁 Project Structure

```
src/
├── lib/
│   ├── tag/
│   │   ├── types.ts          # TAG type definitions
│   │   ├── generator.ts      # TAG ID generation + MoAI blocks
│   │   ├── scanner.ts        # ripgrep-based scanning + chains
│   │   ├── validator.ts      # Integrity + immutability validation
│   │   └── index.ts          # Unified export
│   └── trust/
│       ├── types.ts          # TRUST type definitions
│       ├── level1.ts         # Structure verification
│       ├── level2.ts         # Quality verification
│       ├── level3.ts         # Deep analysis + TAG integration
│       ├── reporter.ts       # Report generation
│       └── index.ts          # Unified export
├── index.ts                  # Main entry point
└── README.md                 # This file

.claude/
├── hooks/
│   └── tag-enforcer.ts       # @IMMUTABLE protection hook
└── settings.local.json       # Hook configuration

dist/                         # Compiled JavaScript (auto-generated)
```

## 🚀 Quick Start

### For My-Spec Commands

The helpers are designed to be called from `.claude/commands/ms.*.md` commands:

#### Example: `/ms.tasks` command

```markdown
### 2. TAG ID Generation

For each Functional Requirement (FR) in spec.md:

**Extract Domain**:
- Use `TAG.extractDomain(frTitle, frNumber)`
- Match against domain keywords: AUTH, USER, PAY, CART, etc.

**Count Existing TAGs**:
- Use `TAG.countTAGsForDomain(domain)`

**Generate TAG ID**:
- Use `TAG.generateNextTAGID(domain, count)`
- Format: `{DOMAIN}-{count+1:03d}`
```

#### Example: `/ms.analyze` command

```markdown
### TRUST Verification

Run complete TRUST verification:

```bash
# Run TRUST verification
node -e "
  const { TRUST } = require('./dist/index');
  (async () => {
    const result = await TRUST.runTRUSTVerification('.');
    console.log(result.report);
    process.exit(result.blocked ? 1 : 0);
  })();
"
```

If CRITICAL violations found → Block execution
```

## 🔧 Development

### Build

```bash
npm run build        # Compile TypeScript
npm run build:watch  # Watch mode
```

### Testing

```bash
# Test TAG scanner (requires ripgrep)
node -e "
  const { TAG } = require('./dist/index');
  (async () => {
    const tags = await TAG.scanAllTAGs('.');
    console.log('Found', tags.length, 'TAGs');
  })();
"

# Test TRUST verification
node -e "
  const { TRUST } = require('./dist/index');
  (async () => {
    const result = await TRUST.runTRUSTVerification('.');
    console.log(result.report);
  })();
"
```

## 📄 License

MIT

## 🙏 Credits

- **TAG System**: Inspired by [MoAI-ADK](https://github.com/modu-ai/moai-adk)
- **TRUST Principles**: My-Spec Constitution
- **ripgrep**: Fast TAG scanning powered by [ripgrep](https://github.com/BurntSushi/ripgrep)
