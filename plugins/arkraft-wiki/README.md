# arkraft-wiki Plugin

`arkraft-wiki` repo에 지식 문서를 생성/업데이트하는 **`wikify`** skill을 제공.

## 적용 범위 — arkraft-wiki 전용

이 plugin은 **`arkraft-wiki` repo 전용**으로 설계되었습니다. `wiki_root` path는 settings로 사용자별 generic하게 지정되지만, **section taxonomy(`references/wiki-structure.md`)와 harness 검사 항목(`references/harness-summary.md`)은 arkraft-wiki repo의 구조에 고정**되어 있습니다 (start/market/tech/agents·quant·engineering/discussions/decisions/timeline + 11 hooks).

다른 wiki repo에 이 plugin을 응용하려면:

- 이 plugin을 **fork** 후 `references/wiki-structure.md`(섹션 분류 + lifecycle 규칙)와 `references/harness-summary.md`(hook 검사 항목)를 **해당 wiki repo의 실제 구조에 맞게 교체**해야 합니다.
- `repos[]` settings는 이미 generic — 다른 wiki repo의 source-of-knowledge repo 목록을 사용자가 지정 가능.
- `wikify` skill 본체와 wrapper 흐름(settings → context bundle → choo-choo 위임)은 wiki-agnostic이므로 그대로 재사용 가능.

즉: **wiki_root 경로**는 settings로 변경 가능하지만, **wiki 구조/lifecycle/harness 어휘**는 fork + edit이 필요합니다. 이 plugin이 generic library 형태로 제공되지 않는 이유는 — wiki ecosystem마다 section 분류와 enforcement가 너무 달라서 generic 추상화가 의미가 없기 때문 (각 wiki의 hooks가 SSOT이고 plugin은 그걸 인용만).

## 핵심 설계 — Thin wrapper

이 plugin은 wiki content를 직접 작성하지 않습니다. 대신:

1. 사용자별 `wiki_root` 경로를 settings에서 읽고
2. wiki-specific 컨텍스트(section 구조, lifecycle, harness 검사 항목, repo scan 목록)를 묶어
3. `run-ralph:choo-choo`에 위임 — 실제 iterative 작성은 Ralph Loop에서 진행

`arkraft-wiki` repo 자체의 PreToolUse / PostToolUse / Stop hooks 11종이 wiki content 검증의 단일 source of truth. plugin은 그 hooks를 **복사하지 않고** 그 검사 항목을 choo-choo prompt에 인용해 Acceptance Criteria L1으로 활용.

## 설치

```bash
/plugin install wogus-plugins:arkraft-wiki
```

의존: `run-ralph` plugin (필수). `wf` plugin (있으면 choo-choo가 wf 5-단계 거치는 옵션도 활용; 없어도 동작).

## 설정

settings 파일을 다음 둘 중 한 곳에 생성 (per-project 우선):

```
{project}/.claude/arkraft-wiki.local.md   ← per-project (gitignored 권장)
~/.claude/arkraft-wiki.local.md           ← user-global
```

minimum frontmatter:

```yaml
---
wiki_root: /absolute/path/to/arkraft-wiki
---
```

template 전체는 `skills/wikify/references/arkraft-wiki.local.md.template` 참고.

`wiki_root`가 없거나 디렉터리가 존재하지 않으면 skill은 실행 거부 + 안내 메시지. **default path 추측 안 함.**

## 사용

```
/arkraft-wiki:wikify "OAuth 통합 결정사항 wiki에 정리해줘"
/arkraft-wiki:wikify "지식화하자"
/arkraft-wiki:wikify "이번 작업 wiki에 추가"
```

Korean trigger keywords: `지식화하자`, `지식화`, `wiki에 추가해줘`, `wiki 문서로 남겨줘`, `wikify`, `wiki 정리`, `wiki에 정리`.

호출하면:
1. wikify가 settings 읽고 wiki-specific 컨텍스트 묶음
2. `Skill(run-ralph:choo-choo, args: <wiki authoring task + 컨텍스트>)` 위임
3. choo-choo Phase 1 Clarify에서 섹션/제목/new-vs-update 사용자 확인
4. Phase 1.5 dispatch는 보통 TRIVIAL (doc-only) — ralph 직행
5. Ralph Loop 반복하며 `wiki_root/content/...` 에 draft → wiki repo의 PreToolUse hooks 자동 fire (placement / depth / title / mermaid / refs / timeline 검증) → revise → 통과
6. 마지막에 `cd $wiki_root && ./build.sh` 실행 → site/ refresh → Stop content-checklist 통과
7. choo-choo Phase 6 보고서 + promise emit

## 제공 컴포넌트

```
plugins/arkraft-wiki/
├── .claude-plugin/plugin.json
├── README.md                       (이 파일)
└── skills/wikify/
    ├── SKILL.md                    (얇은 wrapper — choo-choo 위임)
    └── references/
        ├── wiki-structure.md       (section taxonomy + lifecycle + depth 규칙 + section semantics)
        ├── repo-list.md            (default 9-repo scan list + settings override 규칙)
        ├── harness-summary.md      (11 hooks 검사 항목 — AC L1 derivation 가이드)
        ├── prompt-template.md      (choo-choo args 템플릿)
        └── arkraft-wiki.local.md.template  (settings starter)
```

## arkraft-wiki repo와의 관계

| 책임 | 위치 | 비고 |
|------|------|------|
| wiki content 작성 logic (iterative draft) | run-ralph plugin (Ralph Loop) | choo-choo가 진행 |
| section/lifecycle/title 구조 enforce | **arkraft-wiki repo의 hooks** | wikify는 인용만 |
| build (`./build.sh`, site/ 갱신) | **arkraft-wiki repo의 build.sh** | Worker가 마지막에 실행 |
| Worker에게 wiki 컨벤션 가이드 | 이 plugin의 references/ | choo-choo prompt 컨텍스트 |

dual-source drift 방지: arkraft-wiki repo의 hooks가 변경되면 plugin의 `harness-summary.md` 도 PR로 갱신. plugin은 hooks를 복사하지 않으므로 runtime mirror 동기화 비용 없음, 다만 문서 sync 책임만.

## 언어

trigger / 사용자 응답 / wiki 본문 모두 **한국어** 기본. 인스트럭션 / SKILL.md / references 본문은 영어 (의도 정확성 — wogus-plugin 전 plugin 공통 컨벤션).

## v1.0.0

- wikify SKILL (thin wrapper)
- 4 references (wiki-structure / repo-list / harness-summary / prompt-template)
- settings template (`arkraft-wiki.local.md.template`)
- 0 hooks (의도적 — wiki repo의 hooks가 source of truth)
