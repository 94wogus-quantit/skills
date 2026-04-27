# Team Composition

Guide for assembling an Agent team that fits the requested task before launching Ralph Loop.

## Why a team

A single Worker that authors changes AND judges its own completion will emit the completion-promise prematurely (self-approval problem). Spawning an independent Reviewer and QA each iteration enforces a three-party agreement before completion is recognized.

## Mandatory roles (required for every task)

| Role | Agent | Responsibility | Artifact |
|------|-------|----------------|----------|
| **Worker** | (Main Ralph Loop session) | Advance one unmet Success Criterion per iteration. Edit code/docs. | git diff, file changes |
| **Reviewer** | `ralph-reviewer` | Judge Level 2 (Structural) — patterns, abstractions, layer boundaries. | `.ralph/<slug>/review-{iter}.md`, VERDICT: LGTM/REVISE |
| **QA** | `ralph-qa` | Run Level 1 (Concrete) checks + judge Level 3 (Holistic) when applicable. | `.ralph/<slug>/qa-{iter}.md`, VERDICT: PASS/FAIL |

**Reviewer and QA can never be skipped.** This separation is the entire mechanism that prevents self-approval.

## Default team templates by task type

Pick the matching template, then add custom roles only when a clear trigger applies.

### Refactoring

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | — |
| Reviewer | `ralph-reviewer` | + behavioral equivalence before/after, deduplication completeness |
| QA | `ralph-qa` | + all existing tests must pass |
| (optional) Architecture-Reviewer | ad-hoc | Only for large structural moves — layer violations, circular deps |

### Bug Fix

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | Write the reproducing test first, then fix |
| Reviewer | `ralph-reviewer` | + root cause vs. symptom patch distinction |
| QA | `ralph-qa` | + actually execute the reproduction scenario, regression sweep |
| (optional) Reproducer | ad-hoc | When reproduction setup is non-trivial — automate env setup |

### Feature Addition

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | — |
| Reviewer | `ralph-reviewer` | + new abstractions consistent with existing patterns |
| QA | `ralph-qa` | + happy path + edge cases verified |
| (optional) API-Designer | ad-hoc | When exposing new external API — spec consistency, compatibility |
| (optional) Test-Writer | ad-hoc | When test authoring needs to be split off |

### Infra (Terraform / Helm / K8s)

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | + run `make fmt && make validate` |
| Reviewer | `ralph-reviewer` | + reuse existing modules vs. define new |
| QA | `ralph-qa` | + `terraform plan` diff matches intent |
| (optional) Cost-Auditor | ad-hoc | When adding cost-sensitive resources (RDS, ElastiCache, NAT) |
| (optional) Security-Reviewer | ad-hoc | When changing IAM / SG / public endpoints |

### Documentation / Wiki

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | — |
| Reviewer | `ralph-reviewer` | + structural consistency (heading hierarchy, section order) |
| QA | `ralph-qa` | + Level 3 (reader-perception) emphasized |
| (optional) Reader-Persona | ad-hoc | Read as the named persona ("a backend dev who just joined — can they grasp X in 5 min?") |

### Test Writing

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | — |
| Reviewer | `ralph-reviewer` | + test isolation, fixture reuse, mocking adequacy |
| QA | `ralph-qa` | + execute every new test, observe coverage delta |

### Design / Meta (ADR, integration design, workflow redesign, architecture decisions)

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | Draft / refine the design artifact (ADR, integration spec, dispatcher design, etc.). The "diff" is changes to the design document, not source code. |
| Reviewer | `ralph-reviewer` | + structural integrity of the design: required sections present, alternatives explicitly weighed, decisions trace back to constraints, terminology consistent with existing glossary |
| QA | `ralph-qa` | + L1: file/section existence, no `TODO`/`TBD` markers, no broken cross-refs. + L3: target reader can grasp the decision and its rationale (persona-driven). |
| (optional) Domain-Expert | ad-hoc | When the design must preserve contracts of multiple existing systems (e.g., merging two skills) — verifies each system's invariants are honored |
| (optional) Reader-Persona | ad-hoc | When the design has a specific downstream reader (future maintainer, new hire, user of the merged artifact) |

