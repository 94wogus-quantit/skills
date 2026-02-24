
## 2026-02-23 - notify 플러그인: 훅 전용 최소 설계

### 결정 사항
- MCP·스킬·에이전트 없이 훅(Stop + Notification)만으로 구성된 플러그인 신규 추가
- plugins/notify/hooks/notify.sh 단일 스크립트로 팝업 + TTS 처리

### 근거
- 알림 기능은 Claude 작업 완료 후 비동기로 발송하면 충분 → MCP/스킬 과잉 설계
- Idiot Index ~1.5x (최소 설계 달성)

### osascript 실행: Python subprocess (heredoc 금지)
- 문제: Unquoted heredoc에서 `$NOTIFY_MSG` 내 backtick이 shell에 의해 명령으로 실행됨
- 해결: Python `subprocess.Popen(['osascript', '-e', script])` + sys.argv 패턴
- AppleScript 문자열 이스케이핑: `"` → `'` 치환 (backslash escape 대신)

### JSON 파싱: 단일 Python 호출 + JSON 출력
- 문제: pipe `|` 구분자 방식은 transcript_path에 `|` 포함 시 오작동
- 해결: stdin을 Python3 1회로 파싱 → JSON 출력 → 각 필드를 별도 Python 호출로 추출

### 4단계 content fallback
1. Notification `message` 필드 (인라인, 직접 제공)
2. Stop `reason` 필드 (Claude 직접 제공, transcript 파싱보다 신뢰도 높음)
3. `transcript_path` 파싱: JSONL assistant text → 텍스트 패턴 regex
4. `~/.claude/history.jsonl` user prompt (최후 수단)

### 영향받는 컴포넌트
- plugins/notify/ (신규)
- .claude-plugin/marketplace.json (v3.28.0, 10개 플러그인)
- ARCHITECTURE.md: 훅 전용 플러그인 패턴, 훅 스크립트 보안 패턴 Invariants 추가

### 주의사항
- macOS 전용 (osascript, say 명령)
- Yuna 음성 별도 다운로드 필요 (시스템 환경설정 → 접근성 → 음성 콘텐츠)
- 훅 스크립트는 항상 exit 0 (Claude 블로킹 방지)
