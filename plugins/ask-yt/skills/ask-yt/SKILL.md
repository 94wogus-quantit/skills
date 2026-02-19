---
name: ask-yt
description: |
  Ask YouTube's built-in Gemini AI about video content using CDP automation.
  Use when user provides a YouTube URL and wants to ask questions about the video.
  Supports multi-turn questioning: open the panel once, ask multiple questions.
  Triggers on:
  - "YouTube 영상에 대해 질문해줘" + URL
  - "이 유튜브 영상 요약해줘" + URL
  - "/ask-yt [URL] [question]"
  - User wants to query YouTube's Ask/질문하기 built-in AI feature
---

## ⚠️ Language Policy

- Output to user: **KOREAN** by default
- Phase instructions: **ENGLISH** (mandatory)

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp__plugin_ask-yt_yt__open_ask_panel` | Navigate to video URL and open the Ask panel (call once per video) |
| `mcp__plugin_ask-yt_yt__ask_video` | Ask a question in the open panel (call multiple times) |
| `mcp__plugin_ask-yt_yt__close_session` | Close the Playwright session when done |

---

## Phase 0: Chrome CDP Auto-Setup (Automated Fallback)

**Trigger this phase automatically** when:
- `open_ask_panel` returns a Chrome connection error, OR
- Starting the skill for the first time

Do NOT ask the user to run commands manually. Execute each step using Bash, and only pause to ask the user for decisions.

### Step 0-1: Check if CDP is already running

```bash
curl -s http://localhost:9222/json/version 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('connected:', d['Browser'])" 2>/dev/null \
  || echo "not_connected"
```

- If `connected:` → CDP is already running. **Skip to Phase 2.**
- If `not_connected` → proceed to Step 0-2.

### Step 0-2: List available Chrome profiles (run silently, present result to user)

```bash
python3 -c "
import json, os
base = os.path.expanduser('~/Library/Application Support/Google/Chrome')
profiles = []
for name in sorted(os.listdir(base)):
    pref = os.path.join(base, name, 'Preferences')
    if os.path.isfile(pref):
        try:
            d = json.load(open(pref))
            email = (d.get('account_info') or [{}])[0].get('email', '(없음)')
            profiles.append((name, email))
            print(f'{name}: {email}')
        except: pass
"
```

Present the profile list to the user and ask which to use via `AskUserQuestion` (one option per profile).
Default to the profile that looks like their main YouTube account.

### Step 0-3: Ask permission to kill Chrome and set up CDP

Use `AskUserQuestion` to confirm:
- "Chrome을 종료하고 CDP 모드로 재시작할까요?"
- Options: "네, 진행해주세요" / "아니요, 수동으로 할게요"

If user declines → provide manual instructions and stop.

### Step 0-4: Kill Chrome

```bash
pkill -9 -f "Google Chrome" 2>/dev/null; sleep 1; echo "종료 완료"
```

### Step 0-5: Check if Chrome-CDP directory already exists, ask whether to re-copy

```bash
PROFILE="<selected_profile>"
CDP_DIR="$HOME/Library/Application Support/Google/Chrome-CDP"
if [ -d "$CDP_DIR/$PROFILE" ]; then
  echo "exists"
else
  echo "not_exists"
fi
```

- If `exists` → Use `AskUserQuestion`:
  - "기존 Chrome-CDP 프로필이 있습니다. 재사용할까요, 아니면 최신 프로필로 다시 복사할까요?"
  - Options: "재사용 (빠름)" / "다시 복사 (최신 쿠키·세션 반영)"
- If `not_exists` → proceed to copy automatically.

### Step 0-6: Copy profile (if needed)

```bash
PROFILE="<selected_profile>"
SRC="$HOME/Library/Application Support/Google/Chrome/$PROFILE"
DST="$HOME/Library/Application Support/Google/Chrome-CDP"

rm -rf "$DST/$PROFILE"
mkdir -p "$DST"
cp -r "$SRC" "$DST/$PROFILE"
cp "$HOME/Library/Application Support/Google/Chrome/Local State" "$DST/" 2>/dev/null
rm -f "$DST/$PROFILE/LOCK"
echo "복사 완료"
```

### Step 0-7: Launch Chrome with CDP in background

```bash
PROFILE="<selected_profile>"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome-CDP" \
  --profile-directory="$PROFILE" \
  --no-first-run \
  2>/dev/null &
echo "Chrome 시작됨 (PID: $!)"
```

### Step 0-8: Verify CDP connection (retry loop, up to 10 attempts)

```bash
for i in $(seq 1 10); do
  RESULT=$(curl -s http://localhost:9222/json/version 2>/dev/null | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d['Browser'])" 2>/dev/null)
  if [ -n "$RESULT" ]; then
    echo "✅ CDP 연결 성공: $RESULT"
    break
  fi
  echo "⏳ 연결 대기 중... ($i/10)"
  sleep 1
done

if [ -z "$RESULT" ]; then
  echo "❌ CDP 연결 실패"
fi
```

- On success → proceed to Phase 2.
- On failure after 10 attempts → report error to user with the common errors table below.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| CDP 연결 실패 (10회 시도) | Chrome이 아직 시작되지 않음 | 잠시 후 재시도 또는 Step 0-4부터 반복 |
| Profile selection screen appears | 프로필 이름 불일치 | Step 0-2에서 정확한 디렉토리 이름 확인 |
| `질문하기` button not found | YouTube 로그인 안 됨 | CDP Chrome에서 youtube.com에 직접 로그인 |
| `Ask 기능이 지원되지 않습니다` | 해당 영상 미지원 | 다른 영상으로 시도 (라이브 스트림 등 불가) |

---

## Phase 1: Input Collection

Collect the following from the user:

1. **YouTube URL** — must be `https://www.youtube.com/watch?v=...`
2. **Question(s)** — what to ask the YouTube AI

If either is missing, use `AskUserQuestion`.

---

## Phase 2: Open Panel

Call `mcp__plugin_ask-yt_yt__open_ask_panel` once per video:

```
tool: mcp__plugin_ask-yt_yt__open_ask_panel
args:
  url: <YouTube URL>
  cdp_port: 9222      (기본값)
  timeout_ms: 30000   (기본값)
```

**On connection error** → immediately run Phase 0 (automated setup), then retry `open_ask_panel`.

---

## Phase 3: Ask Questions

Call `mcp__plugin_ask-yt_yt__ask_video` for each question:

```
tool: mcp__plugin_ask-yt_yt__ask_video
args:
  question: <질문 텍스트>
  timeout_ms: 30000   (기본값, 필요 시 증가)
```

Repeat without calling `open_ask_panel` again for follow-up questions on the same video.

---

## Phase 4: Display Result

Format and display the answer to the user.

**출력 형식**:

```markdown
## YouTube AI 답변

{answer}

---

### 💡 추천 후속 질문

- {chip_1}
- {chip_2}
- {chip_3}
```

- If `chips` is empty, omit the "추천 후속 질문" section.
- If the user wants to ask more questions, loop back to Phase 3.
- When done, call `mcp__plugin_ask-yt_yt__close_session` to clean up.
