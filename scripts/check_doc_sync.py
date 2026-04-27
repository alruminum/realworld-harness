#!/usr/bin/env python3
"""
check_doc_sync.py — Document Sync 자동 게이트

git diff 의 변경 파일을 Change-Type 으로 분류하고, 동반 산출물 요건을 검사한다.
Document-Exception 스코핑은 현재 diff 의 추가 라인만 유효 (과거 누적 엔트리 무효).

사용법:
  로컬:   python3 scripts/check_doc_sync.py
  CI:     python3 scripts/check_doc_sync.py <base> <head>

종료 코드:
  0  = PASS
  1  = FAIL (누락 산출물 + Exception 없음)
  2  = ERROR (git 호출 실패 등)

Spec: orchestration/policies.md §2~6
Python 3.9+ stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# orchestration/policies.md §2 정의의 코드 표현
SPEC_PATTERNS = [
    re.compile(r"^docs/harness-spec\.md$"),
    re.compile(r"^docs/harness-architecture\.md$"),
    re.compile(r"^docs/proposals\.md$"),
    re.compile(r"^prd\.md$"),
    re.compile(r"^trd\.md$"),
]

INFRA_PATTERNS = [
    re.compile(r"^hooks/"),
    re.compile(r"^harness/"),
    re.compile(r"^scripts/"),
    re.compile(r"^\.claude-plugin/"),
]

AGENT_PATTERNS = [
    re.compile(r"^agents/.+\.md$"),
]

TEST_PATTERNS = [
    re.compile(r"^tests/"),
]

# 기본 fall-through = docs

# 동반 산출물
CHANGELOG = "orchestration/changelog.md"
RATIONALE = "orchestration/rationale.md"

# Type 우선순위 (높을수록 강함)
TYPE_PRIORITY = {"spec": 5, "infra": 4, "agent": 3, "docs": 2, "test": 1}


def classify(file_path: str) -> str:
    """파일 경로 → Change-Type 분류. 우선순위: spec > infra > agent > test > docs."""
    for p in SPEC_PATTERNS:
        if p.search(file_path):
            return "spec"
    for p in INFRA_PATTERNS:
        if p.search(file_path):
            return "infra"
    for p in AGENT_PATTERNS:
        if p.search(file_path):
            return "agent"
    for p in TEST_PATTERNS:
        if p.search(file_path):
            return "test"
    return "docs"


def get_changed_files(base: str = "", head: str = "") -> list[str]:
    """git diff 로 변경 파일 목록 추출.

    인자 없으면: staged 변경 (pre-commit hook 용)
    인자 있으면: git diff --name-only base head (CI 용)
    """
    if base and head:
        cmd = ["git", "diff", "--name-only", base, head]
    else:
        cmd = ["git", "diff", "--name-only", "--cached"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"[check_doc_sync] git diff 실패: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_diff_added_lines(base: str = "", head: str = "") -> str:
    """git diff 의 추가 라인(+로 시작, +++ 헤더 제외) 추출."""
    if base and head:
        cmd = ["git", "diff", base, head]
    else:
        cmd = ["git", "diff", "--cached"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        return ""

    added = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    return "\n".join(added)


def get_commit_message_subject_and_body() -> str:
    """현재 staged commit msg 가 있으면 추출 (pre-commit hook 컨텍스트).

    .git/COMMIT_EDITMSG 또는 stdin 소스를 검사. 없으면 빈 문자열.
    """
    msg_file = REPO_ROOT / ".git" / "COMMIT_EDITMSG"
    if msg_file.exists():
        try:
            return msg_file.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


def find_document_exception(*sources: str) -> tuple[bool, str]:
    """Document-Exception 라인 파싱.

    여러 소스(diff 추가 라인, commit msg)에서 검색. 사유 길이 ≥ 10 검증.

    Returns:
        (found, reason_or_error)
        found=True 이면 reason은 사유 텍스트
        found=False 이면 reason은 "" 또는 무효 사유 사유
    """
    pattern = re.compile(r"Document-Exception:\s*(.+)")
    invalid_reason_msg = ""
    for source in sources:
        for line in source.splitlines():
            m = pattern.search(line)
            if m:
                reason = m.group(1).strip()
                if len(reason) >= 10:
                    return (True, reason)
                invalid_reason_msg = f"사유 너무 짧음 ({len(reason)}자, 최소 10자): '{reason}'"
    return (False, invalid_reason_msg)


def determine_required_companions(change_type: str) -> list[str]:
    """Change-Type 별 동반 필수 산출물 목록 (orchestration/policies.md §2)."""
    if change_type == "spec":
        return [CHANGELOG, RATIONALE]
    if change_type in ("infra", "agent", "docs"):
        return [CHANGELOG]
    return []  # test


def main() -> int:
    base = sys.argv[1] if len(sys.argv) >= 3 else ""
    head = sys.argv[2] if len(sys.argv) >= 3 else ""

    changed = get_changed_files(base, head)
    if not changed:
        print("[check_doc_sync] 변경 파일 없음 → skip")
        return 0

    classified = [(f, classify(f)) for f in changed]
    top_type = max((t for _, t in classified), key=lambda t: TYPE_PRIORITY[t])

    print(f"[check_doc_sync] 변경 파일 {len(changed)}개, top type: {top_type}")
    for f, t in classified:
        marker = "←" if t == top_type else " "
        print(f"  [{t:6}] {marker} {f}")

    required = determine_required_companions(top_type)
    if not required:
        print(f"[check_doc_sync] {top_type} type — 동반 산출물 요건 없음 ✓")
        return 0

    changed_set = set(changed)
    missing = [r for r in required if r not in changed_set]

    if not missing:
        print(f"[check_doc_sync] 동반 산출물 모두 갖춤: {required} ✓")
        return 0

    # Document-Exception 검사 (diff 추가 라인 + commit msg)
    diff_added = get_diff_added_lines(base, head)
    commit_msg = get_commit_message_subject_and_body()
    has_exception, reason = find_document_exception(diff_added, commit_msg)

    if has_exception:
        print(f"[check_doc_sync] 누락 산출물 {missing} — Document-Exception 인정")
        print(f"  사유: '{reason[:80]}{'...' if len(reason) > 80 else ''}'")
        return 0

    # 차단
    print()
    print(f"[check_doc_sync] ✗ FAIL — {top_type} 변경에 동반 산출물 누락")
    for m in missing:
        print(f"  누락: {m}")
    print()
    print("해결 방법:")
    print(f"  1. 누락된 산출물({', '.join(missing)})을 같은 commit/PR에 추가")
    print(f"  2. 또는 commit msg / PR body 에 'Document-Exception: <10자 이상 사유>' 명시")
    if reason and not has_exception:
        print(f"  ⚠️ 현재 Document-Exception 발견됐으나 무효: {reason}")
    print()
    print("룰: orchestration/policies.md §2~3")
    return 1


if __name__ == "__main__":
    sys.exit(main())
