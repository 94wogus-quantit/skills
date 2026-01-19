#!/usr/bin/env python3
"""
GitLab CI MCP Server
GitLab CI/CD 파이프라인 및 MR Discussion 관리를 위한 MCP 서버

CI Tools (9개):
- ci_status: 현재 파이프라인 상태 조회
- ci_list: 최근 파이프라인 목록
- ci_jobs: job 목록 (status_filter 옵션)
- ci_trace: job 로그 조회
- ci_cancel_job: 특정 job 취소
- ci_cancel_pipeline: 파이프라인 취소
- ci_trigger_job: 수동 job 트리거
- ci_run: 새 파이프라인 시작
- ci_retry_job: 실패 job 재시도

MR Discussion Tools (3개):
- mr_get: 현재 브랜치 또는 지정 MR 정보 조회
- mr_discussions: Discussion 전체 목록 조회 (필터링 지원, 내부 pagination)
- mr_resolve_discussion: Discussion 해결 처리
"""

import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gitlab-ci")


def run_glab_command(args: list[str], timeout: int = 30) -> tuple[bool, str]:
    """glab 명령어 실행 헬퍼"""
    try:
        result = subprocess.run(
            ["glab"] + args, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "glab CLI not found. Install: brew install glab"
    except subprocess.TimeoutExpired:
        return False, "glab command timed out"
    except Exception as e:
        return False, str(e)


def parse_json_output(output: str) -> dict | list | None:
    """JSON 출력 파싱"""
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


# ============================================================
# CI Tools (9개)
# ============================================================


@mcp.tool()
def ci_status() -> dict:
    """
    현재 파이프라인 상태를 조회합니다.

    Returns:
        - success: 성공 여부
        - status: 파이프라인 상태 (running, success, failed, etc.)
        - pipeline_id: 파이프라인 ID
        - web_url: 파이프라인 웹 URL
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "status", "--output", "json"])

    if not success:
        return {"success": False, "status": None, "message": f"파이프라인 상태 조회 실패: {output}"}

    data = parse_json_output(output)
    if data is None:
        # JSON이 아닌 경우 텍스트 상태로 반환
        return {"success": True, "status": output, "message": output}

    return {
        "success": True,
        "status": data.get("status"),
        "pipeline_id": data.get("id"),
        "web_url": data.get("web_url"),
        "ref": data.get("ref"),
        "message": f"파이프라인 #{data.get('id')}: {data.get('status')}",
    }


@mcp.tool()
def ci_list(count: int = 10) -> dict:
    """
    최근 파이프라인 목록을 조회합니다.

    Args:
        count: 조회할 파이프라인 수 (기본값: 10)

    Returns:
        - success: 성공 여부
        - pipelines: 파이프라인 목록
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "list", "-P", str(count), "--output", "json"])

    if not success:
        return {"success": False, "pipelines": [], "message": f"파이프라인 목록 조회 실패: {output}"}

    data = parse_json_output(output)
    if data is None:
        return {"success": False, "pipelines": [], "message": "JSON 파싱 실패"}

    pipelines = []
    for p in data:
        pipelines.append({
            "id": p.get("id"),
            "status": p.get("status"),
            "ref": p.get("ref"),
            "created_at": p.get("created_at"),
            "web_url": p.get("web_url"),
        })

    return {
        "success": True,
        "pipelines": pipelines,
        "count": len(pipelines),
        "message": f"최근 {len(pipelines)}개 파이프라인 조회 완료",
    }


@mcp.tool()
def ci_jobs(status_filter: str = "") -> dict:
    """
    현재 파이프라인의 job 목록을 조회합니다.

    Args:
        status_filter: 상태 필터 (running, failed, success, pending, manual, 빈 문자열=전체)

    Returns:
        - success: 성공 여부
        - jobs: job 목록
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "get", "--output", "json"])

    if not success:
        return {"success": False, "jobs": [], "message": f"job 목록 조회 실패: {output}"}

    data = parse_json_output(output)
    if data is None:
        return {"success": False, "jobs": [], "message": "JSON 파싱 실패"}

    jobs = data.get("jobs", [])

    # 상태 필터 적용
    if status_filter:
        jobs = [j for j in jobs if j.get("status") == status_filter]

    result_jobs = []
    for j in jobs:
        result_jobs.append({
            "id": j.get("id"),
            "name": j.get("name"),
            "stage": j.get("stage"),
            "status": j.get("status"),
            "web_url": j.get("web_url"),
        })

    filter_msg = f" (필터: {status_filter})" if status_filter else ""
    return {
        "success": True,
        "jobs": result_jobs,
        "count": len(result_jobs),
        "message": f"{len(result_jobs)}개 job 조회 완료{filter_msg}",
    }


@mcp.tool()
def ci_trace(job_id: int) -> dict:
    """
    특정 job의 로그를 조회합니다.

    Args:
        job_id: job ID

    Returns:
        - success: 성공 여부
        - log: job 로그 내용
        - message: 상태 메시지
    """
    success, output = run_glab_command(["ci", "trace", str(job_id)], timeout=60)

    if not success:
        return {"success": False, "log": None, "message": f"job #{job_id} 로그 조회 실패: {output}"}

    # 로그가 너무 길면 마지막 500줄만 반환
    lines = output.split("\n")
    if len(lines) > 500:
        output = "\n".join(["... (truncated) ..."] + lines[-500:])

    return {
        "success": True,
        "job_id": job_id,
        "log": output,
        "lines": len(lines),
        "message": f"job #{job_id} 로그 조회 완료 ({len(lines)} lines)",
    }


@mcp.tool()
def ci_cancel_job(job_id: int) -> dict:
    """
    특정 job을 취소합니다.

    Args:
        job_id: 취소할 job ID

    Returns:
        - success: 성공 여부
        - job_id: job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(["api", "--method", "POST", f"projects/:fullpath/jobs/{job_id}/cancel"])

    if not success:
        return {"success": False, "job_id": job_id, "message": f"job #{job_id} 취소 실패: {output}"}

    return {
        "success": True,
        "job_id": job_id,
        "message": f"✅ job #{job_id} 취소 완료",
    }


