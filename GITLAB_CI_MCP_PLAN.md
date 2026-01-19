# 구현 계획: gitlab-mr 스킬 → MCP 전환

## 개요

gitlab-mr 플러그인의 CI 관련 스킬 4개 + list-discussions 스킬을 로컬 MCP 서버로 전환합니다.

**목표**:
- 스킬 오버헤드 제거
- git-local MCP와 동일한 패턴 유지
- 코드량 감소 및 도구 조합성 향상

**참조**: `GITLAB_MR_MCP_REFACTOR_REPORT.md`

---

## Task 목록

### Task 0: 전제조건 확인 [P0]

**목적**: 구현 시작 전 필수 환경 검증

**확인 항목**:
1. glab CLI 설치 여부
2. glab 인증 상태
3. Python 환경 (FastMCP 의존성)

**의존성**: 없음

**성공 기준**:
- [ ] `glab --version` 출력 확인 (최소 v1.30.0 이상 권장)
- [ ] `glab auth status` 인증 완료 상태
- [ ] `python3 -c "from mcp.server.fastmcp import FastMCP"` 성공

**테스팅 전략**:
- **테스트 유형**: 환경 검증
- **테스트 케이스**:
  1. **Given**: 개발 환경
     **When**: `glab --version` 실행
     **Then**: 버전 번호 출력 (예: "glab version 1.36.0")
  2. **Given**: glab 설치됨
     **When**: `glab auth status` 실행
     **Then**: "Logged in to gitlab.com" 또는 "Logged in to [host]" 출력
  3. **Given**: Python 환경
     **When**: FastMCP import 시도
     **Then**: ImportError 없이 성공
- **실패 시 조치**:
  - glab 미설치: `brew install glab` 또는 공식 설치 가이드 참조
  - 인증 실패: `glab auth login` 실행
  - FastMCP 없음: `pip install mcp` 실행

---

### Task 1: gitlab_ci_server.py 생성 [P0]

**목적**: GitLab CI MCP 서버 핵심 구현

**파일**: `plugins/gitlab-mr/gitlab_ci_server.py`

**구현 내용**:
1. FastMCP 기반 MCP 서버 생성
2. `run_glab_command()` 헬퍼 함수 구현
3. **CI 도구 (9개)**:
   - `ci_status()` - 파이프라인 상태 조회
   - `ci_list(count)` - 최근 파이프라인 목록
   - `ci_jobs(status_filter)` - job 목록 (필터링)
   - `ci_trace(job_id)` - job 로그
   - `ci_cancel_job(job_id)` - job 취소
   - `ci_cancel_pipeline(pipeline_id)` - 파이프라인 취소
   - `ci_trigger_job(job_id)` - 수동 job 트리거
   - `ci_run(branch)` - 새 파이프라인 시작
   - `ci_retry_job(job_id)` - 실패 job 재시도
4. **MR Discussion 도구 (3개)**:
   - `mr_get(mr_iid)` - 현재 브랜치 또는 지정 MR 정보 조회
   - `mr_discussions(mr_iid, resolved_filter)` - Discussion 전체 목록 조회
     - `resolved_filter`: "all" | "unresolved" | "resolved"
     - 내부적으로 pagination 처리하여 전체 반환 (호출자는 신경 쓸 필요 없음)
   - `mr_resolve_discussion(mr_iid, discussion_id)` - Discussion 해결 처리

**의존성**: Task 0

**성공 기준**:
- [ ] 모든 도구가 glab CLI 명령어를 정상 실행
- [ ] 각 도구가 일관된 dict 형식 반환 (success, 결과, message)
- [ ] glab 미설치 시 명확한 에러 메시지 반환
- [ ] 에러 케이스에서 적절한 에러 처리

