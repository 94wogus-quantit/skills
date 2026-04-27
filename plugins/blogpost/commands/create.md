---
description: 새 블로그 글을 작성하고 S3에 업로드합니다. 토픽을 입력하면 6-agent 파이프라인이 자료 조사 → 자료 검토 → 이미지 큐레이션 → 초안 작성 → 초안 검토 → HTML 렌더링을 수행합니다.
argument-hint: <블로그 글 토픽 / 주제 설명>
---

# /blogpost:create — 새 블로그 글 작성

You are the orchestrator for the 6-agent blog authoring pipeline. The user supplied a topic in `$ARGUMENTS`. Drive the pipeline end-to-end, ask the user only when explicitly required, and finish by syncing the entire blog folder to S3.

## Phase 0 — Settings + topic

1. Read `~/.claude/blogpost.local.md` via `Read`. The file MUST exist with YAML frontmatter at the top:
   ```yaml
   ---
   bucket: <S3 bucket name>
   prefix: <path prefix, e.g. "wogus">
   ---
   ```
   If the file is missing or either key is empty, stop and tell the user (in Korean):
   ```
   ⚠️ ~/.claude/blogpost.local.md 파일이 필요합니다.

   다음 형식으로 만들어주세요:

   ---
   bucket: arkraft-report-output
   prefix: wogus
   ---

   (bucket: 업로드할 S3 버킷, prefix: 버킷 내 폴더 prefix)
   ```
2. Capture `$ARGUMENTS` as the raw topic. If empty, ask the user via AskUserQuestion for the topic before proceeding.

## Phase 1 — Folder name

Derive a slug from the topic (kebab-case, ≤40 chars, lowercase ASCII). Today's date in `YYYY-MM-DD`.

Use `AskUserQuestion` with this single question (in Korean):

```
header: "폴더명"
question: "이 블로그 글의 작업 폴더 이름은?"
options:
  - label: "blog-{YYYY-MM-DD}-{slug}  (Recommended)"
    description: "추천 — 예시 URL과 동일한 패턴. 자동 도출된 slug 사용."
  - label: "사용자 지정"
    description: "직접 입력. AskUserQuestion에서 'Other'로 자유 입력."
```

If the user picks Recommended, use `blog-<today>-<slug>`. If the user picks 사용자 지정 / Other, use their input verbatim (validate: kebab-case, no spaces, ≤60 chars; if invalid, re-ask).

Resolve the absolute path: `<workspace_root>/<folder>` where `workspace_root` defaults to `~/blog/` (create with `mkdir -p ~/blog/` if missing). Call this `<blog_folder>` for the rest of the command.

## Phase 2 — Folder skeleton

```bash
mkdir -p "<blog_folder>"/{_source/{web,repo,refs},image,review-history,_render}
touch "<blog_folder>/초안.md" "<blog_folder>/index.html"
```

Initialize `<blog_folder>/metadata.json`:

```json
{
  "topic": "<the user's topic verbatim>",
  "tags": [],
  "created_at": "<ISO date>",
  "folder": "<folder name>",
  "images": []
}
```

If the user mentioned reference URLs in the topic (heuristic: lines starting with http), append them to `metadata.json["refs"]` so the researcher fetches them.

Initialize `<blog_folder>/outline.md` empty (researcher fills it in Phase 3).

## Phase 3 — Research loop (researcher → research-reviewer)

Loop variables: `iteration = 1`.

```
loop:
  Spawn blogpost-researcher with (blog_folder, topic, gap_notes if any, iteration)
  Spawn blogpost-research-reviewer with (blog_folder, iteration)
  Read the verdict line from review-history/research-review-<iteration>.md.
  If VERDICT: OK → break loop.
  If VERDICT: MORE_NEEDED:
    iteration += 1
    Set gap_notes from the review file's "부족한 토픽" section.
    Continue loop.
  Iteration cap: if iteration > 5, hard-break with a warning to the user.
```

## Phase 4 — Image curation

Spawn `blogpost-image-curator` with (blog_folder, topic, image_targets=auto from outline.md, iteration=1). Wait for completion.

The agent updates `metadata.json["images"]` and `image-log.md`.

## Phase 5 — Write + writing-review loop

Loop variables: `iteration = 1`.

```
loop:
  Spawn blogpost-writer with (blog_folder, iteration, revision_notes if any)
  Spawn blogpost-writing-reviewer with (blog_folder, iteration)
  Read the verdict line.
  If VERDICT: OK → break loop.
  If VERDICT: RESEARCH_GAP:
    iteration += 1
    Spawn blogpost-researcher with the gap_notes from the writing-review file.
    Spawn blogpost-research-reviewer (just a sanity check, accept whatever it returns).
    Set revision_notes = "research-gap fixed; rewrite affected sections".
    Continue loop.
  If VERDICT: IMAGE_GAP:
    iteration += 1
    Spawn blogpost-image-curator with the named image_targets from the writing-review file.
    Set revision_notes = "image-gap fixed; reference new images in affected sections".
    Continue loop.
  Iteration cap: if iteration > 6, hard-break and notify user.
```

## Phase 6 — HTML render

1. Spawn `blogpost-html-renderer` with (blog_folder). Wait for `_render/body.html` and `_render/toc.json` to exist.
2. Run the render script:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/render.py" "<blog_folder>"
   ```
   This wraps `_render/body.html` in `templates/blog.html.j2` and writes `<blog_folder>/index.html`.
3. Verify `index.html` is non-empty and contains `<aside`, `<main`, `<figure` markup. If not, halt and report.

## Phase 7 — S3 sync

Run:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/sync_s3.sh" up "<blog_folder>"
```

The script reads bucket+prefix from `~/.claude/blogpost.local.md` and runs `aws s3 sync` for the folder. Show the resulting public URL to the user (constructed as `https://<bucket>.s3.<region or s3>.amazonaws.com/<prefix>/<folder>/index.html`; if region isn't in settings, omit it from the URL and tell the user to confirm).

## Phase 8 — Final report (Korean)

```
✅ 블로그 글 작성 완료

- 폴더: <blog_folder>
- S3: s3://<bucket>/<prefix>/<folder>/
- 공개 URL (예상): https://<bucket>.s3.amazonaws.com/<prefix>/<folder>/index.html
- 파일:
  - 초안.md (N자)
  - index.html
  - image/ (N개 이미지)
  - _source/ (N개 자료)
- iteration: research N회, writing N회

수정이 필요하면 /blogpost:update <folder> 로 다시 받아 편집 후 재업로드하세요.
```

## Hard constraints

- Use `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths (scripts/, templates/) — this resolves at runtime.
- Never proceed past Phase 0 without valid settings.
- Each agent spawn is via the `Agent` tool with `subagent_type: "blogpost-<name>"`.
- Read each verdict line from disk after the agent returns; do not trust verbal summaries.
- If aws CLI fails (Phase 7), do NOT delete the local folder — the user can retry with `/blogpost:update`.
