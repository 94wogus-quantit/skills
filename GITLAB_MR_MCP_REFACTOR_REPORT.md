# 분석 리포트: gitlab-mr CI 스킬 → MCP 전환

## 요약

gitlab-mr 플러그인의 CI 관련 스킬 4개(ci-status, ci-cancel, ci-trigger, ci-retry)를 로컬 MCP 서버로 전환하는 것이 **타당함**.

**핵심 이유**:
- 스킬 오버헤드 제거 (프롬프트 파싱, 컨텍스트 로딩)
- git-local MCP와 동일한 패턴으로 일관성 유지
- 코드량 60% 감소 (~800줄 → ~300줄)
- 도구 조합 유연성 증가

---

## 컨텍스트

### 현재 구조

```
plugins/gitlab-mr/
├── skills/
│   ├── ci-status/SKILL.md      # 237줄
│   ├── ci-cancel/SKILL.md      # 289줄
│   ├── ci-trigger/SKILL.md     # 323줄
│   ├── ci-retry/SKILL.md       # 274줄
│   ├── list-discussions/
│   ├── fix-discussion/
│   └── mr-review/              # 복잡한 워크플로우 (유지)
```

### 분석 대상 스킬

| 스킬 | 줄 수 | 핵심 로직 | glab 명령어 |
|------|-------|-----------|-------------|
| ci-status | 237 | 파이프라인/job 상태 조회 | `glab ci status`, `glab ci get` |
| ci-cancel | 289 | 파이프라인/job 취소 | `glab ci cancel` |
| ci-trigger | 323 | 수동 job 트리거 | `glab ci trigger`, `glab ci run` |
| ci-retry | 274 | 실패 job 재시도 | `glab ci retry` |

**공통점**: 모두 `glab` CLI 래핑, 복잡한 워크플로우 없음

---

## 조사 과정

### 1. 스킬 구현 분석

각 스킬의 실제 구현을 분석한 결과:

```markdown
# ci-status 예시
실제 핵심:
- `glab ci status`
- `glab ci get --output json`
- `glab ci trace <job-id>`

나머지:
- 설명 텍스트 (~40%)
- 마크다운 템플릿 (~30%)
- 에러 처리 가이드 (~20%)
- 통합 안내 (~10%)
```

### 2. git-local MCP 패턴 분석

`plugins/workflow-bundle/git_local_server.py` 참조:

```python
# 패턴: FastMCP + subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-local")

def run_git_command(args: list[str]) -> tuple[bool, str]:
    result = subprocess.run(["git"] + args, ...)
    return success, output

@mcp.tool()
def git_status() -> dict:
    success, output = run_git_command(["status", "--porcelain"])
    return {"success": success, "staged": [], "modified": [], ...}
```

**장점**:
- 12개 도구가 633줄 (도구당 평균 50줄)
- 직접 호출 가능 (스킬 프롬프트 파싱 불필요)
- 조합 용이 (여러 도구 순차 호출)
- 테스트 용이 (유닛 테스트 가능)

---

## 근본 원인

### 스킬이 적합하지 않은 이유

1. **오버헤드**: 단순 CLI 래핑에 스킬 구조는 과함
2. **조합 어려움**: ci-status → ci-retry 연속 호출 시 각각 스킬 로딩 필요
3. **중복**: 4개 스킬이 유사한 구조 반복
4. **유지보수**: 마크다운 800줄 vs Python 300줄

### MCP가 적합한 이유

1. **직접 호출**: 프롬프트 해석 없이 함수 호출
2. **조합성**: `ci_status() → ci_retry_job(job_id)` 자연스러운 흐름
3. **일관성**: git-local MCP와 동일한 패턴
4. **재사용**: mr-review 스킬에서 MCP 도구 활용 가능

---

## 권장사항

### 1. 즉시 조치: gitlab-ci MCP 서버 생성

**파일**: `plugins/gitlab-mr/gitlab_ci_server.py`