**테스팅 전략**:
- **테스트 유형**: 수동 통합 테스트 + 에러 케이스 검증
- **테스트 케이스**:

  **성공 경로 (Happy Path)**:
  1. **Given**: GitLab 프로젝트 디렉토리에서 실행
     **When**: `ci_status()` 호출
     **Then**: `{"success": True, "status": "...", "pipeline_id": ..., "message": "..."}` 반환

  2. **Given**: 실행 중인 파이프라인 존재
     **When**: `ci_jobs(status_filter="running")` 호출
     **Then**: running 상태 job만 포함된 목록 반환

  3. **Given**: 실패한 job 존재 (job_id: 12345)
     **When**: `ci_retry_job(12345)` 호출
     **Then**: `{"success": True, "job_id": 12345, "message": "✅ job #12345 재시도 완료"}` 반환

  **MR Discussion 테스트**:
  4. **Given**: 현재 브랜치에 MR 존재
     **When**: `mr_get()` 호출 (mr_iid 생략)
     **Then**: 현재 브랜치의 MR 정보 반환

  5. **Given**: MR에 unresolved discussion 3개 존재
     **When**: `mr_discussions(mr_iid=123, resolved_filter="unresolved")` 호출
     **Then**: 3개 discussion 목록 반환

  6. **Given**: MR에 discussion 150개 존재 (API 100개 제한)
     **When**: `mr_discussions(mr_iid=123, resolved_filter="all")` 호출
     **Then**: 150개 전체 반환 (내부적으로 2번 API 호출)

  7. **Given**: MR에 resolved discussion 5개, unresolved 10개 존재
     **When**: `mr_discussions(mr_iid=123, resolved_filter="resolved")` 호출
     **Then**: resolved된 5개만 반환

  **에러 케이스 (Error Path)**:
  4. **Given**: glab CLI 미설치 환경
     **When**: 임의 도구 호출
     **Then**: `{"success": False, "message": "glab CLI not found. Install: brew install glab"}` 반환

  5. **Given**: GitLab 인증 만료
     **When**: `ci_status()` 호출
     **Then**: `{"success": False, "message": "..."}` (glab 에러 메시지 포함)

  6. **Given**: 존재하지 않는 job_id (99999999)
     **When**: `ci_retry_job(99999999)` 호출
     **Then**: `{"success": False, "job_id": 99999999, "message": "job 재시도 실패: ..."}` 반환

  7. **Given**: 타임아웃 상황 (네트워크 지연)
     **When**: 30초 이상 응답 없음
     **Then**: `{"success": False, "message": "glab command timed out"}` 반환

- **검증 명령**:
  ```bash
  # 서버 실행 테스트 (GitLab 프로젝트에서)
  cd plugins/gitlab-mr && python3 -c "from gitlab_ci_server import ci_status; print(ci_status())"

  # 에러 케이스 테스트 (glab 없는 환경 시뮬레이션)
  PATH="" python3 -c "from gitlab_ci_server import ci_status; print(ci_status())"
  ```

---

### Task 2: .mcp.json 생성 [P0]

**목적**: MCP 서버를 플러그인에 등록

**파일**: `plugins/gitlab-mr/.mcp.json`

**구현 내용**:
```json
{
  "mcpServers": {
    "gitlab-ci": {
      "command": "python3",
      "args": ["${CLAUDE_PLUGIN_ROOT}/gitlab_ci_server.py"]
    }
  }
}
```

**의존성**: Task 1

**성공 기준**:
- [ ] Claude Code 재시작 후 gitlab-ci 서버 자동 시작
- [ ] 도구 목록에 `mcp__plugin_gitlab-mr_gitlab-ci__ci_status` 등 표시

**테스팅 전략**:
- **테스트 유형**: 수동 통합 테스트
- **테스트 케이스**:
  1. **Given**: .mcp.json 파일 생성 완료
     **When**: Claude Code 재시작
     **Then**: `/mcp` 명령에서 gitlab-ci 서버 표시
  2. **Given**: gitlab-ci 서버 실행 중
     **When**: `ci_status()` 도구 호출
     **Then**: 파이프라인 상태 정상 반환
  3. **Given**: GitLab 프로젝트 외부 디렉토리
     **When**: `ci_status()` 도구 호출
     **Then**: 적절한 에러 메시지 반환

---

### Task 3: 기존 스킬 삭제 [P1]

