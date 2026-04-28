# Orchestration Policies

> 운영 룰 카탈로그. 헌법(`docs/harness-spec.md`)이 *무엇을·왜* 강제하는지 정의한다면, 본 문서는 워크플로우 변경의 *기록·추적·검증* 절차를 정의한다.

작성: 2026-04-27 (Phase 0 가벼운 버전)
다음 갱신 예정: Phase 2 — 자동 게이트(`scripts/check_doc_sync.py`) 활성화 시점

---

## 1. Task-ID 형식

- **형식**: `HARNESS-CHG-YYYYMMDD-NN`
- **예시**: `HARNESS-CHG-20260427-01`
- **발급**: 모든 워크플로우 변경에 1개 발급
- **연결**: WHAT 로그(`changelog.md`)와 WHY 로그(`rationale.md`)를 동일 ID로 묶음

같은 날 여러 변경이 있으면 `-01`, `-02` 식으로 일련번호. 충돌 방지를 위해 PR 생성 시점에 `changelog.md` 마지막 항목 확인.

---

## 2. Change-Type 5종

| 토큰 | 감시 경로 | 동반 필수 산출물 |
|---|---|---|
| `spec` | `docs/harness-spec.md`, `docs/harness-architecture.md`, `docs/proposals.md`, `prd.md`, `trd.md` | `changelog.md` + `rationale.md` (양쪽 필수) |
| `infra` | `hooks/`, `harness/`, `scripts/`, `.claude-plugin/`, `.github/` | `changelog.md` + 영향 받는 spec 문서 검토 표시 |
| `agent` | `agents/*.md`, `agents/**/*.md` | `changelog.md` + 영향 받는 spec 문서 검토 표시 |
| `docs` | `README.md`, `CHANGELOG.md`, `docs/` (spec/proposals 외), `templates/` | `changelog.md` |
| `test` | `tests/pytest/` | (산출물 추가 없음) |

> **분류 충돌 시 우선순위**: `spec` > `infra` > `agent` > `docs` > `test`. 한 PR이 여러 유형을 포함하면 가장 강한 유형의 산출물 요건이 적용된다.

---

## 3. Document-Exception 스코핑

동반 산출물을 갖추기 어려운 경우 (예: 단순 typo, urgent hotfix) 커밋 메시지 또는 PR 본문에 명시:

```
Document-Exception: <사유>
```

### 판정 룰

- **유효**: 현재 diff의 *추가 라인*에 `Document-Exception:` 토큰이 있는 경우
- **무효**: 과거 커밋·과거 changelog 엔트리에 있던 Exception은 재사용 불가 (자동 게이트는 git diff로만 검증)
- **사유 길이**: 최소 10자 이상 (단순 "exempt" 같은 텍스트 거부)

### Phase 2 자동 게이트

- `scripts/check_doc_sync.py` (Python) — `git diff --name-only` 로 변경 파일 추출 → Change-Type 자동 분류 → 동반 산출물 검사 → Document-Exception 라인 파싱
- `scripts/hooks/pre-commit.sh` — git pre-commit 훅용 한 줄 래퍼
- `hooks/commit-gate.py` — Claude Code PreToolUse(Bash) 훅에 doc sync 체크 통합
- 실패 시: 커밋·머지 차단

Phase 0~1에선 위 게이트 비활성. 룰만 명시.

---

## 4. 작업 절차

```
1. 시작
   ├─ 새 Task-ID 발급 (changelog.md 마지막 번호 + 1)
   └─ rationale.md에 WHY 4섹션(Rationale / Alternatives / Decision / Follow-Up) 초안 작성

2. 수행
   ├─ 변경 진행
   └─ changelog.md에 WHAT 1줄 추가 (Type, Files, Title)

3. 완료
   ├─ rationale.md WHY 섹션 확정
   └─ 동반 산출물(Change-Type별) 갖추기

4. PR
   ├─ PR title: <Task-ID> <한 줄 요약>
   └─ PR body: changelog.md 항목 인용 + Document-Exception(있을 시)

5. 머지
   ├─ squash merge (commit msg 본문에 Task-ID 포함)
   └─ post-commit-cleanup이 1회성 플래그 정리
```

---

## 5. 로그 분리 원칙 (WHAT vs WHY)

