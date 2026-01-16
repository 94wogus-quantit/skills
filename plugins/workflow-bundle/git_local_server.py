#!/usr/bin/env python3
"""
Git Local MCP Server
로컬 Git 저장소 관리를 위한 MCP 서버

Tools (브랜치 관리):
- get_current_branch: 현재 브랜치 이름 반환
- check_branch_protection: 보호된 브랜치(main/master/staging)인지 확인
- create_feature_branch: 새 feature 브랜치 생성
- list_branches: 모든 브랜치 목록 조회
- switch_branch: 브랜치 전환

Tools (Git 작업):
- git_status: 파일 상태 확인 (staged, modified, untracked, deleted)
- git_log: 최근 커밋 히스토리 조회
- git_add: 파일 스테이징
- git_commit: 커밋 생성
- git_diff: 변경 내용 통계
- git_push: 원격 저장소 푸시 (force 옵션 지원)
- git_squash: 여러 커밋을 하나로 합치기
"""

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-local")

PROTECTED_BRANCHES = ["main", "master", "staging"]


def run_git_command(args: list[str]) -> tuple[bool, str]:
    """Git 명령어 실행 헬퍼"""
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, timeout=10
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
        return {"success": True, "branch": output, "message": f"현재 브랜치: {output}"}
    return {"success": False, "branch": None, "message": f"브랜치 확인 실패: {output}"}


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
            "message": f"브랜치 확인 실패: {branch}",
        }

    is_protected = branch in PROTECTED_BRANCHES

    return {
        "success": True,
        "branch": branch,
        "is_protected": is_protected,
        "needs_new_branch": is_protected,
        "message": f"⚠️ 보호된 브랜치입니다: {branch}. 새 feature 브랜치를 생성하세요."
        if is_protected
        else f"✅ Feature 브랜치에서 작업 중: {branch}",
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
            "message": "브랜치 이름이 필요합니다.",
        }

    # 브랜치 생성 시도
    success, output = run_git_command(["checkout", "-b", branch_name])

    if success:
        return {
            "success": True,
            "branch": branch_name,
            "message": f"✅ 브랜치 생성 및 체크아웃 완료: {branch_name}",
        }

    # 이미 존재하는 브랜치인 경우
    if "already exists" in output:
        # 기존 브랜치로 전환 시도
        switch_success, switch_output = run_git_command(["checkout", branch_name])
        if switch_success:
            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ 기존 브랜치로 전환: {branch_name}",
            }
        return {
            "success": False,
            "branch": None,
            "message": f"브랜치 전환 실패: {switch_output}",
        }

    return {"success": False, "branch": None, "message": f"브랜치 생성 실패: {output}"}


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
            "message": f"브랜치 목록 조회 실패: {output}",
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
        "message": f"총 {len(branches)}개 브랜치, 현재: {current}",
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
            "message": f"✅ 브랜치 전환 완료: {branch_name}",
        }

    return {"success": False, "branch": None, "message": f"브랜치 전환 실패: {output}"}


# ============================================================
# Git 작업 도구 (Tier 1)
# ============================================================


@mcp.tool()
def git_status() -> dict:
    """
    Git 저장소의 파일 상태를 반환합니다.

    Returns:
        - success: 성공 여부
        - staged: 스테이징된 파일 목록
        - modified: 수정된 파일 목록 (스테이징 안 됨)
        - untracked: 추적되지 않는 파일 목록
        - deleted: 삭제된 파일 목록
        - message: 상태 요약 메시지
    """
    success, output = run_git_command(["status", "--porcelain"])

    if not success:
        return {
            "success": False,
            "staged": [],
            "modified": [],
            "untracked": [],
            "deleted": [],
            "message": f"상태 확인 실패: {output}",
        }

    staged = []
    modified = []
    untracked = []
    deleted = []

    for line in output.split("\n"):
        if not line:
            continue

        # porcelain 형식: XY filename
        # X = 스테이징 영역 상태, Y = 작업 디렉토리 상태
        if len(line) < 3:
            continue

        x_status = line[0]  # 스테이징 영역
        y_status = line[1]  # 작업 디렉토리
        filename = line[3:]

        # 스테이징된 파일 (A=추가, M=수정, D=삭제, R=이름변경)
        if x_status in ["A", "M", "R"]:
            staged.append(filename)
        elif x_status == "D":
            deleted.append(filename)

        # 작업 디렉토리 수정 (스테이징 안 됨)
        if y_status == "M":
            modified.append(filename)
        elif y_status == "D" and x_status != "D":
            deleted.append(filename)

        # 추적되지 않는 파일
        if x_status == "?" and y_status == "?":
            untracked.append(filename)

    total = len(staged) + len(modified) + len(untracked) + len(deleted)
    message = f"총 {total}개 변경: staged {len(staged)}, modified {len(modified)}, untracked {len(untracked)}, deleted {len(deleted)}"

    return {
        "success": True,
        "staged": staged,
        "modified": modified,
        "untracked": untracked,
        "deleted": deleted,
        "message": message if total > 0 else "✅ 작업 디렉토리가 깨끗합니다",
    }


