# Workflow Bundle Plugin

체계적인 소프트웨어 개발 워크플로우를 위한 Skills + Agent + MCP 번들.

## 설치

```bash
/plugin install wogus-plugins:wf
```

## 포함된 Skills (5개)

| Skill | 설명 |
|-------|------|
| **analyze** | 이슈 분석 및 root cause 파악 |
| **plan** | 반복적 리뷰를 통한 구현 계획 수립 |
| **execute** | 계획 실행 및 TodoList 추적 |
| **record** | 문서화 (README, CHANGELOG, CLAUDE.md) |
| **mr-review** | GitLab MR 코드 리뷰 (7가지 검증) |

## 워크플로우

```
analyze → plan → execute → record
```

## 포함된 Agent

- **requirement-validator**: JIRA AC 추적 및 검증

## 포함된 MCP

- **seq-think**: 단계별 사고 도구

## 언어

모든 출력은 **한국어**가 기본입니다.
