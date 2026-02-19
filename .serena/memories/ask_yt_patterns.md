# ask-yt 플러그인: YouTube CDP 자동화 패턴 (v3.27.0)

## 핵심 아키텍처: Stateful MCP Server

```python
# 글로벌 세션 상태 - MCP 서버가 살아있는 동안 유지
_pw = None
_page: Page | None = None

# open_ask_panel() → ask_video() → close_session() 순서로 호출
```

- **멀티턴 지원**: `_pw`/`_page` 글로벌로 세션 유지
- **자동 재연결**: `_page.title()` ping으로 연결 상태 확인, 끊기면 재연결

## Chrome CDP 실행 제약

Chrome은 기본 user-data-dir에서 `--remote-debugging-port` 플래그를 차단한다:

```
오류: DevTools remote debugging requires a non-default data directory
```

**해결책**: 기존 프로필을 복사하여 비기본 경로 사용:
```bash
cp -r ~/Library/Application\ Support/Google/Chrome/Default \
      ~/Library/Application\ Support/Google/Chrome-CDP/Default
# LOCK 파일 삭제 필수
rm -f ~/Library/Application\ Support/Google/Chrome-CDP/Default/LOCK
```

## YouTube Trusted Types CSP 우회

`page.wait_for_function(JS_STRING)` → `EvalError: Trusted Type assignment` 오류.

**해결책**: JS 문자열 평가 대신 Python 폴링 루프:
```python
deadline = time.time() + timeout_ms / 1000
while time.time() < deadline:
    if len(page.query_selector_all('markdown-div')) > initial_md_count:
        break
    time.sleep(0.5)
```

## Polymer 이벤트 트리거

`page.fill()` → Polymer 웹 컴포넌트 이벤트 미트리거 → 전송 버튼 비활성화.

**해결책**:
```python
textarea.click()
page.keyboard.type(question, delay=30)  # 타이핑 딜레이로 실제 입력 시뮬레이션
page.keyboard.press('Enter')           # 전송 버튼 클릭 대신 Enter 키 사용
```

## AI 응답 완성 감지

YouTube Ask는 스트리밍 방식으로 응답. 두 단계로 완성 감지:
1. `markdown-div` 카운트 증가 → AI 응답 등장 시작
2. `button.ytwYouChatChipsDataChip` 카운트 증가 → 응답 완성 및 후속 칩 생성

## uvx + playwright 실행

```json
{
  "yt": {
    "command": "uvx",
    "args": ["--from", "mcp[cli]", "--with", "playwright", "mcp", "run", "${CLAUDE_PLUGIN_ROOT}/youtube_ask_server.py"]
  }
}
```

**중요**: `--with playwright` 없으면 `ImportError: No module named 'playwright'` 발생.

## 셀렉터 참고

| 요소 | 셀렉터 |
|------|--------|
| Ask 버튼 (직접) | `button[aria-label="질문하기"], button[aria-label="Ask"]` |
| 더보기 메뉴 | `button[aria-label="추가 작업"]` |
| 패널 열림 확인 | `ytd-engagement-panel-section-list-renderer[target-id="PAyouchat"][visibility="ENGAGEMENT_PANEL_VISIBILITY_EXPANDED"]` |
| 입력창 | `textarea.chatInputViewModelChatInput` |
| AI 응답 텍스트 | `markdown-div`의 마지막 요소 |
| 후속 칩 | `button.ytwYouChatChipsDataChip[data-disabled="false"]` |
