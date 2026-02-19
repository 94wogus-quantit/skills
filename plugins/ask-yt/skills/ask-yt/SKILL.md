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

## Phase 3: Deep-Dive Questioning Loop

Execute a chain questioning strategy: **every answer seeds the next question**. Do NOT ask generic questions — always base the next question on specific content from the previous answer.

### Step 3-1: Opening (2 questions)

Ask these two questions first to map the territory:

1. `이 영상의 핵심 내용을 전체적으로 요약해줘` — broad map of the video
2. Based on the summary answer: pick the **single most surprising or counterintuitive claim** and ask specifically about it

### Step 3-2: Answer Analysis (run after EVERY answer)

After receiving each answer, extract:

| Element | What to look for |
|---------|-----------------|
| **Named claim** | A specific assertion that could be challenged or expanded |
| **Unexplained mechanism** | Something stated as fact but without "how" |
| **Specific term/concept** | A named methodology, framework, or proper noun |
| **Implied consequence** | An outcome mentioned but not fully explored |
| **Chip hints** | The returned chips often signal important untouched topics |

Rank these by how much depth they could yield. Pick the TOP ONE and go to Step 3-3.

### Step 3-3: Follow-up Question Formulation

Formulate the next question using EXACT terms and quotes from the previous answer. Choose one pattern:

| Pattern | Template |
|---------|----------|
| **Mechanism** | `앞서 "[exact term]"을 언급했는데, 이게 실제로 어떻게 동작하는지 메커니즘을 구체적으로 설명해줘` |
| **Evidence** | `"[specific claim]"의 구체적인 수치, 사례, 또는 실험 결과가 있어?` |
| **Implication** | `[concept]이 실제 [개발자/기업/학생]에게 어떤 구체적인 변화를 요구하는지 설명해줘` |
| **Counter** | `[claim]에 반하는 사례나 이 주장의 한계는 어떤 게 있어?` |
| **Connection** | `앞서 말한 [topic A]와 [topic B]가 실제로 어떻게 연결되는지 설명해줘` |
| **Drill-down** | `[specific sub-topic from answer]에 대해 훨씬 더 자세히 설명해줘` |

**NEVER ask a question already answered. NEVER ask a generic question like "더 설명해줘" without anchoring to specific content.**

### Step 3-4: Loop Termination

Stop the loop when:
- **12+ questions asked** AND all major themes have at least one deep-dive follow-up, OR
- **Hard limit: 15 questions**
- Last 2 consecutive answers yielded no new concepts (diminishing returns)

On termination → call `close_session` → proceed to **Phase 5**.

---

## Phase 4: Display & Loop

After each `ask_video` call:

1. Show the answer to the user in this compact format:

```markdown
**[Q{n}]** {question}

{answer}
```

2. Immediately return to **Phase 3, Step 3-2** to analyze and formulate the next question.
3. Do NOT wait for user input between questions — keep the chain moving autonomously.
4. When the termination condition in Step 3-4 is met, call `close_session` and proceed to Phase 5.

---

## Phase 5: Generate Insight Document

After closing the session, compile all Q&A into a structured insight document.

**Step 5-1: Determine file name**

Extract the video ID from the URL:

```python
import re
video_id = re.search(r'[?&]v=([^&]+)', url).group(1)
filename = f"YT_{video_id}_INSIGHTS.md"
```

**Step 5-2: Write the document**

Use the Write tool to create `{filename}` in the current working directory.

**문서 형식**:

```markdown
# YouTube AI 인사이트

> **영상**: {url}
> **일시**: {YYYY-MM-DD}
> **질문 수**: {n}개 (심층 체인 질문)

---

## Q1. {question_1}

{answer_1}

---

## Q2. {question_2}

{answer_2}

(모든 Q&A 쌍 포함 — 생략하지 말 것)

---

## 핵심 주제별 인사이트

### {주제 1: 자동 추출}
{주제 1에 해당하는 Q&A들을 종합한 심층 분석, 2-4 단락}

### {주제 2}
{...}

(주요 주제 3-5개)

---

## 실전 적용 가이드

- **당장 할 수 있는 것**: {즉시 실행 가능한 액션 3개}
- **중기적으로 바꿔야 할 것**: {3-6개월 내 변화 2-3개}
- **장기적으로 고려할 것**: {큰 방향성 1-2개}

---

## 핵심 명언 & 개념

> "{영상에서 나온 인상적인 발언 1}"

> "{인상적인 발언 2}"

- **[핵심 개념 1]**: {한 줄 정의}
- **[핵심 개념 2]**: {한 줄 정의}
```

**Rules:**
- Include ALL Q&A pairs verbatim — do NOT summarize or truncate them
- Omit chip suggestions (UI artifacts)
- "핵심 주제별 인사이트": group related Q&As by theme and synthesize — this is the main analytical value
- "실전 적용 가이드": concrete, actionable — no vague statements
- "핵심 명언 & 개념": extract exact quotes and define key terms introduced in the video
- If fewer than 3 questions were asked, omit everything except Q&A pairs and a brief 종합 인사이트 section

**Step 5-3: Notify user**

Tell the user: `📄 인사이트 문서가 저장되었습니다: {filename}`
