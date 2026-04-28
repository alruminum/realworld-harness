#!/usr/bin/env python3
"""
check_test_sync.py — Test Sync 자동 게이트

harness/ 또는 hooks/ 변경 시 tests/** 동반 여부를 검사한다.
Tests-Exception 스코핑은 현재 diff 의 추가 라인만 유효 (과거 누적 엔트리 무효).

사용법:
  로컬:   python3 scripts/check_test_sync.py
  CI:     python3 scripts/check_test_sync.py <base> <head>

종료 코드:
  0  = PASS
  1  = FAIL (harness/hooks 변경 + tests 0 + Tests-Exception 없음)
  2  = ERROR (git 호출 실패 등)

Spec: orchestration/policies.md §8
Python 3.9+ stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# orchestration/policies.md §8 정의의 코드 표현
TRIGGER_PATTERNS = [
    re.compile(r"^harness/"),
    re.compile(r"^hooks/"),
]

TEST_PATH_PATTERNS = [
    re.compile(r"^tests/"),
]

EXCEPTION_PATTERN = re.compile(r"Tests-Exception:\s*(.+)")
MIN_REASON_LEN = 10


def get_changed_files(base: str = "", head: str = "", repo_root: Path | None = None) -> list[str]:
    """git diff 로 변경 파일 목록 추출.

    인자 없으면: staged 변경 (pre-commit hook 용)
    인자 있으면: git diff --name-only base head (CI 용)
    """
    cwd = repo_root or Path.cwd()
    if base and head:
        cmd = ["git", "diff", "--name-only", base, head]
    else:
        cmd = ["git", "diff", "--name-only", "--cached"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"[check_test_sync] git diff 실패: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_diff_added_lines(base: str = "", head: str = "", repo_root: Path | None = None) -> str:
    """git diff 의 추가 라인(+로 시작, +++ 헤더 제외) 추출."""
    cwd = repo_root or Path.cwd()
    if base and head:
        cmd = ["git", "diff", base, head]
    else:
        cmd = ["git", "diff", "--cached"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        return ""

    added = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    return "\n".join(added)


def get_commit_message_subject_and_body(repo_root: Path | None = None) -> str:
    """현재 staged commit msg 가 있으면 추출 (pre-commit hook 컨텍스트).

    .git/COMMIT_EDITMSG 또는 stdin 소스를 검사. 없으면 빈 문자열.
    """
    root = repo_root or Path.cwd()
    msg_file = root / ".git" / "COMMIT_EDITMSG"
    if msg_file.exists():
        try:
            return msg_file.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


def find_tests_exception(*sources: str) -> tuple[bool, str]:
    """Tests-Exception 라인 파싱.

    여러 소스(diff 추가 라인, commit msg)에서 검색. 사유 길이 ≥ 10 검증.

    Returns:
        (found, reason_or_error)
        found=True 이면 reason은 사유 텍스트
        found=False 이면 reason은 "" 또는 무효 사유 사유
    """
    invalid_reason_msg = ""
    for source in sources:
        for line in source.splitlines():
            m = EXCEPTION_PATTERN.search(line)
            if m:
                reason = m.group(1).strip()
                if len(reason) >= MIN_REASON_LEN:
                    return (True, reason)
                invalid_reason_msg = f"사유 너무 짧음 ({len(reason)}자, 최소 {MIN_REASON_LEN}자): '{reason}'"
    return (False, invalid_reason_msg)


def main() -> int:
    base = sys.argv[1] if len(sys.argv) >= 3 else ""
    head = sys.argv[2] if len(sys.argv) >= 3 else ""

    repo_root = Path.cwd()

    changed = get_changed_files(base, head, repo_root)
    if not changed:
        print("[check_test_sync] 변경 파일 없음 → skip")
        return 0

    trigger_files = [f for f in changed if any(p.search(f) for p in TRIGGER_PATTERNS)]
    test_files = [f for f in changed if any(p.search(f) for p in TEST_PATH_PATTERNS)]

    has_trigger = len(trigger_files) > 0
    has_tests = len(test_files) > 0

    print(f"[check_test_sync] 변경 파일 {len(changed)}개, trigger: {len(trigger_files)}개, tests: {len(test_files)}개")
    for f in changed:
        is_trigger = any(p.search(f) for p in TRIGGER_PATTERNS)
        is_test = any(p.search(f) for p in TEST_PATH_PATTERNS)
        if is_trigger:
            print(f"  [trigger] {f}")
        elif is_test:
            print(f"  [test  ] {f}")
        else:
            print(f"  [other ] {f}")

    if not has_trigger:
        print("[check_test_sync] 트리거 경로 변경 없음 → 게이트 대상 아님 ✓")
        return 0

    if has_tests:
        print("[check_test_sync] tests/** 동반 확인 ✓")
        return 0

    # Tests-Exception 검사 (diff 추가 라인 + commit msg)
    diff_added = get_diff_added_lines(base, head, repo_root)
    commit_msg = get_commit_message_subject_and_body(repo_root)
    has_exception, reason = find_tests_exception(diff_added, commit_msg)

    if has_exception:
        print("[check_test_sync] tests/** 동반 누락 — Tests-Exception 인정")
        print(f"  사유: '{reason[:80]}{'...' if len(reason) > 80 else ''}'")
        return 0

    # 차단
    print()
    print("[check_test_sync] ✗ FAIL — harness/hooks 변경에 tests/** 동반 누락")
    print("  변경 트리거 파일:")
    for f in trigger_files:
        print(f"    [trigger] {f}")
    print()
    print("해결 방법:")
    print("  1. tests/pytest/ 또는 tests/** 아래 회귀 테스트 추가 후 같은 PR 에 포함")
    print("  2. 또는 commit msg / PR body 에 'Tests-Exception: <10자 이상 사유>' 명시")
    print("       (예: 'Tests-Exception: docstring-only refactor — 행동 불변')")
    if reason and not has_exception:
        print(f"  ⚠️ 현재 Tests-Exception 발견됐으나 무효: {reason}")
    print()
    print("룰: orchestration/policies.md §8")
    return 1


if __name__ == "__main__":
    sys.exit(main())
