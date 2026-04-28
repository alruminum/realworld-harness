---
issue: 34
type: bugfix
depth: simple
identifier_candidate: HARNESS-CHG-20260428-34 [34.1]
related: HARNESS-CHG-20260428-14 [14.5] (PR #21, no_changes 즉시 escalate 도입)
---

# Impl 계획 — Issue #34 autocheck no_changes 오판 (test-only commit stranded)

> Status: **LIGHT_PLAN_READY** (depth=simple, helpers.py 단일 파일 분기 보강 + rollback 정책 보강)
> Branch (제안): `harness/autocheck-no-changes-test-only`
> PR title (제안): `HARNESS-CHG-20260428-34 [34.1] autocheck no_changes 오판 — test-only commit PASS + stranded 방지`

## 변경 동기 (요약)

2026-04-28 jajang `run_20260428_163700` 에서 발견. engineer 가 정상적으로 회귀 테스트 파일 (`apps/api/tests/...`) 을 커밋(`611fbb8`) 했지만 autocheck 가 `apps/api/app/**` (engineer_scope) 미변경을 보고 `no_changes` FAIL → escalate. push 안 됨. PR #128 이 직전 커밋(`727e704`)에서 squash merge → `611fbb8` 이 worktree 안에 orphan 으로 stranded.

근본 원인 두 개:

1. **autocheck 의 no_changes 판정**(`helpers.py:284-310`)이 "engineer_scope 변경 여부"만 보고, 직전 커밋이 test-only 정상 커밋(TDD lock-in 또는 회귀테스트 추가)인지 검사하지 않음.
2. **`rollback_attempt`** (`helpers.py:230-242`) 가 JSONL 이벤트만 기록하고 "keep-on-branch" 신호만 출력 — 실제 git 상태는 손대지 않음. 이로 인해 부정 케이스(빈 커밋·scope 외 commit)에서 worktree 안에 commit 이 stranded.

연관: HARNESS-CHG-20260428-14 [14.5] (PR #21) 가 no_changes 즉시 escalate 를 도입했으나 *이미 만들어진 commit 이 stranded 되는 문제* + *test-only 정상 커밋 오인 문제* 는 미해결 상태였음.

## 수용 기준 (이슈 본문 1:1 매핑)

| 요구사항 ID | 이슈 본문 | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|---|
| REQ-001 | 본문 §수용기준 1 | autocheck no_changes 분기 진입 시 `git log -1 --name-only HEAD` 로 직전 커밋 변경 파일 확인 | (TEST) `tests/pytest/test_autocheck_no_changes.py::TestREQ001LastCommitInspection::test_inspects_last_commit_on_no_changes` | helpers.py 가 `git log -1 --name-only HEAD` 호출 (subprocess capture 검증 또는 임시 git repo 시나리오에서 PASS 결과 도출) |
| REQ-002 | 본문 §수용기준 2 | 직전 커밋이 test 파일만(또는 test + plan 문서) 포함 → PASS 처리 + push 진행 | (TEST) `TestREQ002TestOnlyCommitPass::test_test_only_commit_returns_pass`, `test_test_and_plan_commit_returns_pass`, `test_plan_only_commit_returns_pass` | `run_automated_checks(...)` 반환값 = `(True, "")` |
| REQ-003 | 본문 §수용기준 3 | 직전 커밋이 의도 외 파일(or 빈 커밋) → escalate 유지 + `git reset --hard origin/<branch>` 로 commit 롤백 (stranded 방지). origin/<branch> 부재 시 `git reset --hard HEAD~1` 폴백 | (TEST) `TestREQ003RollbackOnInvalidScope::test_mixed_commit_resets_hard`, `test_empty_commit_resets_hard`, `test_no_origin_falls_back_to_head_minus_one` | reset 후 worktree HEAD 가 직전 커밋 이전을 가리킴. test 환경에서 `git rev-parse HEAD` 결과로 검증 |
| REQ-004 | 본문 §수용기준 4 | 풀 사이클 (qa → architect → engineer → validator → pr-reviewer) — `harness/helpers.py` invariant 영역 | (MANUAL: 위임 흐름은 Git history / GitHub PR review log / orchestration changelog 로만 검증 가능, 자동 단위 테스트 비대상) PR 본문에 본 impl 링크 + 위임 흐름 명시 | engineer 직접 호출 금지, pr-reviewer 통과 후 squash merge |
| REQ-005 | 본문 §수용기준 5 | 회귀 테스트 1개 이상 추가 (test-only PASS + rollback 케이스 + G5 보강) | (TEST) 신규 `tests/pytest/test_autocheck_no_changes.py` (7개 클래스 ≥11 TC — REQ-001~003 분해 + REQ-006~008 invariant 보호 + G5 hard_reset JSONL 분류 + passthrough build_fail) | pytest 통과 |
| REQ-006 | (보강) | "test-only" 분류 정의 — `tests/`, `__tests__/`, `*.spec.{ts,tsx,js,jsx,py}`, `*.test.{ts,tsx,js,jsx}`, `_test.py`, `test_*.py` | (TEST) `TestREQ006Classification::test_classify_*` (4 케이스) | classifier 함수가 의도된 categorization 반환 |
| REQ-007 | (보강) | "plan 문서" 분류 정의 — `docs/impl/`, `docs/bugfix/`, `docs/milestones/` (worktree 보호 prefixes 와 정합) | (TEST) `TestREQ006Classification::test_classify_plan_only` | category=`plan_only` |
| REQ-008 | (보강) | 두 카테고리 외 파일 1개라도 섞이면 `mixed` 로 분류 → escalate (test-only 로 해석하지 않음) | (TEST) `TestREQ006Classification::test_mixed_commit_does_not_pass` | category=`mixed`, escalate 분기 진입 |

## 변경 파일 목록 + 인터페이스 영향

| 파일 | 변경 | 비고 |
|---|---|---|
| `harness/helpers.py` | `run_automated_checks` 의 no_changes 분기에 직전 커밋 분류 + PASS/escalate 분기 추가. `rollback_attempt` 시그니처 확장 (옵션 인자 추가, 기존 호출 호환). 신규 private helper `_classify_last_commit_files()` 추가. test-only 판정은 `path_resolver.test_paths_extract_regex()` 로 위임 (G4 참조). | 메인 변경 파일 |
| `harness/core.py` | **클래스 속성 제거 + 모듈 레벨 상수 신설** + `_copy_untracked_plan_files` 의 `self._PLAN_PREFIXES` → `_PLAN_PREFIXES` 교체 (G1 결정 (α) 클래스 속성 제거형). 외부 `WorktreeManager._PLAN_PREFIXES` 속성 접근 불가 (실 사용처 0개로 안전). | 2개 라인 변경(class 본문 정의 1줄 삭제 + module-level 상수 1줄 신설) + `self._PLAN_PREFIXES` → `_PLAN_PREFIXES` 1곳 교체 |
| `harness/path_resolver.py` | `_V1_TEST_PATHS_REGEX` 보강 — pytest `_test.py` / `test_*.py` 패턴 추가 (현재 `r"src/[^ ]+\.(?:test|spec)\.[jt]sx?"` 만이라 pytest 누락). G4 (a) 결정에 따라 test-only 분류가 path_resolver 위임이므로 누락 시 mixed 오분류 위험. | 정규식 1개 라인 갱신 + V2 자동 합성 본문도 동일 패턴 추가 |
| `tests/pytest/test_autocheck_no_changes.py` | **신규** — 회귀 테스트 (REQ-001~003, REQ-006~008) | 임시 git repo + 실제 subprocess (`tests/pytest/test_worktree.py` 컨벤션 따름) |
| `orchestration/changelog.md` | `HARNESS-CHG-20260428-34 [34.1]` 항목 추가 | 평소 절차 |

### `core._PLAN_PREFIXES` SSOT 승격 (G1) — 옵션 (α) 클래스 속성 제거형 단일 채택

현재 (`harness/core.py:1375`, `:1390`):
```python
class WorktreeManager:
    ...
    _PLAN_PREFIXES = ("docs/bugfix/", "docs/impl/", "docs/milestones/")  # 클래스 속성
    ...
    def _copy_untracked_plan_files(self, wt_path, reused=False):
        ...
        if not rel or not rel.startswith(self._PLAN_PREFIXES):  # 인스턴스 경유
            continue
```

수정 후 — 옵션 (α) 클래스 속성 제거형:
```python
# 모듈 레벨 (class 정의 직전)
_PLAN_PREFIXES = ("docs/bugfix/", "docs/impl/", "docs/milestones/")

class WorktreeManager:
    ...
    # 클래스 본문에는 _PLAN_PREFIXES 정의 없음 — 클래스 속성 자체를 제거.
    # alias 라인 (`_PLAN_PREFIXES = _PLAN_PREFIXES`) 도 두지 않음.
    def _copy_untracked_plan_files(self, wt_path, reused=False):
        ...
        # self._PLAN_PREFIXES → _PLAN_PREFIXES (모듈 변수 직접 참조)
        if not rel or not rel.startswith(_PLAN_PREFIXES):
            continue
```

본 PR 채택: **옵션 (α) 클래스 속성 제거형**. `_PLAN_PREFIXES` 의 실 사용처는 `_copy_untracked_plan_files` 의 `self._PLAN_PREFIXES` 참조 1곳뿐 (`harness/core.py:1390`). 자식 클래스 override 가능성 0, 외부에서 `WorktreeManager._PLAN_PREFIXES` 속성을 참조하는 코드도 0 (grep 확인) → 클래스 속성 자체를 제거해도 안전. 거절안 (β) (클래스 alias 유지형) 은 §결정 2 표 참조.

→ `helpers.py` 가 `from .core import _PLAN_PREFIXES` 로 임포트 가능. 진짜 SSOT 달성 (의사코드 fallback 트리는 임포트 실패 시 안전망으로만 동작).

### `rollback_attempt` 시그니처 (호환성 유지)

현재 (line 230-242):
```python
def rollback_attempt(
    attempt_num: int,
    run_logger: Optional[RunLogger] = None,
) -> None:
```

수정 (의도 — keyword-only optional 추가):
```python
def rollback_attempt(
    attempt_num: int,
    run_logger: Optional[RunLogger] = None,
    *,
    hard_reset: bool = False,
    feature_branch: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
```

기존 16개 호출처 (실측 grep — 본 PR 시점 `harness/impl_loop.py`) 는 위치인자 변경 없이 그대로 동작 (default = keep-on-branch). **본 impl 은 helpers.py 내부에서 새 분기에서만** `hard_reset=True, feature_branch=..., cwd=work_cwd` 로 호출 — `impl_loop.py` 16개 호출처 중 14개는 수정 0, 2개(`:510`, `:1226` no_changes 분기)만 keyword 인자 추가.

> validator 의 G2 갭 보고는 "19개" 였으나 실측 (`grep -n "rollback_attempt(" harness/impl_loop.py`) 기준 16개. 본 PR 표는 16개 전수.

`grep` 결과 (회귀 테스트 단계에서도 동일 값 검증 가능):
```
398   510   531   647   663   1121
1226  1243  1297  1339  1357  1367
1440  1452  1575  1589
```

분기 분류 전수 (코드 읽고 확인):

| line | 분기 (직전 if/elif) | hard_reset 적용? |
|---|---|---|
| 398 | `if not check_agent_output("engineer", eng_out):` (engineer agent 출력 0) | ❌ |
| 510 | `if check_err.startswith("no_changes:"):` (run_simple no_changes) | ✅ **본 PR** |
| 531 | autocheck_fail (run_simple, no_changes 외) | ❌ |
| 647 | `if not check_agent_output("pr-reviewer", pr_out):` (run_simple pr_fail no-output) | ❌ |
| 663 | `if pr_result != "LGTM":` (run_simple pr_fail CHANGES_REQUESTED) | ❌ |
| 1121 | `if not check_agent_output("engineer", eng_out):` (run_std/deep) | ❌ |
| 1226 | `if check_err.startswith("no_changes:"):` (run_std/deep no_changes) | ✅ **본 PR** |
| 1243 | autocheck_fail (run_std/deep, no_changes 외) | ❌ |
| 1297 | `if test_result.returncode != 0:` (GREEN test_fail) | ❌ |
| 1339 | `if not check_agent_output("validator", val_out):` (validator no-output) | ❌ |
| 1357 | `SPEC_MISSING` 분기 (architect MODULE_PLAN 복구 후) | ❌ |
| 1367 | `if val_result != "PASS":` (validator FAIL) | ❌ |
| 1440 | `if not check_agent_output("pr-reviewer", pr_out):` (run_std/deep pr_fail no-output) | ❌ |
| 1452 | `if pr_result != "LGTM":` (run_std/deep pr_fail CHANGES_REQUESTED) | ❌ |
| 1575 | `if not check_agent_output("security-reviewer", sec_out):` (deep security no-output) | ❌ |
| 1589 | `if sec_result != "SECURE":` (deep VULNERABILITIES_FOUND) | ❌ |

**14개 (line 398, 531, 647, 663, 1121, 1243, 1297, 1339, 1357, 1367, 1440, 1452, 1575, 1589) keep-on-branch 유지 사유**:
- 모든 fail 케이스가 *engineer / validator / pr-reviewer / security-reviewer 의 정상 산출이 있는 commit* 을 기록한 직후. retry 시 직전 commit 위에 fix-up commit 으로 갈음하는 패턴이 기존 의도. hard_reset 하면 `attempt-N-fix` 누적 이력 + 직전 lint/build 성공 상태가 사라져 회귀 분석 어려움.
- stranded 위험은 commit 의 *내용* 이 의도 외인 케이스에 한정 — no_changes 분기에서만 발생 (engineer 가 의도와 다른 파일을 잘못 commit 한 케이스).

**호출 전수 점검 (helpers 외 다른 모듈)**: `grep -rn "run_automated_checks\|rollback_attempt" harness/` 결과 — `impl_loop.py` 외 호출 없음. bugfix loop 가 별도 모듈로 분리되어 있다면 확인 필요 (현재 `harness/` 트리에는 bugfix 전용 모듈 없음 — `harness/bugfix_loop.py` 부재 확인됨). 따라서 **본 PR 의 `bugfix loop 도 helpers 공유` 가설은 grep 결과 철회**: 현재 RWHarness 에서 `run_automated_checks` / `rollback_attempt` 호출은 `impl_loop.py` 단독.

## invariant 결정 항목

### 1. "test-only" 정의 — path_resolver SSOT 위임 (G4)

직전 커밋의 변경 파일이 test 파일인지 판정하는 기준은 **`harness/path_resolver.py:test_paths_extract_regex()` 의 컴파일된 정규식을 재사용**한다. 그 외 별도 SSOT 신설 금지 (G4 결정).

```python
# harness/helpers.py — _is_test_file()
from .path_resolver import test_paths_extract_regex

_TEST_RE = test_paths_extract_regex()

def _is_test_file(path: str) -> bool:
    return bool(_TEST_RE.search(path))
```

매칭 대상 (path_resolver 가 V1 fallback 으로 보장하는 패턴):

| 패턴 | 매칭 예 | 근거 |
|---|---|---|
| basename 끝이 `.test.{ts,tsx,js,jsx}` | `Button.test.tsx` | jest/vitest |
| basename 끝이 `.spec.{ts,tsx,js,jsx}` | `auth.spec.ts` | mocha/vitest/playwright |
| basename 끝이 `_test.py` 또는 시작이 `test_*.py` | `test_recordings.py`, `recordings_test.py` | pytest 표준 (path_resolver V1 보강 — 본 PR 변경) |
| 경로에 `/tests/`, `/__tests__/` 디렉토리 | `apps/api/tests/test_recordings.py`, `src/components/__tests__/Button.test.tsx` | path_resolver V2 자동 합성 + V1 fallback 보강 (본 PR) |

**path_resolver V1 보강 (본 PR 동시 변경)**:

현재 `_V1_TEST_PATHS_REGEX = r"src/[^ ]+\.(?:test|spec)\.[jt]sx?"` 는:
- `src/` prefix 강제 → monorepo `apps/api/...` 누락
- pytest `_test.py` / `test_*.py` 누락
- `/tests/` 디렉토리 무명 (basename 만 잡음)

→ 본 PR 에서 다음 형태로 보강:
```python
_V1_TEST_PATHS_REGEX = (
    r"(?:^|/)(?:tests|__tests__)/[^ ]+"
    r"|(?:^|/)test_[^/ ]+\.py$"
    r"|[^ /]+_test\.py$"
    r"|[^ /]+\.(?:test|spec)\.(?:ts|tsx|js|jsx|mjs|cjs)$"
)
```

V2 자동 합성 본문 (`test_paths_extract_regex()` 의 `body = ...`) 도 위 패턴 기반으로 재합성. cfg.test_paths 미명시 케이스에서 monorepo 자동 추론 가능.

**구현 위치**: `_is_test_file()` 은 `harness/helpers.py` 모듈에서 `path_resolver.test_paths_extract_regex()` 의 컴파일된 결과를 1회 캐시. `_classify_last_commit_files()` private helper 가 사용.

**왜 별도 SSOT 신설 안 하는가** (G4 결정 근거):
- `path_resolver.test_paths_extract_regex()` 는 이미 test-engineer 산출 추출 + V2 monorepo 자동 합성을 처리하는 SSOT.
- helpers 가 자체 regex 를 또 만들면 path_resolver 와 drift 발생 (예: 신규 test 디렉토리 패턴 추가 시 한 곳만 갱신되는 위험).
- 두 곳의 의미가 동일 (test 파일이냐 아니냐) 이므로 한 SSOT 가 옳음.

### 2. "plan 문서" 정의

직전 커밋의 변경 파일들이 *모두* 아래 prefix 한 개 이상으로 시작하면 plan 문서로 간주:

| Prefix | 의미 |
|---|---|
| `docs/impl/` | impl 계획 (RWHarness 인프라 컨벤션 — `docs/harness-architecture.md` `docs/impl/{issue}-{이름}.md` 평탄화) |
| `docs/bugfix/` | bugfix 노트 |
| `docs/milestones/` | 일반 프로젝트 마일스톤 스냅샷 (jajang 등) |

**근거**: `harness/core.py` `_PLAN_PREFIXES` 와 정합 — worktree 보호 prefix 와 동일 (이미 [14.2] / [26.1] 에서 검증된 분류 기준 재사용 → 분류 기준이 두 곳에 흩어지지 않도록 본 impl 에서는 `core.py` 의 `_PLAN_PREFIXES` 를 import 해 단일 SSOT 로 참조).

### 3. classification 결과

`_classify_last_commit_files(file_list: list[str]) -> str` 반환값:

| 반환 | 조건 | autocheck 분기 |
|---|---|---|
| `"empty"` | `git log -1 --name-only HEAD` 결과 0줄 (e.g. `git commit --allow-empty`) | escalate + reset |
| `"test_only"` | 모든 파일이 test 패턴 매칭 | **PASS** |
| `"plan_only"` | 모든 파일이 plan prefix 매칭 | **PASS** |
| `"test_and_plan"` | 모든 파일이 test ∪ plan 매칭 (둘 다 섞여도 OK) | **PASS** |
| `"mixed"` | 위 3개 카테고리 외 파일이 1개라도 포함 | escalate + reset |

> **두 카테고리 외 파일이 1개라도 섞이면 mixed** — test 9개 + 잘못된 src 1개 같은 케이스도 stranded 위험이 있으므로 보수적으로 escalate. 의도된 src 변경이라면 engineer_scope diff 가 잡아냈어야 함 (no_changes 진입 자체가 비정상 신호).

### 4. 빈 커밋 처리

`empty` 분류 — `git commit --allow-empty` 같은 비정상 케이스. 즉시 escalate + `git reset --hard HEAD~1` (origin 분기는 가능하면 그쪽으로). 빈 커밋은 stranded 되더라도 무해하지만 attempt 카운트와 changelog 일관성을 위해 reset.

### 5. `origin/<branch>` 부재 처리 (rollback fallback chain)

첫 push 전에 fail 케이스가 발생하면 `origin/<feature_branch>` ref 가 존재하지 않음. fallback chain:

```
1차: git rev-parse --verify origin/<feature_branch>  → 성공 시 git reset --hard origin/<feature_branch>
2차 (origin ref 없음): git reset --hard HEAD~1
3차 (HEAD~1 도 없음 — 첫 커밋): rollback skip + 경고 로그 (worktree 가 첫 커밋 직후이므로 수동 정리 필요)
```

3차 케이스는 거의 발생 안 함 (worktree 는 main 으로부터 분기되어 항상 부모 커밋 존재). 단 안전장치로 `git rev-parse HEAD~1` 검증 후 진행.

## 로직 의사코드

`harness/helpers.py` 변경 부분.

```python
# ── 모듈 레벨 ───────────────────────────────────────────────
# G1: core 의 _PLAN_PREFIXES 는 본 PR 에서 모듈 레벨로 승격됨 — 정상 import 가능.
# G4: test 패턴은 path_resolver 의 SSOT regex 를 재사용 (별도 regex 신설 금지).
try:
    from .core import _PLAN_PREFIXES  # type: ignore[attr-defined]
    from .path_resolver import test_paths_extract_regex
except ImportError:
    from core import _PLAN_PREFIXES  # type: ignore[attr-defined]
    from path_resolver import test_paths_extract_regex

# 1회 컴파일 캐시 (path_resolver 가 cfg/v2 분기를 이미 처리함)
_TEST_RE = test_paths_extract_regex()


def _is_test_file(path: str) -> bool:
    return bool(_TEST_RE.search(path))


def _is_plan_file(path: str) -> bool:
    # _PLAN_PREFIXES 는 module-level 상수 (G1 PR 동시 변경) — fallback 불필요.
    return any(path.startswith(p) for p in _PLAN_PREFIXES)


def _classify_last_commit_files(files: list[str]) -> str:
    """직전 커밋 파일 목록을 5개 카테고리 중 하나로 분류."""
    if not files:
        return "empty"
    has_test = False
    has_plan = False
    for f in files:
        if _is_test_file(f):
            has_test = True
        elif _is_plan_file(f):
            has_plan = True
        else:
            return "mixed"
    if has_test and has_plan:
        return "test_and_plan"
    if has_test:
        return "test_only"
    return "plan_only"


def _hard_reset_worktree(
    feature_branch: Optional[str],
    cwd: Optional[str],
    run_logger: Optional[RunLogger],
) -> str:
    """fallback chain 으로 worktree HEAD 를 이전 커밋으로 되돌린다.

    반환값: 사용된 reset 타겟 ("origin/<br>" / "HEAD~1" / "skipped").
    """
    import subprocess
    _run = (lambda *a, **kw: subprocess.run(*a, cwd=cwd, **kw)) if cwd else subprocess.run

    target = "skipped"
    if feature_branch:
        r = _run(
            ["git", "rev-parse", "--verify", "--quiet",
             f"refs/remotes/origin/{feature_branch}"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            target = f"origin/{feature_branch}"
    if target == "skipped":
        # HEAD~1 fallback
        r = _run(
            ["git", "rev-parse", "--verify", "--quiet", "HEAD~1"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            target = "HEAD~1"

    if target != "skipped":
        _run(
            ["git", "reset", "--hard", target],
            capture_output=True, text=True, timeout=10,
        )
        hlog(f"ROLLBACK hard reset → {target}")
    else:
        hlog("ROLLBACK skipped — neither origin/<branch> nor HEAD~1 available")
    if run_logger:
        run_logger.log_event({
            "event": "rollback_hard_reset",
            "target": target,
            "branch": feature_branch or "",
            "t": int(time.time()),
        })
    return target


def rollback_attempt(
    attempt_num: int,
    run_logger: Optional[RunLogger] = None,
    *,
    hard_reset: bool = False,
    feature_branch: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    """JSONL rollback 이벤트 기록 + (옵션) 실제 git reset.

    기존 호출자(impl_loop.py 17개): 위치인자만 사용 — keep-on-branch 동작 유지.
    no_changes mixed/empty 분기에서만 hard_reset=True 로 호출.
    """
    method = "keep-on-branch"
    if hard_reset:
        target = _hard_reset_worktree(feature_branch, cwd, run_logger)
        method = f"hard-reset:{target}"

    if run_logger:
        run_logger.log_event({
            "event": "rollback",
            "attempt": attempt_num,
            "method": method,
            "t": int(time.time()),
        })
    hlog(f"ROLLBACK attempt={attempt_num} method={method}")
```

`run_automated_checks` 의 no_changes 분기 수정 (line 306-310 영역):

```python
# 기존
if not has_uncommitted and not has_committed:
    msg = "no_changes: engineer가 아무 파일도 수정하지 않음"
    out_file.write_text(msg, encoding="utf-8")
    print("AUTOMATED_CHECKS_FAIL: no_changes")
    return False, msg

# 수정 (의도)
if not has_uncommitted and not has_committed:
    # 직전 커밋 파일 검사 — test-only / plan-only 정상 케이스 허용
    r_log = _run(
        ["git", "log", "-1", "--name-only", "--format="],
        capture_output=True, text=True, timeout=5,
    )
    last_commit_files = [
        f.strip() for f in (r_log.stdout or "").splitlines() if f.strip()
    ] if r_log.returncode == 0 else []
    classification = _classify_last_commit_files(last_commit_files)

    if classification in ("test_only", "plan_only", "test_and_plan"):
        # PASS 처리 — push 진행. 후속 검사(2~7) 그대로 통과시킨다.
        hlog(
            f"no_changes 분기에서 {classification} commit 발견 — PASS 처리 "
            f"(파일 {len(last_commit_files)}개)"
        )
        # G3: fall-through to checks 2~7 (package.json/PROTECTED/Scope/lint/build/test).
        # checks 2~4 는 워킹트리 vs HEAD 비교라 commit 후 자동 통과 (의도된 동작 —
        # invariant 검증은 commit 직전 단계에서 이미 끝남).
        # checks 5~7 (lint/build/test) 만 실질적 추가 검증을 수행:
        #   - lint: 변경 파일 0개라 _changed_src=[] → config.lint_command 전체 실행
        #     (set 되어 있을 때).
        #   - build/test: config 명령이 set 되어 있으면 무조건 실행. test-only commit
        #     의 회귀 영향을 잡는 마지막 안전망.
        # 별도 플래그 set 불필요 — 분기를 그대로 빠져나가면 자연 fall-through.
    else:
        # mixed / empty — escalate + hard reset
        msg = (
            f"no_changes_or_invalid_scope: 직전 커밋 분류={classification}, "
            f"파일={last_commit_files[:5]}"
        )
        out_file.write_text(msg, encoding="utf-8")
        print(f"AUTOMATED_CHECKS_FAIL: no_changes ({classification})")
        # ★ rollback 은 **caller (impl_loop.py)** 가 fail_type=='no_changes' 분기에서
        #   기존처럼 호출. 단 이번 PR 에서 caller 도 hard_reset=True 로 업그레이드.
        return False, msg
```

> **caller(impl_loop.py) 수정**: `impl_loop.py:510` 과 `:1226` 의 `rollback_attempt(attempt, run_logger)` 두 곳을 `rollback_attempt(attempt, run_logger, hard_reset=True, feature_branch=feature_branch, cwd=work_cwd)` 로 변경. 다른 15개 호출처는 그대로 (autocheck_fail / pr-reviewer fail 등은 keep-on-branch 가 기존 의도).

## rollback_attempt 정책 결정

| 옵션 | 설명 | 채택 여부 |
|---|---|---|
| (a) `keep-on-branch` 유지 + 분기에서 인라인 reset | 호출자에서 `subprocess.run(["git","reset","--hard",...])` 직접 호출 | ❌ — fallback chain 로직이 두 caller 에 중복. 검증·테스트 면적 ↑ |
| (b) `rollback_attempt` 에 `hard_reset` 모드 추가 (keyword-only optional) | 시그니처 확장, 기존 17개 호출 호환 유지 | ✅ **채택** |
| (c) 신규 함수 `rollback_attempt_hard()` 추가 | 별도 함수로 의도 분리 | ❌ — 두 함수가 거의 동일 로직, 사일런트 drift 위험 |

**선택 근거**:
- (b) 가 fallback chain 을 한 곳(`_hard_reset_worktree`) 에 집중 → 회귀 테스트가 그 하나만 커버하면 됨.
- 기존 17개 호출처 손대지 않음 (PR diff 최소화).
- `method=` 문자열로 JSONL 분류 가능 (`keep-on-branch` vs `hard-reset:origin/...` vs `hard-reset:HEAD~1` vs `hard-reset:skipped`) — review session 분석 시 로그만 봐도 분기 식별.

## 회귀 테스트 (`tests/pytest/test_autocheck_no_changes.py`)

신규 파일. 컨벤션은 `tests/pytest/test_worktree.py` 와 동일 — 임시 git repo + 실제 subprocess (`subprocess.run(["git",...])`). mock 안 함.

### 테스트 클래스 구조

```python
"""test_autocheck_no_changes.py — Issue #34 회귀 테스트.

run_automated_checks 의 no_changes 분기에서 직전 커밋이 test-only 인 경우 PASS 처리 +
mixed/empty 인 경우 hard reset 으로 stranded 방지.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.helpers import (  # noqa: E402
    _classify_last_commit_files,
    rollback_attempt,
    run_automated_checks,
)
from harness.core import StateDir  # noqa: E402


def _init_repo(repo: Path) -> None:
    """임시 git repo + 첫 커밋 (main branch)."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "README.md").write_text("seed\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def _commit(repo: Path, files: dict[str, str], msg: str) -> str:
    """파일 dict 를 worktree 에 쓰고 커밋. 반환: HEAD sha."""
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", msg], check=True)
    r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def _make_state_dir(tmp_path: Path) -> StateDir:
    sd_path = tmp_path / "state"
    sd_path.mkdir()
    return StateDir(sd_path)


def _impl_file_with_scope(tmp_path: Path, allowed: list[str]) -> Path:
    f = tmp_path / "impl.md"
    body = "## 수정 파일\n" + "\n".join(f"- `{a}`" for a in allowed) + "\n"
    f.write_text(body)
    return f


# ── REQ-006~008: classification helper ─────────────────────────

class TestREQ006Classification:
    def test_classify_empty(self):
        assert _classify_last_commit_files([]) == "empty"

    def test_classify_test_only_jest(self):
        assert _classify_last_commit_files(
            ["src/components/__tests__/Button.test.tsx"]
        ) == "test_only"

    def test_classify_test_only_pytest(self):
        assert _classify_last_commit_files(
            ["apps/api/tests/test_recordings.py"]
        ) == "test_only"

    def test_classify_plan_only(self):
        assert _classify_last_commit_files(
            ["docs/impl/34-foo.md", "docs/bugfix/bar.md"]
        ) == "plan_only"

    def test_classify_test_and_plan(self):
        assert _classify_last_commit_files(
            ["apps/api/tests/test_x.py", "docs/impl/34-foo.md"]
        ) == "test_and_plan"

    def test_classify_mixed(self):
        assert _classify_last_commit_files(
            ["apps/api/tests/test_x.py", "apps/api/app/main.py"]
        ) == "mixed"

    def test_classify_underscore_test_py(self):
        assert _classify_last_commit_files(
            ["apps/api/recordings_test.py"]
        ) == "test_only"


# ── REQ-001/002: test-only commit → PASS ────────────────────────

class TestREQ002TestOnlyCommitPass:
    def test_test_only_commit_returns_pass(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        # feature branch + test-only commit
        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/x"], check=True
        )
        _commit(
            repo,
            {"apps/api/tests/test_x.py": "def test_a(): pass\n"},
            "test(api): regression",
        )

        impl = _impl_file_with_scope(tmp_path, ["apps/api/tests/test_x.py"])
        sd = _make_state_dir(tmp_path)
        cfg = SimpleNamespace(lint_command="", build_command="", test_command="")

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert ok, f"test-only commit 은 PASS 여야 함. err={err}"

    def test_plan_only_commit_returns_pass(self, tmp_path, monkeypatch):
        # 동일 패턴 — docs/impl/ 만 커밋
        ...

    def test_test_and_plan_commit_returns_pass(self, tmp_path, monkeypatch):
        # 동일 패턴 — tests/ + docs/impl/ 함께 커밋
        ...


# ── REQ-001: git log -1 --name-only HEAD 가 호출되는지 ──────────

class TestREQ001LastCommitInspection:
    def test_inspects_last_commit_on_no_changes(self, tmp_path, monkeypatch):
        # test-only commit 시나리오에서 PASS 결과로 내부 호출 검증
        # (호출 자체를 mock 으로 검증하지 않음 — 결과 PASS 가 곧 호출 증거)
        ...


# ── REQ-003: mixed/empty → hard reset ───────────────────────────

class TestREQ003RollbackOnInvalidScope:
    def test_mixed_commit_resets_hard(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)
        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/y"], check=True
        )
        before_sha = _commit(repo, {"foo.txt": "1\n"}, "first")
        # mixed: docs 외 파일만 — 본 fix 의 mixed 케이스
        bad_sha = _commit(repo, {"random.txt": "2\n"}, "bad")

        # caller 모방: rollback_attempt(hard_reset=True, ...) 호출
        rollback_attempt(
            1, run_logger=None,
            hard_reset=True, feature_branch="feat/y", cwd=str(repo),
        )

        r = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        # origin 이 없으므로 HEAD~1 fallback → before_sha 로 reset
        assert r.stdout.strip() == before_sha, "HEAD~1 fallback 로 reset 되어야 함"

    def test_empty_commit_resets_hard(self, tmp_path, monkeypatch):
        # git commit --allow-empty 후 동일 검증
        ...

    def test_no_origin_falls_back_to_head_minus_one(self, tmp_path, monkeypatch):
        # origin remote 자체 없을 때 HEAD~1 폴백 — test_mixed_commit_resets_hard 와
        # 동일 시나리오. 명시적 케이스로 한번 더 작성.
        ...


# ── REQ-004 회귀 보호: 기존 keep-on-branch 호출 호환 ────────────

class TestRollbackBackwardCompat:
    def test_default_call_no_reset(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)
        before_sha = _commit(repo, {"a.txt": "1\n"}, "x")

        # 기존 호출 패턴
        rollback_attempt(1, run_logger=None)

        r = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        assert r.stdout.strip() == before_sha, (
            "hard_reset 미지정 시 HEAD 변경되지 않아야 함"
        )


# ── G5: hard_reset target 별 JSONL 분류 검증 ──────────────────

class TestRollbackJSONLClassification:
    """rollback_attempt(hard_reset=True) 의 JSONL 이벤트가 method/target 을 정확히 기록.

    review session 분석 시 로그만 봐도 분기 식별 가능해야 함.
    """
    def test_origin_target_logged_when_origin_exists(self, tmp_path, monkeypatch):
        # 1. 임시 bare remote + clone + push 로 origin/<br> 생성
        # 2. mixed commit 후 rollback_attempt(hard_reset=True, feature_branch=br)
        # 3. JSONL events 에 event=='rollback_hard_reset', target=='origin/<br>' 검증
        # 4. event=='rollback', method=='hard-reset:origin/<br>' 검증
        ...

    def test_head_minus_one_target_logged_when_no_origin(self, tmp_path, monkeypatch):
        # origin remote 없는 케이스 — target=='HEAD~1' 로 분류 기록 검증
        ...

    def test_skipped_target_logged_when_first_commit(self, tmp_path, monkeypatch):
        # 첫 커밋 직후 (HEAD~1 도 없음) — target=='skipped' 분류 + 경고 로그
        ...


# ── G5: passthrough 후 build_command fail 케이스 ──────────────

class TestREQ002BuildFailAfterPassthrough:
    """test-only commit PASS → build_command 실행 → build 실패 → escalate 정상.

    G3 의 passthrough 동작이 의도대로 작동함을 보장. test-only commit 이 build 회귀를
    유발하는 케이스(예: production code 가 의존하는 internal API 를 test 가 import 했지만
    그 API 가 test 환경에서 빌드 실패 트리거).
    """
    def test_test_only_commit_then_build_fail_returns_fail(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)
        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "-b", "feat/x"], check=True
        )
        _commit(
            repo,
            {"apps/api/tests/test_x.py": "def test_a(): pass\n"},
            "test(api): regression",
        )

        impl = _impl_file_with_scope(tmp_path, ["apps/api/tests/test_x.py"])
        sd = _make_state_dir(tmp_path)
        # build_command 가 항상 fail 하도록 설정
        cfg = SimpleNamespace(
            lint_command="",
            build_command="exit 1",  # always fail
            test_command="",
        )

        ok, err = run_automated_checks(
            str(impl), cfg, sd, "test", cwd=str(repo), run_tests=False,
        )
        assert not ok, "build 실패 시 PASS 가 아니어야 함"
        assert "build_fail" in err, f"err 메시지에 build_fail 포함 기대. 실제={err}"
```

### 픽스처 전략 — 결정 근거

- **실제 git 디렉토리 사용** (`subprocess.run(["git", ...])` 직접 호출). subprocess mock 안 함.
- 근거: `helpers.py` 의 git 호출은 진짜 git 의 stdout 포맷에 의존 (`git log -1 --name-only --format=` 의 정확한 출력) — mock 으로 fake 하면 포맷이 어긋날 때 silent pass. 실제 git 으로 하면 production 과 동일 시나리오. `tests/pytest/test_worktree.py` 와 동일 컨벤션.
- 임시 worktree 에서 `git config user.email/user.name` set 안 하면 commit 실패 — `_init_repo` 에서 set.

## 결정 근거 (Why this approach)

### 결정 1: classifier 는 별도 helper, regex 는 모듈 레벨 상수

| 대안 | 평가 |
|---|---|
| (a) inline if/else 체인 | 테스트 면적 작아짐, regex 재사용 안 됨. ❌ — REQ-006~008 단위 테스트가 어려움 |
| (b) `_classify_last_commit_files()` 별도 함수 + 모듈 상수 | 단위 테스트 직접 호출 가능, regex 재컴파일 회피 | ✅ |

### 결정 2: SSOT 통일 — `core._PLAN_PREFIXES` import (G1 옵션 (α) 채택)

`docs/impl/`, `docs/bugfix/`, `docs/milestones/` 가 두 곳에 하드코딩되면 drift 발생 (예: 신규 `docs/specs/` prefix 추가 시 한쪽만 업데이트). `core.py` 가 worktree 보호 prefix 의 실 SSOT 이므로 helpers 에서 import.

**문제 (G1 갭)**: 현재 `core.py:1375` 의 `_PLAN_PREFIXES` 는 `WorktreeManager` *클래스 속성* 이라 `from .core import _PLAN_PREFIXES` 는 항상 ImportError. 즉 의사코드의 import 분기는 사실상 fallback 100% 사용 → SSOT 효과 0.

**채택안 (α) — 클래스 속성 제거형**: `core.py` 에서 클래스 안의 `_PLAN_PREFIXES` 정의를 *제거* 하고 모듈 레벨에 신설. `_copy_untracked_plan_files` 의 `self._PLAN_PREFIXES` 참조 1곳을 `_PLAN_PREFIXES` 로 교체. alias 라인(`_PLAN_PREFIXES = _PLAN_PREFIXES`) 두지 않음 — 외부에서 `WorktreeManager._PLAN_PREFIXES` 를 참조하는 코드 0개 (grep 확인) 이므로 속성 호환 유지 불필요.

**대안 평가**:

| 옵션 | 평가 |
|---|---|
| (α) module-level 승격 + 클래스 속성 제거 (실 사용처 0개) | ✅ **채택**. `self._PLAN_PREFIXES` → `_PLAN_PREFIXES` 1곳 교체 + class 본문 정의 1줄 삭제 + module-level 1줄 신설. 진짜 SSOT. 자식 클래스 override 가능성 / 외부 속성 접근 0개로 안전 |
| (β) module-level 승격 + 클래스 alias 유지 (`WorktreeManager._PLAN_PREFIXES = _PLAN_PREFIXES`) | ❌ alias 1줄이 dead code (외부 사용처 0). 같은 값을 두 이름에 묶어두면 향후 변경 시 한쪽만 갱신될 위험 잔존 |
| (γ) helpers 에서 `WorktreeManager._PLAN_PREFIXES` 참조 | ❌ class import 가 무거움 + WorktreeManager 의 다른 의존성(circular import 위험) 끌어옴 |
| (δ) helpers 에 inline + `# MUST mirror core.py:1375` 주석 | ❌ drift 위험 본질 미해결 (validator/architect 가 다음 변경에서 한쪽만 갱신할 수 있음) |

### 결정 3: `rollback_attempt` 시그니처 확장 vs 신규 함수

위 §rollback_attempt 정책 결정 표 참조. (b) 채택 — 17개 호출처 손대지 않음.

### 결정 4: helpers.py 안에서 passthrough — 실제 동작 (G3 정정)

PASS 처리 시 분기를 빠져나가지 않고 후속 검사 2~7 (package.json / PROTECTED / scope guard / lint / build / test) 를 그대로 진행. 단 **현재 코드 기준 각 검사가 test-only commit 케이스에서 실제로 어떻게 동작하는지** 정확히 명시:

| # | 검사 | 사용 git diff 인자 | test-only commit 시 실제 동작 |
|---|---|---|---|
| 2 | `package.json` 새 deps | `git show HEAD:package.json` + `git diff HEAD -- package.json` | 워킹트리 vs HEAD 비교 → 변경 0 → **자동 통과** (실제 검증 0) |
| 3 | PROTECTED 파일 | `git diff HEAD -- {pf}` | 워킹트리 vs HEAD 비교 → 변경 0 → **자동 통과** (실제 검증 0) |
| 4 | ImplScopeGuard | `git diff --name-only HEAD` | 워킹트리 vs HEAD 비교 → `changed = []` → out_of_scope 비어 **자동 통과** (실제 검증 0) |
| 5 | lint | `git diff --name-only --diff-filter=ACMR HEAD` + `config.lint_command` | 변경 0 → `_changed_src = []` → `_lint_cmd = config.lint_command` (전체 lint 실행). config.lint_command 가 set 되어 있으면 **전체 lint 실행** |
| 6 | build | `config.build_command` shell 실행 | 변경 무관 — config.build_command 가 set 되어 있으면 **실행** |
| 7 | test (run_tests=True 한정) | `config.test_command` shell 실행 | 변경 무관 — **실행** |

**요약**: ImplScopeGuard / PROTECTED / package.json 검사는 test-only commit 후 워킹트리 = HEAD 라서 자동 통과 (의도된 invariant 검증은 commit 직전 시점에 끝났음). lint / build / test 는 config 명령이 set 되어 있으면 실제 실행 — test-only commit 의 회귀 영향을 잡는 마지막 안전망.

> **이전 본 §의 오기**: "test-only commit 도 ImplScopeGuard·lint invariant 적용" 이라고 적었으나 ImplScopeGuard 는 *워킹트리 변경* 을 본다. test-only commit 직후 워킹트리는 HEAD 와 같아 무조건 통과. 실제 invariant 검증은 commit 단계 전에 engineer 단계에서 끝나거나 build/test 가 잡는다.

**`has_committed = True` 의 의도**: 의사코드 line 287 의 `has_committed = True` 는 사실상 **dead assignment** (이후 코드 흐름에서 참조 안 됨 — line 306 의 if 문은 위에서 통과했고 그 아래 검사 2~7 은 has_committed 를 보지 않음). 본 PR 은 이 라인을 삭제하거나 의도 명시 주석으로 대체:

```python
# (제거 또는 다음으로 대체)
# fall-through to checks 2~7 (package.json/PROTECTED/Scope/lint/build/test).
# checks 2~4 는 워킹트리 vs HEAD 비교라 commit 후 자동 통과 — 의도된 동작.
# checks 5~7 만 실질적 추가 검증을 수행 (config 명령이 set 되어 있을 때).
```

### 결정 5: rollback fallback chain — origin → HEAD~1 → skip

`origin/<branch>` 채택 우선 이유: feature branch 의 마지막 push 상태가 정확히 stranded 직전 상태. HEAD~1 은 *직전 attempt 의 commit* 일 수도 있어 부정확할 가능성 있지만, origin 이 없을 때의 차선책. `git reset --hard HEAD~1` 도 부적절한 시나리오(첫 커밋)만 skip.

### 결정 6: caller 수정 범위 (impl_loop.py 두 곳만 — 16개 전수 분류)

| 호출처 | 분기 | 본 PR 수정? |
|---|---|---|
| `impl_loop.py:510` | run_simple no_changes | ✅ `hard_reset=True, feature_branch=feature_branch, cwd=work_cwd` 추가 |
| `impl_loop.py:1226` | run_std/deep no_changes | ✅ `hard_reset=True, feature_branch=feature_branch, cwd=work_cwd` 추가 |
| `impl_loop.py:531` | autocheck_fail (run_simple, no_changes 외) | ❌ keep-on-branch 유지 |
| `impl_loop.py:1243` | autocheck_fail (run_std/deep, no_changes 외) | ❌ keep-on-branch 유지 |
| `impl_loop.py:398` | engineer no-output (run_simple) | ❌ |
| `impl_loop.py:1121` | engineer no-output (run_std/deep) | ❌ |
| `impl_loop.py:647` | pr-reviewer no-output (run_simple) | ❌ |
| `impl_loop.py:1440` | pr-reviewer no-output (run_std/deep) | ❌ |
| `impl_loop.py:663` | pr-reviewer CHANGES_REQUESTED (run_simple) | ❌ |
| `impl_loop.py:1452` | pr-reviewer CHANGES_REQUESTED (run_std/deep) | ❌ |
| `impl_loop.py:1297` | GREEN test_fail | ❌ |
| `impl_loop.py:1339` | validator no-output | ❌ |
| `impl_loop.py:1357` | SPEC_MISSING 복구 후 retry | ❌ |
| `impl_loop.py:1367` | validator FAIL | ❌ |
| `impl_loop.py:1575` | security-reviewer no-output (deep) | ❌ |
| `impl_loop.py:1589` | security VULNERABILITIES_FOUND (deep) | ❌ |

14개 호출처는 그대로 — hard_reset 은 stranded 위험이 있는 no_changes 분기 한정. 그 외 fail 분기는 직전 commit 의 내용이 정상이고 fix-up commit 으로 보정하는 패턴이라 reset 하면 누적 이력 + 직전 lint/build 성공 상태가 사라짐.

## 주의사항

### bugfix loop 영향 (G2 grep 결과 — 가설 철회)

QA 분석에서 "bugfix loop 도 helpers 공유" 가설이 있었으나 **본 PR 시점 (2026-04-28) `harness/` 트리 grep 결과 `run_automated_checks` / `rollback_attempt` 호출은 `harness/impl_loop.py` 단독**:

```
$ grep -rn "run_automated_checks\|rollback_attempt" harness/
harness/impl_loop.py:32: from .helpers import (... rollback_attempt, run_automated_checks ...)
harness/impl_loop.py:53: from helpers import (... rollback_attempt, run_automated_checks ...)
harness/impl_loop.py:398, 510, 531, 647, 663, 1121, 1226, 1243, 1297, 1339, 1357, 1367, 1440, 1452, 1575, 1589 — rollback_attempt(...)
harness/impl_loop.py:486, 1209 — run_automated_checks(...)
harness/helpers.py:227, 230 — 정의 자체
harness/helpers.py:260, 263 — 정의 자체
```

bugfix 별도 모듈 (`bugfix_loop.py` 등) 부재. 따라서 helpers 단일 수정 + impl_loop.py 두 분기(`:510`, `:1226`) caller keyword 인자 추가 만으로 본 fix 가 모든 호출 경로를 커버한다. 향후 bugfix loop 가 분리되면 그 시점 별도 검토.

### `impl_loop.py:491-518`, `1212-1233` 의 no_changes 분기

helpers.run_automated_checks 가 `("test_only" 등)` 케이스에서 `(True, "")` 반환 → caller 의 `if not check_ok:` 가 False → no_changes 분기 자체로 들어가지 않고 정상 commit/push 진행. **automatic 해소.** 추가 caller 수정 불필요 (mixed/empty 케이스에서 `hard_reset=True` 인자 추가 외).

### run_automated_checks 후속 검사 순서 영향 (G3 정정)

passthrough 시 검사 2(package.json) → 3(PROTECTED) → 4(ImplScopeGuard) → 5(lint) → 6(build) → 7(test) 순서로 진행. **단 검사 2~4 는 워킹트리 vs HEAD 비교라 test-only commit 직후 워킹트리 = HEAD 인 케이스에서 자동 통과**(실제 invariant 검증 0). 의도된 동작 — 그 검사들은 commit *직전* 시점의 보호 장치이고 commit 이 끝났으면 이미 지켜진 셈.

검사 5(lint) 의 `git diff --name-only --diff-filter=ACMR HEAD` 도 변경 파일 0개를 반환 → `_changed_src = []`. **단 plan 의 이전 표현 ("결과 0개 → lint 명령 자체 스킵") 은 오기다** — `helpers.py:413-414` 코드는 `_changed_src` 가 비어 있어도 `_lint_cmd = config.lint_command` 로 *전체 lint 명령을 그대로 실행*한다. config.lint_command 가 set 되어 있으면 본 fix 의 test-only commit 케이스에서 전체 lint 가 돌아간다 — 이는 의도된 동작 (회귀 안전망).

검사 6(build) 도 명령 실행. 검사 7(test) 은 `run_tests=True` 일 때만 실행되며, simple depth 만 True. std/deep 은 TDD 단계에서 별도 실행이므로 중복 회피 (본 fix 도 동일).

### CLAUDE.md / 화이트리스트 영향

본 fix 는 helpers.py 단일 파일 + tests + changelog. CLAUDE.md / orchestration-rules.md 변경 없음.

## 비목표

- bugfix loop 의 별도 분기 신설 — 본 fix 는 helpers 공유 경로만. bugfix loop 에서 추가 분기 필요하면 별도 issue.
- "PR auto-rebase on stranded commit detection" — 본 fix 는 사후 stranded 방지(hard reset). 사전 자동 PR 갱신은 out of scope.
- worktree 의 추가 reflog/snapshot 백업 — `git reset --hard` 가 reflog 에 기록되므로 복구 가능. 별도 백업 불필요.
- ~~test pattern 정규식의 외부 설정화~~ → **G4 결정에 따라 본 PR 에서 `path_resolver.test_paths_extract_regex()` 위임으로 통합 완료** (별도 impl 불필요). cfg.test_paths 명시 케이스 / V2 monorepo 자동 합성 케이스가 자동으로 적용된다.

## 비변경 (의도)

- `harness/impl_loop.py` 의 15개 다른 `rollback_attempt` 호출처 — keep-on-branch 유지.
- `harness/core.py` `_PLAN_PREFIXES` *값* — `("docs/bugfix/", "docs/impl/", "docs/milestones/")` 그대로. **클래스 속성 제거 + 모듈 레벨 신설** (위치 이동 표현보다 정확 — 옵션 (α), G1).
- `harness/path_resolver.py` `engineer_scope_pathspecs()` / `engineer_scope_extract_regex()` — 변경 없음. (`_V1_TEST_PATHS_REGEX` 만 G4 보강 — pytest 패턴 추가)
- 기타 helpers.py 함수 (load_constraints, append_failure, append_success, check_agent_output, budget_check, generate_pr_body, save_impl_meta, setup_hlog, log_decision, log_phase, _extract_reflection, _write_reflection, extract_acceptance_criteria, extract_polish_items) — 손대지 않음.

## 검증 명령

```bash
python3 -m py_compile harness/helpers.py
python3 -m pytest tests/pytest/test_autocheck_no_changes.py -v
python3 -m pytest tests/pytest/test_worktree.py tests/pytest/test_session_state_fallback.py -v  # 회귀
```

## 위임 흐름

```
이 light-plan (architect 산출)
  → engineer 호출 (메인 단독 src 변경 금지 룰 준수)
  → validator
  → pr-reviewer
  → squash merge
  → orchestration/changelog.md 에 HARNESS-CHG-20260428-34 [34.1] 항목 추가
```

## Linked

- 선행: `HARNESS-CHG-20260428-14 [14.5]` (PR #21) — no_changes 즉시 escalate 도입. 본 fix 가 그 결과로 발생한 두 hole(test-only 오인 + stranded) 메움.
- 컨텍스트: jajang `run_20260428_163700` 의 #127 회귀테스트 attempt 재현 케이스 (commit 611fbb8 stranded).
- SSOT 참조: `harness/core.py` `_PLAN_PREFIXES` (worktree 보호 prefix 와 분류 기준 통일).
