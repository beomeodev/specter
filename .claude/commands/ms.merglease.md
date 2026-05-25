---
description: "Merge open PR → release: gh pr merge → master pull → tag + GitHub Release. Successor to /fin and /finq."
---

# /ms.merglease — Merge + Release in one command

Post-`/fin` (or `/finq`) workflow: merge the open PR for the current branch, switch to master, and cut a tagged GitHub Release with auto-generated notes.

**Naming**: portmanteau of *merge* + *release*. Reads like "merge-lease" — merge it, then release it.

## Usage

```
/ms.merglease                      # auto: detect PR + propose version + confirm
/ms.merglease v0.21.0              # explicit version (skip the proposal step)
/ms.merglease --strategy=squash    # change merge strategy (default: merge)
/ms.merglease --no-release         # only merge, skip the release step
```

## Preconditions

1. `/fin` or `/finq` already ran (commits pushed, PR open).
2. `gh` CLI installed + authenticated (verified by `gh auth status`).
3. Current branch is a feature branch (not `master`) with an open PR.
4. The branch tracks `origin/<branch>` (push completed).

If any precondition fails: friendly Korean error + abort. No partial state.

## Execution sequence

```
1. Pre-flight checks       (gh installed + auth + open PR + CI status)
2. Decide merge strategy   (default: merge commit, matches project precedent)
3. Merge the PR            (gh pr merge --merge)
4. Switch to master + pull (verify the merge landed)
5. Propose version + notes (auto-generated, user confirms)
6. Tag + push tag          (annotated tag on the merge commit)
7. Create GitHub Release   (gh release create --notes-file ...)
8. Optional: cleanup       (delete merged feature branch locally + remote)
9. Report                  (PR URL, tag URL, release URL)
```

Steps 3, 6, 7 are destructive (visible to others / hard to reverse). Each is preceded by a clear summary + explicit confirmation prompt.

---

## Step 1. Pre-flight checks

```bash
# 1.1 gh CLI available + authenticated
if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh CLI 미설치. 호스트에서 설치: https://cli.github.com/"
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "❌ gh 인증 안 됨. 호스트에서: gh auth login --hostname github.com --git-protocol ssh --web"
  exit 1
fi

# 1.2 Current branch is NOT master
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "master" ] || [ "$BRANCH" = "main" ]; then
  echo "❌ 이미 master 에 있어요. /ms.merglease 는 feature 브랜치에서 호출해야 합니다."
  echo "   (PR 머지 후 release 만 다시 하려면 /ms.release 별도 명령을 만드세요.)"
  exit 1
fi

# 1.3 Open PR exists for current branch
if ! PR_JSON=$(gh pr view --json number,state,title,mergeable,statusCheckRollup 2>&1); then
  echo "❌ 현재 브랜치 ($BRANCH) 에 열린 PR이 없어요."
  echo "   먼저 /fin 또는 /finq 로 PR을 만드세요."
  exit 1
fi

PR_NUM=$(echo "$PR_JSON" | jq -r .number)
PR_STATE=$(echo "$PR_JSON" | jq -r .state)
PR_MERGEABLE=$(echo "$PR_JSON" | jq -r .mergeable)
PR_TITLE=$(echo "$PR_JSON" | jq -r .title)

if [ "$PR_STATE" != "OPEN" ]; then
  echo "❌ PR #${PR_NUM} 상태가 OPEN 이 아니에요 (현재: $PR_STATE)."
  exit 1
fi

# 1.4 CI status check (soft warn — operator can override)
FAILING_CHECKS=$(echo "$PR_JSON" | jq -r '
  .statusCheckRollup[]? | select(.conclusion == "FAILURE") | .name
' | head -5)
if [ -n "$FAILING_CHECKS" ]; then
  echo "⚠️  PR #${PR_NUM} CI 실패 항목이 있습니다:"
  echo "$FAILING_CHECKS" | sed 's/^/    - /'
  echo ""
  echo "    그래도 머지하려면 사용자 명시적 확인이 필요해요."
  # User must confirm via prompt or --force flag
fi

# 1.4b Override safeguard — classify before admin-merging a red/absent CI.
# If remote CI is unavailable (e.g. Actions billing/quota), an empty rollup is
# NOT "all green". Before overriding, validate locally so a real regression
# doesn't slip in buried under pre-existing baseline failures.
#
#   → Recommend delegating to the `local-ci` subagent to reproduce the gates
#     locally (lint/types/tests/build) and report pass/fail per gate.
#
# local-ci REPORTS ONLY — it makes no merge decision. The override call
# (infra/billing vs env vs real regression vs baseline) stays the operator's,
# per the admin-override decision framework. Do NOT auto-merge on its output.

# 1.5 Mergeable state
if [ "$PR_MERGEABLE" = "CONFLICTING" ]; then
  echo "❌ PR #${PR_NUM} 에 머지 충돌이 있어요. 먼저 충돌을 해결하세요:"
  echo "    git fetch origin master && git merge origin/master"
  exit 1
fi
```

