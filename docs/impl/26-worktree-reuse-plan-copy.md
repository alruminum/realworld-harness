---
issue: 26
type: bugfix
depth: simple
identifier_candidate: HARNESS-CHG-20260428-26 [26.1]
related: HARNESS-CHG-20260428-14.2 (PR #18, commit 4eb20b3)
---

# Impl 계획 — Issue #26 worktree 재사용 시 untracked plan 파일 미복사 ([14.2] hole)

> Status: **LIGHT_PLAN_READY** (depth=simple, 국소 분기 추가 + 가드)
> Branch (제안): `harness/worktree-reuse-plan-copy`
> PR title (제안): `HARNESS-CHG-20260428-26 [26.1] worktree 재사용 시 untracked plan 자동 복사 ([14.2] hole)`

## 변경 대상

- 파일: `harness/core.py`
- 함수: `WorktreeManager.create_or_reuse()` (line 1357-1369), `WorktreeManager._copy_untracked_plan_files()` (line 1377-1399)
- 요약: reuse 분기 (`if wt_path.exists(): return wt_path`) 가 `_copy_untracked_plan_files()` 를 건너뛰는 hole 을 메운다. 동시에 재사용 worktree 의 기존 파일 보존 가드를 `_copy_untracked_plan_files` 안에 추가해 [14.2] fresh path 회귀 없이 동작.

## 배경 (요약)

- [14.2] (commit 4eb20b3, PR #18) 가 fresh worktree 생성 path 에만 plan 복사를 추가.
- jajang #127 (run_20260428_163700) 에서 동일 issue 의 worktree + branch + OPEN PR 재사용 흐름이 발현 → reuse 분기가 즉시 return → engineer SPEC_GAP_FOUND → architect 우회 (\$1.82/회 낭비).
- 본 fix 는 reuse 분기에도 동일 호출을 넣고, 부수효과 가드 한 줄을 더해 "재사용 worktree 내 modified plan" 보호.

## 수정 내용

### 1. `create_or_reuse` — reuse 분기에 복사 호출 추가

현재 (line 1357-1369):
```python
def create_or_reuse(self, branch_name: str, issue_num: str) -> Path:
    wt_path = self.worktree_path(issue_num)
    if wt_path.exists():
        return wt_path                            # ← 복사 스킵 (hole)
    r = _git("show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}")
    if r.returncode == 0:
        _git("worktree", "add", str(wt_path), branch_name, check=True)
    else:
        default = _default_branch()
        _git("worktree", "add", "-b", branch_name, str(wt_path), default, check=True)
    self._copy_untracked_plan_files(wt_path)
    return wt_path
```

수정 (의도):
```python
def create_or_reuse(self, branch_name: str, issue_num: str) -> Path:
    wt_path = self.worktree_path(issue_num)
    reused = wt_path.exists()
    if not reused:
        r = _git("show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}")
        if r.returncode == 0:
            _git("worktree", "add", str(wt_path), branch_name, check=True)
        else:
            default = _default_branch()
            _git("worktree", "add", "-b", branch_name, str(wt_path), default, check=True)
    self._copy_untracked_plan_files(wt_path, reused=reused)
    return wt_path
```

분기 단순화: fresh / reuse 둘 다 마지막에 동일한 `_copy_untracked_plan_files` 호출. `reused` 플래그로 안에서 가드 + 로그 분기.

### 2. `_copy_untracked_plan_files` — `reused` 가드 추가

현재 (line 1377-1399, 발췌):
```python
def _copy_untracked_plan_files(self, wt_path: Path) -> None:
    ...
    for line in r.stdout.splitlines():
        ...
        dst = wt_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)             # ← reuse 시 덮어쓰기 위험
            copied += 1
        ...
    if copied:
        print(f"[HARNESS] worktree 진입: untracked plan 파일 {copied}개 복사 ({wt_path.name})")
```

수정 (의도):
```python
def _copy_untracked_plan_files(self, wt_path: Path, reused: bool = False) -> None:
    ...
    copied = 0
    skipped = 0
    for line in r.stdout.splitlines():
        ...
        dst = wt_path / rel
        # reuse 케이스: 같은 경로 파일이 worktree 에 이미 있으면 보존 (덮어쓰기 방지).
        # fresh 케이스: dst 가 존재할 일이 없음 — 가드는 no-op.
        if reused and dst.exists():
            skipped += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
            copied += 1
        except OSError:
            pass
    if copied or skipped:
        mode = "재사용" if reused else "진입"
        msg = f"[HARNESS] worktree {mode}: untracked plan 파일 {copied}개 복사 ({wt_path.name})"
        if skipped:
            msg += f", 기존 {skipped}개 보존"
        print(msg)
```

### 가드 정책 (의도적 선택)

- **덮어쓰기 방지 = `dst.exists()` 가드** (mtime 비교 X). 이슈 본문이 두 옵션을 제시했으나 `dst.exists()` 채택 이유:
  - mtime 비교는 worktree 진입 직전 main 에서 plan 을 막 저장한 케이스를 잘못 덮어쓸 수 있음 (mtime 더 큼 ≠ "안전한 업데이트").
  - 본 fix 의 목표는 "reuse 분기 hole 메우기"이지 "main↔worktree plan 양방향 동기화" 가 아님 — 후자는 비목표 (이슈 본문 명시).
  - 단순한 정책 = 회귀 위험 ↓.
- **비목표 (이번 fix 에서 다루지 않음)**: 같은 issue 의 plan 이 main 에서 변경되어 worktree 의 stale 본을 갱신하고 싶은 시나리오. 별도 정책 논의 필요.

## 수정 파일

| 파일 | 변경 | 비고 |
|---|---|---|
| `harness/core.py` | `create_or_reuse` 분기 정리 + `_copy_untracked_plan_files` 시그니처에 `reused` 파라미터 추가 | line 1357-1399 영역 |
| `tests/pytest/test_worktree.py` | **신규** — reuse 시나리오 회귀 테스트 (REQ-001 / REQ-002) | conftest.py 의 `tmp_path` 사용 |

> 인터페이스 변경: `_copy_untracked_plan_files(wt_path, reused=False)` — 외부 호출 없음 (private), default 값으로 fresh path 호환 유지.

## 회귀 테스트 (`tests/pytest/test_worktree.py`)

신규 파일. pytest 컨벤션 (`tests/pytest/conftest.py` 의 `tmp_path` 활용 + `subprocess` 로 실 git 명령). git mock 대신 임시 git repo 직접 생성 — `_git` 가 `subprocess.run` 호출이고, 기존 [14.2] 검증도 "임시 git repo + 실제 worktree add" 방식으로 했음.

```python
# tests/pytest/test_worktree.py
"""test_worktree.py — WorktreeManager 회귀 테스트.

Issue #26: reuse 분기에서 untracked plan 파일이 복사되지 않던 hole.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.core import WorktreeManager  # noqa: E402


def _init_repo(repo: Path) -> None:
    """임시 git repo 초기화 + 더미 commit."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "README.md").write_text("seed\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def _write_untracked_plan(repo: Path, rel: str, content: str) -> Path:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


class TestREQ001ReusePlanCopy:
    """REQ-001: reuse worktree + main 의 untracked plan → 복사된다."""

    def test_reuse_copies_untracked_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)  # _git() 는 cwd 기반

        wm = WorktreeManager(repo, prefix="test")
        # 1차: fresh 생성
        wt1 = wm.create_or_reuse("test/issue-42", "42")
        assert wt1.exists()

        # main 에 untracked plan 추가 (commit 안 함)
        _write_untracked_plan(repo, "docs/impl/26-foo.md", "PLAN BODY\n")

        # 2차: 같은 이슈 재호출 → reuse 분기
        wt2 = wm.create_or_reuse("test/issue-42", "42")
        assert wt2 == wt1

        copied = wt2 / "docs/impl/26-foo.md"
        assert copied.exists(), "reuse 분기에서 untracked plan 이 복사되어야 함"
        assert copied.read_text() == "PLAN BODY\n"


class TestREQ002ReusePreserveExisting:
    """REQ-002: reuse worktree 에 이미 존재하는 동일 경로 파일은 보존."""

    def test_reuse_does_not_overwrite_existing_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        wm = WorktreeManager(repo, prefix="test")
        wt = wm.create_or_reuse("test/issue-42", "42")

        # main 과 worktree 양쪽에 같은 경로 파일을 다른 내용으로 작성
        _write_untracked_plan(repo, "docs/impl/26-foo.md", "MAIN VERSION\n")
        wt_plan = wt / "docs/impl/26-foo.md"
        wt_plan.parent.mkdir(parents=True, exist_ok=True)
        wt_plan.write_text("WORKTREE LOCAL EDIT\n")

        # reuse 호출
        wm.create_or_reuse("test/issue-42", "42")

        # worktree 본 보존되어야 함 (덮어쓰기 금지)
        assert wt_plan.read_text() == "WORKTREE LOCAL EDIT\n"


class TestREQ003FreshPathRegression:
    """REQ-003: [14.2] fresh 생성 path 동작 회귀 없음 — 신규 worktree 에 untracked plan 그대로 복사."""

    def test_fresh_create_still_copies_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        _write_untracked_plan(repo, "docs/bugfix/#42-bug.md", "BUG NOTE\n")

        wm = WorktreeManager(repo, prefix="test")
        wt = wm.create_or_reuse("test/issue-42", "42")

        assert (wt / "docs/bugfix/#42-bug.md").read_text() == "BUG NOTE\n"
```

> 가설: pytest 가 `harness.core` 를 import 할 수 있어야 한다 — `tests/pytest/conftest.py:23` 가 ROOT 를 sys.path 에 추가하므로 OK. 별도 fixture 추가 불필요.

## 수용 기준

| 요구사항 ID | 내용 | 검증 방법 | 통과 조건 |
|---|---|---|---|
| REQ-001 | worktree 재사용 케이스에서 main 의 untracked plan 이 worktree 로 복사 | (TEST) `tests/pytest/test_worktree.py::TestREQ001ReusePlanCopy::test_reuse_copies_untracked_plan` | 복사된 파일 존재 + 내용 일치 |
| REQ-002 | 재사용 worktree 에 동일 경로 파일이 이미 있으면 보존 (덮어쓰기 금지) | (TEST) `TestREQ002ReusePreserveExisting::test_reuse_does_not_overwrite_existing_plan` | worktree 측 내용 그대로 |
| REQ-003 | [14.2] fresh 생성 path 회귀 없음 | (TEST) `TestREQ003FreshPathRegression::test_fresh_create_still_copies_plan` | 신규 worktree 에 plan 정상 복사 |
| REQ-004 | 로그 출력에 "재사용" 케이스가 식별됨 | (REVIEW) stdout `[HARNESS] worktree 재사용: untracked plan 파일 N개 복사 ...` 또는 `..., 기존 M개 보존` 포함 | engineer 가 print 메시지 분기 확인 |

## 검증 명령

```bash
python3 -m py_compile harness/core.py
python3 -m pytest tests/pytest/test_worktree.py -v
```

## 비변경 (의도)

- `WorktreeManager.remove`, `worktree_path`, `list_active`, `__init__` — 손대지 않음.
- `_PLAN_PREFIXES` 패턴 (`docs/bugfix/`, `docs/impl/`, `docs/milestones/`) — 그대로.
- main repo 의 untracked plan — 그대로 보존 (worktree 로 cp 만, mv 아님).
- src/ 경계 — 변함없음. 본 fix 도 hooks/agents 의 경계 검증을 우회하지 않음.

## 비목표

- main 에서 plan 이 modify 됐는데 reuse worktree 의 stale 본을 업데이트하는 시나리오 — 별도 정책 (이슈 본문 §3 마지막 줄과 동일한 입장).
- main↔worktree 양방향 동기화 — out of scope.
- 동일 issue 를 다른 plan 으로 재진입 — 보수적으로 "이미 있으면 보존". 의도적 갱신은 사용자가 수동 정리.

## 위임 흐름

```
이 light-plan (architect 산출) 
  → engineer 호출 (메인 단독 src 변경 금지 룰 준수)
  → validator
  → pr-reviewer
  → squash merge
  → orchestration/changelog.md 에 HARNESS-CHG-20260428-26 [26.1] 항목 추가
```

## Linked

- 선행: `HARNESS-CHG-20260428-14.2` (PR #18, commit 4eb20b3) — fresh path 의 plan 복사. 본 fix 가 reuse 분기로 동일 정책 확장.
- 컨텍스트: jajang `run_20260428_163700` 의 #127 mock_s3 attempt 재현 케이스.