**목적**: MCP로 전환된 스킬 제거

**삭제 대상**:
- `plugins/gitlab-mr/skills/ci-status/`
- `plugins/gitlab-mr/skills/ci-cancel/`
- `plugins/gitlab-mr/skills/ci-trigger/`
- `plugins/gitlab-mr/skills/ci-retry/`
- `plugins/gitlab-mr/skills/list-discussions/`

**의존성**: Task 1, Task 2 (MCP 작동 확인 후)

**성공 기준**:
- [ ] 5개 스킬 디렉토리 삭제 완료
- [ ] `/ci-status`, `/list-discussions` 호출 시 스킬 없음 (MCP 도구로 대체)

**테스팅 전략**:
- **테스트 유형**: 수동 검증
- **테스트 케이스**:
  1. **Given**: 스킬 삭제 명령 실행
     **When**: `ls plugins/gitlab-mr/skills/` 실행
     **Then**: ci-status, ci-cancel, ci-trigger, ci-retry, list-discussions 디렉토리 없음
  2. **Given**: 스킬 삭제 완료
     **When**: MCP 도구 `ci_status()` 호출
     **Then**: 정상 작동 (MCP로 대체 확인)
  3. **Given**: 스킬 삭제 완료
     **When**: MCP 도구 `mr_discussions()` 호출
     **Then**: 정상 작동 (MCP로 대체 확인)
  4. **Given**: 스킬 삭제 완료
     **When**: `/ci-status` 또는 `/list-discussions` 스킬 호출 시도
     **Then**: "Unknown skill" 메시지 표시
- **검증 명령**:
  ```bash
  ls plugins/gitlab-mr/skills/  # ci-status, list-discussions 등 없어야 함
  ```

---

### Task 4: 문서 업데이트 [P2]

**목적**: 변경사항 문서화

**수정 파일**:

#### 4-1. CLAUDE.md 업데이트

**수정 내용**:
- "Available Skills" 섹션에서 CI 스킬 제거
- "Git Local MCP" 섹션 아래에 "GitLab CI MCP" 섹션 추가

**추가할 내용**:
```markdown
## GitLab MCP (v3.16.0)

GitLab CI/CD 및 MR 관리를 위한 MCP 서버. gitlab-mr에 포함.

### CI 파이프라인 조회 도구
- **ci_status**: 현재 파이프라인 상태 조회
- **ci_list**: 최근 파이프라인 목록
- **ci_jobs**: job 목록 (status_filter 옵션)
- **ci_trace**: job 로그 조회

### CI 파이프라인 제어 도구
- **ci_cancel_job**: 특정 job 취소
- **ci_cancel_pipeline**: 파이프라인 취소
- **ci_trigger_job**: 수동 job 트리거
- **ci_run**: 새 파이프라인 시작
- **ci_retry_job**: 실패 job 재시도

### MR Discussion 도구
- **mr_get**: 현재 브랜치 또는 지정 MR 정보 조회
- **mr_discussions**: Discussion 전체 목록 조회
  - `resolved_filter`: "all" | "unresolved" | "resolved"
  - 내부적으로 pagination 처리하여 전체 반환
- **mr_resolve_discussion**: Discussion 해결 처리
```

#### 4-2. mr-review, fix-discussion 스킬 확인 및 업데이트

**목적**: mr-review, fix-discussion 스킬이 삭제된 스킬을 참조하는지 확인하고 MCP 참조로 변경

**확인 사항**:
1. `plugins/gitlab-mr/skills/mr-review/SKILL.md`에서 ci-status, ci-cancel, ci-trigger, ci-retry, list-discussions 참조 검색
2. `plugins/gitlab-mr/skills/fix-discussion/SKILL.md`에서 list-discussions 참조 검색
3. 참조 발견 시 MCP 도구로 업데이트

**예상 변경**:
```markdown
# Before (스킬 참조)
CI 상태 확인: `ci-status` 스킬 사용

# After (MCP 도구 참조)
CI 상태 확인: MCP 도구 `ci_status()` 또는 `ci_jobs(status_filter="failed")` 사용
```

