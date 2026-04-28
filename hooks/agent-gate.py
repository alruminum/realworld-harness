#!/usr/bin/env python3
"""
agent-gate.py — PreToolUse(Agent) 글로벌 훅

## 책임 분리 원칙 (A1)
이 훅 = "외부 직접 호출 방지" — 에이전트가 하네스 없이 호출되는 것을 차단.
내부 순서 보장(engineer 전 plan validation, pr-reviewer 전 validator 등)은
harness/impl_*.sh 스크립트가 담당한다. 여기서는 중복하지 않는다.

이 훅이 담당하는 것:
  - 프롬프트 검증 (이슈 번호, architect Mode)
  - harness_only 에이전트의 하네스 외부 호출 차단
  - engineer의 main branch 직접 작업 차단
  - background 에이전트 금지
  - 에이전트 호출 로그 + 활성 플래그

이 훅이 담당하지 않는 것 (impl_*.sh 에서 관리):
  - engineer 전 plan_validation_passed 필요 (→ impl_std.sh:54)
  - validator CODE_VALIDATION 전 test-engineer 필요 (→ impl_std.sh:300)
  - pr-reviewer 전 validator B 필요 (→ impl_std.sh:360)
  - designer → design-critic 순서 (→ design.sh)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import re
import subprocess
from datetime import datetime
from harness_common import (
    get_prefix, get_state_dir, get_flags_dir, deny, flag_exists, FLAGS,
    HARNESS_ONLY_AGENTS, ISSUE_REQUIRED_AGENTS, CUSTOM_AGENTS,
    ARCHITECT_HARNESS_ONLY_MODES, VALIDATOR_HARNESS_ONLY_MODES,
    detect_architect_mode, detect_validator_mode, is_harness_enabled,
)
import session_state as ss

PREFIX = get_prefix()


def _is_active_flag_fresh() -> bool:
    """HARNESS_ACTIVE flag mtime + TTL > now → fresh.
    skill-stop-protect.py started_at+ttl 패턴을 harness_common.auto_gc_stale_flag 로 일반화.
    §1.3 — Phase 2 W2.
    """
    from pathlib import Path as _Path
    from harness_common import auto_gc_stale_flag  # §1.8 신설
    fp = _Path(flag_path(PREFIX, FLAGS.HARNESS_ACTIVE))
    ttl = int(os.environ.get("HARNESS_GUARD_V2_FLAG_TTL_SEC", "21600"))  # 6h default
    return auto_gc_stale_flag(fp, ttl, "agent-gate")


def _has_tracking_id(prompt: str) -> bool:
    """추적 ID 존재 확인.
    v1: 단일 regex. v2: tracker.parse_ref 위임 (백엔드 단일 책임).
    §1.3 — Phase 2 W2.
    """
    if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") != "1":
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))
    try:
        from harness.tracker import parse_ref as _parse_ref  # type: ignore
    except ImportError:
        return bool(re.search(r"#\d+|LOCAL-\d+", prompt))  # v1 폴백
    # 프롬프트에서 추적 ID 후보 찾기 (모든 백엔드 지원)
    for token in re.findall(r"#\d+|LOCAL-\d+|\b\d+\b", prompt):
        try:
            _parse_ref(token)
            return True
        except (ValueError, Exception):
            continue
    return False


def flag(name: str) -> bool:
    """v1: 단순 존재. v2: HARNESS_ACTIVE 한정 age check + auto-GC.
    §1.3 — Phase 2 W2.
    """
    if (
        name == FLAGS.HARNESS_ACTIVE
        and os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") == "1"
    ):
        return _is_active_flag_fresh()
    return flag_exists(PREFIX, name)


def main():
    # 화이트리스트 가드 — `~/.claude/harness-projects.json`에 등록된 프로젝트에서만 동작.
    if not is_harness_enabled():
        sys.exit(0)

    try:
        d = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    t = d.get("tool_input", {})
    agent = t.get("subagent_type", "")
    prompt = t.get("prompt", "")
    bg = t.get("run_in_background", False)

    # Phase 3: 훅 stdin에서 session_id 파싱 — live.json 기록에 사용
    session_id = ss.session_id_from_stdin(d)

    if not agent:
        sys.exit(0)

    # 1. 프롬프트 검증: 추적 ID 필수 에이전트
    #    추적 ID = `#N` (GitHub) 또는 `LOCAL-N` (LocalBackend, harness/tracker.py).
    #    백엔드는 `harness/tracker.py` 가 환경에 따라 자동 선택 — gh CLI 미설치 환경
    #    에서도 LocalBackend 폴백으로 추적성 보존 (HARNESS-CHG-20260428-01).
    #    예외: SYSTEM_DESIGN — 전체 구조 설계, 특정 이슈 귀속 아님
    #    예외: TASK_DECOMPOSE — 이슈를 생성하는 역할
    #    예외: TECH_EPIC — 기술 에픽 초안, 이슈 선행 생성 아님
    #    예외: LIGHT_PLAN — qa/외부 경로에서 이슈 자동 주입 가능
    #    예외: DOCS_SYNC — impl 이미 완료 상태라 이슈 번호 무의미
    if agent in ISSUE_REQUIRED_AGENTS:
        is_exempt = agent == "architect" and re.search(
            r"SYSTEM_DESIGN|TASK_DECOMPOSE|TECH_EPIC|LIGHT_PLAN|DOCS_SYNC",
            prompt, re.IGNORECASE
        )
        if not is_exempt and not _has_tracking_id(prompt):  # §1.3 — v1/v2 분기 헬퍼
            # V2 deny enrichment — §1.3 / W4
            if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") == "1":
                deny(f"❌ {agent} 호출 전 추적 ID 등록 필요. "
                     f"프롬프트에 추적 ID(#NNN 또는 LOCAL-NNN)가 없습니다. "
                     f"발급: `python3 -m harness.tracker create-issue --title \"...\"` "
                     f"(백엔드는 환경에 따라 github/local 자동 선택)\n"
                     f"진단: tracker.parse_ref 검증 (V2) | 시도된 백엔드: github,local")
            else:
                deny(f"❌ {agent} 호출 전 추적 ID 등록 필요. "
                     f"프롬프트에 추적 ID(#NNN 또는 LOCAL-NNN)가 없습니다. "
                     f"발급: `python3 -m harness.tracker create-issue --title \"...\"` "
                     f"(백엔드는 환경에 따라 github/local 자동 선택)")

    # 2. 프롬프트 검증: architect 호출 시 Mode 명시 권장 (강제 아님)
    #    에이전트 본문의 "모드 미지정 시 입력 내용으로 판단" 규칙에 위임.
    #    캐주얼 진입로("간단히 해줘") 지원을 위해 block→warn.
    if agent == "architect":
        if not re.search(r"SYSTEM_DESIGN|MODULE_PLAN|SPEC_GAP|TASK_DECOMPOSE|TECH_EPIC|LIGHT_PLAN|DOCS_SYNC",
                         prompt, re.IGNORECASE):
            sys.stderr.write(
                "⚠️ architect 호출에 모드 키워드 미지정 — 에이전트가 입력으로 판단합니다. "
                "대규모 작업이면 SYSTEM_DESIGN/MODULE_PLAN/LIGHT_PLAN 등을 명시하세요.\n"
            )

    # 3. 하네스 내부 에이전트는 harness/executor.py 경유 필수
    if agent in HARNESS_ONLY_AGENTS and not flag(FLAGS.HARNESS_ACTIVE):
        cmds = {
            "engineer": 'python3 "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/harness/executor.py" impl --impl <path> --issue <REF>',
            "architect": 'python3 "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}/harness/executor.py" impl|plan ...',
        }
        # V2 deny enrichment — §1.3 / W4 (flag fresh 진단)
        if os.environ.get("HARNESS_GUARD_V2_AGENT_GATE") == "1":
            from pathlib import Path as _Path
            _flag_age_info = ""
            try:
                _fp = _Path(flag_path(PREFIX, FLAGS.HARNESS_ACTIVE))
                if _fp.exists():
                    import time as _t
                    _age = int(_t.time() - _fp.stat().st_mtime)
                    _ttl = int(os.environ.get("HARNESS_GUARD_V2_FLAG_TTL_SEC", "21600"))
                    _flag_age_info = f" | flag fresh? False (auto-GC at age={_age}s > ttl={_ttl}s)"
                else:
                    _flag_age_info = " | flag missing"
            except Exception:
                pass
            deny(
                f"❌ {agent}는 harness/executor.py를 통해서만 호출 가능. "
                f"{get_flags_dir()}/{PREFIX}_{FLAGS.HARNESS_ACTIVE} 없음. "
                f"직접 호출 금지 → {cmds.get(agent, 'executor.py')}\n"
                "\n"
                "🚫 패닉 회로 — 직전에 executor 가 SPEC_GAP_ESCALATE / 무진전 / 외부 종료\n"
                "   등으로 멈췄다고 해서 이 에이전트를 직접 부르지 마라. 우회 시도는\n"
                "   상태 추적 붕괴 + I-2 위반이다. 대신:\n"
                "   1. executor.py 재실행 (`--force-retry` 옵션으로 cooldown 우회 가능)\n"
                "   2. 새 셸/세션 (stale 상태 자동 복구 — HARNESS-CHG-20260428-06)\n"
                "   3. 그래도 막히면 유저 보고 — 메인 Claude 영역 아님.\n"
                f"진단: HARNESS_ACTIVE flag{_flag_age_info} (V2)"
            )
        else:
            deny(
                f"❌ {agent}는 harness/executor.py를 통해서만 호출 가능. "
                f"{get_flags_dir()}/{PREFIX}_{FLAGS.HARNESS_ACTIVE} 없음. "
                f"직접 호출 금지 → {cmds.get(agent, 'executor.py')}\n"
                "\n"
                "🚫 패닉 회로 — 직전에 executor 가 SPEC_GAP_ESCALATE / 무진전 / 외부 종료\n"
                "   등으로 멈췄다고 해서 이 에이전트를 직접 부르지 마라. 우회 시도는\n"
                "   상태 추적 붕괴 + I-2 위반이다. 대신:\n"
                "   1. executor.py 재실행 (`--force-retry` 옵션으로 cooldown 우회 가능)\n"
                "   2. 새 셸/세션 (stale 상태 자동 복구 — HARNESS-CHG-20260428-06)\n"
                "   3. 그래도 막히면 유저 보고 — 메인 Claude 영역 아님."
            )

    # 3a. Mode-level 게이트 — architect/validator 세분화
    #     product-plan 스킬 6단계처럼 SYSTEM_DESIGN은 메인 Claude 직접 호출 허용이지만,
    #     MODULE_PLAN/SPEC_GAP/PLAN_VALIDATION/CODE_VALIDATION 등은 harness 경유 필수.
    if not flag(FLAGS.HARNESS_ACTIVE):
        if agent == "architect":
            mode = detect_architect_mode(prompt)
            if mode in ARCHITECT_HARNESS_ONLY_MODES:
                deny(f"❌ architect {mode}는 harness/executor.py 경유만 허용됩니다. "
                     f"메인 Claude 직접 호출 금지. "
                     f'→ python3 "${{CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/realworld-harness}}/harness/executor.py" plan|impl --issue <REF> ... '
                     f"(plan_loop/impl_loop가 내부에서 자동 호출)")
        elif agent == "validator":
            mode = detect_validator_mode(prompt)
            if mode in VALIDATOR_HARNESS_ONLY_MODES:
                deny(f"❌ validator {mode}는 harness/executor.py 경유만 허용됩니다. "
                     f"메인 Claude 직접 호출 금지. "
                     f"→ executor.py impl/plan이 attempt 내부에서 자동 호출 (중복 호출 방지)")

    # 4. engineer는 feature branch에서만 실행 (main 보호)
    if agent == "engineer" and flag(FLAGS.HARNESS_ACTIVE):
        try:
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            current_branch = branch_result.stdout.strip()
            if current_branch in ("main", "master"):
                deny("❌ engineer는 feature branch에서만 실행 가능. "
                     f"현재: {current_branch}. "
                     "harness가 create_feature_branch()를 먼저 호출해야 합니다.")
        except Exception:
            pass

    # 5. 백그라운드 에이전트 금지
    if bg:
        deny(f"❌ 백그라운드 에이전트 금지. {agent} 호출 시 run_in_background=false 필수. "
             "포그라운드에서만 실행해야 중단 가능.")

    # 6. 에이전트 호출 로그
    caller = "harness-executor" if flag(FLAGS.HARNESS_ACTIVE) else "main-claude"
    ts = datetime.now().strftime("%H:%M:%S")
    snippet = prompt[:80].replace("\n", " ")
    try:
        with open(f"{get_state_dir()}/{PREFIX}-agent-calls.log", "a") as f:
            f.write(f"[{ts}] {caller} → {agent} | {snippet}\n")
    except Exception:
        pass

    # 7. Phase 3: 활성 에이전트를 세션 live.json에 기록.
    #    CC 내장 서브에이전트(Explore, Plan 등)는 우리 권한 제어 대상이 아니므로 기록하지 않는다.
    #    → 훅이 활성 에이전트 판정 시 live.json만 읽음 (env var 폴백/TTL/화이트리스트 필터 불필요).
    if agent in CUSTOM_AGENTS and session_id:
        try:
            ss.update_live(session_id, agent=agent)
        except Exception:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
