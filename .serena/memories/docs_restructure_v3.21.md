# v3.21.0 문서 구조 개선 (2026-01-30)

## 결정 사항
- CLAUDE.md / README.md / CHANGELOG.md 3개 문서의 역할을 명확히 분리
- CLAUDE.md를 442줄에서 ~235줄로 경량화 (-207줄)
- README.md에서 인라인 버전 변경사항 제거 (-59줄)

## 문서 역할 정의
| 문서 | 독자 | 포함 내용 | 제외 |
|------|------|----------|------|
| CLAUDE.md | AI Agent | 구조, 규칙, 가이드라인, Known Issues, ADR 요약 | MCP 도구 목록, 설치 가이드, ADR 전문 |
| README.md | 사용자(사람) | 설치, 사용법, 기능 소개, Marketplace 배포 | 아키텍처 결정사항, 개발 가이드라인 |
| CHANGELOG.md | 둘 다 | 버전 인덱스 + changelogs/ 링크 | 상세 내용 |

## 삭제된 섹션 (CLAUDE.md)
- Git MCP 섹션 (~39줄): Agent가 tool list에서 자동 인식
- CI MCP 섹션 (~36줄): Agent가 tool list에서 자동 인식
- Skills vs Agents 표 (~10줄): 불필요한 중복
- AC Traceability Example (~13줄): Skills 설명에 이미 내포
- ADR 전문 (~88줄): 요약 테이블 + docs/ 링크로 대체
- Marketplace 상세 (~31줄): 2줄 요약 + README 참조로 대체

## 근본 원인
"모든 정보를 CLAUDE.md에 넣는" 패턴으로 성장. record 스킬이 ADR 전문을 직접 삽입하고, MCP 도구 추가 시 사용 예시까지 포함하는 관행.

## 향후 주의사항
- 새 MCP 도구 추가 시 CLAUDE.md에 사용 예시를 넣지 말 것 (Agent가 tool list에서 자동 인식)
- ADR은 최근 3개만 요약 테이블로 유지, 전문은 docs/architecture/decisions/에 보관
- 버전별 변경사항은 CHANGELOG.md + changelogs/에만 기록