---

## Step 2. Decide merge strategy

```bash
# Default: --merge (merge commit) — matches project precedent (PR #15, #16, ..., #26 all merge-commits)
# Alternative: --squash | --rebase
STRATEGY="${ARG_STRATEGY:-merge}"

case "$STRATEGY" in
  merge|squash|rebase) ;;
  *)
    echo "❌ 알 수 없는 strategy: $STRATEGY (사용 가능: merge / squash / rebase)"
    exit 1
    ;;
esac
```

---

## Step 3. Merge the PR

**This is a destructive operation (changes master).** Display summary + require explicit confirmation.

```bash
echo "🔀 PR #${PR_NUM} 머지 준비"
echo "    Title:    $PR_TITLE"
echo "    Branch:   $BRANCH"
echo "    Strategy: $STRATEGY (merge commit 유지)"
echo ""
echo "이대로 진행할까요? 머지 후 master 가 업데이트되고, 되돌리려면 revert PR 가 필요합니다."
# AI agent: ask user via AskUserQuestion ("진행" / "취소") before next bash block
```

After user confirms:

```bash
gh pr merge "$PR_NUM" --"$STRATEGY" --delete-branch=false 2>&1
# --delete-branch=false: leave the branch for Step 8 to handle (operator-configurable)
```

If merge fails (e.g., required reviews missing): show error + exit. Tag/release will not happen.

---

## Step 4. Switch to master + pull

```bash
# Determine base branch (master/main)
BASE_BRANCH="master"
if ! git rev-parse --verify "origin/${BASE_BRANCH}" >/dev/null 2>&1; then
  BASE_BRANCH="main"
fi

git checkout "$BASE_BRANCH"
git pull --ff-only origin "$BASE_BRANCH"

# Verify the merge commit is now master HEAD
NEW_MASTER_SHA=$(git rev-parse HEAD)
echo "✓ master 업데이트됨: $NEW_MASTER_SHA"

# Sanity check: the merge commit message should reference the PR
MERGE_MSG=$(git log -1 --pretty=%s)
if ! echo "$MERGE_MSG" | grep -q "#${PR_NUM}"; then
  echo "⚠️  master HEAD 메시지에 PR #${PR_NUM} 참조가 없어요:"
  echo "    $MERGE_MSG"
  echo "    (squash 머지면 정상; merge-commit 머지면 비정상)"
fi
```

If `--no-release` 플래그면 여기서 종료 + Step 9 report (release 부분만 생략).

---

## Step 5. Propose version + generate release notes

### 5.1 Detect current version + last tag

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
LAST_TAG_VERSION="${LAST_TAG#v}"
COMMITS_SINCE=$(git rev-list "${LAST_TAG}..HEAD" --count)

if [ "$COMMITS_SINCE" -eq 0 ]; then
  echo "⚠️  ${LAST_TAG} 이후 새 커밋이 없어요. 릴리즈 스킵."
  exit 0
fi
```

### 5.2 Compute the next version (SemVer from the last tag — NEVER from spec number)

**Versioning rule (authoritative):** the version is derived **only** from the
last git tag + the conventional-commit types since it. The spec/feature number
is **never** an input — `minor` and the spec number diverged long ago
(e.g. Feature 039 shipped as v0.63.0, not v0.39.0). Computing `v0.<spec>.0` is a
known bug and is removed here.

```bash
# base = last tag (already resolved above as $LAST_TAG / $LAST_TAG_VERSION).
IFS='.' read -r MAJOR MINOR PATCH <<<"$LAST_TAG_VERSION"

SUBJECTS=$(git log "${LAST_TAG}..HEAD" --no-merges --format='%s')
BODIES=$(git log "${LAST_TAG}..HEAD" --no-merges --format='%b')