@mcp.tool()
def ci_cancel_pipeline(pipeline_id: int = 0) -> dict:
    """
    파이프라인을 취소합니다.

    Args:
        pipeline_id: 취소할 파이프라인 ID (0이면 현재 파이프라인)

    Returns:
        - success: 성공 여부
        - pipeline_id: 파이프라인 ID
        - message: 결과 메시지
    """
    # 현재 파이프라인 ID 가져오기
    if pipeline_id == 0:
        success, output = run_glab_command(["ci", "get", "--output", "json"])
        if not success:
            return {"success": False, "pipeline_id": None, "message": f"현재 파이프라인 조회 실패: {output}"}

        data = parse_json_output(output)
        if data is None:
            return {"success": False, "pipeline_id": None, "message": "JSON 파싱 실패"}

        pipeline_id = data.get("id")

    success, output = run_glab_command(["api", "--method", "POST", f"projects/:fullpath/pipelines/{pipeline_id}/cancel"])

    if not success:
        return {"success": False, "pipeline_id": pipeline_id, "message": f"파이프라인 #{pipeline_id} 취소 실패: {output}"}

    return {
        "success": True,
        "pipeline_id": pipeline_id,
        "message": f"✅ 파이프라인 #{pipeline_id} 취소 완료",
    }


@mcp.tool()
def ci_trigger_job(job_id: int) -> dict:
    """
    수동 job을 트리거합니다.

    Args:
        job_id: 트리거할 job ID

    Returns:
        - success: 성공 여부
        - job_id: job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(["api", "--method", "POST", f"projects/:fullpath/jobs/{job_id}/play"])

    if not success:
        return {"success": False, "job_id": job_id, "message": f"job #{job_id} 트리거 실패: {output}"}

    return {
        "success": True,
        "job_id": job_id,
        "message": f"✅ job #{job_id} 트리거 완료",
    }


@mcp.tool()
def ci_run(branch: str = "") -> dict:
    """
    새 파이프라인을 시작합니다.

    Args:
        branch: 파이프라인을 실행할 브랜치 (빈 문자열이면 현재 브랜치)

    Returns:
        - success: 성공 여부
        - pipeline_id: 생성된 파이프라인 ID
        - web_url: 파이프라인 웹 URL
        - message: 결과 메시지
    """
    args = ["ci", "run"]
    if branch:
        args.extend(["--branch", branch])

    success, output = run_glab_command(args)

    if not success:
        return {"success": False, "pipeline_id": None, "message": f"파이프라인 시작 실패: {output}"}

    # 출력에서 파이프라인 ID와 URL 추출 시도
    return {
        "success": True,
        "message": f"✅ 파이프라인 시작 완료\n{output}",
    }


@mcp.tool()
def ci_retry_job(job_id: int) -> dict:
    """
    실패한 job을 재시도합니다.

    Args:
        job_id: 재시도할 job ID

    Returns:
        - success: 성공 여부
        - job_id: job ID
        - message: 결과 메시지
    """
    success, output = run_glab_command(["api", "--method", "POST", f"projects/:fullpath/jobs/{job_id}/retry"])

    if not success:
        return {"success": False, "job_id": job_id, "message": f"job #{job_id} 재시도 실패: {output}"}

    return {
        "success": True,
        "job_id": job_id,
        "message": f"✅ job #{job_id} 재시도 완료",
    }


# ============================================================
# MR Discussion Tools (3개)
# ============================================================


@mcp.tool()
def mr_get(mr_iid: int = 0) -> dict:
    """
    현재 브랜치 또는 지정 MR 정보를 조회합니다.

    Args:
        mr_iid: MR IID (0이면 현재 브랜치의 MR)

    Returns:
        - success: 성공 여부
        - mr: MR 정보
        - message: 상태 메시지
    """
    if mr_iid == 0:
        # 현재 브랜치의 MR 조회
        success, output = run_glab_command(["mr", "view", "--output", "json"])
    else:
        success, output = run_glab_command(["mr", "view", str(mr_iid), "--output", "json"])

    if not success:
        return {"success": False, "mr": None, "message": f"MR 조회 실패: {output}"}

    data = parse_json_output(output)
    if data is None:
        return {"success": False, "mr": None, "message": "JSON 파싱 실패"}

    mr_info = {
        "iid": data.get("iid"),
        "title": data.get("title"),
        "state": data.get("state"),
        "source_branch": data.get("source_branch"),
        "target_branch": data.get("target_branch"),
        "author": data.get("author", {}).get("username"),
        "web_url": data.get("web_url"),
        "has_conflicts": data.get("has_conflicts"),
        "draft": data.get("draft"),
    }

    return {
        "success": True,
        "mr": mr_info,
        "message": f"MR !{mr_info['iid']}: {mr_info['title']}",
    }


@mcp.tool()
def mr_discussions(mr_iid: int = 0, resolved_filter: str = "all") -> dict:
    """
    MR의 Discussion 전체 목록을 조회합니다 (내부적으로 pagination 처리).

    Args:
        mr_iid: MR IID (0이면 현재 브랜치의 MR)
        resolved_filter: 필터 옵션 ("all", "unresolved", "resolved")

    Returns:
        - success: 성공 여부
        - discussions: Discussion 목록
        - count: Discussion 수
        - message: 상태 메시지
    """
    # MR IID가 0이면 현재 MR의 IID를 가져옴
    if mr_iid == 0:
        mr_result = mr_get(0)
        if not mr_result["success"]:
            return {"success": False, "discussions": [], "message": mr_result["message"]}
        mr_iid = mr_result["mr"]["iid"]

    # 전체 discussion을 가져오기 위해 pagination 처리
    all_discussions = []
    page = 1
    per_page = 100

    while True:
        success, output = run_glab_command([
            "api", f"projects/:fullpath/merge_requests/{mr_iid}/discussions",
            "--paginate",
            "-X", "GET",
            "-f", f"per_page={per_page}",
            "-f", f"page={page}",
        ])

        if not success:
            if all_discussions:
                # 이미 일부 데이터를 가져왔으면 그것만 반환
                break
            return {"success": False, "discussions": [], "message": f"Discussion 조회 실패: {output}"}

        data = parse_json_output(output)
        if data is None or not isinstance(data, list):
            break

        if len(data) == 0:
            break

        all_discussions.extend(data)

        # 100개 미만이면 마지막 페이지
        if len(data) < per_page:
            break

        page += 1

    # Discussion 파싱 및 필터링
    result_discussions = []
    for d in all_discussions:
        # 시스템 노트 제외 (코드 리뷰 discussion만)
        notes = d.get("notes", [])
        if not notes:
            continue

        first_note = notes[0]

        # 시스템 노트 스킵
        if first_note.get("system", False):
            continue

        is_resolved = d.get("resolved", False)

        # 필터 적용
        if resolved_filter == "unresolved" and is_resolved:
            continue
        if resolved_filter == "resolved" and not is_resolved:
            continue

        result_discussions.append({
            "id": d.get("id"),
            "resolved": is_resolved,
            "resolvable": d.get("resolvable", False),
            "author": first_note.get("author", {}).get("username"),
            "body": first_note.get("body", "")[:200],  # 미리보기용 200자
            "created_at": first_note.get("created_at"),
            "note_count": len(notes),
            "position": first_note.get("position"),
        })

    filter_msg = ""
    if resolved_filter == "unresolved":
        filter_msg = " (미해결만)"
    elif resolved_filter == "resolved":
        filter_msg = " (해결됨만)"

    return {
        "success": True,
        "discussions": result_discussions,
        "count": len(result_discussions),
        "mr_iid": mr_iid,
        "message": f"MR !{mr_iid}의 {len(result_discussions)}개 Discussion 조회 완료{filter_msg}",
    }


@mcp.tool()
def mr_resolve_discussion(mr_iid: int, discussion_id: str) -> dict:
    """
    Discussion을 해결 처리합니다.

    Args:
        mr_iid: MR IID
        discussion_id: Discussion ID

    Returns:
        - success: 성공 여부
        - message: 결과 메시지
    """
    success, output = run_glab_command([
        "api", "--method", "PUT",
        f"projects/:fullpath/merge_requests/{mr_iid}/discussions/{discussion_id}",
        "-f", "resolved=true",
    ])

    if not success:
        return {"success": False, "message": f"Discussion 해결 실패: {output}"}

    return {
        "success": True,
        "mr_iid": mr_iid,
        "discussion_id": discussion_id,
        "message": f"✅ Discussion {discussion_id} 해결 완료",
    }


if __name__ == "__main__":
    mcp.run()
