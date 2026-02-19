# ask-yt

YouTube 내장 AI(Ask/질문하기)에게 질문하는 Claude Code 플러그인.
Playwright CDP 기반으로 YouTube Gemini AI의 응답을 자동화합니다.

## 요구사항

- **Chrome** (CDP 모드 실행 필요)
- **YouTube 로그인** (Chrome 세션에서)
- `uvx` (Python 패키지 실행)

## ⚠️ 사전 조건: Chrome CDP 활성화

플러그인 사용 전 Chrome을 CDP 포트와 함께 실행해야 합니다.

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222
```

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222
```

연결 확인:
```bash
curl -s http://localhost:9222/json/version | python3 -m json.tool
```

## 설치

```bash
# 플러그인 디렉토리에 복사
cp -r plugins/ask-yt ~/.claude/plugins/ask-yt
```

또는 Claude Code Marketplace에서 설치:
```
/marketplace install ask-yt
```

## 사용법

### Skill 사용

```
ask-yt 스킬 실행: https://www.youtube.com/watch?v=xxxxx
질문: 이 영상의 핵심 내용을 요약해줘
```

### MCP 직접 호출

```python
mcp__plugin_ask-yt_yt__ask_video(
    url="https://www.youtube.com/watch?v=xxxxx",
    question="이 영상에서 설명하는 주요 개념이 뭐야?",
    cdp_port=9222,      # 기본값
    timeout_ms=30000    # 기본값 (ms)
)
```

**반환값:**
```json
{
  "answer": "이 영상은 ...",
  "chips": ["더 자세히 설명해줘", "예시 코드 있어?"]
}
```

## 알려진 제한사항

- YouTube에서 "질문하기(Ask)" 기능을 지원하는 영상에서만 동작합니다
  - 광고, 라이브 스트림, 일부 저작권 영상은 미지원
- Chrome이 CDP 모드로 실행 중이어야 합니다 (일반 실행 모드 불가)
- YouTube에 로그인된 상태여야 합니다
- 응답은 스트리밍되므로 기본 30초 타임아웃 내에 완성되어야 합니다

## 트러블슈팅

| 에러 | 원인 | 해결 |
|------|------|------|
| `Chrome을 CDP 모드로 실행해주세요` | Chrome 미실행 또는 CDP 포트 불일치 | 위 사전 조건 참조 |
| `Ask 기능이 지원되지 않습니다` | 해당 영상에서 YouTube Ask 미지원 | 다른 영상으로 시도 |
| `응답 대기 시간 초과` | 네트워크 지연 또는 YouTube 서버 느림 | `timeout_ms=60000`으로 증가 후 재시도 |