HAS_BREAKING=$(printf '%s\n%s\n' "$SUBJECTS" "$BODIES" | grep -qE '(^|\s)BREAKING CHANGE|!:' && echo 1 || echo "")
HAS_FEAT=$(printf '%s\n' "$SUBJECTS"   | grep -qE '^feat(\([^)]+\))?!?:' && echo 1 || echo "")
HAS_FIX=$(printf '%s\n'  "$SUBJECTS"   | grep -qE '^(fix|perf)(\([^)]+\))?!?:' && echo 1 || echo "")
HAS_OTHER=$(printf '%s\n' "$SUBJECTS"  | grep -qE '^(chore|docs|refactor|build|ci|test|style)(\([^)]+\))?:' && echo 1 || echo "")

if [ -n "$HAS_BREAKING" ]; then
  # Project is 0.x: stay in 0.x, treat breaking as a minor bump until 1.0 is
  # declared explicitly by the operator (pass an explicit version to override).
  PROPOSED_VERSION="v${MAJOR}.$((MINOR + 1)).0"
  BUMP_REASON="breaking change (0.x → minor bump; pass explicit version for 1.0)"
elif [ -n "$HAS_FEAT" ]; then
  PROPOSED_VERSION="v${MAJOR}.$((MINOR + 1)).0"
  BUMP_REASON="feat present → minor bump"
elif [ -n "$HAS_FIX" ]; then
  PROPOSED_VERSION="v${MAJOR}.${MINOR}.$((PATCH + 1))"
  BUMP_REASON="fix/perf only → patch bump"
elif [ -n "$HAS_OTHER" ]; then
  # Tooling-only chore: default to NO release (suggest --no-release). If the
  # operator still wants a tag, fall through to a patch bump on confirm.
  PROPOSED_VERSION="v${MAJOR}.${MINOR}.$((PATCH + 1))"
  BUMP_REASON="chore/docs only → consider --no-release; else patch bump"
else
  PROPOSED_VERSION="v${MAJOR}.${MINOR}.$((PATCH + 1))"
  BUMP_REASON="no conventional types detected → patch bump (verify manually)"
fi

echo "🔢 제안 버전: ${PROPOSED_VERSION}  (마지막 태그 ${LAST_TAG} 기준 — ${BUMP_REASON})"
```

### 5.3 Generate release notes

```bash
NOTES_FILE=$(mktemp -t release-notes-XXXX.md)

cat > "$NOTES_FILE" <<EOF
# ${PROPOSED_VERSION} — [TODO: 한 줄 요약]

${COMMITS_SINCE} commits since ${LAST_TAG}.

## Features

$(git log "${LAST_TAG}..HEAD" --no-merges --format='- %s ([%h](../../commit/%H))' |
    grep -E '^- feat(\([^)]+\))?:' | head -20)

## Fixes

$(git log "${LAST_TAG}..HEAD" --no-merges --format='- %s ([%h](../../commit/%H))' |
    grep -E '^- fix(\([^)]+\))?:' | head -20)

## Chore / DevX

$(git log "${LAST_TAG}..HEAD" --no-merges --format='- %s ([%h](../../commit/%H))' |
    grep -E '^- (chore|docs|refactor|build|ci)(\([^)]+\))?:' | head -20)

## Schema migrations

$(git diff --name-only "${LAST_TAG}..HEAD" | grep -E '^db/migrations/[0-9]+_' | sort | sed 's/^/- /')

## Merged PRs

$(git log "${LAST_TAG}..HEAD" --merges --format='- %s' | sed 's|Merge pull request #\([0-9]*\) from .*|- [#\1](../../pull/\1)|')

## Operator notes

[TODO: 운영자가 머지/배포 후 알아야 할 것 — DB 백업 권장, env 변경, 새 admin URL 등]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF

echo "📝 릴리즈 노트 draft: $NOTES_FILE"
echo "    (사용자가 '[TODO: ...]' 부분 채워주세요)"
```

### 5.4 Confirm with user

AI agent: use `AskUserQuestion` to present:
- Proposed version (e.g., `v0.21.0`)
- Commit count + summary
- Show first 30 lines of generated notes
- Ask: "이대로 진행? / 버전 수정 / 노트 더 손볼게요"

If user wants to edit notes manually: pause for them to edit `$NOTES_FILE`, then re-confirm.

---

## Step 6. Tag + push tag

**Destructive: visible to everyone, hard to delete cleanly.** Confirm before.

```bash
TARGET_SHA=$(git rev-parse HEAD)