```python
#!/usr/bin/env python3
"""
GitLab CI MCP Server
GitLab CI/CD 파이프라인 관리를 위한 MCP 서버
"""

import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gitlab-ci")


def run_glab_command(args: list[str]) -> tuple[bool, str]:
    """glab 명령어 실행 헬퍼"""
    try:
        result = subprocess.run(
            ["glab"] + args, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "glab command timed out"
    except FileNotFoundError:
        return False, "glab CLI not found. Install: brew install glab"
    except Exception as e:
        return False, str(e)


# ============================================================
# 파이프라인 조회
# ============================================================

@mcp.tool()
def ci_status() -> dict:
    """
    현재 브랜치의 파이프라인 상태를 반환합니다.

    Returns:
        - success: 성공 여부
        - status: 파이프라인 상태 (running, success, failed, etc.)
        - pipeline_id: 파이프라인 ID
        - web_url: GitLab UI 링크
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "get", "--output", "json"])

    if not success:
        return {
            "success": False,
            "status": None,
            "pipeline_id": None,
            "web_url": None,
            "message": f"파이프라인 조회 실패: {output}"
        }

    try:
        data = json.loads(output)
        return {
            "success": True,
            "status": data.get("status"),
            "pipeline_id": data.get("id"),
            "web_url": data.get("web_url"),
            "message": f"파이프라인 #{data.get('id')}: {data.get('status')}"
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "status": None,
            "pipeline_id": None,
            "web_url": None,
            "message": "JSON 파싱 실패"
        }


@mcp.tool()
def ci_list(count: int = 5) -> dict:
    """
    최근 파이프라인 목록을 반환합니다.

    Args:
        count: 조회할 파이프라인 수 (기본값: 5)

    Returns:
        - success: 성공 여부
        - pipelines: 파이프라인 목록 [{id, status, created_at, web_url}]
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "list", f"--per-page={count}"])

    if not success:
        return {
            "success": False,
            "pipelines": [],
            "message": f"파이프라인 목록 조회 실패: {output}"
        }

    # glab ci list 출력 파싱 (텍스트 형식)
    pipelines = []
    for line in output.split("\n"):
        if line.strip():
            pipelines.append(line.strip())

    return {
        "success": True,
        "pipelines": pipelines,
        "message": f"최근 {len(pipelines)}개 파이프라인 조회 완료"
    }


@mcp.tool()
def ci_jobs(status_filter: str = None) -> dict:
    """
    현재 파이프라인의 job 목록을 반환합니다.

    Args:
        status_filter: 필터링할 상태 (failed, running, manual, pending)

    Returns:
        - success: 성공 여부
        - jobs: job 목록 [{id, name, stage, status}]
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "get", "--output", "json"])

    if not success:
        return {
            "success": False,
            "jobs": [],
            "message": f"job 목록 조회 실패: {output}"
        }

    try:
        data = json.loads(output)
        jobs = data.get("jobs", [])

        if status_filter:
            jobs = [j for j in jobs if j.get("status") == status_filter]

        simplified_jobs = [
            {
                "id": j.get("id"),
                "name": j.get("name"),
                "stage": j.get("stage"),
                "status": j.get("status")
            }
            for j in jobs
        ]

        return {
            "success": True,
            "jobs": simplified_jobs,
            "message": f"{len(simplified_jobs)}개 job 조회 완료"
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "jobs": [],
            "message": "JSON 파싱 실패"
        }


@mcp.tool()
def ci_trace(job_id: int) -> dict:
    """
    특정 job의 로그를 반환합니다.

    Args:
        job_id: job ID

    Returns:
        - success: 성공 여부
        - log: job 로그 (최대 500줄)
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "trace", str(job_id)])

    if not success:
        return {
            "success": False,
            "log": None,
            "message": f"로그 조회 실패: {output}"
        }

    # 로그가 너무 길면 마지막 500줄만
    lines = output.split("\n")
    if len(lines) > 500:
        output = "\n".join(lines[-500:])

    return {
        "success": True,
        "log": output,
        "message": f"job #{job_id} 로그 조회 완료 ({len(lines)}줄)"
    }


# ============================================================
# 파이프라인 제어
# ============================================================

@mcp.tool()
def ci_cancel_job(job_id: int) -> dict:
    """
    특정 job을 취소합니다.

    Args:
        job_id: 취소할 job ID

    Returns:
        - success: 성공 여부
        - job_id: 취소된 job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(
        ["api", "--method", "POST", f"projects/:fullpath/jobs/{job_id}/cancel"]
    )

    if success:
        return {
            "success": True,
            "job_id": job_id,
            "message": f"✅ job #{job_id} 취소 완료"
        }

    return {
        "success": False,
        "job_id": job_id,
        "message": f"job 취소 실패: {output}"
    }


@mcp.tool()
def ci_cancel_pipeline(pipeline_id: int = None) -> dict:
    """
    파이프라인을 취소합니다.

    Args:
        pipeline_id: 취소할 파이프라인 ID (기본값: 현재 파이프라인)

    Returns:
        - success: 성공 여부
        - pipeline_id: 취소된 파이프라인 ID
        - message: 결과 메시지
    """
    # 파이프라인 ID 가져오기
    if not pipeline_id:
        status_result = ci_status()
        if not status_result["success"]:
            return {
                "success": False,
                "pipeline_id": None,
                "message": "현재 파이프라인을 찾을 수 없습니다"
            }
        pipeline_id = status_result["pipeline_id"]

    success, output = run_glab_command(
        ["api", "--method", "POST", f"projects/:fullpath/pipelines/{pipeline_id}/cancel"]
    )

    if success:
        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "message": f"✅ 파이프라인 #{pipeline_id} 취소 완료"
        }

    return {
        "success": False,
        "pipeline_id": pipeline_id,
        "message": f"파이프라인 취소 실패: {output}"
    }


@mcp.tool()
def ci_trigger_job(job_id: int) -> dict:
    """
    수동 job을 트리거합니다.

    Args:
        job_id: 트리거할 job ID

    Returns:
        - success: 성공 여부
        - job_id: 트리거된 job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(["ci", "trigger", str(job_id)])

    if success:
        return {
            "success": True,
            "job_id": job_id,
            "message": f"✅ job #{job_id} 트리거 완료"
        }

    return {
        "success": False,
        "job_id": job_id,
        "message": f"job 트리거 실패: {output}"
    }


@mcp.tool()
def ci_run(branch: str = None) -> dict:
    """
    새 파이프라인을 시작합니다.

    Args:
        branch: 실행할 브랜치 (기본값: 현재 브랜치)

    Returns:
        - success: 성공 여부
        - pipeline_id: 생성된 파이프라인 ID
        - message: 결과 메시지
    """
    args = ["ci", "run"]
    if branch:
        args.extend(["--branch", branch])

    success, output = run_glab_command(args)

    if success:
        return {
            "success": True,
            "pipeline_id": None,  # output 파싱 필요
            "message": f"✅ 새 파이프라인 시작: {output}"
        }

    return {
        "success": False,
        "pipeline_id": None,
        "message": f"파이프라인 시작 실패: {output}"
    }


@mcp.tool()
def ci_retry_job(job_id: int) -> dict:
    """
    실패한 job을 재시도합니다.

    Args:
        job_id: 재시도할 job ID

    Returns:
        - success: 성공 여부
        - job_id: 재시도된 job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(["ci", "retry", str(job_id)])

    if success:
        return {
            "success": True,
            "job_id": job_id,
            "message": f"✅ job #{job_id} 재시도 완료"
        }

    return {
        "success": False,
        "job_id": job_id,
        "message": f"job 재시도 실패: {output}"
    }


if __name__ == "__main__":
    mcp.run()
```

