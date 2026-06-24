---
description: "Merge open PR → release: gh pr merge → master pull → tag + GitHub Release. (Delegated to Antigravity)"
argument-hint: "[version] [--no-release]"
---

# /ms.merglease - Merge & Release (Delegated)

Delegate the PR merging, master pull, conventional version proposal, tagging, and GitHub Release creation to the **Google Antigravity CLI**.

## Execution Steps

### Step 1: 🚀 Delegate Merge & Release Pipeline to Antigravity

Invoke Google Antigravity to perform the entire merge, checkout, tagging, and release creation process:

```text
/antigravity:rescue --fresh --model gemini-2.5-pro --effort medium <Prompt>
```

#### Antigravity Prompt:
```text
You are running the SPECTER /ms.merglease merge and release pipeline.

Tasks to execute:
1. Pre-flight checks:
   - Verify that 'gh' CLI is installed and authenticated.
   - Check that the current branch is a feature branch (not master/main) and has an open PR.
   - Check CI status on the PR and warn if failing.
2. PR Merge:
   - Propose the merge strategy (default: merge commit) and confirm with the user.
   - Run 'gh pr merge <PR_NUM> --merge --delete-branch=false'.
3. Checkout master & Pull:
   - Run 'git checkout master && git pull --ff-only origin master'.
4. Version Proposal & Release Notes:
   - Read the last git tag, calculate the next version based on conventional commits since the tag.
   - Generate release notes draft and save it to a temporary file.
   - Propose version and display notes preview.
5. Create and Push Tag:
   - Create an annotated git tag for the new version and push it to origin.
6. Create GitHub Release:
   - Create a GitHub Release using the 'gh release create' command.
7. Branch cleanup (if requested).

Write your results, including the PR merge status, new tag, and release URL clearly in your final report.
```

---

### Step 2: Report Success

Claude summarizes the work:

```text
✅ /ms.merglease 완료! (Antigravity 위임 완료)

🔀 PR 머지 및 릴리즈 태그 생성이 Antigravity CLI를 통해 백그라운드/서브세션에서 성공적으로 처리되었습니다.
```