echo "🏷️  태그 생성 준비"
echo "    Tag:    $PROPOSED_VERSION"
echo "    Target: $TARGET_SHA"
echo "    Notes:  $NOTES_FILE"
echo ""
# User confirms via AskUserQuestion

# After confirmation:
TAG_MSG="${PROPOSED_VERSION} — $(head -1 "$NOTES_FILE" | sed 's/^# //; s/ — / — /')"
git tag -a "$PROPOSED_VERSION" -m "$TAG_MSG" "$TARGET_SHA"
git push origin "$PROPOSED_VERSION"

echo "✓ 태그 푸시 완료"
```

---

## Step 7. Create GitHub Release

```bash
RELEASE_URL=$(gh release create "$PROPOSED_VERSION" \
  --title "$(head -1 "$NOTES_FILE" | sed 's/^# //')" \
  --notes-file "$NOTES_FILE" 2>&1)

if echo "$RELEASE_URL" | grep -q "^https://"; then
  echo "✓ GitHub Release 생성: $RELEASE_URL"
else
  echo "❌ Release 생성 실패: $RELEASE_URL"
  echo "    수동 fallback: gh release create $PROPOSED_VERSION --title \"...\" --notes-file $NOTES_FILE"
fi
```

---

## Step 8. (Optional) Branch cleanup

Default: leave the merged branch alone. The operator can configure `--cleanup` flag to delete:

```bash
if [ "$ARG_CLEANUP" = "1" ]; then
  echo "🧹 브랜치 정리 중..."
  git branch -d "$BRANCH" 2>&1 || git branch -D "$BRANCH"
  git push origin --delete "$BRANCH" 2>&1
  echo "✓ $BRANCH 삭제 완료 (local + remote)"
fi
```

---

## Step 9. Report

```
✅ /ms.merglease 완료!

🔀 PR Merged: https://github.com/{owner}/{repo}/pull/${PR_NUM}
🏷️  Tag: ${PROPOSED_VERSION} → ${TARGET_SHA}
📦 Release: ${RELEASE_URL}
🧹 Branch cleanup: [enabled / skipped]

🚀 배포 (자동배포가 아닐 수 있음 — 프로젝트 배포 형태 확인):
  태그/릴리즈만으로 운영에 반영되지 않는 형태(예: image-baked 컨테이너)라면
  프로젝트의 배포 절차를 반드시 수행하세요. 일반 절차:
    1) 배포 환경에서 master 최신화
    2) 빌드/재배포 (예: docker compose up -d --build)
    3) 인스턴스/컨테이너가 실제로 교체됐는지 확인 (캐시 hit 로 미반영 주의)
    4) 반영 안 보이면 캐시 계층(CDN → 서비스워커 → 브라우저) 순서대로 배제
  ※ CI/CD 가 v* 태그로 자동배포하도록 설정돼 있으면 이 단계는 자동입니다.

📋 그 외:
  - 운영자 변경사항 안내 (DB 백업, env vars, 스키마 마이그레이션 등)
  - 다음 feature 브랜치 작업 시작