| 항목 | WHAT (`changelog.md`) | WHY (`rationale.md`) |
|---|---|---|
| 무엇을 바꿨나 | ✓ | — |
| 왜 바꿨나 | — | ✓ Rationale |
| 어떤 대안을 검토했나 | — | ✓ Alternatives |
| 왜 이 대안을 선택했나 | — | ✓ Decision |
| 후속 작업은 무엇인가 | — | ✓ Follow-Up |
| Task-ID 색인 | ✓ 헤더 | ✓ 섹션 헤더 |

> **6개월 후 "왜 이렇게 했더라?"** 에 답하는 자산은 `rationale.md`. PR 메시지·커밋 메시지에 분산 작성하지 말 것.

---

## 6. 자동 게이트 (Phase 2 활성화 예정 — 명세만 정의)

### 6.1 분류 알고리즘 (`scripts/check_doc_sync.py`)

```python
def classify(file_path: str) -> ChangeType:
    # 우선순위 순 매칭
    if matches(file_path, SPEC_PATTERNS):   return "spec"
    if matches(file_path, INFRA_PATTERNS):  return "infra"
    if matches(file_path, AGENT_PATTERNS):  return "agent"
    if matches(file_path, TEST_PATTERNS):   return "test"
    return "docs"  # default
```

### 6.2 검증 단계

1. `git diff --name-only $base $head` → 변경 파일 목록
2. 각 파일을 Change-Type으로 분류
3. PR 전체의 우선순위 최상위 유형 결정
4. 해당 유형의 동반 산출물이 동일 diff에 포함됐는지 검사
5. 누락 시 → `Document-Exception:` 라인 파싱 → 유효하면 통과, 아니면 차단

### 6.3 통합 지점

- 로컬: `git commit` → `.git/hooks/pre-commit` → `scripts/check_doc_sync.py`
- Claude Code: `Bash(git commit ...)` PreToolUse → `hooks/commit-gate.py` → 동일 스크립트 호출
- CI: GitHub Actions `pull_request` → `scripts/check_doc_sync.py $BASE $HEAD`

3중 강제로 어떤 경로(메인 Claude / 다른 에이전트 / 휴먼)로 들어와도 게이트 우회 불가.

---

## 8. test-sync 게이트 (PR-time)

> 같은 패턴: §3 Document-Exception (`scripts/check_doc_sync.py`) 와 골격 공유. 본 §8 은 코드 변경에 대한 회귀 테스트 동반 강제만 다룬다.

### 8.1 트리거 경로

| 토큰 | 감시 경로 | 동반 필수 |
|---|---|---|
| `code` | `harness/`, `hooks/` | `tests/**` 아래 1개 이상 변경 |

비트리거: `docs/`, `agents/`, `scripts/` 자체, `.github/`, `prd.md`, `trd.md`, `templates/`, `orchestration/` — 본 게이트 미적용 (§2~3 doc-sync 게이트는 별도).

### 8.2 Tests-Exception 스코핑

동반 테스트 추가가 어려운 경우 (docstring/comment-only refactor, mass-rename 등) 커밋 메시지 또는 PR 본문에 명시:

```
Tests-Exception: <10자 이상 사유>
```

판정 룰 (§3 Document-Exception 와 동일):
- 유효: 현재 diff 의 *추가 라인* 또는 현재 commit msg 에 마커 + 사유 ≥ 10자
- 무효: 과거 commit / 과거 changelog 엔트리 재사용 불가
- 사유 길이: 최소 10자 (단순 "skip" 거부)

### 8.3 통합 지점

- CI: GitHub Actions `pull_request` → `scripts/check_test_sync.py $BASE $HEAD` (.github/workflows/test-sync.yml)
- 로컬 (선택): `git commit` 시 pre-commit 훅 — Stage A2 범위 외 (epic #30 후속 단계)

### 8.4 본 게이트가 있었으면 차단됐을 사례

[14.1]~[14.5] 5건 연속 commit. 모두 harness/ or hooks/ 코드 변경 + tests 0 + Tests-Exception 미명시. retroactive 시뮬레이션 결과는 issue #32 PR body 에 첨부.

---

## 9. 본 문서 갱신 룰

- 본 문서 자체의 변경은 `Change-Type: spec` 으로 분류 (감시 경로 `docs/proposals.md`와 동일 우선순위 적용)
- 즉, 본 문서를 바꾸려면 `changelog.md` + `rationale.md` 양쪽 항목이 필요
- 단, Phase 0~1에선 자동 게이트 비활성이므로 휴먼 enforce
