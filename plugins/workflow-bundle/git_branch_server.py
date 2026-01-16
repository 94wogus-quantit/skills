#!/usr/bin/env python3
"""
Git Local MCP Server
로컬 Git 저장소 브랜치 관리를 위한 MCP 서버

Tools:
- get_current_branch: 현재 브랜치 이름 반환
- check_branch_protection: 보호된 브랜치(main/master/staging)인지 확인
- create_feature_branch: 새 feature 브랜치 생성
- list_branches: 모든 브랜치 목록 조회
"""

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-local")

PROTECTED_BRANCHES = ["main", "master", "staging"]


def run_git_command(args: list[str]) -> tuple[bool, str]:
    """Git 명령어 실행 헬퍼"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except Exception as e:
        return False, str(e)


@mcp.tool()
def get_current_branch() -> dict:
    """현재 브랜치 이름을 반환합니다."""
    success, output = run_git_command(["branch", "--show-current"])
    if success:
        return {
            "success": True,
            "branch": output,
            "message": f"현재 브랜치: {output}"
        }
    return {
        "success": False,
        "branch": None,
        "message": f"브랜치 확인 실패: {output}"
    }


@mcp.tool()
def check_branch_protection() -> dict:
    """
    현재 브랜치가 보호된 브랜치(main/master/staging)인지 확인합니다.

    Returns:
        - branch: 현재 브랜치 이름
        - is_protected: 보호된 브랜치 여부
        - needs_new_branch: 새 브랜치 생성 필요 여부
        - message: 상태 메시지
    """
    success, branch = run_git_command(["branch", "--show-current"])

    if not success:
        return {
            "success": False,
            "branch": None,
            "is_protected": False,
            "needs_new_branch": False,
            "message": f"브랜치 확인 실패: {branch}"
        }

    is_protected = branch in PROTECTED_BRANCHES

    return {
        "success": True,
        "branch": branch,
        "is_protected": is_protected,
        "needs_new_branch": is_protected,
        "message": f"⚠️ 보호된 브랜치입니다: {branch}. 새 feature 브랜치를 생성하세요."
                   if is_protected
                   else f"✅ Feature 브랜치에서 작업 중: {branch}"
    }


@mcp.tool()
def create_feature_branch(branch_name: str) -> dict:
    """
    새 feature 브랜치를 생성하고 체크아웃합니다.

    Args:
        branch_name: 생성할 브랜치 이름 (예: feature/JIRA-123)

    Returns:
        - success: 성공 여부
        - branch: 생성된 브랜치 이름
        - message: 결과 메시지
    """
    if not branch_name:
        return {
            "success": False,
            "branch": None,
            "message": "브랜치 이름이 필요합니다."
        }

    # 브랜치 생성 시도
    success, output = run_git_command(["checkout", "-b", branch_name])

    if success:
        return {
            "success": True,
            "branch": branch_name,
            "message": f"✅ 브랜치 생성 및 체크아웃 완료: {branch_name}"
        }

    # 이미 존재하는 브랜치인 경우
    if "already exists" in output:
        # 기존 브랜치로 전환 시도
        switch_success, switch_output = run_git_command(["checkout", branch_name])
        if switch_success:
            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ 기존 브랜치로 전환: {branch_name}"
            }
        return {
            "success": False,
            "branch": None,
            "message": f"브랜치 전환 실패: {switch_output}"
        }

    return {
        "success": False,
        "branch": None,
        "message": f"브랜치 생성 실패: {output}"
    }


@mcp.tool()
def list_branches(include_remote: bool = False) -> dict:
    """
    모든 브랜치 목록을 조회합니다.

    Args:
        include_remote: 원격 브랜치 포함 여부 (기본값: False)

    Returns:
        - branches: 브랜치 목록
        - current: 현재 브랜치
        - protected: 보호된 브랜치 목록 (존재하는 것만)
    """
    args = ["branch", "-a"] if include_remote else ["branch"]
    success, output = run_git_command(args)

    if not success:
        return {
            "success": False,
            "branches": [],
            "current": None,
            "message": f"브랜치 목록 조회 실패: {output}"
        }

    branches = []
    current = None

    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("* "):
            current = line[2:]
            branches.append(current)
        elif line and not line.startswith("remotes/"):
            branches.append(line)
        elif include_remote and line.startswith("remotes/"):
            branches.append(line)

    # 존재하는 보호된 브랜치 찾기
    existing_protected = [b for b in branches if b in PROTECTED_BRANCHES]

    return {
        "success": True,
        "branches": branches,
        "current": current,
        "protected": existing_protected,
        "message": f"총 {len(branches)}개 브랜치, 현재: {current}"
    }


@mcp.tool()
def switch_branch(branch_name: str) -> dict:
    """
    지정한 브랜치로 전환합니다.

    Args:
        branch_name: 전환할 브랜치 이름

    Returns:
        - success: 성공 여부
        - branch: 전환된 브랜치 이름
        - message: 결과 메시지
    """
    success, output = run_git_command(["checkout", branch_name])

    if success:
        return {
            "success": True,
            "branch": branch_name,
            "message": f"✅ 브랜치 전환 완료: {branch_name}"
        }

    return {
        "success": False,
        "branch": None,
        "message": f"브랜치 전환 실패: {output}"
    }


if __name__ == "__main__":
    mcp.run()