```

---

## Error handling

| 상황 | 메시지 + 대응 |
|---|---|
| `gh` 미설치 | "❌ gh CLI 미설치" + 설치 안내 |
| `gh` 인증 안 됨 | "❌ gh 인증 안 됨" + login 명령 |
| master/main 에서 호출 | "❌ feature 브랜치에서 호출하세요" |
| 열린 PR 없음 | "❌ PR 없어요 — 먼저 /fin 또는 /finq" |
| PR 상태 OPEN 아님 | "❌ PR #N 상태 (CLOSED / MERGED) — 이미 머지됨" |
| CI 실패 | "⚠️ 실패한 체크 N개" + 강제 머지 옵션 안내 |
| 충돌 | "❌ 머지 충돌 — rebase 또는 merge master 필요" |
| `gh pr merge` 실패 | 머지 안 됨; tag/release 스킵; 에러 표시 + 수동 안내 |
| `git pull --ff-only` 실패 | "⚠️ master fast-forward 실패 — 수동 확인 필요" |
| Tag 이미 존재 | "⚠️ ${PROPOSED_VERSION} 이미 존재 — 다른 버전 또는 force-update?" |
| `gh release create` 실패 | 태그는 푸시됐으니 수동 fallback 안내 |

---

## Design decisions

### Why "merglease" (not just /ms.release)?

`/fin` 이 push + PR open 까지 한다면, 자연스러운 follow-up은 "PR 검토 + 머지 + release". 두 동작은 거의 항상 같이 일어남 (release 는 머지된 master 에서만 의미 있음).

**Merge + Release 통합 시 장점**:
- 운영자가 한 명령으로 끝낼 수 있음
- "머지하고 release 안 함" / "release 한다고 머지를 빠뜨림" 같은 실수 방지
- 버전 자동 제안 + 릴리즈 노트 자동 생성 (operator 수정 가능)

**`--no-release` 플래그로 분리 옵션 유지**: release 까지 자동화하기 부담스러운 경우 (예: 사내 정책상 release approval 필요) merge 만 수행.

### Why SemVer-from-last-tag (NOT spec-number-as-version)?

옛 버전은 `v0.<spec번호>.0` 을 썼는데 이건 **버그**였음 — `minor` 와 spec 번호가
오래전 갈라져서 (Feature 039 가 실제로는 v0.63.0 으로 릴리즈됨) 매번 틀린 버전을
제안하고 operator 가 손으로 교정해야 했음.

**규칙**: 버전 입력은 **오직** (마지막 git 태그) + (그 이후 conventional-commit 타입)뿐.
spec/feature 번호는 절대 입력이 아님.
- `feat` 있음 → **minor +1**
- `fix`/`perf` 만 → **patch +1**
- `chore`/`docs`/`refactor`/`ci` 만 → 기본 `--no-release` 권장 (원하면 patch +1)
- `BREAKING CHANGE`/`!` → 0.x 단계라 **minor +1** (1.0 은 operator 가 명시 버전으로 선언)

`git describe` 마지막 태그가 single source of truth. 명시 버전 인자 (`/ms.merglease v0.70.0`) 로 항상 override 가능.

### Why tag the merge commit (not the PR's feature-branch tip)?

머지 후 master HEAD = 머지 커밋. 태그는 master 의 한 점을 가리켜야 `git checkout v0.21.0` 가 master 의 시점을 복원함. PR HEAD (feature branch 의 마지막 커밋) 를 태그하면 master 와 다른 git history 가리켜 혼란.

### Why call `AskUserQuestion` between steps?

Constitution X: 머지/태그/릴리즈는 destructive shared-state 동작. 사용자 명시적 동의 없이는 진행하지 않음. `/fin` 이 이미 push + PR open 까지 했으니 머지 "Yes" 한 번이면 충분 — 그 후로는 사용자 인지 없이 release 까지 자동 진행.

---

## Implementation notes (for the AI agent)

This skill is **multi-step interactive**, not a single bash invocation. The skill's executor should:

1. Run pre-flight checks via Bash → if fail, exit with friendly error
2. Use `AskUserQuestion` to confirm merge (show PR title + strategy)
3. Run `gh pr merge` via Bash
4. Run `git checkout master && git pull` via Bash
5. Run version-detect + notes-generate via Bash → write to `$NOTES_FILE`
6. Use `AskUserQuestion` to confirm version + show notes preview
7. (Optional) Pause for user to edit `$NOTES_FILE` if they ask
8. Run `git tag -a` + `git push origin v*` via Bash
9. Run `gh release create` via Bash
10. Output Step 9 final report

If the user passes `--no-release`: stop after step 4 (still do branch-merge), report Step 9 with release section saying "skipped".

If a step fails (merge conflict, CI block, network): **stop immediately**, report what landed and what didn't, do NOT roll back automatically. The operator decides cleanup manually.

## Relationship to other commands

```
/ms.specify → /ms.clarify → /ms.plan → /ms.tasks → /ms.implement → /fin
                                                                     ↓
                                                        (PR review on GitHub)
                                                                     ↓
                                                            /ms.merglease ← YOU ARE HERE
                                                                     ↓
                                                            (release tag + GitHub Release)
                                                                     ↓
                                          (deploy: auto via CI/CD if configured, else run your project's deploy step — see Step 9)
```

`/fin` and `/finq` push + open PR. **`/ms.merglease` is the natural follow-up after PR is review-approved**: merge it, cut a versioned release, then deploy — automatically if a v* tag triggers your CI/CD, otherwise run your project's deploy step (image-baked stacks need a rebuild + container recreation; see Step 9).
