#!/usr/bin/env python3
"""skill-gate.py — PreToolUse(Skill) 글로벌 훅.

Phase 4.A: Skill 툴 호출 시 활성 스킬을 live.json.skill에 기록한다.

다른 훅(agent-boundary, harness-router, orch-rules-first)이 스킬 맥락을 읽어
정당한 작업을 오인 차단하지 않도록 한다.

청소는 PostToolUse(Skill)이 단일 책임자(post-skill-flags.py).
heavy 스킬은 PostToolUse가 청소하지 않고 Stop 훅 보호(skill-stop-protect.py)가
lifecycle을 관리한다.

설계 메모:
- OMC `skill-active-state.json` 분리 파일 모델 대신 `live.json.skill`로 통합.
  이유: live.json이 이미 세션 단일 소스 — 별도 파일은 청소 책임자 분산을 야기
  (OMC `cancel-skill-active-state-gap.md`가 정확히 그 결함을 박제).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS_DIR))

import session_state as ss  # noqa: E402
from skill_protection import get_skill_level  # noqa: E402


def _read_stdin() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError, ValueError):
        return {}


def _log_diag(event: dict) -> None:
    """진단 집계 — harness-state/.logs/skill-gate.jsonl
    §1.4 — Phase 2 W2/W4.
    """
    try:
        log_dir = ss.state_root() / ".logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "skill-gate.jsonl"
        event["ts"] = int(time.time())
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _skill_name(d: dict) -> str:
    """Skill 툴 입력에서 스킬 이름 추출. 가능한 키 변형 모두 시도.
    §1.4: 키 변형 silent 실패를 V2 활성 시 진단.
    """
    inp = d.get("tool_input") or {}
    for key in ("skill", "skillName", "name"):
        v = inp.get(key)
        if v:
            return v
    # v2: 이름 없음을 진단 — 메인 Claude Skill 호출 형식 변경 시 silent missing 차단
    if os.environ.get("HARNESS_GUARD_V2_SKILL_GATE") == "1":
        sys.stderr.write(
            f"[skill-gate] WARN: Skill tool_input missing skill name. keys={list(inp.keys())}\n"
        )
        _log_diag({"event": "skill_name_missing", "tool_input_keys": list(inp.keys())})
    return ""


def main() -> int:
    d = _read_stdin()
    if d.get("tool_name") != "Skill":
        return 0
    name = _skill_name(d)
    if not name:
        return 0

    sid = ss.session_id_from_stdin(d) or ss.current_session_id()
    if not sid:
        return 0

    level = get_skill_level(name)
    v2_on = os.environ.get("HARNESS_GUARD_V2_SKILL_GATE") == "1"
    try:
        ss.set_active_skill(sid, name, level)
        # v2 success 진단 — 5번째 위험 (silent missing) 사전 가시화
        if v2_on:
            _log_diag({"event": "set_skill_ok", "sid": sid, "skill": name, "level": level})
    except Exception as e:
        # v1: silent pass (regression 0).
        # v2: stderr 경고 + diag log. passive recorder 본질 유지 (차단 없음).
        if v2_on:
            sys.stderr.write(
                f"[skill-gate] WARN: set_active_skill failed (sid={sid[:8]}…, skill={name}): {e}\n"
                f"  → downstream guards (agent-boundary/issue-gate/commit-gate) may false-block.\n"
                f"  → check live.json writability: ls -la .claude/harness-state/.sessions/{sid}/live.json\n"
            )
            _log_diag({"event": "set_skill_fail", "sid": sid, "skill": name, "err": str(e)})
        # silent pass 자체는 v1/v2 동일 — 본 가드는 deny 권한 없음
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
