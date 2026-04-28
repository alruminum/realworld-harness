---
issue: 31
type: feature
depth: simple
identifier_candidate: HARNESS-CHG-20260428-27.A1
parent_epic: 30
related: HARNESS-CHG-20260428-26 [26.1] (PR #29, [14.2] hole retroactive 케이스)
---

# Impl 계획 — Issue #31 light-plan 분기 enumeration 섹션 강제 (Stage A1)

> Status: **LIGHT_PLAN_READY** (depth=simple, 가이드라인 텍스트 보강 + 형식 회귀 테스트 1개)
> Branch (제안): `harness/light-plan-branch-enumeration`
> PR title (제안): `HARNESS-CHG-20260428-27.A1 light-plan 분기 enumeration 섹션 강제 (Path coverage 누락 차단)`

## 변경 대상

- 파일: `agents/architect/light-plan.md` — 산출물 템플릿에 "분기 enumeration" 섹션 강제
- 파일: `agents/validator/plan-validation.md` — 동 섹션이 비어있거나 분기 1개만이면 PLAN_VALIDATION_FAIL 게이트 추가
- 파일: `tests/pytest/test_plan_template.py` — **신규** 형식 회귀 테스트 (정규식 기반)
- 요약: [14.2] hole 사례를 일반화 — light-plan 작성자가 수정 함수의 모든 분기를 명시적으로 enumerate 하도록 템플릿·검증 게이트·자동 회귀 검사 3축 강제.

## 배경 (요약)

- **#26 [14.2] hole**: `WorktreeManager.create_or_reuse()` 의 `if wt_path.exists(): return wt_path` reuse 분기에서 `_copy_untracked_plan_files()` 가 누락. fresh path 만 plan 복사 호출이 들어가 동일 이슈 재진입마다 \$1.82 낭비.
- **본질적 결함**: light-plan 작성자가 fresh path 만 의식하고 reuse path 를 enumerate 안 함 → 회귀 테스트도 그 분기 누락 → 머지 후 jajang 런에서 발현.
- **본 fix 방향** (메타 회귀 차단): 산출물 템플릿에 "변경 대상 함수의 *모든* 호출 사이트 + 내부 분기 + out-of-scope 라벨" 섹션을 필수로 만들고, validator 가 빈 enumeration 을 거부.
- **자가 적용**: 본 impl 도 산출물에 분기 enumeration 섹션을 채워 retroactive 검증.

## 수정 내용

### 1. `agents/architect/light-plan.md` — "변경 대상" 다음에 "분기 enumeration" 섹션 추가

현재 템플릿 (line 42-58):
```markdown
# [이슈 제목]

## 변경 대상
- 파일: `src/path/to/file.ts`
- 컴포넌트/함수: `componentName` (line NN-NN)
- 요약: [1-2문장 — 무엇을 왜 바꾸는지]

## 수정 내용
- [구체적 변경 사항]

## 수용 기준
| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | [변경 확인] | (TEST) | [vitest TC 또는 검증 설명] |
```

수정 후 (의도):
```markdown
# [이슈 제목]

## 변경 대상
- 파일: `src/path/to/file.ts`
- 컴포넌트/함수: `componentName` (line NN-NN)
- 요약: [1-2문장 — 무엇을 왜 바꾸는지]

## 분기 enumeration

수정 대상 함수/클래스의 **모든 호출 사이트 + 모든 내부 분기**를 빠짐없이 나열한다.
의도적으로 다루지 않는 분기는 `out-of-scope` 라벨로 명시 (회귀 가능성 평가 포함).

| 분기 / 호출 사이트 | 위치 | fix 적용 여부 | 회귀 가능성 / out-of-scope 사유 |
|---|---|---|---|
| [분기 A — 예: fresh 생성 path] | `file.ts:NN` | YES | 본 fix 의 1차 대상 |
| [분기 B — 예: reuse 분기] | `file.ts:MM` | YES | [14.2] hole. 본 fix 가 동일 정책 확장 |
| [분기 C — 예: error path] | `file.ts:KK` | NO (out-of-scope) | 별도 이슈 (#NN). 본 fix 와 독립 — 회귀 없음 |

> **최소 2행 필수.** 분기가 하나뿐인 단순 함수면 `single-branch` 라벨로 한 줄 + "단일 분기 함수 — enumeration 불필요" 사유 명시.
> **out-of-scope 분기**도 반드시 명시 — "안 봤다"가 아니라 "보고 의도적으로 제외했다" 를 문서화.

## 수정 내용
- [구체적 변경 사항]

## 수용 기준
...
```

또한 §"LIGHT_PLAN_READY 게이트" 자가 체크에 한 항목 추가:
```markdown
- [ ] 분기 enumeration 섹션 존재 + 최소 2행 (또는 single-branch 라벨로 명시적 단일 분기 선언)
```

### 2. `agents/validator/plan-validation.md` — 체크리스트 §A 에 항목 추가

현재 §A (line 22-30):
```markdown
| 항목 | 확인 기준 |
|---|---|
| 생성/수정 파일 목록 | 구체적 파일 경로가 명시되어 있는가 |
| 인터페이스 정의 | TypeScript 타입/Props/함수 시그니처가 명시되어 있는가 |
| 핵심 로직 | 의사코드 또는 구현 가능한 스니펫이 존재하는가 (빈 섹션이면 FAIL) |
| 에러 처리 방식 | throw/반환/상태 업데이트 중 어떤 전략인지 명시되어 있는가 |
| 의존 모듈 실재 | 계획이 참조하는 모듈/함수가 실제 소스에 존재하는가 |
```

수정 후:
```markdown
| 항목 | 확인 기준 |
|---|---|
| 생성/수정 파일 목록 | 구체적 파일 경로가 명시되어 있는가 |
| 인터페이스 정의 | TypeScript 타입/Props/함수 시그니처가 명시되어 있는가 |
| 핵심 로직 | 의사코드 또는 구현 가능한 스니펫이 존재하는가 (빈 섹션이면 FAIL) |
| 에러 처리 방식 | throw/반환/상태 업데이트 중 어떤 전략인지 명시되어 있는가 |
| 의존 모듈 실재 | 계획이 참조하는 모듈/함수가 실제 소스에 존재하는가 |
| **분기 enumeration** | **`## 분기 enumeration` 섹션이 있고, 데이터 행이 2행 이상이거나 `single-branch` 라벨이 명시되어 있는가** ([14.2] hole 회귀 차단) |

> "분기 enumeration" 행이 0개거나 단일 분기인데 single-branch 라벨이 없으면 즉시 FAIL.
> light-plan 산출물 (`docs/impl/N-*.md` 또는 `docs/bugfix/#N-*.md`) 에만 적용 — module-plan 은 §"핵심 로직" 의사코드가 동등 역할.
```

§"출력 형식" 섹션의 §A 출력 표에도 동일 행 추가:
```markdown
| 분기 enumeration | PASS/FAIL | (행 수) |
```

### 3. `tests/pytest/test_plan_template.py` — 신규 형식 회귀 테스트

```python
"""test_plan_template.py — light-plan 산출물 형식 회귀 (Issue #31).

[14.2] hole (#26) retroactive 사례:
  light-plan 작성자가 수정 함수의 reuse 분기를 enumerate 안 함 → 회귀 테스트 누락 → 머지 후 발현.
본 테스트는 "분기 enumeration 섹션이 없거나 비어있는" light-plan 을
정규식 검사로 거부한다. LLM 의 enumeration 의미적 정확성은 비목표 (사람 영역).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ── 검증 정규식 ──────────────────────────────────────────────────────────
# §"분기 enumeration" 섹션이 존재해야 한다.
SECTION_HEADER = re.compile(r"^##\s+분기\s*enumeration\s*$", re.MULTILINE)

# 헤더 다음~다음 §## 헤더 직전까지를 섹션 본문으로 추출.
SECTION_BODY = re.compile(
    r"^##\s+분기\s*enumeration\s*$(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

# 표의 데이터 행 ("|" 로 시작 + 셀 4개 이상, 헤더/구분자 제외).
TABLE_DATA_ROW = re.compile(
    r"^\|(?!\s*[-:|\s]+\|\s*$)(?!\s*분기\b).+\|.+\|.+\|.+\|\s*$",
    re.MULTILINE,
)

# single-branch 라벨 (단일 분기 함수 명시 escape hatch).
SINGLE_BRANCH_LABEL = re.compile(r"single-branch", re.IGNORECASE)


def _has_branch_enumeration(text: str) -> tuple[bool, str]:
    """광범위 검사. (passed, reason) 반환."""
    if not SECTION_HEADER.search(text):
        return False, "§분기 enumeration 섹션 누락"

    m = SECTION_BODY.search(text)
    if not m:
        return False, "§분기 enumeration 섹션 본문 추출 실패"

    body = m.group(1)
    rows = TABLE_DATA_ROW.findall(body)
    has_single_label = bool(SINGLE_BRANCH_LABEL.search(body))

    if not rows and not has_single_label:
        return False, "분기 enumeration 표가 비어있고 single-branch 라벨도 없음"
    if len(rows) < 2 and not has_single_label:
        return False, f"분기 행 {len(rows)}개 — 최소 2행 또는 single-branch 라벨 필요"
    return True, "OK"


# ── 합성 픽스처 — light-plan 산출물 형식 검사 ─────────────────────────────

VALID_TWO_BRANCH = """
# Sample

## 변경 대상
- 파일: `foo.py`

## 분기 enumeration

| 분기 / 호출 사이트 | 위치 | fix 적용 여부 | 회귀 가능성 |
|---|---|---|---|
| fresh path | `foo.py:10` | YES | 본 fix 1차 대상 |
| reuse path | `foo.py:20` | YES | [14.2] hole 메우기 |

## 수정 내용
"""

VALID_SINGLE_BRANCH = """
## 분기 enumeration

| 분기 | 위치 | fix 적용 | 사유 |
|---|---|---|---|
| 단일 진입점 (single-branch) | `bar.py:5` | YES | 단일 분기 함수 — enumeration 불필요 |

## 수정 내용
"""

INVALID_NO_SECTION = """
# Sample

## 변경 대상
## 수정 내용
"""

INVALID_EMPTY_SECTION = """
## 분기 enumeration

(아직 작성 안 함)

## 수정 내용
"""

INVALID_SINGLE_ROW_NO_LABEL = """
## 분기 enumeration

| 분기 | 위치 | fix 적용 | 사유 |
|---|---|---|---|
| only path | `x.py:1` | YES | 본 fix |

## 수정 내용
"""


class TestBranchEnumerationRegex:
    """light-plan 산출물 형식 회귀 — 정규식만 (LLM 의미 검증은 비목표)."""

    def test_two_branch_table_passes(self):
        ok, reason = _has_branch_enumeration(VALID_TWO_BRANCH)
        assert ok, reason

    def test_single_branch_label_passes(self):
        ok, reason = _has_branch_enumeration(VALID_SINGLE_BRANCH)
        assert ok, reason

    def test_missing_section_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_NO_SECTION)
        assert not ok
        assert "누락" in reason

    def test_empty_section_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_EMPTY_SECTION)
        assert not ok
        assert "비어있" in reason or "행" in reason

    def test_single_row_without_label_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_SINGLE_ROW_NO_LABEL)
        assert not ok
        assert "1개" in reason or "최소" in reason


class TestActualLightPlanArtifacts:
    """현재 repo 의 light-plan 산출물이 형식 게이트를 통과하는지 회귀 검사.

    docs/impl/*.md 중 frontmatter 에 `depth: simple` 인 파일만 대상.
    (module-plan / deep depth 는 §"핵심 로직" 의사코드가 등가 역할 — 본 게이트 면제)
    """

    def _light_plan_files(self) -> list[Path]:
        out = []
        for p in (ROOT / "docs" / "impl").glob("*.md"):
            text = p.read_text(encoding="utf-8")
            if re.search(r"^depth:\s*simple\s*$", text, re.MULTILINE):
                out.append(p)
        return out

    def test_self_apply_branch_enumeration(self):
        """이 impl 자체 (#31) 가 자기 게이트를 통과해야 한다 — meta-recursive 검증."""
        target = ROOT / "docs" / "impl" / "31-light-plan-branch-enumeration.md"
        if not target.exists():
            pytest.skip("self impl not yet committed")
        ok, reason = _has_branch_enumeration(target.read_text(encoding="utf-8"))
        assert ok, f"self-apply violation: {reason}"
```

> 가설: pytest 가 `tests/pytest/conftest.py:23` 의 `ROOT` 추가로 `harness/` 등을 import 하고 있다 — 본 테스트는 import 없이 정규식만 쓰므로 conftest 영향 없음.
> 픽스처는 모두 인라인 문자열 — 외부 파일 의존 없음. `TestActualLightPlanArtifacts` 만 실 산출물 의존이고, self impl 미존재 시 skip.

## 수정 파일

| 파일 | 변경 | 비고 |
|---|---|---|
| `agents/architect/light-plan.md` | "분기 enumeration" 섹션 템플릿 + LIGHT_PLAN_READY 자가 체크 1행 추가 | line 42-58 영역 + 73-79 영역 |
| `agents/validator/plan-validation.md` | §A 체크리스트에 "분기 enumeration" 행 추가 + 출력 표에도 동일 추가 | line 22-30 + line 66-94 영역 |
| `tests/pytest/test_plan_template.py` | **신규** — 정규식 형식 회귀 테스트 (REQ-003) | conftest.py 의 ROOT/sys.path 자동 활용 |

> 인터페이스 변경: 없음. 모두 가이드라인 텍스트 + 정규식 스펙.

## 분기 enumeration

본 fix 자체가 retroactive 검증이므로 변경 함수가 아닌 **변경 대상 게이트**의 모든 진입 분기를 enumerate.

| 분기 / 진입점 | 위치 | fix 적용 여부 | 회귀 가능성 / out-of-scope 사유 |
|---|---|---|---|
| LIGHT_PLAN_READY 산출 (architect) | `agents/architect/light-plan.md` 템플릿 | YES | 분기 enumeration 섹션 + 자가 체크 행 추가 — 1차 대상 |
| PLAN_VALIDATION (validator §A) | `agents/validator/plan-validation.md` line 22-30 | YES | 빈 enumeration 거부 게이트 — 1차 대상 |
| MODULE_PLAN 산출 (architect) | `agents/architect/module-plan.md` | NO (out-of-scope) | module-plan 은 §"핵심 로직" 의사코드가 동등 역할. 별도 epic #30 후속 단계에서 결정. 회귀 가능성: low — 본 게이트는 light-plan 산출물에만 적용 |
| 회귀 테스트 자체 (regex 검사) | `tests/pytest/test_plan_template.py` | YES | 형식만 검증. LLM 의미 검증은 비목표 (이슈 본문 §비목표) |
| 기존 [14.2] retroactive 적용 | (메타) | NO (out-of-scope, 문서화만) | A1 출시 후 backfill 별도 트랙 (이슈 본문 §비목표). 본 impl §"[14.2] retroactive 검증" 섹션에서 "본 게이트가 있었다면 차단됐을 것" 만 문서화 |

## [14.2] retroactive 검증 (수용 기준 4)

#26 (PR #29, `docs/impl/26-worktree-reuse-plan-copy.md`) 가 본 게이트를 retroactive 로 적용했다면:

원래 [14.2] PR #18 의 light-plan (가설 — 실제 산출물 미보존) 이 다음 표만 가졌을 것이라고 추정:

| 분기 / 호출 사이트 | 위치 | fix 적용 |
|---|---|---|
| fresh worktree 생성 path | `core.py:1366` | YES |

→ **단일 행 + single-branch 라벨 없음** → `_has_branch_enumeration` 가 `len(rows) < 2 and not has_single_label` 에서 FAIL → PLAN_VALIDATION_FAIL → architect 가 reuse 분기를 강제로 enumerate 했어야 함.

원래 작성자가 `if wt_path.exists(): return wt_path` 라인을 한번 보고:
- 분기 B (reuse) 를 표에 추가 → "fix 적용: NO (의도) / 회귀 가능성: 동일 issue 재진입 시 plan 복사 누락" 으로 문서화 강제
- 그 시점에 "어, 이거 복사도 빠지네" 자각 → fresh + reuse 양쪽에 호출 추가하는 진짜 fix 로 확장
- 또는 의도적으로 reuse 미적용이면 회귀 가능성을 드러내고 별도 추적 이슈 생성

→ 현재 시점에서 우리가 #26 으로 메우는 hole 이 [14.2] 시점에 메워졌을 가능성이 높다.

## 수용 기준

| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | light-plan 가이드라인에 "분기 enumeration" 섹션 명시 | (TEST) `tests/pytest/test_plan_template.py::TestBranchEnumerationRegex::test_two_branch_table_passes` + `test_single_branch_label_passes` | 두 합성 픽스처가 PASS |
| REQ-002 | plan-validation 게이트가 빈 / 단일행 enumeration 거부 | (TEST) `TestBranchEnumerationRegex::test_missing_section_fails` + `test_empty_section_fails` + `test_single_row_without_label_fails` | 세 합성 픽스처가 FAIL + reason 문자열에 "누락"/"비어있"/"행" 또는 "최소" 포함 |
| REQ-003 | 형식 회귀 테스트 1개 추가 | (TEST) `tests/pytest/test_plan_template.py` 파일 자체 존재 + pytest 수집 | `python3 -m pytest tests/pytest/test_plan_template.py -v` 가 5개 이상 테스트 수집 |
| REQ-004 | [14.2] retroactive 시나리오 문서화 — 본 게이트가 있었다면 reuse 분기가 enumeration 에 잡혔어야 함 | (REVIEW) impl 파일의 §"[14.2] retroactive 검증" 섹션 내용 검토 | 가설 표 + "왜 차단됐을 것인가" 1문단 명시 |

## 검증 명령

```bash
python3 -m pytest tests/pytest/test_plan_template.py -v
# 통과 후 self-apply 검증:
python3 -m pytest tests/pytest/test_plan_template.py::TestActualLightPlanArtifacts -v
```

## 비변경 (의도)

- `agents/architect/module-plan.md` — 손대지 않음 (분기 enumeration 게이트는 light-plan 한정).
- `agents/architect/spec-gap.md` / `task-decompose.md` 등 다른 architect 모드 — 동일.
- 기존 light-plan 산출물 retroactive 보강 — A1 출시 후 backfill 별도 트랙 (이슈 본문 §비목표).
- 자동 분기 추출 (AST 분석) — 비목표. 정규식 형식 검사만 (이슈 본문 §비목표).

## 비목표

- LLM 출력의 "의미적 정확성" 검증 — 사람 영역. 본 게이트는 "섹션이 있고 행이 있다" 까지만 강제.
- 분기 자동 추출 (AST 분석 등) — 과한 엔지니어링. 정규식 형식 검사만.
- 기존 [14.2] / [13] / [LOCAL-1] 등 retroactive 적용 — A1 출시 후 backfill 별도 트랙.
- module-plan / spec-gap 등 light-plan 외 모드로의 확장 — epic #30 후속 단계.

## 위임 흐름

```
이 light-plan (architect 산출)
  → engineer 호출 (메인 단독 agents/ 변경 금지 룰 준수)
  → validator (PLAN_VALIDATION 자기 적용 — 본 impl 의 §분기 enumeration 표 통과 확인)
  → pr-reviewer
  → squash merge
  → orchestration/changelog.md 에 HARNESS-CHG-20260428-27.A1 항목 추가
```

## Linked

- 부모 epic: #30 (Stage A 메타 회귀 차단 epic)
- 선행 사례: `HARNESS-CHG-20260428-26 [26.1]` (PR #29, `docs/impl/26-worktree-reuse-plan-copy.md`) — [14.2] hole 메움 + 본 fix 의 retroactive 시험 케이스.
- 관련: `HARNESS-CHG-20260428-14.2` (PR #18, commit 4eb20b3) — fresh path 의 plan 복사. 본 fix 의 retroactive 분석 대상.
