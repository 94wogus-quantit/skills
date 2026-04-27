# blogpost

다중 에이전트 블로그 작성 + 이미지 큐레이션 + S3 동기화 플러그인.

`/blogpost:create <토픽>` 한 번이면 다음을 자동으로 처리합니다:

1. **자료 조사** — 웹 검색·페치 + 로컬 repo 그렙으로 `_source/{web,repo,refs}/`에 자료 적재
2. **자료 검토** — 부족한 토픽이 있으면 다시 자료 조사 (loop)
3. **이미지 큐레이션** — 토픽에 맞는 CC 라이선스 이미지를 web에서 검색 → `curl`로 `image/`에 다운로드 → 출처/라이선스를 `metadata.json`에 기록
4. **초안 작성** — `_source/` + outline + image refs로 `초안.md` 작성
5. **초안 검토** — 자료 미비 / 이미지 미비 / OK 판정 (loop으로 4·3 단계로 회귀)
6. **HTML 렌더** — html-renderer 에이전트가 `_render/body.html` + `_render/toc.json` 생성 → `render.py`가 Jinja layout 적용 → `index.html`
7. **S3 sync** — `aws s3 sync`로 폴더째 업로드

`/blogpost:update <폴더명>`으로 기존 글 폴더를 S3에서 받아와 편집 후 다시 업로드할 수 있습니다.

## 설치

이 plugin은 wogus-plugins marketplace를 통해 자동 설치됩니다. 별도의 의존성:

- **aws CLI** — `aws s3 sync`에 사용. `command -v aws`로 설치 확인.
- **curl** — 이미지 다운로드에 사용.
- **Python 3 + jinja2** — `pip install jinja2`. `render.py`가 사용.

## 설정 — `~/.claude/blogpost.local.md`

전역 설정 파일을 직접 만들어주세요. **저장소에 체크인되지 않는 사용자별 파일**이며 자동 생성되지 않습니다.

```markdown
---
bucket: arkraft-report-output
prefix: wogus
---

# blogpost — 사용자 설정

업로드 대상 S3 위치만 명시. (이 파일 본문은 자유 메모용 — plugin은 frontmatter만 읽습니다.)
```

| 필드     | 필수 | 설명 |
|---------|------|------|
| bucket  | O    | 업로드할 S3 버킷 이름. 예: `arkraft-report-output` |
| prefix  | O    | 버킷 내 경로 prefix. 슬래시 없이. 예: `wogus` |

업로드 결과 URL 패턴:

```
https://<bucket>.s3.amazonaws.com/<prefix>/<folder>/index.html
```

예시:

```
https://arkraft-report-output.s3.us-east-1.amazonaws.com/wogus/blog-2026-04-23-ai-agent-design/index.html
```

## 사용법

### 새 글 작성

```
/blogpost:create AI 에이전트 설계 패턴 — 자료조사부터 라이프사이클까지
```

플러그인이 폴더 이름을 `blog-{YYYY-MM-DD}-{slug}` 형식으로 추천합니다 (AskUserQuestion으로 변경 가능). 작업 폴더 기본 위치는 `~/blog/<folder>/` 이며 `BLOGPOST_WORKSPACE` 환경변수로 변경 가능합니다.

### 기존 글 수정

```
/blogpost:update blog-2026-04-23-my-topic
```

S3에서 폴더를 받아와 `~/blog/<folder>/` 에 풀어줍니다. 사용자가 직접 `초안.md` / `image/` / `metadata.json`을 편집한 뒤 같은 명령을 다시 실행하면 HTML 재생성 + 재업로드까지 자동 진행됩니다.

> **v1.0.0 제한사항**: 로컬 에디터 자동 통합은 없습니다. 사용자가 수동으로 편집한 뒤 다시 명령을 실행하는 round-trip 방식입니다. 이미지를 추가/삭제할 경우 반드시 `metadata.json["images"]` 매핑도 함께 갱신해야 라이선스 표기가 정확하게 유지됩니다.

## 폴더 구조 (런타임에 생성됨)

