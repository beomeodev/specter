---
description: "Finish workflow: sync docs → update daily log → CI checks → commit → push → PR auto-create (Delegated to Antigravity)"
argument-hint: ""
---

# /fin - Finish Workflow (Delegated)

Sync living docs and update the daily log locally, then delegate CI checks, staging, committing, pushing, and GitHub PR creation to the **Google Antigravity CLI**.

## Execution Steps

### Step 1: 📄 Sync Living Documents (/ms.up-docs)

Claude Code runs the document synchronization locally to ensure staged documentation is up to date:

```bash
/ms.up-docs --docs=dev
```

This updates `docs/dev_daily.md` and API specifications based on staged files.

---

### Step 2: 🚀 Delegate Publish & PR Pipeline to Antigravity

Invoke Google Antigravity to run local CI checks, stage files, commit with conventional messages, push the branch, and manage the GitHub pull request:

```text
/antigravity:rescue --fresh --model gemini-3.5-flash --effort medium <Prompt>
```

#### Antigravity Prompt:
```text
You are running the SPECTER /fin publish pipeline.

Tasks to execute:
1. Run local CI checks:
   - Check if .specify/review-state.txt exists and print its warning context.
   - Run locally-runnable gates (lint -> types -> tests -> build) using the project's default runner (e.g., 'make ci' or test commands).
   - If any check fails, STOP immediately and report the failure.
2. Stage and Commit:
   - Review changed files and build an explicit staging list (do not run 'git add .').
   - Stage the features, tests, docs, and configurations related to the current feature.
   - Format staged files using pre-commit hooks (if configured).
   - Generate a meaningful conventional commit message (feat/fix/chore/docs/test).
   - Execute git commit.
3. Push:
   - Push the committed branch to origin.
4. PR Auto-create:
   - Auto-detect the latest docs/PR_*_BODY.md file.
   - Use 'gh' CLI to create a new PR or edit the body if one already exists.
   - Output the PR URL.

Do not edit code files except staging and formatting. Write your results and the PR URL clearly in your final report.
```

---

### Step 3: Report Success

Claude summarizes the work:

```text
✅ /fin 완료! (Antigravity 위임 완료)

📄 Living Documents 동기화 완료 (/ms.up-docs)
🚀 CI 체크, Git 커밋, Push 및 PR 자동 생성이 Antigravity CLI를 통해 백그라운드/서브세션에서 처리되었습니다.

📋 다음 단계:
  1. 제공된 PR URL에서 결과 검토 (수동)
  2. (feature 브랜치에서) /ms.merglease  (PR 머지 + tag + release 발행)
```
