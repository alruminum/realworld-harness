# RealWorld Harness

> Production-grade Agent Workflow Engine for Claude Code.
>
> 현실 세계 프로덕트 조직(기획·UX·아키·엔지·QA·리뷰)을 에이전트로 시뮬레이션하는 결정론적 5단계 워크플로우.

![status](https://img.shields.io/badge/status-alpha-yellow) ![license](https://img.shields.io/badge/license-MIT-green)

---

## 왜 만들었나

LLM 기반 에이전트가 똑똑해질수록, 단일 거대 에이전트에게 자율성을 주는 게 트렌드다. 하지만 실제 프로덕트에 들어가는 코드 — 특히 B2B / 엔터프라이즈 — 는 게이트·검증·재현성이 필수다.

**RealWorld Harness의 핵심 원칙: 에이전트는 진화해도 워크플로우는 불변.** 절차가 시스템의 가드레일이다.

## 무엇을 제공하나

- **Python 훅** — 에이전트 권한 경계, 게이트, 상태 관리
- **역할별 에이전트** — product-planner, ux-architect, architect, engineer, validator, designer, pr-reviewer 등
- **5단계 워크플로우** — 기획-UX → 설계 → 구현 → 디자인 → 리뷰-커밋
- **결정론적 게이트** — 마커 기반 자동 흐름 + 유저 명시 승인 게이트
- **Task-ID 기반 거버넌스** — 모든 변경에 WHAT(`changelog.md`) / WHY(`rationale.md`) 분리 로그

## 현재 상태

🚧 **Alpha (v0.1.0-alpha)** — `~/.claude/` 의 작동 중인 하네스 시스템을 플러그인 배포판으로 마이그레이션 중.

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 클린업 + 거버넌스 골격 | 진행 중 |
| 1 | 코어 마이그레이션 (~/.claude → 플러그인 구조) | 대기 |
| 2 | 철학 명시화 (§0 Core Invariant) + 자동 게이트 | 대기 |
| 3 | clean install smoke test + v1.0.0 태그 + 마켓플레이스 PR | 대기 |

자세한 로드맵: [`docs/proposals.md §4`](docs/proposals.md)

## 문서

| 문서 | 역할 |
|---|---|
| [`docs/harness-spec.md`](docs/harness-spec.md) | 헌법 (목적·불변식·게이트·비목표) |
| [`docs/harness-architecture.md`](docs/harness-architecture.md) | 기술 구현 (훅·핸드오프·세션·경계) |
| [`docs/proposals.md`](docs/proposals.md) | 배포 방향 제안 + 거버넌스 통합 방안 |
| [`docs/analysis-current-harness.md`](docs/analysis-current-harness.md) | 현재 ~/.claude 시스템 도면 |
| [`docs/plan-plugin-distribution.md`](docs/plan-plugin-distribution.md) | 정본 설계 문서 (2026-04-21 갱신) |
| [`orchestration/policies.md`](orchestration/policies.md) | Task-ID + Change-Type + Document-Exception 룰 |
| [`orchestration/changelog.md`](orchestration/changelog.md) | WHAT 로그 |
| [`orchestration/rationale.md`](orchestration/rationale.md) | WHY 로그 |

## License

MIT — [LICENSE](LICENSE).

---

## English

**RealWorld Harness** is a production-grade agent workflow engine for Claude Code. It simulates a real-world product organization (PM · UX · Architect · Engineer · QA · Reviewer) as specialized agents, enforcing deterministic 5-phase workflows.

**Core invariant**: agents may evolve, but the workflow does not. Process is the moat.

🚧 Currently in alpha. See [`docs/harness-spec.md`](docs/harness-spec.md) for the system constitution and [`docs/proposals.md`](docs/proposals.md) for the migration roadmap.
