---
description: 기존 블로그 글 폴더를 S3에서 다운받아 로컬에서 편집하고 다시 S3에 업로드합니다. 폴더 단위 round-trip.
argument-hint: <folder name e.g. blog-2026-04-27-foo>
---

# /blogpost:update — 기존 블로그 글 편집

You are the orchestrator for the round-trip update flow. The user supplies a folder name in `$ARGUMENTS`. Pull from S3, prompt the user to edit, confirm, then push back.

## Phase 0 — Settings + folder name

1. Read `~/.claude/blogpost.local.md` (same as create). Halt with the same Korean error message if missing.
2. Capture `$ARGUMENTS` as `folder`. If empty, AskUserQuestion the user for the folder name. Validate kebab-case, no slashes.

## Phase 1 — Sync down

Resolve `<blog_folder> = ~/blog/<folder>` (default workspace).

```bash
mkdir -p ~/blog
"${CLAUDE_PLUGIN_ROOT}/scripts/sync_s3.sh" down "<folder>"
```

The script:

- runs `aws s3 sync s3://<bucket>/<prefix>/<folder>/ <blog_folder>/`
- exits non-zero if the S3 path is empty (folder doesn't exist remotely) — halt and tell the user the folder name may be wrong.

After sync, confirm `<blog_folder>/초안.md` exists.

## Phase 2 — User edit prompt (v1.0.0 fallback)

In v1.0.0 we do NOT integrate a local editor. Instead, tell the user (in Korean):

```
📥 S3에서 폴더를 받아왔습니다: <blog_folder>

다음 파일들을 자유롭게 편집하세요:
- <blog_folder>/초안.md          (글 본문)
- <blog_folder>/image/           (이미지 추가/교체/삭제)
- <blog_folder>/metadata.json    (이미지 출처/라이선스 매핑은 반드시 함께 갱신)

편집을 마치면 같은 명령을 다시 실행하면 자동으로 HTML 재생성 + S3 재업로드까지 진행됩니다:

  /blogpost:update <folder>

지금은 어떻게 할까요?
```

Use AskUserQuestion:

```
header: "다음 단계"
question: "편집은 어떻게 진행하시겠어요?"
options:
  - label: "지금 편집 끝났음 — HTML 재생성 + 업로드"
    description: "이미 파일을 수정한 상태. Phase 3-4로 진행."
  - label: "에디터에서 편집할게요 — 잠시 대기"
    description: "사용자가 직접 ~/blog/<folder>/ 안의 파일 수정. 종료 후 다시 /blogpost:update 호출하면 됨."
```

If the user picks "잠시 대기", emit:

```
✋ 편집 후 다시 실행해주세요:
  /blogpost:update <folder>
```

…and stop the command.

If the user picks "지금 편집 끝났음", proceed.

## Phase 3 — Re-render

Detect what changed via `git status`-style check on the folder (compare against the just-synced state). If `초안.md` or `image/` or `metadata.json` changed:

1. Re-spawn `blogpost-html-renderer` for `<blog_folder>` to regenerate `_render/body.html` and `_render/toc.json` against the edited content.
2. Run:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/render.py" "<blog_folder>"
   ```
3. Verify `<blog_folder>/index.html` non-empty and contains `<aside`, `<main`, `<figure` (skip `<figure` check if the post has no images).

If nothing changed, skip rendering and tell the user — but still do Phase 4 in case S3 has drift.

## Phase 4 — Sync up

Show a confirmation prompt before sync (S3 writes can overwrite). Use AskUserQuestion:

```
header: "S3 업로드"
question: "변경사항을 S3에 올릴까요?"
options:
  - label: "올린다"
    description: "aws s3 sync로 이 폴더를 s3://<bucket>/<prefix>/<folder>/ 로 업로드"
  - label: "취소"
    description: "업로드하지 않고 종료. 로컬 폴더는 유지."
```

On confirm:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/sync_s3.sh" up "<folder>"
```

## Phase 5 — Final report

```
✅ 블로그 글 업데이트 완료

- 폴더: <blog_folder>
- S3: s3://<bucket>/<prefix>/<folder>/
- 공개 URL (예상): https://<bucket>.s3.amazonaws.com/<prefix>/<folder>/index.html
- 변경된 파일: <list from diff>
```

## Hard constraints

- Settings missing → halt at Phase 0.
- S3 path empty (sync down returns 0 files) → halt, do not create empty local folder.
- Never delete the local folder automatically; user keeps the working copy.
- aws CLI failure on sync up → log the exact error and tell user to retry with `/blogpost:update <folder>` once they fix credentials.
- Image attribution in `metadata.json` is the user's responsibility during manual edits — warn them if they remove an image file but leave the metadata entry, or vice versa (Phase 3 sanity check).
