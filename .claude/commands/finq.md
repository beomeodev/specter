---
description: "Quick finish: sync docs → update daily log → commit → push → PR auto-create (NO CI checks) (Delegated to Antigravity)"
argument-hint: ""
---

# /finq - Quick Finish Workflow (Delegated)

Sync living docs and update the daily log locally, then delegate staging, committing, pushing, and GitHub PR creation to the **Google Antigravity CLI** (skipping local CI checks).

## Execution Steps

### Step 1: 📄 Sync Living Documents (/ms.up-docs)

Claude Code runs the document synchronization locally to ensure staged documentation is up to date:

```bash
/ms.up-docs --docs=dev
```

---

### Step 2: 🚀 Delegate Quick Publish & PR Pipeline to Antigravity

Invoke Google Antigravity to stage files, commit with conventional messages, push the branch, and manage the GitHub pull request in the background:

```text
/antigravity:rescue --fresh --model gemini-2.5-pro --effort medium <Prompt>
```

#### Antigravity Prompt:
```text
You are running the SPECTER /finq quick publish pipeline.

Tasks to execute:
1. Stage and Commit (CI skipped):
   - Review changed files and build an explicit staging list (do not run 'git add .').
   - Stage the features, tests, docs, and configurations related to the current feature.
   - Format staged files using pre-commit hooks (if configured).
   - Generate a meaningful conventional commit message (feat/fix/chore/docs/test/wip).
   - Execute git commit.
2. Push:
   - Push the committed branch to origin.
3. PR Auto-create:
   - Auto-detect the latest docs/PR_*_BODY.md file.
   - Use 'gh' CLI to create a new PR or edit the body if one already exists.
   - Output the PR URL.

Do not edit code files except staging and formatting. Write your results and the PR URL clearly in your final report.
```

---

### Step 3: Report Success

Claude summarizes the work:

```text
✅ /finq 완료! (Antigravity 위임 완료 - CI 생략)

📄 Living Documents 동기화 완료 (/ms.up-docs)
💾 Git 커밋, Push 및 PR 자동 생성이 Antigravity CLI를 통해 백그라운드/서브세션에서 완료되었습니다.

⚠️ CI 체크를 생략했습니다. 머지 전에 반드시:
   1. '/fin' 또는 'make ci' 로 검증
   2. GitHub Actions 결과 확인
```
