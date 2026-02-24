# notify 플러그인

Claude Code 작업 완료(`Stop`) 또는 사용자 확인 요청(`Notification`) 시 macOS 음성(TTS) + 팝업 알림을 자동 발송하는 플러그인입니다.

## 기능

- **작업 완료 알림**: Claude가 작업을 완료하면 "Glass" 사운드 + 팝업 + 음성 안내
- **확인 요청 알림**: Claude가 사용자 확인을 요청하면 "Ping" 사운드 + 팝업 + 음성 안내
- **내용 담긴 음성**: 단순 "완료" 대신 실제 작업 내용을 음성으로 읽어줌
- **4단계 fallback**: Notification message → Stop reason → transcript 파싱 → history.jsonl

> **macOS 전용**: `osascript`(팝업)와 `say`(TTS)를 사용합니다.

## 설치

### 1. Marketplace를 통한 설치

```bash
# settings.json에 추가
# ~/.claude/settings.json
{
  "notify@wogus-plugins": true
}
```

### 2. 수동 설치

```bash
# 레포지토리를 클론하거나 플러그인 디렉토리를 복사한 후
# ~/.claude/settings.json에 플러그인 활성화 추가
```

### 3. Claude Code 재시작

훅은 세션 시작 시 로드됩니다. 설치 후 **Claude Code를 재시작**해야 합니다.

```bash
# 현재 세션 종료 후
claude  # 재시작
```

### 4. 훅 로드 확인

```
/hooks
```

`Stop`, `Notification` 훅이 목록에 표시되면 설치 완료.

## 음성 설정

### 기본 음성: Yuna (한국어)

이 플러그인은 기본적으로 **Yuna** 음성을 사용합니다 (한국어 Premium Neural 음성).

#### Siri 음성은 사용할 수 없나요?

**불가능합니다.** macOS의 `say` 명령어는 시스템 TTS 엔진을 사용하며, Siri의 음성 합성 엔진에는 직접 접근할 수 없습니다. 대신 Yuna가 가장 자연스러운 한국어 음성입니다.

#### Yuna 음성 설치 확인

```bash
say -v "?" | grep Yuna
```

출력 예시: `Yuna        ko_KR    # 안녕하세요. 제 이름은 유나입니다.`

출력이 없으면 Yuna가 설치되지 않은 것입니다.

#### Yuna 음성 설치 방법

1. macOS **시스템 환경설정** → **손쉬운 사용** → **음성 콘텐츠**
2. 시스템 음성 → **Yuna** 선택 후 다운로드
3. 또는: **설정** → **접근성** → **음성 콘텐츠** → **시스템 음성** → **Yuna**

#### 다른 한국어 음성 목록

```bash
say -v "?" | grep ko_KR
```

| 음성 | 특징 |
|------|------|
| Yuna | Premium Neural (권장) |
| Eddy | 남성 |
| Flo | 여성 |
| Grandma | 할머니 |
| Grandpa | 할아버지 |
| Reed | 남성 |
| Rocko | 남성 |
| Sandy | 여성 |
| Shelley | 여성 |

#### 음성 변경 방법

`notify.sh`의 Yuna 감지 코드를 수정하세요:

```bash
# notify.sh 내 음성 선택 부분
VOICE=""
if say -v "?" 2>/dev/null | grep -q "^Rocko "; then
    VOICE="Rocko"
fi
```

## macOS 알림 권한 설정

팝업 알림이 표시되지 않으면 알림 권한이 필요합니다:

1. **시스템 환경설정** → **알림 및 집중 모드**
2. **Script Editor** (또는 터미널 앱) 찾기
3. **알림 허용** 설정

> 알림이 차단되어도 TTS 음성은 정상 작동합니다.

## 디버그 방법

### stdin 데이터 확인 (첫 실행 후)

플러그인 첫 실행 시 Claude가 전달하는 stdin 데이터가 저장됩니다:

```bash
cat /tmp/claude_notify_debug.json | python3 -m json.tool
```

이를 통해 실제 `transcript_path`, `session_id` 등의 값을 확인할 수 있습니다.

디버그 파일을 초기화하려면:

```bash
rm /tmp/claude_notify_debug.json
```

### 직접 테스트

```bash
# Stop 이벤트 시뮬레이션
echo '{"hook_event_name":"Stop","transcript_path":"","session_id":"test"}' | \
    bash plugins/notify/hooks/notify.sh
echo "Exit: $?"

# Notification 이벤트 시뮬레이션
echo '{"hook_event_name":"Notification","message":"PR 리뷰가 필요합니다","session_id":"test"}' | \
    bash plugins/notify/hooks/notify.sh
echo "Exit: $?"
```

### 음성 직접 테스트

```bash
for v in Yuna Rocko Sandy; do
    echo "Testing $v..."
    say -v "$v" "안녕하세요, 클로드 작업이 완료되었습니다"
    sleep 3
done
```

## 동작 방식

### 메시지 내용 추출 (4단계 fallback)

1. **1차**: Notification 이벤트의 `message` 필드 (가장 신뢰도 높음)
2. **1.5차**: Stop 이벤트의 `reason` 필드
3. **2차**: `transcript_path` 파일 파싱 (JSONL → 텍스트 패턴)
4. **3차**: `~/.claude/history.jsonl`에서 마지막 user prompt

### 보안

- **Shell injection 방지**: `osascript`를 Python `subprocess.Popen(['osascript', '-e', ...])` 방식으로 실행하여 backtick, `$VAR` 등의 shell 해석을 완전히 차단
- **UTF-8 안전 truncation**: `head -c` 대신 Python `[:100]`으로 문자 기준 절단

### 항상 exit 0

알림 스크립트의 실패가 Claude 작업을 중단시키지 않도록 항상 `exit 0`으로 종료합니다.

## 파일 구조

```
plugins/notify/
├── .claude-plugin/
│   └── plugin.json      # 플러그인 메타데이터
├── hooks/
│   ├── hooks.json       # Stop + Notification 훅 설정
│   └── notify.sh        # 메인 알림 스크립트
└── README.md            # 이 파일
```

## 알려진 제한사항

- macOS 전용 (Linux/Windows 미지원)
- Python3 필요 (macOS 기본 설치)
- transcript_path 포맷이 버전마다 다를 수 있음 (디버그 파일로 확인)
- SubagentStop 미포함 (서브에이전트 완료 시 알림 없음, Stop만 트리거)
