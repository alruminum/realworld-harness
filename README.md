# RealWorld Harness

> **Production-grade Agent Workflow Engine for Claude Code.**
>
> 현실 세계 프로덕트 조직(기획 · UX · 아키 · 엔지 · QA · 리뷰)을 역할별 에이전트로 시뮬레이션하는 **결정론적 5단계 워크플로우** + **Task-ID 기반 거버넌스**.

![status](https://img.shields.io/badge/status-v0.1.0--alpha-green) ![license](https://img.shields.io/badge/license-MIT-green) ![release](https://img.shields.io/badge/release-public-brightgreen)

---

## Core Invariant — 워크플로우 불변

> 에이전트의 능력이 시간에 따라 향상된다고 가정한다.
> **워크플로우는 그렇지 않다. Process layer는 시스템의 영속적 자산이다.**

모델은 6개월마다 갈아엎히지만, 절차 레이어는 자산으로 축적된다. RealWorld Harness는 그 절차를 **코드로 강제**한다.

→ 자세한 헌법: [`docs/harness-spec.md §0`](docs/harness-spec.md)

---

## 왜 만들었나

LLM 기반 에이전트가 똑똑해질수록, 단일 거대 에이전트에게 자율성을 몰아주는 게 트렌드다. 하지만 실제 프로덕트에 들어가는 코드 — 특히 B2B / 엔터프라이즈 — 는 **게이트·검증·재현성이 필수**다.

| 흔한 트렌드 | RealWorld Harness |
|---|---|
| 단일 거대 에이전트의 자율성 극대화 | 역할별 분업 + 명시적 게이트 |
| Self-correcting loop (자동 복구) | ESCALATE → 유저 게이트 → 재계약 (SPEC_GAP) |
| Memory가 알아서 진화 | 워크플로우는 고정, agent_tiers로 모델만 교체 |
| 데모/연구 우선 | 프로덕션·B2B·6개월+ 유지보수 우선 |

이 시스템은 **데모나 연구용 도구가 아니라, 실제 서비스에 들어가는 코드를 만드는 데 쓰는 것**을 목표로 한다.

## 무엇을 제공하나

- **Python 훅** — 에이전트 권한 경계, 게이트, 상태 관리, 이슈 lock, 토큰 폭주 방지
- **역할별 에이전트** — `product-planner`, `plan-reviewer`, `ux-architect`, `architect`, `engineer`, `test-engineer`, `validator`, `designer`, `design-critic`, `pr-reviewer`, `qa`, `security-reviewer`
- **5단계 워크플로우** — 기획-UX → 설계 → 구현(attempt 0..3 + SPEC_GAP 동결) → 디자인 → 리뷰-커밋
- **결정론적 게이트** — 마커 기반 자동 흐름 + 유저 명시 승인 게이트 + ESCALATE 자동 복구 금지
- **`agent_tiers`** — `harness.config.json` 에서 high/mid/low tier만 매핑하면 모델 교체 시 워크플로우 코드 무수정
- **Task-ID 기반 거버넌스** — 모든 변경에 WHAT(`changelog.md`) / WHY(`rationale.md`) 분리 로그 + Document-Exception 스코핑 + git pre-commit + Claude Code commit-gate 3중 강제

## 현재 상태

🚧 **Alpha (v0.1.0-alpha)** — `~/.claude/` 의 작동 중인 하네스 시스템을 플러그인 배포판으로 마이그레이션 중.

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 클린업 + 거버넌스 골격 | ✅ 완료 (`HARNESS-CHG-20260427-01`) |
| 1 | 코어 마이그레이션 (~/.claude → 플러그인 구조 + PLUGIN_ROOT 추상화) | ✅ 완료 (`HARNESS-CHG-20260427-02`) |
| 2 | 철학 명시화 (§0 Core Invariant) + agent_tiers + 자동 거버넌스 게이트 | ✅ 완료 (`HARNESS-CHG-20260427-03`) |
| 3 | 독립 정본화 + smoke-test (50/50) + GitHub Actions + E2E 가이드 | ✅ 완료 (`HARNESS-CHG-20260427-04`) |
| 4 | `v0.1.0-alpha` tag + public 전환 + GitHub Release | ✅ 완료 (`HARNESS-CHG-20260427-05`) |

자세한 로드맵: [`docs/proposals.md §4`](docs/proposals.md)

## 설치

`v0.1.0-alpha` — public repo, 두 가지 경로.

### 의존성

- Claude Code (플러그인 시스템 지원 버전)
- Python 3.9+ (stdlib only — 추가 패키지 X)
- (선택) `gh` CLI — GitHub 이슈 자동 생성에 사용 (qa 에이전트)
- (선택) Pencil MCP — 디자인 시안 (designer 에이전트)

### A. 마켓플레이스 install (권장)

**1) Claude Code 세션에서:**