**테스트 케이스**:
1. **Given**: mr-review 스킬 파일
   **When**: "ci-status", "ci-cancel", "ci-trigger", "ci-retry" 문자열 검색
   **Then**: 참조 있으면 MCP 도구로 변경, 없으면 변경 불필요

---

#### 4-3. CHANGELOG.md 업데이트

**추가할 내용**:
```markdown
## v3.16.0 (2026-01-19)

### Added
- **GitLab MCP 서버**: gitlab-mr 플러그인에 CI/CD 및 MR 관리 MCP 추가
  - CI 도구 (9개): ci_status, ci_list, ci_jobs, ci_trace, ci_cancel_job, ci_cancel_pipeline, ci_trigger_job, ci_run, ci_retry_job
  - MR 도구 (3개): mr_get, mr_discussions, mr_resolve_discussion

### Removed
- **스킬 5개 삭제**: ci-status, ci-cancel, ci-trigger, ci-retry, list-discussions
  - MCP 도구로 대체 (더 빠르고 조합 용이)

### Migration Guide
- 기존 `/ci-status` → MCP 도구 `ci_status()` 사용
- 기존 `/list-discussions` → MCP 도구 `mr_discussions(resolved_filter="unresolved")` 사용
```

**의존성**: Task 3

**성공 기준**:
- [ ] CLAUDE.md에 GitLab CI MCP 섹션 추가
- [ ] mr-review 스킬에서 CI 스킬 참조 확인 및 업데이트 (필요시)
- [ ] CHANGELOG.md에 v3.16.0 변경사항 기록

**테스팅 전략**:
- **테스트 유형**: 리뷰
- **테스트 케이스**:
  1. 마크다운 문법 오류 없음
  2. 버전 번호 일관성 확인

---

### Task 5: 버전 업데이트 [P2]

**목적**: 플러그인 버전 증가

**수정 파일**: `.claude-plugin/marketplace.json`

**변경 내용**:
- `metadata.version`: "3.15.1" → "3.16.0"

**의존성**: Task 4

**성공 기준**:
- [ ] marketplace.json 버전 업데이트 완료

**테스팅 전략**:
- **테스트 유형**: JSON 검증
- **검증 명령**:
  ```bash
  cat .claude-plugin/marketplace.json | jq '.metadata.version'
  # 출력: "3.16.0"
  ```

---

## 실행 순서

```
Task 0 (전제조건 확인)
    ↓
Task 1 (MCP 서버 생성)
    ↓
Task 2 (MCP 등록)
    ↓
[검증: MCP 도구 작동 확인]
    ↓
Task 3 (스킬 삭제)
    ↓
Task 4 (문서 업데이트: CLAUDE.md, mr-review, CHANGELOG)
    ↓
Task 5 (버전 업데이트)
    ↓
[최종 검증]
```

---

## 리스크 및 완화

| 리스크 | 가능성 | 영향 | 완화 방법 |
|--------|--------|------|-----------|
| glab CLI 호환성 문제 | 낮음 | 높음 | glab 버전 체크 추가 |
| FastMCP 의존성 | 낮음 | 중간 | git-local에서 검증됨 |
| Breaking Change | 확실 | 중간 | CHANGELOG 마이그레이션 가이드 |

---

## 롤백 계획

MCP 전환 실패 시:
1. `git revert` 로 스킬 삭제 취소
2. `.mcp.json`에서 gitlab-ci 서버 제거
3. `gitlab_ci_server.py` 삭제

---

## 예상 결과

| 지표 | Before | After |
|------|--------|-------|
| 코드량 | ~1,450줄 (스킬 5개) | ~450줄 (Python) |
| 도구 수 | 5개 스킬 | 12개 MCP 도구 |
| 호출 방식 | 스킬 프롬프트 | 직접 함수 호출 |
| Pagination | 스킬에서 처리 | MCP 내부 자동 처리 (전체 반환) |
| 필터링 | 고정 (unresolved만) | 유연 (all/unresolved/resolved) |
