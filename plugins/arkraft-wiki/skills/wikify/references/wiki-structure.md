# arkraft-wiki — section structure & lifecycle

This reference documents the invariants of the arkraft-wiki content tree. Use it to inform the choo-choo task description so the Ralph Loop's Phase 1 Clarify and Phase 3 Acceptance Criteria can pin down placement decisions accurately.

## Top-level section taxonomy

```
content/
├── start/        — 제품 이해 기본 문서 (vision, philosophy, glossary, system-overview, contributing)
├── market/       — 세일즈, 고객, 경쟁 (pipeline, market-overview, objections, partnerships)
├── tech/         — 기술 도메인 지식
│   ├── agents/   — AI 에이전트별 (alpha, insight, portfolio, report, data, ...)
│   ├── quant/    — 퀀트 / 금융 도메인 지식 (전략, 백테스트, 리스크, 포트폴리오)
│   └── engineering/ — 개발 프로세스, 인프라, 시스템 구성
├── discussions/  — 논의 중 (분석, 제안, RFC) — 결정 전
├── decisions/    — 결정 완료 ADR (불변)
└── timeline/     — 이벤트 (decision / release / sales / milestone / incident)
```

## Lifecycle: discussions → decisions

```
open question
  ↓
discussions/{slug}/index.md     (status: active | proposed)
  ↓ (decision lands)
decisions/{slug}/index.md       (status: decided, immutable)
  ↓ (implementation rolls out)
[supersede earlier ADR if applicable, status: superseded]
```

- **분석 / 제안 / RFC** → `discussions/`
- **결정 확정** → `decisions/`
- **기술 지식 / 가이드** → `tech/{agents|quant|engineering}/...`

## Folder pattern (enforced by `enforce-folder-doc.sh` + `validate-depth.sh`)

Every page is `dir/index.md`. Allowed depths under `content/`:

| Depth | Pattern | Example |
|-------|---------|---------|
| 1 | `content/{section}/index.md` | `content/tech/index.md` |
| 2 | `content/{section}/{component}/index.md` | `content/tech/agents/alpha/index.md` |
| 3 | `content/{section}/{component}/{grouping}/index.md` | `content/tech/agents/alpha/history/index.md` |
| 4 | `content/{section}/{component}/{grouping}/{slug}/index.md` | `content/tech/agents/alpha/history/negative-constraints/index.md` |

≥ 5 folders deep → blocked by `validate-depth.sh`.

Exempt: `content/index.md` (root index).

## status frontmatter (lifecycle-tracked pages)

Files under `content/discussions/...` and `content/tech/{section}/{component}/{slug}/...` must include:

```html
<!-- status: active -->
```

Allowed values: `active | decided | shipped | superseded | archived`.

Exempt: `content/{start,market,timeline}/**`, section/sub-section/component landing pages (`{section}/index.md`, `{section}/{component}/index.md` directly).

`validate-content-placement.sh` blocks Write/Edit on tracked files when status is missing.

## Title convention (enforced by `validate-title.sh`)

Hard rules:
- Length ≤ 60 chars (CJK counted as 1)
- No status words in the title (status frontmatter already carries it — duplication is noise)

Soft rules (CLAUDE.md only, not blocked):
- Use `—` (em-dash) for qualifier separator
- 두괄식 (lead with the conclusion)
- No emoji, no meta prefix, prefer slug-style brevity over subtitle

## Deprecated folders (blocked outright)

`validate-content-placement.sh` blocks any Write into:
- `content/decisions/`  ← deprecated path (canonical decisions live elsewhere now — check current INDEX before writing)
- `content/memo/`        ← deprecated
- `content/tech/`        ← flattened into `agents/`, `quant/`, `engineering/` top-level

If the user requests a doc and the natural placement is one of these, surface the conflict in Phase 1 Clarify.

## Wiki-internal references

Use the shortcode `{{wiki:slug}}` for cross-references between pages. `validate-wiki-refs.sh` blocks writes containing slugs that don't exist on the filesystem (no fallback rendering — dead links become silent rot otherwise).

## Mermaid diagrams

Mermaid blocks are embedded raw into the build. `validate-mermaid.sh` blocks parser-fatal syntax (the `unquoted-brace` pattern was responsible for two prior incidents — PR#124 and PR#127). When a diagram makes sense, use Mermaid; `suggest-mermaid.sh` (PostToolUse) flags ASCII diagrams as candidates for conversion.

## Build (`build.sh`)

After any content change, the user must run `./build.sh` from `$WIKI_ROOT`. The Stop hook `content-checklist.sh` blocks session exit if `content/` is newer than `site/index.html` — the build artifact must stay in sync. `remind-build.sh` (PostToolUse) is a softer reminder.

## Section semantics — what goes where

| If the doc is… | Section | Why |
|----------------|---------|-----|
| Vision / philosophy / system-overview / glossary / contributing | `start/` | "처음 합류한 사람이 제품을 이해하기 위해 읽는 것" |
| Sales pipeline / market analysis / customer objections / partnership context | `market/` | "비기술 인원이 외부와 의사결정할 때 참고하는 것" |
| Agent별 동작 원리 / 알고리즘 / 의사결정 트리 (alpha, insight, portfolio, report, data 등) | `tech/agents/{name}/...` | "이 agent를 처음 다루는 개발자가 5분 안에 mental model 만드는 것" |
| 퀀트 전략 / 리스크 모델 / 백테스트 방법론 / 시장 미시구조 | `tech/quant/...` | "퀀트 도메인 지식 — 시간이 지나도 유효한 fundamentals" |
| CI/CD / infra / 시스템 다이어그램 / 운영 룬북 | `tech/engineering/...` | "온콜 / 배포 / 디버깅 시 참조하는 운영성 지식" |
| 진행 중인 분석 / RFC / 제안 / "이게 맞을까?" | `discussions/...` | "결정되지 않은 상태 — status: active" |
| "이 결정을 했고 이유는 X" 류의 ADR | `decisions/...` | "이미 결정 — status: decided, 이후 supersede만 변경" |
| 이벤트 로그 (출시 / 의사결정 / 사고 / 마일스톤) | `timeline/...` | "분기말 회고 / 외부 보고에 인용하는 시점 데이터" |

이 표는 choo-choo의 Phase 1 Clarify에서 사용자에게 "이 작업은 어느 섹션이 자연스러운가" 질문하는 근거가 된다.
