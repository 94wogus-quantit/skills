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

## Phase 0: Chrome CDP Setup (First-time / On Error)

**Run this phase only if Chrome is not already running in CDP mode**, or if `open_ask_panel` returns a Chrome connection error.

### Why CDP Setup Is Needed

Chrome's DevTools Protocol (CDP) lets Playwright connect to an existing Chrome and automate it.
Key constraints discovered during development:

1. **Default user-data-dir is blocked**: Chrome refuses `--remote-debugging-port` when using its default data dir (`~/Library/Application Support/Google/Chrome`). A separate `--user-data-dir` is required.
2. **Login session must be preserved**: Guest mode or a fresh profile won't have YouTube login — Ask/질문하기 button only appears when logged in.
3. **Solution**: Copy the existing Chrome profile to a new directory, then launch with that as `--user-data-dir`.

### Step-by-step Setup

**Step 1**: Find available Chrome profiles.

Run:
```bash
python3 -c "
import json, os
base = os.path.expanduser('~/Library/Application Support/Google/Chrome')
for name in sorted(os.listdir(base)):
    pref = os.path.join(base, name, 'Preferences')
    if os.path.isfile(pref):
        try:
            d = json.load(open(pref))
            email = (d.get('account_info') or [{}])[0].get('email', '(없음)')
            print(f'{name:15} → {email}')
        except: pass
"
```

Ask the user which profile to use (they need to be logged into YouTube in that profile).

**Step 2**: Close Chrome completely.

Ask the user to quit Chrome (Cmd+Q), then confirm:
```bash
pkill -9 -f "Google Chrome" 2>/dev/null && echo "종료됨"
```

**Step 3**: Copy the profile to a CDP-safe directory.

```bash
PROFILE="Default"   # or "Profile 2", etc. — from Step 1
rm -rf ~/Library/Application\ Support/Google/Chrome-CDP
mkdir -p ~/Library/Application\ Support/Google/Chrome-CDP
cp -r ~/Library/Application\ Support/Google/Chrome/"$PROFILE" \
      ~/Library/Application\ Support/Google/Chrome-CDP/"$PROFILE"
cp ~/Library/Application\ Support/Google/Chrome/Local\ State \
   ~/Library/Application\ Support/Google/Chrome-CDP/ 2>/dev/null
rm -f ~/Library/Application\ Support/Google/Chrome-CDP/"$PROFILE"/LOCK
echo "복사 완료"
```

**Step 4**: Launch Chrome with CDP.

```bash
PROFILE="Default"   # same as Step 3
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome-CDP" \
  --profile-directory="$PROFILE" \
  --no-first-run \
  2>/dev/null &

# Verify CDP is open
for i in 1 2 3 4 5; do
  curl -s http://localhost:9222/json/version | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print('✅ Connected:', d['Browser'])" \
    2>/dev/null && break
  sleep 1
done
```

**Step 5**: Verify YouTube login in CDP browser.

```bash
# Check if YouTube session is active
python3 -c "
from playwright.sync_api import sync_playwright
import time
pw = sync_playwright().start()
b = pw.chromium.connect_over_cdp('http://localhost:9222')
p = b.contexts[0].new_page()
p.goto('https://www.youtube.com', wait_until='domcontentloaded')
time.sleep(2)
avatar = p.query_selector('button#avatar-btn')
print('로그인됨:', avatar is not None)
pw.stop()
"
```

If **not logged in**: Open `http://localhost:9222` in a regular browser tab, navigate to YouTube, and log in manually. Then retry.

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `DevTools remote debugging requires a non-default data directory` | Using Chrome's default data dir | Use `--user-data-dir` pointing to a COPIED profile directory |
| CDP port never opens (curl fails) | Chrome already running without CDP | `pkill -9 -f "Google Chrome"` then relaunch |
| Profile selection screen appears | Chrome can't find the profile name | Check exact profile directory name from Step 1 |
| `질문하기` button not found | Not logged in to YouTube | Verify login in Step 5 |
| `Ask 기능이 지원되지 않습니다` | Video doesn't support Ask feature | Try another video (live streams and some videos don't support Ask) |

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

On error, run Phase 0 to set up Chrome CDP, then retry.

---

## Phase 3: Ask Questions

Call `mcp__plugin_ask-yt_yt__ask_video` for each question:

```
tool: mcp__plugin_ask-yt_yt__ask_video
args:
  question: <질문 텍스트>
  timeout_ms: 30000   (기본값, 필요 시 증가)
```

Repeat without calling `open_ask_panel` again for follow-up questions.

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