```
<blog_folder>/
├── _source/
│   ├── web/         # web fetch 결과 (markdown 형식)
│   ├── repo/        # 로컬 repo 그렙 결과
│   └── refs/        # 사용자 지정 참고 URL 페치 결과
├── image/           # 본문에 임베드된 이미지 (CC 라이선스만)
├── review-history/  # 각 iteration의 reviewer 판정 로그
├── _render/
│   ├── body.html    # html-renderer 에이전트 산출물 (HTML body 조각)
│   └── toc.json     # TOC 사이드바 데이터
├── outline.md       # researcher가 도출한 섹션 개요
├── metadata.json    # 제목/태그/생성일 + images 매핑 (filename, source_url, license, attribution)
├── 초안.md           # 메인 markdown 초안 (writer 산출물)
└── index.html       # 최종 HTML (render.py 산출물; S3 업로드 대상)
```

S3 sync 시 `_source/`, `_render/`, `review-history/`는 업로드에서 제외됩니다 (작업 산출물; 결과 호스팅에는 불필요). 다음만 업로드됩니다:

- `초안.md`, `outline.md`, `metadata.json`
- `image/` 디렉토리
- `index.html`

## 이미지 라이선스 정책 (HARD)

- 사용 가능: **Unsplash** (Unsplash License), **Pexels** (Pexels License), **Wikimedia Commons** (CC0 / CC-BY / CC-BY-SA), 기타 CC0/CC-BY/Public Domain 명시 출처
- 사용 금지: Google Images 결과물(원본 라이선스 미확인), 워터마크 stock 이미지, 기업 마케팅 이미지(라이선스 명시 없는 경우), **라이선스를 확인할 수 없는 모든 이미지**
- 출처는 `metadata.json["images"]`의 `source_url`, `license`, `attribution`에 기록되며 `index.html`의 `<figcaption>`에 자동 노출됩니다.

이미지 큐레이션 에이전트 (`blogpost-image-curator`)가 적합한 CC 이미지를 찾지 못한 경우 해당 섹션은 이미지 없이 진행되며 `review-history/image-log.md`에 기록됩니다.

## 에이전트 구성

| 에이전트 | 역할 |
|---------|------|
| blogpost-researcher | 웹/repo/refs 자료 수집 → `_source/` 적재 + outline.md 갱신 |
| blogpost-research-reviewer | `_source/` 점검 → MORE_NEEDED / OK 판정 |
| blogpost-image-curator | CC 이미지 검색·다운로드 → `image/` 적재 + metadata.json 갱신 |
| blogpost-writer | `_source/` + outline + images → `초안.md` 작성 |
| blogpost-writing-reviewer | `초안.md` 점검 → RESEARCH_GAP / IMAGE_GAP / OK 판정 |
| blogpost-html-renderer | `초안.md` + images → enriched `_render/body.html` + `_render/toc.json` (figure/callout/section semantics 부여) |

`render.py`는 markdown→HTML 1:1 변환을 하지 않습니다. html-renderer 에이전트가 의미 구조를 부여한 HTML 조각을 `_render/body.html`에 작성하면, `render.py`는 이를 Jinja 레이아웃에 wrap만 합니다.

## 트러블슈팅

| 증상 | 원인 / 해결 |
|------|------------|
| `~/.claude/blogpost.local.md 파일이 필요합니다` | 위 "설정" 섹션대로 파일 생성. |
| `aws CLI가 설치되어 있지 않습니다` | `brew install awscli` (macOS) 또는 https://aws.amazon.com/cli/ 참고. AWS 자격증명도 별도 필요 (`aws configure`). |
| `S3에서 받아올 파일이 없습니다` (update) | 폴더 이름이 정확한지 확인. `aws s3 ls s3://<bucket>/<prefix>/` 로 직접 조회 가능. |
| HTML 렌더 결과 빈 화면 | `_render/body.html`이 비어 있는지 확인. html-renderer 에이전트 재실행 필요. |
| 이미지가 깨져 보임 | `metadata.json["images"][].filename`과 실제 파일명이 일치하는지 확인. |

## 스모크 테스트

번들된 픽스처로 `render.py`만 즉시 검증할 수 있습니다:

```bash
cd plugins/blogpost
python scripts/render.py scripts/test_fixture
# OK: wrote scripts/test_fixture/index.html (...)
```

생성된 `scripts/test_fixture/index.html`을 브라우저로 열면 좌측 floating TOC + 본문 + figure(이미지+caption)가 보이면 정상입니다.

## 스코프 외 (v1.0.0)

- AI 이미지 생성 (Midjourney/DALL-E 등)
- 로컬 에디터 자동 통합 (vim/code launch)
- CDN / CloudFront 캐시 invalidation
- 다중 언어 동시 편성
- 이미지 후처리 (resize / crop / webp 변환)
