#!/usr/bin/env python3
"""
commit-gate.py — PreToolUse(Bash) 글로벌 훅
git commit 전 pr-reviewer LGTM 확인.
프로젝트별 인라인 원라이너를 대체.

prefix는 환경변수 HARNESS_PREFIX로 주입 (기본값: mb).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import re
import subprocess
import time
from harness_common import get_prefix, get_state_dir, get_flags_dir, deny, flag_path, flag_exists, FLAGS, ISSUE_CREATORS, is_harness_enabled
import session_state as ss

PREFIX = get_prefix()


def _matches_tracker_mutate(cmd: str) -> bool:
    """harness.tracker MUTATING_SUBCOMMANDS 의 동적 매칭.
    v1 fallback: 정적 (create-issue|comment) regex.
    §1.2 — Phase 2 W2.
    """
    if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") != "1":
        # v1 동작 (line 55-56 그대로)
        return bool(
            re.search(r"harness\.tracker\s+(create-issue|comment)", cmd)
            or re.search(r"harness/tracker\.py\s+(create-issue|comment)", cmd)
        )
    try:
        from harness.tracker import MUTATING_SUBCOMMANDS  # §1.8 신설
    except ImportError:
        sys.stderr.write("[commit-gate] WARN: tracker.MUTATING_SUBCOMMANDS import failed; v1 fallback\n")
        return bool(re.search(r"harness\.tracker\s+(create-issue|comment)", cmd))
    if not MUTATING_SUBCOMMANDS:
        sys.stderr.write("[commit-gate] WARN: MUTATING_SUBCOMMANDS empty; v1 fallback\n")
        return bool(re.search(r"harness\.tracker\s+(create-issue|comment)", cmd))
    sub_pat = "|".join(re.escape(s) for s in MUTATING_SUBCOMMANDS)
    return bool(
        re.search(rf"harness\.tracker\s+({sub_pat})", cmd)
        or re.search(rf"harness/tracker\.py\s+({sub_pat})", cmd)
    )


def _has_engineer_change(staged: str) -> bool:
    """staged 파일이 engineer_scope 패턴 중 하나라도 매치하는지.
    v1: 정적 ^src/. v2: harness_common._load_engineer_scope() 위임.
    §1.2 / §4.8 — 두 flag 중 하나라도 활성이면 V2 동작.
    """
    v2_on = (
        os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") == "1"
        or os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") == "1"
        or os.environ.get("HARNESS_GUARD_V2_ALL") == "1"
    )
    if not v2_on:
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    try:
        from harness_common import _load_engineer_scope  # §1.8
        patterns = _load_engineer_scope()
    except Exception as e:
        sys.stderr.write(f"[commit-gate] WARN: engineer_scope load failed ({e}); v1 fallback\n")
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    if not patterns:
        sys.stderr.write("[commit-gate] WARN: engineer_scope empty; v1 fallback ^src/\n")
        return bool(re.search(r"^src/", staged, re.MULTILINE))
    # regex 컴파일 실패 방어 (§4.2)
    try:
        combined_re = re.compile("(" + "|".join(patterns) + ")", re.MULTILINE)
    except re.error as e:
        sys.stderr.write(f"[commit-gate] WARN: engineer_scope regex invalid ({e}); v1 fallback ^src/\n")
        combined_re = re.compile(r"^src/", re.MULTILINE)
    return bool(combined_re.search(staged))


def _is_issue_creator_active(stdin_data=None):
    """Phase 3: live.json 단일 소스로 판정.
    ISSUE_CREATORS(qa, designer, architect, product-planner) 중 하나라도 활성이면 True.
    """
    agent = ss.active_agent(stdin_data=stdin_data)
    return agent in ISSUE_CREATORS


def main():
    # 화이트리스트 가드 — `~/.claude/harness-projects.json` 등록된 프로젝트에서만 동작.
    if not is_harness_enabled():
        sys.exit(0)

    try:
        d = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cmd = d.get("tool_input", {}).get("command", "")

    # ── Gate 1: 추적 이슈 변경 명령 직접 호출 차단 ──────────────────────
    # QA/designer 에이전트만 이슈를 생성/수정할 수 있다. 메인 Claude 직접 호출 금지.
    # 가드 대상:
    #   - gh issue create/edit (직접 CLI)
    #   - gh api ... issues ... POST/PATCH
    #   - python3 -m harness.tracker create-issue / comment (추적 ID 추상화 CLI)
    #     → 백엔드(github/local) 무관하게 동일하게 가드 (HARNESS-CHG-20260428-01).
    _IS_GH_ISSUE_MUTATE = (
        re.search(r"gh\s+issue\s+(create|edit)", cmd)
        or re.search(r"gh\s+api\s+.*issues.*--method\s+POST", cmd)
        or re.search(r"gh\s+api\s+.*issues.*-X\s+(POST|PATCH)", cmd)
        or re.search(r"gh\s+api\s+.*issues/\d+.*-X\s+PATCH", cmd)
        or _matches_tracker_mutate(cmd)  # v1/v2 모두 통과 (§1.2)
    )
    if _IS_GH_ISSUE_MUTATE and os.environ.get("HARNESS_INTERNAL") != "1" and not _is_issue_creator_active(d):
        # V2 deny enrichment (§1.2 / W4)
        if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") == "1":
            try:
                from harness.tracker import MUTATING_SUBCOMMANDS as _msc
                _msc_listed = ", ".join(sorted(_msc))
            except Exception:
                _msc_listed = "create-issue, comment (static)"
            deny(
                "❌ [hooks/commit-gate.py] 추적 이슈 변경 명령 직접 호출 금지.\n"
                "이슈 생성/수정은 QA 에이전트가, 디자인 이슈는 designer 에이전트가 처리한다.\n"
                "차단된 명령 형식: gh issue create/edit, gh api issues POST/PATCH, "
                "python3 -m harness.tracker create-issue|comment.\n"
                f"올바른 흐름: /qa 스킬 → QA 에이전트 분석·이슈 생성/수정 → python3 executor.py impl --issue <REF> --prefix {PREFIX}\n"
                f"진단: cmd matched MUTATING_SUBCOMMANDS=[{_msc_listed}] | tracker source: V2"
            )
        else:
            deny(
                "❌ [hooks/commit-gate.py] 추적 이슈 변경 명령 직접 호출 금지.\n"
                "이슈 생성/수정은 QA 에이전트가, 디자인 이슈는 designer 에이전트가 처리한다.\n"
                "차단된 명령 형식: gh issue create/edit, gh api issues POST/PATCH, "
                "python3 -m harness.tracker create-issue|comment.\n"
                f"올바른 흐름: /qa 스킬 → QA 에이전트 분석·이슈 생성/수정 → python3 executor.py impl --issue <REF> --prefix {PREFIX}"
            )

    # ── Gate 2: (removed in v6 — bugfix 모드 제거에 따라 is_bug 게이트 삭제)

    # ── Gate 3: 인터뷰 진행 중 executor.sh 호출 차단 ───────────────────
    # harness-router.py가 AMBIGUOUS 분류 시 interview_state.json을 생성.
    # 인터뷰 완료(DONE) 전까지 구현 루프 진입 금지.
    _interview_path = f"{get_state_dir()}/{PREFIX}_interview_state.json"
    _IS_EXECUTOR_ANY = re.search(r"executor\.(sh|py)\s+(impl|bugfix|design|plan)\b", cmd)
    if _IS_EXECUTOR_ANY and os.path.exists(_interview_path) and os.environ.get("HARNESS_INTERNAL") != "1":
        deny(
            "❌ [hooks/commit-gate.py] 인터뷰 진행 중 — executor.py 호출 불가.\n"
            "요구사항 명확화 인터뷰를 먼저 완료하세요.\n"
            "현재 질문에 답변하면 다음 단계로 진행됩니다."
        )

    # git commit 명령이 아니면 통과
    if not re.search(r"git\s+commit", cmd):
        sys.exit(0)

    # ── Gate 4: 거버넌스 Document Sync 게이트 ──────────────────────────
    # 현재 프로젝트에 scripts/check_doc_sync.py 가 있으면 실행 (RWHarness 거버넌스).
    # 없으면 skip — 다른 프로젝트엔 영향 없음.
    _doc_sync = os.path.join(os.getcwd(), "scripts", "check_doc_sync.py")
    if os.path.isfile(_doc_sync) and os.environ.get("HARNESS_INTERNAL") != "1":
        try:
            _r = subprocess.run(
                ["python3", _doc_sync],
                capture_output=True, text=True, timeout=15
            )
            if _r.returncode != 0:
                deny(
                    "❌ [hooks/commit-gate.py] Document Sync 게이트 실패\n\n"
                    + (_r.stdout or "") + (_r.stderr or "")
                )
        except subprocess.TimeoutExpired:
            pass  # timeout은 차단 사유 아님 (스크립트 자체 문제 가능성)
        except Exception:
            pass

    # staged 파일에 src/ 가 있는지 확인
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5
        )
        staged = result.stdout
    except Exception:
        sys.exit(0)

    has_src = _has_engineer_change(staged)  # §1.2 — v1/v2 분기 헬퍼
    if not has_src:
        sys.exit(0)

    # feature branch → LGTM 불필요, 자유 커밋
    try:
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        current_branch = branch_result.stdout.strip()
    except Exception:
        current_branch = ""

    if current_branch and current_branch not in ("main", "master"):
        sys.exit(0)

    # src 변경이 있으면 LGTM 필요
    if not os.path.exists(f"{get_flags_dir()}/{PREFIX}_{FLAGS.PR_REVIEWER_LGTM}"):
        # V2 deny enrichment — §1.2 / W4
        if os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") == "1" or os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") == "1":
            _scope_src = "harness.config.json (V2)" if (
                os.environ.get("HARNESS_GUARD_V2_COMMIT_GATE") == "1"
                or os.environ.get("HARNESS_GUARD_V2_AGENT_BOUNDARY") == "1"
            ) else "static fallback"
            deny(
                f"❌ [hooks/commit-gate.py] git commit 전 pr-reviewer LGTM 필요. "
                f"{get_flags_dir()}/{PREFIX}_{FLAGS.PR_REVIEWER_LGTM} 없음.\n"
                f"진단: engineer_scope source: {_scope_src} | matched_pattern: engineer_scope"
            )
        else:
            deny(f"❌ [hooks/commit-gate.py] git commit 전 pr-reviewer LGTM 필요. {get_flags_dir()}/{PREFIX}_{FLAGS.PR_REVIEWER_LGTM} 없음.")

    sys.exit(0)


if __name__ == "__main__":
    main()