@mcp.tool()
def git_log(count: int = 5) -> dict:
    """
    최근 커밋 히스토리를 반환합니다.

    Args:
        count: 반환할 커밋 수 (기본값: 5)

    Returns:
        - success: 성공 여부
        - commits: 커밋 목록 [{hash, message, author, date}]
        - message: 상태 메시지
    """
    # NULL 문자를 구분자로 사용 (커밋 메시지에 | 포함 가능성 대비)
    success, output = run_git_command(
        ["log", "--format=%H%x00%s%x00%an%x00%aI", f"-n{count}"]
    )

    if not success:
        return {"success": False, "commits": [], "message": f"로그 조회 실패: {output}"}

    commits = []
    for line in output.split("\n"):
        if not line:
            continue
        parts = line.split("\x00")
        if len(parts) >= 4:
            commits.append(
                {
                    "hash": parts[0],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3],
                }
            )

    return {
        "success": True,
        "commits": commits,
        "message": f"최근 {len(commits)}개 커밋 조회 완료",
    }


@mcp.tool()
def git_add(files: str = ".") -> dict:
    """
    파일을 스테이징 영역에 추가합니다.

    Args:
        files: 추가할 파일 또는 "." (기본값: "." 전체)

    Returns:
        - success: 성공 여부
        - added_files: 추가된 파일 목록
        - message: 결과 메시지
    """
    if not files:
        return {"success": False, "added_files": [], "message": "파일을 지정해주세요"}

    # git add 실행
    success, output = run_git_command(["add", files])

    if not success:
        return {
            "success": False,
            "added_files": [],
            "message": f"스테이징 실패: {output}",
        }

    # 스테이징된 파일 목록 확인
    _, staged_output = run_git_command(["diff", "--cached", "--name-only"])
    added_files = [f for f in staged_output.split("\n") if f]

    return {
        "success": True,
        "added_files": added_files,
        "message": f"✅ {len(added_files)}개 파일 스테이징 완료",
    }


@mcp.tool()
def git_commit(message: str) -> dict:
    """
    스테이징된 변경사항을 커밋합니다.

    Args:
        message: 커밋 메시지 (필수)

    Returns:
        - success: 성공 여부
        - commit_hash: 생성된 커밋 해시
        - message: 결과 메시지
    """
    # 메시지 검증
    if not message or not message.strip():
        return {
            "success": False,
            "commit_hash": None,
            "message": "커밋 메시지가 비어있습니다",
        }

    # 스테이징된 파일 확인
    _, staged_check = run_git_command(["diff", "--cached", "--name-only"])
    if not staged_check.strip():
        return {
            "success": False,
            "commit_hash": None,
            "message": "스테이징된 파일이 없습니다. 먼저 git_add를 실행하세요.",
        }

    # 커밋 실행
    success, output = run_git_command(["commit", "-m", message.strip()])

    if not success:
        return {
            "success": False,
            "commit_hash": None,
            "message": f"커밋 실패: {output}",
        }

    # 커밋 해시 추출
    _, commit_hash = run_git_command(["rev-parse", "HEAD"])

    return {
        "success": True,
        "commit_hash": commit_hash[:8],  # 짧은 해시
        "message": f"✅ 커밋 완료: {commit_hash[:8]}",
    }


# ============================================================
# Git 작업 도구 (Tier 2)
# ============================================================


@mcp.tool()
def git_diff(staged: bool = False) -> dict:
    """
    변경 내용의 통계를 반환합니다.

    Args:
        staged: True면 스테이징된 변경만 (기본값: False)

    Returns:
        - success: 성공 여부
        - files_changed: 변경된 파일 수
        - insertions: 추가된 줄 수
        - deletions: 삭제된 줄 수
        - files: 변경된 파일 목록
        - message: 상태 메시지
    """
    # 변경된 파일 목록
    args = ["diff", "--name-only"]
    if staged:
        args.insert(1, "--staged")

    success, files_output = run_git_command(args)
    if not success:
        return {
            "success": False,
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
            "files": [],
            "message": f"diff 조회 실패: {files_output}",
        }

    files = [f for f in files_output.split("\n") if f]

    # 통계 조회
    stat_args = ["diff", "--stat"]
    if staged:
        stat_args.insert(1, "--staged")

    _, stat_output = run_git_command(stat_args)

    # 마지막 줄에서 통계 파싱: "X files changed, Y insertions(+), Z deletions(-)"
    insertions = 0
    deletions = 0
    if stat_output:
        lines = stat_output.strip().split("\n")
        if lines:
            last_line = lines[-1]
            import re

            ins_match = re.search(r"(\d+) insertion", last_line)
            del_match = re.search(r"(\d+) deletion", last_line)
            if ins_match:
                insertions = int(ins_match.group(1))
            if del_match:
                deletions = int(del_match.group(1))

    return {
        "success": True,
        "files_changed": len(files),
        "insertions": insertions,
        "deletions": deletions,
        "files": files,
        "message": f"{len(files)}개 파일, +{insertions} -{deletions}"
        if files
        else "변경 없음",
    }


