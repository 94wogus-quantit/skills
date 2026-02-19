---
name: ask-yt
description: Ask YouTube's built-in Gemini AI about video content using CDP automation. Use when user provides a YouTube URL and wants to ask questions about the video. Supports multi-turn questioning: open the panel once, ask multiple questions. Triggers on: "YouTube 영상에 대해 질문해줘" + URL, "이 유튜브 영상 요약해줘" + URL, "/ask-yt [URL] [question]", User wants to query YouTube's Ask/질문하기 built-in AI feature
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

**After successful open_ask_panel**, initialize the JSONL log file using Bash:

```bash
python3 -c "
import re, json, sys
url = sys.argv[1]
video_id = re.search(r'[?&]v=([^&]+)', url).group(1)
filename = f'YT_{video_id}_raw.jsonl'
open(filename, 'w').close()  # truncate/create fresh
print(filename)
" "<YouTube URL>"
```

Save the returned filename (e.g. `YT_EQ-Rnx-k-Ec_raw.jsonl`) — use it in every Phase 4 append step.

---

## Phase 3: Complete Video Dissection

**Goal**: Ask enough questions that someone who reads the final document does NOT need to watch the video. Cover every section, every claim, every example, every demo.

Target: **25–30 questions** total. Run autonomously without waiting for user input.

---

### Step 3-1: Structure Mapping (ALWAYS ask these 2 first)

**Q1 — Full outline:**
```
이 영상의 전체 목차를 타임스탬프와 함께 알려줘.
주요 섹션, 소주제, 각 섹션에서 다루는 핵심 내용을 빠짐없이 정리해줘.
```

**Q2 — Speaker & context:**
```
발표자는 누구이고, 이 발표의 배경(행사명, 개최 맥락, 청중)은 무엇인지 알려줘.
발표자의 전문성과 이 발표를 하게 된 계기도 포함해줘.
```

---

### Step 3-2: Section-by-Section Excavation

From the outline in Q1, identify every major section. For EACH section, ask ALL of the following sub-questions (adapt wording to use exact section names):

**Sub-question A — Verbatim detail:**
```
[섹션명] 부분에서 발표자가 정확히 어떤 말을 했는지 최대한 자세히 알려줘.
구체적인 발언, 예시, 비유, 스토리를 모두 포함해서 설명해줘.
```

**Sub-question B — Data & evidence:**
```
[섹션명]에서 언급된 구체적인 수치, 통계, 사례, 실험 결과가 있으면 전부 알려줘.
```

**Sub-question C — Demos & visuals (if applicable):**
```
[섹션명]에서 화면에 보여준 시연, 코드, 다이어그램, 또는 실시간 데모가 있었으면 설명해줘.
```

Skip Sub-question C if the section clearly has no demo/visual component.

---

### Step 3-3: Cross-Cutting Deep Dives

After all sections are covered, ask these regardless of topic:

**Terminology sweep:**
```
이 영상에서 발표자가 새롭게 정의하거나 독특하게 사용한 용어나 개념이 있어?
각각 발표자의 정의를 그대로 설명해줘.
```

**Most controversial claim:**
```
이 영상에서 가장 논쟁적이거나 반직관적인 주장은 무엇이고,
발표자는 그 근거로 무엇을 제시했어?
```

**Audience Q&A (if exists):**
```
발표 후 청중 질문이나 Q&A 세션이 있었어? 있었다면 어떤 질문과 답변이 오갔는지 알려줘.
```

**Completeness check:**
```
지금까지 내가 묻지 않은 중요한 내용이 이 영상에 남아 있어?
있다면 무엇인지 알려줘.
```

---

### Step 3-4: Chain Follow-ups (run after EVERY answer throughout)

After each answer, scan for these and immediately ask if found:

| Trigger | Follow-up pattern |
|---------|-------------------|
| Named tool/product/company | `"[name]"이 구체적으로 무엇인지, 어떻게 작동하는지 설명해줘` |
| Number/stat without context | `"[stat]"이라는 수치의 출처와 의미를 더 자세히 설명해줘` |
| "~하면 된다" without how | `"[claim]"을 실제로 어떻게 하는지 단계별로 설명해줘` |
| Comparison A vs B | `[A]와 [B]의 차이를 더 구체적으로 설명해줘. 언제 어떤 걸 선택해야 해?` |
| Failure/risk mentioned | `[failure case]가 실제로 발생한 사례나 그 원인을 더 자세히 설명해줘` |
| Chips signal new topic | Use the chip text as the basis for a targeted question |

**Rules:**
- Use EXACT quotes and terms from the previous answer — never ask generically
- Never re-ask something already answered
- Chain follow-ups take priority over moving to the next section if an answer raises something significant

---

### Step 3-5: Termination

Stop when:
- All sections from the outline are excavated AND cross-cutting questions are done, OR
- **Hard limit: 30 questions**

On termination → call `close_session` → proceed to **Phase 5**.

---

## Phase 4: Display, Append & Loop

