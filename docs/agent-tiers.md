# Agent Tiers — 모델 진화 흡수 메커니즘

> Task-ID: `HARNESS-CHG-20260427-03` [2.4]
> 작성: 2026-04-27
> 출처: `docs/proposals.md §3` 제안 C / `docs/harness-spec.md §0` Core Invariant

---

## 1. 왜 tier 추상화인가

**Core Invariant** — *에이전트 능력은 진화하지만 워크플로우는 불변이다.*

이를 코드로 강제하는 가장 깔끔한 표현은: **에이전트 → 모델 직접 지정 금지**, **에이전트 → tier → 모델** 2단 매핑.

| 직접 매핑 (안티패턴) | tier 매핑 (RWHarness) |
|---|---|
| 모델명이 코드에 박힘 | 모델명은 `harness.config.json` 매핑 1곳에만 |
| 모델 가격 변동 → 코드 수정 | 매핑 갱신만 |
| 모델 세대 교체 → 워크플로우 영향 | 워크플로우 무영향, tier 매핑만 갱신 |
| 에이전트 13개 × 모델 N개 = N×13 변경 | 모델 3개 × tier 매핑 = 3 변경 |

---

## 2. 기본 매핑

### 2.1 tier → model

```json
{
  "agent_tiers": {
    "high": "claude-opus-4-7",
    "mid":  "claude-sonnet-4-6",
    "low":  "claude-haiku-4-5"
  }
}
```

### 2.2 agent → tier

| Agent | Tier | 근거 |
|---|---|---|
| `architect` | high | 시스템 설계·모듈 계획·SPEC_GAP — 정확도 최우선 |
| `plan-reviewer` | high | PRD 6차원 현실성 판단 — 거시 추론 |
| `engineer` | mid | attempt 0..3 반복 — 균형 |
| `test-engineer` | mid | TDD 선작성 |
| `validator` | mid | Plan / Code / UX 검증 |
| `pr-reviewer` | mid | LGTM 판정 |
| `designer` | mid | Pencil 시안 ONE/THREE_WAY |
| `ux-architect` | mid | UX Flow 작성 |
| `product-planner` | mid | PRD 작성 |
| `security-reviewer` | mid | 보안 감시 (예약) |
| `qa` | low | 분류 + 라우팅 추천 (단순 분기) |
| `design-critic` | low | 4기준 점수화 (단순 평가) |

---

## 3. 사용 방법

### 3.1 Python 코드에서

```python
from harness.config import load_config, get_agent_model

config = load_config()
model_id = get_agent_model("architect", config)  # "claude-opus-4-7"
```

### 3.2 사용자 override

`{project_root}/.claude/harness.config.json`:

```json
{
  "prefix": "myproj",
  "agent_tiers": {
    "high": "claude-opus-4-8"
  },
  "agent_tier_assignment": {
    "qa": "mid"
  }
}
```

규칙:
- `agent_tiers` 의 user 매핑은 **머지** (high만 override 가능, mid/low는 기본값 유지)
- `agent_tier_assignment` 도 머지 (qa만 mid로, 다른 에이전트는 기본 배정 유지)
- 파일 자체가 없거나 두 필드가 누락이면 모두 기본값

### 3.3 모델 세대 교체 시나리오

Claude Opus 5.0 출시 시:

```diff
 {
   "agent_tiers": {
-    "high": "claude-opus-4-7",
+    "high": "claude-opus-5-0",
     "mid":  "claude-sonnet-4-6",
     "low":  "claude-haiku-4-5"
   }
 }
```

→ workflow 코드 무수정, agent 정의 무수정. 1줄 변경으로 architect/plan-reviewer 모델 일괄 교체.

---

## 4. 폴백 동작

| 상황 | 폴백 |
|---|---|
| `agent_name` 이 `agent_tier_assignment` 에 미정의 | tier `"mid"` |
| tier가 `agent_tiers` 에 미정의 | 기본 `mid` 모델 |
| `agent_tiers["mid"]` 도 누락 | `DEFAULT_AGENT_TIERS["mid"]` (코드 상수) |

`get_agent_model()` 은 **항상 모델 ID 문자열을 반환** (None 반환 없음 — 워크플로우 안정성 우선).

---

## 5. 비목표

- **에이전트별 직접 모델 지정** — `harness.config.json` 에 `agent_models: {architect: "..."}` 같은 직접 지정은 지원하지 않음. tier 추상화를 우회하면 Core Invariant 약화.
- **환경별 분기 (dev / prod)** — v1.1 이후. 현재는 단일 매핑.
- **런타임 동적 tier 변경** — 세션 단위 고정. 변경하려면 config 갱신 + 새 세션.

---

## 6. 변경 이력

| Task-ID | 변경 |
|---|---|
| `HARNESS-CHG-20260427-03` [2.4] | 도입 — `harness/config.py` + 본 문서 |