@mcp.tool()
def git_push(branch: str = None, set_upstream: bool = False, force: bool = False) -> dict:
    """
    현재 브랜치를 원격 저장소에 푸시합니다.

    Args:
        branch: 푸시할 브랜치 (기본값: 현재 브랜치)
        set_upstream: -u 플래그 사용 여부 (기본값: False)
        force: --force 플래그 사용 여부 (기본값: False) ⚠️ 주의: 원격 히스토리를 덮어씁니다

    Returns:
        - success: 성공 여부
        - remote: 원격 저장소 이름
        - branch: 푸시된 브랜치
        - message: 결과 메시지
    """
    # 현재 브랜치 확인
    if not branch:
        _, branch = run_git_command(["branch", "--show-current"])
        if not branch:
            return {
                "success": False,
                "remote": None,
                "branch": None,
                "message": "현재 브랜치를 확인할 수 없습니다",
            }

    # 보호된 브랜치에 force push 방지
    if force and branch in PROTECTED_BRANCHES:
        return {
            "success": False,
            "remote": None,
            "branch": branch,
            "message": f"⚠️ 보호된 브랜치({branch})에 force push는 허용되지 않습니다",
        }

    # 푸시 명령 구성
    args = ["push"]
    if force:
        args.append("--force")
    if set_upstream:
        args.append("-u")
    args.extend(["origin", branch])

    success, output = run_git_command(args)

    if success or "Everything up-to-date" in output:
        return {
            "success": True,
            "remote": "origin",
            "branch": branch,
            "message": f"✅ 푸시 완료: origin/{branch}",
        }

    return {
        "success": False,
        "remote": None,
        "branch": branch,
        "message": f"푸시 실패: {output}",
    }


@mcp.tool()
def git_squash(commit_count: int, message: str = None) -> dict:
    """
    최근 N개의 커밋을 하나로 합칩니다 (squash).

    Args:
        commit_count: 합칠 커밋 수 (2 이상)
        message: 새 커밋 메시지 (기본값: 첫 번째 커밋 메시지 사용)

    Returns:
        - success: 성공 여부
        - commit_hash: 새로 생성된 커밋 해시
        - squashed_count: 합쳐진 커밋 수
        - message: 결과 메시지

    ⚠️ 주의: 이 작업은 히스토리를 변경합니다. 이후 force push가 필요합니다.
    """
    if commit_count < 2:
        return {
            "success": False,
            "commit_hash": None,
            "squashed_count": 0,
            "message": "최소 2개 이상의 커밋이 필요합니다",
        }

    # 현재 브랜치의 커밋 수 확인
    _, log_output = run_git_command(["rev-list", "--count", "HEAD"])
    try:
        total_commits = int(log_output)
        if commit_count > total_commits:
            return {
                "success": False,
                "commit_hash": None,
                "squashed_count": 0,
                "message": f"현재 브랜치에 {total_commits}개의 커밋만 있습니다",
            }
    except ValueError:
        pass  # 계속 진행

    # 커밋 메시지 가져오기 (지정하지 않은 경우 첫 번째 커밋 메시지 사용)
    if not message:
        _, first_msg = run_git_command(["log", f"-1", "--format=%s", f"HEAD~{commit_count - 1}"])
        message = first_msg if first_msg else "Squashed commits"

    # soft reset으로 커밋 되돌리기 (변경사항은 스테이징 유지)
    success, output = run_git_command(["reset", "--soft", f"HEAD~{commit_count}"])
    if not success:
        return {
            "success": False,
            "commit_hash": None,
            "squashed_count": 0,
            "message": f"reset 실패: {output}",
        }

    # 새 커밋 생성
    success, output = run_git_command(["commit", "-m", message])
    if not success:
        return {
            "success": False,
            "commit_hash": None,
            "squashed_count": 0,
            "message": f"커밋 실패: {output}",
        }

    # 새 커밋 해시 가져오기
    _, commit_hash = run_git_command(["rev-parse", "HEAD"])

    return {
        "success": True,
        "commit_hash": commit_hash[:8],
        "squashed_count": commit_count,
        "message": f"✅ {commit_count}개 커밋을 하나로 합침: {commit_hash[:8]}",
    }


if __name__ == "__main__":
    mcp.run()