### Integration / Migration (merging modules/skills, staged migration plans)

| Role | Agent | Extra responsibility |
|------|-------|---------------------|
| Worker | (main) | Advance one slice of the integration per iteration (one module migrated, one section of merge plan finalized). |
| Reviewer | `ralph-reviewer` | + neither original system's invariants are silently dropped, no half-migrated state in the diff |
| QA | `ralph-qa` | + L1: smoke checks for both old and new paths still pass during transition. + L3 (if user-facing): consistent UX across the two systems. |
| (optional) Domain-Expert | ad-hoc | When two domains' rules collide (e.g., two skills with overlapping but slightly different semantics) |

## Custom role definition

When the default team is insufficient, define an ad-hoc role inline in the prompt using this pattern:

```markdown
## Custom Agent: {Role Name}

**Spawning**: `Agent(subagent_type: "general-purpose", name: "{role-name}")`
**Trigger condition**: {when to invoke — every iteration / on file pattern change / on Reviewer request}
**Mandate**: {what verdict it owns — what does it PASS/FAIL or LGTM/REVISE}
**Tools needed**: {Read, Bash, ...}
**Output**: `.ralph/<slug>/{role-name}-{iter}.md` + one-line summary verdict (path is provided absolute via `output_path` in the spawn prompt)
```

### Custom role examples

#### Cost-Auditor (Infra)

```markdown
**Mandate**: 추가/변경된 AWS 리소스의 월 예상 비용 산출. $50/월 초과 리소스는 명시적 정당화 요구.
**Tools**: Read, Bash (aws pricing API 호출)
**Output**: 비용 표 + VERDICT: APPROVED / JUSTIFY-NEEDED
```

#### Reader-Persona (Docs)

```markdown
**Mandate**: 페르소나 "처음 합류한 백엔드 개발자 (해당 코드베이스 무경험)"로 문서를 처음부터 끝까지 읽고 perception 평가.
- 5분 내에 핵심 개념을 파악할 수 있는가?
- 다음에 무엇을 해야 할지 알 수 있는가?
- 모호하거나 모순되는 부분이 있는가?
**Output**: 페르소나 노트 + VERDICT: CLEAR / UNCLEAR
```

#### Security-Reviewer (Infra)

```markdown
**Mandate**: 변경된 IAM policy / Security Group rule / 공개 엔드포인트 검토.
- 최소 권한 원칙 위반 여부
- 0.0.0.0/0 인바운드 존재 여부
- 시크릿 노출 여부
**Output**: 위험 항목 표 + VERDICT: SAFE / RISK-FOUND
```

#### Domain-Expert (Design / Integration)

```markdown
**Mandate**: 통합·재설계 대상이 되는 기존 시스템 각각의 invariant이 새 설계에서도 보존되는지 검증.
- 통합 전 각 시스템의 핵심 계약(public API, 데이터 형식, 사용자 트리거 표현 등) 목록화
- 새 설계 문서가 그 계약을 어떻게 흡수/매핑/대체하는지 1:1 추적
- 누락된 계약 = REVISE 사유
**Output**: 시스템별 invariant 보존 표 + VERDICT: PRESERVED / GAPS-FOUND
```

## Composition workflow (run-ralph Phase 2)

1. Detect task type from clarify answers + initial repo grep.
2. Pick the matching default team from the tables above.
3. Check for custom role triggers:
   - Infra + cost-sensitive resource → Cost-Auditor
   - Docs with named reader → Reader-Persona
   - IAM / SG / public endpoint change → Security-Reviewer
   - Design/integration with multiple existing systems' contracts to honor → Domain-Expert
   - Anything user-specified that isn't covered
4. Show the proposed team to the user and ask for approval / edits.
5. Embed the confirmed team into the Iteration Workflow section of the Phase 4 prompt.
