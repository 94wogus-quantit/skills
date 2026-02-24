#!/bin/bash
# notify.sh - Claude Code 알림 스크립트
# Stop: 작업 완료 내용 음성 읽기
# Notification: interaction 필요 시 알림
#
# 주의: set -e 미사용 (알림 스크립트는 항상 exit 0이어야 함)
# set -o noglob만 적용 (glob 확장 방지)

set -o noglob

# ─── stdin 읽기 (한 번만) ───────────────────────────────────────────
STDIN_DATA=$(cat)

# ─── 디버그 덤프 (처음 한 번만, transcript 포맷 확인용) ─────────────
DEBUG_FILE="/tmp/claude_notify_debug.json"
if [ ! -f "$DEBUG_FILE" ]; then
    echo "$STDIN_DATA" > "$DEBUG_FILE"
fi

# ─── JSON 파싱 (Python3 단일 호출, JSON 출력으로 | 구분자 문제 방지) ─
# 출력: JSON 형식으로 안전하게 파싱
PARSED=$(echo "$STDIN_DATA" | python3 -c "
import json, sys

try:
    d = json.load(sys.stdin)
except Exception:
    print(json.dumps({'hook_event': 'Stop', 'transcript_path': '', 'session_id': '', 'inline_msg': '', 'reason': ''}))
    sys.exit(0)

hook_event = d.get('hook_event_name', 'Stop')
transcript_path = d.get('transcript_path', '')
session_id = d.get('session_id', '')
# Stop/SubagentStop의 reason 필드: 작업 완료 이유 (ex. 'Task completed: PR #123 생성')
reason = d.get('reason', '')

# Notification 이벤트: stdin에서 message 필드 탐색
inline_msg = ''
if hook_event == 'Notification':
    for field in ['message', 'title', 'notification', 'text', 'content']:
        v = d.get(field, '')
        if v and isinstance(v, str) and len(v) > 5:
            inline_msg = v[:200]
            break

print(json.dumps({
    'hook_event': hook_event,
    'transcript_path': transcript_path,
    'session_id': session_id,
    'inline_msg': inline_msg,
    'reason': reason
}))
" 2>/dev/null || echo '{"hook_event":"Stop","transcript_path":"","session_id":"","inline_msg":"","reason":""}')

# JSON에서 각 필드 추출 (Python으로 안전하게)
HOOK_EVENT=$(echo "$PARSED" | python3 -c "import json,sys; print(json.load(sys.stdin).get('hook_event','Stop'))" 2>/dev/null || echo "Stop")
TRANSCRIPT_PATH=$(echo "$PARSED" | python3 -c "import json,sys; print(json.load(sys.stdin).get('transcript_path',''))" 2>/dev/null || echo "")
SESSION_ID=$(echo "$PARSED" | python3 -c "import json,sys; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null || echo "")
INLINE_MSG=$(echo "$PARSED" | python3 -c "import json,sys; print(json.load(sys.stdin).get('inline_msg',''))" 2>/dev/null || echo "")
REASON=$(echo "$PARSED" | python3 -c "import json,sys; print(json.load(sys.stdin).get('reason',''))" 2>/dev/null || echo "")

# ─── 음성 선택 (Yuna 우선, 없으면 시스템 기본) ──────────────────────
# say -v "?" | grep 으로 소리 없이 설치 여부 확인
VOICE=""
if say -v "?" 2>/dev/null | grep -q "^Yuna "; then
    VOICE="Yuna"
fi

# ─── 메시지 내용 추출 ────────────────────────────────────────────────
get_content() {
    local msg="$INLINE_MSG"

    # 1차: Notification inline message (이미 추출됨)
    if [ -n "$msg" ]; then
        echo "$msg"
        return
    fi

    # 1.5차: Stop/SubagentStop의 reason 필드 (transcript보다 신뢰도 높음)
    if [ -n "$REASON" ] && [ "$REASON" != "null" ]; then
        echo "$REASON"
        return
    fi

    # 2차: transcript_path 파일 파싱 (JSONL 시도 → 텍스트 fallback)
    if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
        msg=$(python3 -c "
import json, sys, re

transcript_path = sys.argv[1]
result = ''

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # JSONL 형식 시도 (role/content 구조)
    lines = content.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            role = d.get('role', '')
            if role == 'assistant':
                c = d.get('content', '')
                if isinstance(c, list):
                    for block in c:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            c = block.get('text', '')
                            break
                if isinstance(c, str) and len(c) > 10:
                    result = c[:200]
                    break
        except json.JSONDecodeError:
            continue

    # 텍스트 형식 fallback: Assistant: 패턴 찾기
    if not result:
        matches = re.findall(r'(?:Assistant|Claude)[:：]\s*(.+?)(?:\n\n|\Z)', content, re.DOTALL)
        if matches:
            result = matches[-1].strip()[:200]

except Exception:
    pass

print(result)
" "$TRANSCRIPT_PATH" 2>/dev/null || echo "")
    fi

    # 3차: history.jsonl에서 마지막 user prompt (해당 session)
    # 주의: history.jsonl은 사용자 요청만 기록 (assistant 응답 없음)
    # TTS: "작업 완료. [사용자의 원래 요청 내용]" 형태로 읽힘
    if [ -z "$msg" ] && [ -n "$SESSION_ID" ]; then
        msg=$(python3 -c "
import json, sys, os

history_file = os.path.expanduser('~/.claude/history.jsonl')
session_id = sys.argv[1]
result = ''

try:
    with open(history_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in reversed(lines):
        try:
            d = json.loads(line.strip())
            if d.get('sessionId', '') == session_id:
                display = d.get('display', '')
                if display:
                    result = display[:100]
                    break
        except Exception:
            continue
except Exception:
    pass

print(result)
" "$SESSION_ID" 2>/dev/null || echo "")
    fi

    echo "$msg"
}

CONTENT=$(get_content)

# ─── 알림 메시지 구성 ────────────────────────────────────────────────
if [ "$HOOK_EVENT" = "Stop" ]; then
    if [ -n "$CONTENT" ]; then
        NOTIFY_CONTENT="$CONTENT"
        TTS_MSG="작업 완료. $CONTENT"
        TITLE="Claude Code 완료"
        SOUND="Glass"
    else
        NOTIFY_CONTENT="Claude 작업이 완료되었습니다"
        TTS_MSG="Claude 작업이 완료되었습니다"
        TITLE="Claude Code 완료"
        SOUND="Glass"
    fi
elif [ "$HOOK_EVENT" = "Notification" ]; then
    if [ -n "$CONTENT" ]; then
        NOTIFY_CONTENT="$CONTENT"
        TTS_MSG="확인이 필요합니다. $CONTENT"
        TITLE="Claude Code 확인 요청"
        SOUND="Ping"
    else
        NOTIFY_CONTENT="Claude가 확인을 요청합니다"
        TTS_MSG="Claude가 확인을 요청합니다. 화면을 확인해주세요"
        TITLE="Claude Code 확인 요청"
        SOUND="Ping"
    fi
else
    NOTIFY_CONTENT="Claude 알림"
    TTS_MSG="Claude 알림"
    TITLE="Claude Code"
    SOUND="Glass"
fi

# ─── 팝업 알림 발송 (Python subprocess + sys.argv로 shell injection 완전 방지) ─
# 이유: heredoc/osascript -e 방식은 backtick, $VAR 등 shell 해석 위험
# sys.argv로 값 전달: shell expansion 후 Python이 순수 문자열로 수신
python3 -c "
import subprocess, sys

msg   = sys.argv[1] if len(sys.argv) > 1 else 'Claude 알림'
title = sys.argv[2] if len(sys.argv) > 2 else 'Claude Code'
sound = sys.argv[3] if len(sys.argv) > 3 else 'Glass'

# AppleScript 안전 처리:
#   1. 개행 제거 (AppleScript string은 단일 라인)
#   2. \" → \' 치환 (AppleScript는 backslash escape 없음, 가장 단순한 방법)
#   3. 길이 제한
msg   = msg.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace('\"', \"'\")[:200]
title = title.replace('\n', ' ').replace('\r', '').replace('\"', \"'\")[:50]

# osascript에 직접 전달 (shell 해석 없음, subprocess로 안전)
script = f'display notification \"{msg}\" with title \"{title}\" sound name \"{sound}\"'
subprocess.Popen(['osascript', '-e', script],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
" "$NOTIFY_CONTENT" "$TITLE" "$SOUND" &

# ─── TTS 음성 발송 (비동기, Python으로 문자 기준 100자 제한) ──────────
# 이유: head -c는 바이트 기준으로 한국어 UTF-8 중간 절단 발생
TTS_SHORT=$(python3 -c "import sys; print(sys.argv[1][:100])" "$TTS_MSG" 2>/dev/null || echo "$TTS_MSG")
if [ -n "$VOICE" ]; then
    say -v "$VOICE" "$TTS_SHORT" &
else
    say "$TTS_SHORT" &
fi

# 항상 성공 종료 (exit 2 는 Claude 블로킹)
exit 0