```
/plugin marketplace add alruminum/realworld-harness
/plugin install realworld-harness
```

**2) Claude Code 재시작** — `hooks/hooks.json` 자동 로드.

**3) 적용할 프로젝트 디렉토리에서:**

```bash
cd /path/to/your-project
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh"
```

→ `.claude/harness.config.json` + `.claude/agent-config/` + `.git/hooks/pre-commit` 자동 설치 + 화이트리스트 등록.

### B. 개발 폴백 (clone 후 직접 사용)

```bash
git clone https://github.com/alruminum/realworld-harness.git
export CLAUDE_PLUGIN_ROOT="$(pwd)/realworld-harness"

cd /path/to/your-project
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh"
```

### C. ~/.claude 에 source 시스템이 있는 *기존* 사용자만 — 마이그레이션

> **신규 사용자는 §A 사용. §C 는 *과거에 ~/.claude 에 직접 hooks/, harness/, agents/ 를 두고 사용하던* 사용자 전용 경로.**

기존 ~/.claude 에 RWHarness 의 source(hooks/, harness/, agents/ 등)가 활성화돼있다면 **충돌 회피 정리 후 install** 필요. step-by-step: [`docs/migration-from-source.md`](docs/migration-from-source.md). 백업 → 플러그인 install → settings.json hooks 제거 → source 디렉토리 삭제 → 검증.

## 첫 사용 (5분 검증)

설치 후 가장 빠른 검증 — `/quick` 으로 단일 버그픽스 루프:

```bash
# 테스트 시드 만들기
mkdir -p src && printf 'function add(a, b) { return a - b; }\nmodule.exports = { add };\n' > src/util.js
git add . && git commit -m "seed" --no-verify
```

```
# Claude Code 세션:
/quick add 함수가 잘못 계산함. 2+3=5 가 -1 나옴. 고쳐줘.
```

흐름 관찰: `qa` → `architect LIGHT_PLAN` → `engineer` → `validator` → `pr-reviewer LGTM` → `HARNESS_DONE`.

전체 검증 (5루프) — [`docs/e2e-quickstart.md`](docs/e2e-quickstart.md).

## 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| 훅이 작동 안 함 (메인 Claude 가 그냥 src/ 수정) | 프로젝트가 화이트리스트에 미등록. `/harness-list` 로 확인, `/harness-enable` 로 등록 |
| `setup-rwh.sh: No such file or directory` | `CLAUDE_PLUGIN_ROOT` env 미설정. 옵션 B 의 `export CLAUDE_PLUGIN_ROOT=...` 먼저 |
| 게이트가 너무 엄격 (긴급 hotfix 등) | `SKIP_DOC_SYNC=1 git commit ...` 또는 commit msg 에 `Document-Exception: <10자 이상 사유>` |
| 특정 프로젝트만 일시 비활성 | 프로젝트 루트에 `touch .no-harness` |
| 영구 비활성 | `/harness-disable` 또는 `~/.claude/harness-projects.json` 에서 경로 제거 |

## 외부 발견·공유

