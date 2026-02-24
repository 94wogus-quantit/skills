
## 2026-02-23 - 훅 전용 플러그인 패턴 (notify 플러그인)

### 패턴 설명
MCP·스킬 없이 hooks/hooks.json + hooks/notify.sh만으로 구성된 최소 플러그인 구조.
Claude Code Stop/Notification 이벤트에 반응하여 macOS 팝업 + TTS 알림 발송.

### 파일 구조
```
plugins/notify/
├── .claude-plugin/plugin.json
├── hooks/
│   ├── hooks.json   # Stop + Notification 훅 설정
│   └── notify.sh    # 핵심 알림 스크립트
└── README.md
```

### hooks.json wrapper 포맷 (플러그인 전용)
```json
{
  "description": "설명",
  "hooks": {
    "Stop": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/notify.sh", "timeout": 10}]}],
    "Notification": [{"matcher": "*", "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/notify.sh", "timeout": 10}]}]
  }
}
```

### osascript 보안 패턴 (shell injection 방지)
```python
# ✅ 안전: Python subprocess + sys.argv (shell interpretation 없음)
import subprocess
msg = msg.replace('\n', ' ').replace('"', "'")[:200]
script = f'display notification "{msg}" with title "{title}" sound name "{sound}"'
subprocess.Popen(['osascript', '-e', script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ❌ 위험: heredoc 방식 (backtick injection 가능)
# osascript << APPLESCRIPT
# display notification "$NOTIFY_MSG"
# APPLESCRIPT
```

### stdin JSON 파싱 패턴 (pipe 안전)
```bash
# Python3 단일 호출로 JSON 파싱 후 JSON 출력
PARSED=$(echo "$STDIN_DATA" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps({...}))
")
# 각 필드를 별도 Python 호출로 추출 (pipe 구분자 충돌 방지)
FIELD=$(echo "$PARSED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('field',''))")
```

### UTF-8 안전 truncation
```python
# ✅ 안전: Python character-based
text[:100]

# ❌ 위험: head -c (byte-based, 한국어 깨짐)
# echo "$text" | head -c 200
```

### 항상 exit 0 (Claude 블로킹 방지)
```bash
# 모든 훅 스크립트의 마지막 라인
exit 0
```

### 사용 사례
- 작업 완료 알림 (Stop 훅)
- 사용자 확인 요청 알림 (Notification 훅)
- macOS 전용 시스템 알림

### 주의사항
- AppleScript는 `\"` 이스케이프를 지원하지 않음 → `"` → `'` 치환 사용
- TTS `say -v Yuna`: 한국어 Premium Neural. 미설치 시 시스템 기본 음성 fallback
- timeout: 10으로 설정 (Claude 블로킹 방지)