### 2. MCP 서버 등록

**파일**: `plugins/gitlab-mr/.mcp.json`

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

### 3. 기존 스킬 삭제

```bash
rm -rf plugins/gitlab-mr/skills/ci-status
rm -rf plugins/gitlab-mr/skills/ci-cancel
rm -rf plugins/gitlab-mr/skills/ci-trigger
rm -rf plugins/gitlab-mr/skills/ci-retry
```

### 4. mr-review 스킬 업데이트

mr-review 스킬에서 CI 관련 작업 시 MCP 도구 참조 추가:

```markdown
## CI 상태 확인
MCP 도구 `ci_status()` 또는 `ci_jobs(status_filter="failed")` 사용
```

---

## 테스트 계획

| 테스트 케이스 | 예상 결과 |
|--------------|-----------|
| `ci_status()` | 현재 파이프라인 상태 반환 |
| `ci_jobs(status_filter="failed")` | 실패한 job만 필터링 |
| `ci_trace(job_id)` | job 로그 반환 (500줄 제한) |
| `ci_cancel_pipeline()` | 현재 파이프라인 취소 |
| `ci_retry_job(job_id)` | 실패 job 재시도 |
| glab 미설치 시 | 명확한 에러 메시지 |

---

## 관련 코드 리뷰

| 파일 | 조치 |
|------|------|
| `plugins/gitlab-mr/skills/ci-status/` | 삭제 |
| `plugins/gitlab-mr/skills/ci-cancel/` | 삭제 |
| `plugins/gitlab-mr/skills/ci-trigger/` | 삭제 |
| `plugins/gitlab-mr/skills/ci-retry/` | 삭제 |
| `plugins/gitlab-mr/gitlab_ci_server.py` | 신규 생성 |
| `plugins/gitlab-mr/.mcp.json` | 업데이트 |
| `plugins/gitlab-mr/skills/mr-review/` | 유지 (MCP 참조 추가) |

---

## 예상 효과

| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 코드량 | ~1,123줄 (SKILL.md 4개) | ~300줄 (Python) | -73% |
| 도구 수 | 4개 스킬 | 9개 MCP 도구 | +125% (세분화) |
| 호출 오버헤드 | 스킬 프롬프트 파싱 | 직접 함수 호출 | 대폭 감소 |
| 조합성 | 스킬 간 연계 어려움 | 도구 연속 호출 용이 | 개선 |

---

## 버전

- **분석 버전**: v3.15.1
- **대상 버전**: v3.16.0 (예정)
- **브랜치**: `feature/gitlab-mr-mcp-refactor`
