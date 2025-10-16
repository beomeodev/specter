# CLI Bridge 효율적 사용 가이드

## 🎯 문제: 토큰 제한 (25,000)

Claude Code Extension은 MCP 응답을 25,000 토큰으로 제한합니다.

## 💡 해결책: 스마트 프롬프팅

### 1. **길이 제한 명시**
```
❌ 나쁜 예:
"Analyze ms.review.md for issues"

✅ 좋은 예:
"List TOP 3 critical issues in ms.review.md (max 500 words)"
```

### 2. **구체적 요청**
```
❌ 나쁜 예:
"Review the entire file"

✅ 좋은 예:
"Check only Step 5-6 for logic errors"
```

### 3. **출력 형식 지정**
```
✅ 효율적:
"Output as bullet points:
- Issue: [brief description]
- Line: [number]
- Fix: [one line]
Max 5 issues."
```

## 📊 토큰 사용 비교

| 접근법 | Codex 응답 | Claude 토큰 소모 | 효율성 |
|--------|-----------|----------------|--------|
| 일반 분석 | 230,000 tokens | ❌ 실패 | 0% |
| 요약 요청 | 20,000 tokens | ~25,000 | 80% |
| TOP 3 only | 5,000 tokens | ~8,000 | 95% |
| Yes/No 질문 | 100 tokens | ~500 | 99% |

## 🚀 최적 사용 패턴

### Pattern 1: Progressive Refinement
```
1. "Are there critical issues in ms.review.md? (Yes/No)"
2. If Yes: "List file sections with issues (names only)"
3. "Analyze Step 5 specifically for errors"
```

### Pattern 2: Targeted Questions
```
Instead of: "Analyze everything"
Use: "Is the AGENT_NAME hardcoded? Show the line."
```

### Pattern 3: Streaming Alternative
```python
# Use the streaming server for large analysis
"codex_cli_summary": Automatic truncation
"codex_cli_stream": First chunk only
```

## 🔧 설정 변경 옵션

### Option 1: Use Streaming Server
```json
// .mcp.json
{
  "mcpServers": {
    "cli-bridge-stream": {
      "command": "python3",
      "args": [
        "/workspace/my-spec/.mcp-servers/cli-bridge/server_streaming.py"
      ]
    }
  }
}
```

### Option 2: Direct CLI Usage
```bash
# Bypass MCP for large outputs
echo "Analyze ms.review.md" | codex exec > analysis.md
# Then read analysis.md separately
```

### Option 3: Chunk Requests
```
Use mcp__cli-bridge__codex_cli with prompt "Part 1/3: Analyze Steps 1-3"
Use mcp__cli-bridge__codex_cli with prompt "Part 2/3: Analyze Steps 4-6"
Use mcp__cli-bridge__codex_cli with prompt "Part 3/3: Analyze Steps 7-9"
```

## ⚡ 토큰 효율성 극대화

### Claude의 토큰 소모 최소화 방법:

1. **Codex가 직접 파일 쓰기**
   ```
   "Analyze ms.review.md and write summary to /tmp/review-summary.md"
   ```
   Then: Read /tmp/review-summary.md (작은 파일만 Claude가 읽음)

2. **Binary Questions**
   ```
   "Does ms.review.md have security issues? Reply: YES/NO"
   ```

3. **Line Numbers Only**
   ```
   "List only line numbers with issues: [n1, n2, n3]"
   ```

## 📈 실제 개선 효과

- 일반 요청: 231,459 tokens → ❌ 실패
- 요약 요청: 20,000 tokens → ✅ 성공
- TOP 3만: 5,000 tokens → ✅ 빠름
- Yes/No: 100 tokens → ✅ 즉시

## 🎯 권장사항

1. **항상 길이 제한 명시**: "max 500 words" 또는 "under 5000 tokens"
2. **구체적 질문**: 전체 분석 대신 특정 부분만
3. **단계적 접근**: 큰 작업은 작은 청크로 나누기
4. **파일 출력 활용**: Codex가 파일로 쓰고 Claude가 읽기