After each `ask_video` call:

**Step 4-1: Show answer to user**

```
**[Q{n}]** {question}

{answer}
```

**Step 4-2: Append to JSONL immediately**

Run this Bash command right after displaying the answer (replace `{n}`, `{question}`, `{answer}`, `{chips_json}`, `{jsonl_file}` with actual values):

```bash
python3 - <<'PYEOF'
import json

entry = {
    "q_num": {n},
    "question": {question_as_json_string},
    "answer": {answer_as_json_string},
    "chips": {chips_as_json_array}
}
with open("{jsonl_file}", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print(f"Q{n} 저장 완료")
PYEOF
```

- `{question_as_json_string}`: the question string wrapped in `json.dumps()` style (properly escaped)
- `{answer_as_json_string}`: the answer string properly escaped
- `{jsonl_file}`: the filename initialized in Phase 2

**Step 4-3: Loop**

Immediately return to Phase 3 (Step 3-2 or 3-4) to determine the next question. Do NOT wait for user input. Keep the chain running autonomously until the termination condition.

---

## Phase 5: Generate Complete Video Report

After closing the session, read the JSONL log and write a document comprehensive enough to **fully replace watching the video**.

**Step 5-1: Read all Q&A from JSONL**

```bash
python3 -c "
import json
with open('{jsonl_file}', encoding='utf-8') as f:
    entries = [json.loads(line) for line in f if line.strip()]
print(f'총 {len(entries)}개 Q&A 로드됨')
for e in entries:
    print(f\"Q{e['q_num']}: {e['question'][:60]}...\")
"
```

Verify all entries are present. If any are missing, re-ask those questions via `ask_video` and append manually.

**Step 5-2: Determine report filename**

```bash
python3 -c "
import re, sys
url = sys.argv[1]
video_id = re.search(r'[?&]v=([^&]+)', url).group(1)
print(f'YT_{video_id}_REPORT.md')
" "<YouTube URL>"
```

**Step 5-3: Write the document**

Use the Write tool to create `{report_filename}` in the current working directory. Use ALL entries from the JSONL — never truncate or summarize Q&A content.

**문서 형식**:

````markdown
# {영상 제목} — 완전 해설

> **영상**: {url}
> **발표자**: {speaker name & title}
> **행사**: {event name & date if known}
> **작성일**: {YYYY-MM-DD}
> **분석 질문 수**: {n}개

---

## 한눈에 보기 (Executive Summary)

{영상 전체를 3-5 단락으로 압축. 발표의 핵심 주장, 근거, 결론을 포함.
이 섹션만 읽어도 발표의 80%를 파악할 수 있어야 함.}

---

## 목차

{Q1에서 얻은 타임스탬프 기반 목차를 그대로 재현}

---

## 발표자 & 배경

{Q2 내용. 발표자 소개, 행사 맥락, 발표 동기}

---

## 섹션별 상세 해설

### 1. {섹션명} ({timestamp 범위})

{해당 섹션의 Sub-question A~C 답변을 통합하여 서술.
발표자의 발언을 최대한 재현하되 읽기 쉽게 구조화.
구체적 수치, 예시, 비유를 모두 포함.
데모가 있었으면 "[시연]" 블록으로 표시.}

> **[시연]** {데모 내용 설명}

### 2. {섹션명} ({timestamp 범위})

{...}

(모든 섹션 빠짐없이 포함)

---

## 핵심 용어 사전

| 용어 | 발표자의 정의 |
|------|-------------|
| {term 1} | {definition} |
| {term 2} | {definition} |

---

## 가장 논쟁적인 주장

> **주장**: {controversial claim 원문}

**발표자의 근거:**
{evidence provided}

**비판적 고려:**
{limitations or counterpoints surfaced during questioning}

---

## Q&A 세션 요약

{청중 질문이 있었으면 Q&A 형식으로 재현. 없으면 이 섹션 생략.}

---

## 실전 적용 가이드

### 즉시 실행 (오늘부터)
- {액션 1}
- {액션 2}
- {액션 3}

### 중기 변화 (1-6개월)
- {변화 1}
- {변화 2}

### 큰 방향성 (장기)
- {방향 1}

---

## 핵심 명언

> "{exact quote 1}" — {speaker}

> "{exact quote 2}" — {speaker}

---

## 남은 질문들

{영상에서 다루지 않았거나 답하지 않은 중요한 질문들. 시청자가 추가로 탐구할 주제.}
````

**Rules:**
- 섹션별 상세 해설: 발표자의 실제 발언을 최대한 재현 — 요약이 아니라 재현
- 수치·사례·비유 전부 포함, 절대 생략하지 말 것
- Chip 제안은 문서에 포함하지 않음 (UI artifact)
- 질문이 3개 미만이면 이 포맷 대신 단순 Q&A 나열로 대체

**Step 5-3: Notify user**

Tell the user: `📄 영상 완전 해설 문서가 저장되었습니다: {filename}`
