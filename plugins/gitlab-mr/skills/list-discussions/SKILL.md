---
name: list-discussions
description: GitLab MR의 unresolved discussion 목록을 조회하여 사용자에게 보여줍니다. 현재 브랜치에서 자동으로 MR을 찾거나 MR 번호를 직접 지정할 수 있습니다. Korean triggers: discussion 목록, 디스커션 보기, MR 코멘트, 리뷰 코멘트, unresolved 보기, 미해결 코멘트.
---

# List Discussions

## ⚠️ CRITICAL LANGUAGE POLICY

**DEFAULT LANGUAGE: KOREAN (한국어)**

모든 출력, 분석, 커뮤니케이션은 **한국어**로 작성해야 합니다.

---

## Overview

GitLab MR에 달린 **unresolved discussion**들을 조회하여 사용자에게 보기 쉽게 정리해서 보여줍니다.

**주요 기능**:
- 🔍 **자동 MR 탐지**: 현재 브랜치에서 관련 MR 자동 찾기
- 📋 **Discussion 목록화**: unresolved discussion만 필터링
- 📍 **위치 정보**: 파일, 라인, 코드 스니펫 포함
- 🏷️ **메타데이터**: 작성자, 작성 시간, 심각도 표시

---

## When to Use

**✅ 사용할 때:**
- MR에 달린 리뷰 코멘트를 확인하고 싶을 때
- 해결해야 할 discussion이 무엇인지 파악하고 싶을 때
- fix-discussion skill 실행 전 목록 확인

**❌ 사용하지 않을 때:**
- MR이 없는 브랜치에서 작업 중일 때
- 이미 모든 discussion이 resolved된 MR

---

## Workflow

### Phase 1: MR 식별

**1-1. 사용자 입력 확인**

사용자가 MR 번호를 제공했는지 확인:
- 제공됨: 해당 MR 번호 사용
- 제공 안됨: 현재 브랜치에서 자동 탐지

**1-2. 현재 브랜치에서 MR 찾기**

```bash
# 현재 브랜치 이름 확인
CURRENT_BRANCH=$(git branch --show-current)

# 해당 브랜치의 MR 찾기
glab mr list --source-branch="$CURRENT_BRANCH" --state=opened --json iid,title,web_url
```

**1-3. MR이 없는 경우**

```
⚠️ 현재 브랜치 '$CURRENT_BRANCH'에 연결된 열린 MR이 없습니다.

다음 중 하나를 시도해주세요:
1. MR 번호를 직접 지정: "MR !123의 discussion 보여줘"
2. MR을 먼저 생성: `glab mr create`
```

---

### Phase 2: Discussion 조회

**2-1. MR Discussion 가져오기**

```bash
# MR의 모든 discussion 조회 (JSON 형식)
glab api "projects/:fullpath/merge_requests/${MR_IID}/discussions" | jq '.'
```

**2-2. Unresolved Discussion 필터링**

```bash
# unresolved인 것만 필터링
glab api "projects/:fullpath/merge_requests/${MR_IID}/discussions" | jq '[
  .[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)
]'
```

**2-3. 필요한 정보 추출**

각 discussion에서 추출할 정보:
- `id`: discussion ID (resolve 시 필요)
- `notes[0].body`: 코멘트 내용
- `notes[0].author.name`: 작성자
- `notes[0].created_at`: 작성 시간
- `notes[0].position.new_path`: 파일 경로
- `notes[0].position.new_line`: 라인 번호

---

### Phase 3: 결과 표시

**3-1. 요약 테이블**

```markdown
## 📋 Unresolved Discussions (N개)

| # | 파일 | 라인 | 제목/요약 | 작성자 |
|---|------|------|----------|--------|
| 1 | src/api/user.ts | 45 | SQL Injection 위험 | reviewer1 |
| 2 | src/services/auth.ts | 78 | 에러 핸들링 누락 | reviewer2 |
| 3 | src/utils/validation.ts | 12 | 변수명 개선 필요 | reviewer1 |
```

**3-2. 상세 정보**

각 discussion의 상세 내용:

```markdown
### Discussion #1: SQL Injection 위험

- **파일**: `src/api/user.ts:45`
- **작성자**: reviewer1
- **작성일**: 2025-01-05 10:30
- **Discussion ID**: `abc123def456`

**코멘트 내용**:
> 🔴 **Critical**: SQL Injection Vulnerability
>
> User input is directly used in query...

**관련 코드**:
```typescript
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

---
```

**3-3. 다음 단계 안내**

```markdown
## 🚀 다음 단계

특정 discussion을 수정하려면:
```
fix-discussion skill로 Discussion #1 수정해줘
```

또는 모든 discussion을 순차적으로 수정하려면:
```
fix-discussion skill로 모든 discussion 수정해줘
```
```

---

## Output Format

### 성공 시

```markdown
# MR !456 - Unresolved Discussions

**MR 제목**: Implement user authentication
**브랜치**: feature/user-auth → main
**총 Discussion**: 5개 (unresolved: 3개)

## 📋 Unresolved Discussions

[요약 테이블]

[상세 정보]

## 🚀 다음 단계
...
```

### Discussion 없을 때

```markdown
# MR !456 - All Discussions Resolved ✅

**MR 제목**: Implement user authentication
**브랜치**: feature/user-auth → main

🎉 모든 discussion이 해결되었습니다!

MR을 머지할 준비가 되었습니다.
```

---

## glab CLI Reference

### 필수 명령어

```bash
# MR 목록 조회
glab mr list --source-branch="branch-name" --state=opened

# MR 상세 정보
glab mr view <MR_IID> --json

# Discussion 조회 (API 직접 호출)
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions"

# 특정 Discussion 조회
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions/<DISCUSSION_ID>"
```

### 유용한 jq 필터

```bash
# unresolved만 필터링
jq '[.[] | select(.notes[0].resolvable == true and .notes[0].resolved == false)]'

# 파일별 그룹핑
jq 'group_by(.notes[0].position.new_path)'

# 필요한 필드만 추출
jq '[.[] | {
  id: .id,
  file: .notes[0].position.new_path,
  line: .notes[0].position.new_line,
  body: .notes[0].body,
  author: .notes[0].author.name
}]'
```

---

## Error Handling

### glab 인증 실패

```
❌ GitLab 인증 실패

glab이 인증되어 있는지 확인하세요:
$ glab auth status

인증이 안 되어 있다면:
$ glab auth login
```

### API 접근 권한 없음

```
❌ MR !456에 접근할 수 없습니다.

가능한 원인:
1. MR이 존재하지 않음
2. 해당 프로젝트에 접근 권한 없음
3. MR이 이미 머지/닫힘

확인:
$ glab mr view 456
```

---

## Integration with fix-discussion

이 skill의 출력은 `fix-discussion` skill의 입력으로 사용됩니다.

**Workflow**:
1. `list-discussions` → discussion 목록 확인
2. 사용자가 수정할 discussion 선택
3. `fix-discussion` → 코드 수정, 코멘트, resolve

**데이터 전달**:
- Discussion ID
- 파일 경로
- 라인 번호
- 코멘트 내용 (수정 가이드)