본 repo 자체가 *self-hosted* 마켓플레이스(`marketplace.json` 매니페스트). 다른 사용자가 사용하려면:

- **직접 install**: `/plugin marketplace add alruminum/realworld-harness` (위 §A)
- **공유**: 본 README URL 또는 [v0.1.0-alpha release](https://github.com/alruminum/realworld-harness/releases/tag/v0.1.0-alpha) link 전달
- **(예정) 커뮤니티 큐레이션 등재** — `awesome-claude-code` 또는 Anthropic 공식 큐레이션이 있다면 v1.0.0 시점에 등재 PR 검토

자세한 검증 절차: [`docs/smoke-test-guide.md`](docs/smoke-test-guide.md), [`docs/e2e-quickstart.md`](docs/e2e-quickstart.md)

## 문서

| 문서 | 역할 |
|---|---|
| [`docs/harness-spec.md`](docs/harness-spec.md) | 헌법 (§0 Core Invariant + 게이트·불변식·비목표) |
| [`docs/harness-architecture.md`](docs/harness-architecture.md) | 기술 구현 (훅·핸드오프·세션·경계) |
| [`docs/agent-tiers.md`](docs/agent-tiers.md) | agent_tiers 매핑 정책 (모델 진화 흡수 메커니즘) |
| [`docs/smoke-test-guide.md`](docs/smoke-test-guide.md) | clean install 자동 검증 + 외부 머신/컨테이너 가이드 |
| [`docs/e2e-quickstart.md`](docs/e2e-quickstart.md) | 30분 E2E 검증 경로 (`/quick` 루프 + 거버넌스 게이트 + agent_tiers) |
| [`docs/e2e-test-scenarios.md`](docs/e2e-test-scenarios.md) | 5루프 전체 E2E 시나리오 + 통과 기준 |
| [`orchestration/policies.md`](orchestration/policies.md) | Task-ID + Change-Type 5종 + Document-Exception 룰 |
| [`orchestration/changelog.md`](orchestration/changelog.md) | WHAT 로그 (모든 Task-ID 변경 기록) |
| [`orchestration/rationale.md`](orchestration/rationale.md) | WHY 로그 (Rationale / Alternatives / Decision / Follow-Up) |

> v0.1.0-alpha 이전의 마이그레이션 시점 자료(`migration-plan`, `analysis-current-harness`, `proposals`, `plan-plugin-distribution`)는 git log + `v0.1.0-alpha` tag 의 release archive 에 보존돼있다. 결과는 모두 위 정본 문서에 반영됨.

## License

MIT — [LICENSE](LICENSE).

---

## English

**RealWorld Harness** is a production-grade agent workflow engine for Claude Code. It simulates a real-world product organization (PM · UX · Architect · Engineer · QA · Reviewer) as specialized agents, enforcing **deterministic 5-phase workflows** with **Task-ID based governance**.

### Core Invariant

> Agents are assumed to improve over time. **The workflow is not.** Process layer is the system's persistent value.

When models are swapped every 6 months but the process layer keeps compounding, the moat shifts from "smartest agent" to "tightest process." RealWorld Harness encodes that process.

### Why this exists

Mainstream AI trends push toward maximally autonomous single agents. But production code — especially B2B / enterprise — requires **gates, verification, and reproducibility**. This system aligns with the *production* branch of agentic workflows, not the demo/research branch.

| Common trend | RealWorld Harness |
|---|---|
| Maximize single-agent autonomy | Role-based specialization + explicit gates |
| Self-correcting loop | ESCALATE → user gate → renegotiation (SPEC_GAP) |
| Memory-driven evolution | Workflow stays fixed; only `agent_tiers` model mapping changes |
| Demo / research first | Production / B2B / 6+ month maintenance first |

### Status

🚧 Currently in alpha. See [`docs/harness-spec.md`](docs/harness-spec.md) for the system constitution and [`docs/proposals.md`](docs/proposals.md) for the migration roadmap.
