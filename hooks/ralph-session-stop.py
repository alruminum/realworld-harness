#!/usr/bin/env python3
"""ralph-session-stop.py — ralph-loop 공유 state 파일의 세션 가로채기 차단.

오피셜 `ralph-loop@claude-plugins-official` 훅(`stop-hook.sh`)은 state 파일
`.claude/ralph-loop.local.md` 의 frontmatter `session_id:` 필드와 hook stdin의
session_id를 비교해 다른 세션이면 `exit 0` 한다 (격리). 단 `STATE_SESSION`이
비어있으면 fall-through — 그 첫 fire 세션이 claim을 가져간다.

문제: setup-ralph-loop.sh는 `session_id: ${CLAUDE_CODE_SESSION_ID:-}` 로 박는데,
CC가 이 env를 자식 프로세스에 자동 export하지 않아 빈 값으로 시작. 결과적으로
"엉뚱한 세션 첫 Stop이 ralph 루프를 탈취" 사고가 발생.

이 선행 Stop 훅이 오피셜 훅을 수정하지 않고 root cause를 우회한다:

1. **시작자 식별**: live.json.skill.name == "ralph-loop:ralph-loop" 인 세션이
   진짜 ralph 시작 세션. PreToolUse(Skill) 훅이 미리 기록해 둔다.
2. **시작자 첫 fire**: state.session_id 비어있고 내가 시작자면 → 내 SID 박음.
   오피셜 훅이 정상 진행.
3. **비시작자 fire**: state.session_id 비어있고 내가 시작자가 아니면 →
   placeholder `__pending_<short>__` 박음. 오피셜 훅에서 STATE_SESSION ≠
   HOOK_SESSION → `exit 0` (claim 차단).
4. **시작자 늦은 fire**: state.session_id == placeholder, 내가 시작자면 →
   내 SID로 교체. 오피셜 정상 진행.
5. **다른 세션 이미 점유**: state.session_id가 진짜 SID이고 내 SID와 다르면
   → cross-session JSONL 박제, 출력 없음 (오피셜이 알아서 격리 — STATE_SESSION
   != HOOK_SESSION이므로 exit 0).

레거시 cc_session_id 필드는 더 이상 쓰지 않는다 (오피셜이 안 보는 우리 전용
필드였음 — 격리에 무용). 기존 state 파일 호환을 위해 무시만 한다.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS_DIR))

import session_state as ss  # noqa: E402

STATE_FILENAME = ".claude/ralph-loop.local.md"
OFFICIAL_SID_FIELD = "session_id"
RALPH_SKILL_NAMES = {"ralph-loop:ralph-loop", "ralph-loop"}
PENDING_PREFIX = "__pending_"


def _read_stdin_json() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _find_state_file(start: Path):
    project_root = ss._find_project_root(start)
    candidate = project_root / STATE_FILENAME
    return candidate if candidate.exists() else None


def _parse_session_id_field(content: str) -> str:
    """오피셜 frontmatter의 `session_id:` 필드 추출.
    `[ \\t]*`로 제한 — `\\s*`는 multiline에서 newline까지 먹어 다음 줄을 잘못 잡는다.
    """
    m = re.search(rf"^{OFFICIAL_SID_FIELD}:[ \t]*(\S*)[ \t]*$", content, flags=re.MULTILINE)
    return m.group(1) if m else ""


def _set_session_id_field(content: str, sid: str) -> str:
    """frontmatter의 `session_id:` 필드를 sid로 교체. 없으면 frontmatter에 주입."""
    pattern = re.compile(rf"^{OFFICIAL_SID_FIELD}:[^\n]*$", flags=re.MULTILINE)
    if pattern.search(content):
        return pattern.sub(f"{OFFICIAL_SID_FIELD}: {sid}", content, count=1)
    # 없으면 frontmatter 안쪽에 주입
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return content
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            insert = f"{OFFICIAL_SID_FIELD}: {sid}\n"
            return "".join(lines[:i] + [insert] + lines[i:])
    return content


def _atomic_write(state_file: Path, content: str) -> None:
    tmp = state_file.with_suffix(state_file.suffix + f".{uuid.uuid4().hex}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, state_file)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass


def _is_ralph_initiator(sid: str) -> bool:
    """현재 세션이 ralph-loop의 시작자인지 — 3-layer fallback.

    Staged rollout: HARNESS_GUARD_V2_RALPH_FALLBACK=1 일 때만 2~3차 활성.
    미설정 시 v1 동작 (live.json.skill 단일 검사) 유지 — regression 0.

    1차 (always): live.json.skill.name ∈ RALPH_SKILL_NAMES
    2차 (V2): live.json._meta.skill_started_at 존재 (skill-gate 가 partial 기록 흔적)
    3차 (V2): RALPH_SESSION_INITIATOR env var == sid (skill-gate.jsonl corroboration 포함)
              또는 ralph-cross-session.jsonl 에 본 sid 의 claim_self 이벤트가 있는지

    §1.9 / §4.7 — Phase 2 W4 (5번째 위험 실측 케이스 영구 fix).
    """
    # 1차 — v1 경로 (변경 없음)
    skill = ss.get_active_skill(sid)
    if skill and skill.get("name", "") in RALPH_SKILL_NAMES:
        return True

    # V2 staged rollout — 미설정 시 v1 결과 (False) 반환
    if os.environ.get("HARNESS_GUARD_V2_RALPH_FALLBACK") != "1":
        return False

    # 2차 — _meta 흔적 (skill-gate 가 _meta 만 쓰고 skill 갱신 실패한 partial 케이스)
    try:
        live_p = ss.live_path(sid)
        if live_p.exists():
            data = json.loads(live_p.read_text(encoding="utf-8"))
            meta = data.get("_meta") or {}
            # skill-gate 가 partial 흔적을 _meta 에 남기는 경우 (W4 보강과 함께 도입)
            if meta.get("skill_started_at") and meta.get("skill_name", "") in RALPH_SKILL_NAMES:
                _log_event({
                    "event": "fallback_meta_match",
                    "sid": sid,
                    "skill_name": meta.get("skill_name"),
                })
                return True
    except (json.JSONDecodeError, OSError):
        pass

    # 3차 — env var + skill-gate.jsonl corroboration (§4.7 false-positive 차단)
    env_initiator = os.environ.get("RALPH_SESSION_INITIATOR", "")
    if env_initiator and env_initiator == sid:
        # 보강: skill-gate.jsonl 에 최근 30분 내 본 sid 의 ralph 호출 흔적
        try:
            log_p = ss.state_root() / ".logs" / "skill-gate.jsonl"
            if log_p.exists():
                recent_threshold = int(time.time()) - 1800  # 30 min
                for line in log_p.read_text(encoding="utf-8").splitlines()[-200:]:
                    try:
                        evt = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if (
                        evt.get("sid") == sid
                        and evt.get("event") == "set_skill_ok"
                        and evt.get("skill") in RALPH_SKILL_NAMES
                        and evt.get("ts", 0) >= recent_threshold
                    ):
                        _log_event({"event": "fallback_env_match_corroborated", "sid": sid})
                        return True
                # env match 했지만 corroboration 실패 — false-positive 의심
                _log_event({"event": "fallback_env_match_uncorroborated", "sid": sid})
                return False
        except (json.JSONDecodeError, OSError):
            pass
        # log 자체 없음 → env 만 신뢰 (조기 도입 시 fallback)
        _log_event({"event": "fallback_env_match", "sid": sid})
        return True

    # 3차-b — ralph-cross-session.jsonl 에서 본 sid 의 claim_self 이벤트 검색
    try:
        log_p = ss.state_root() / ".logs" / "ralph-cross-session.jsonl"
        if log_p.exists():
            for line in log_p.read_text(encoding="utf-8").splitlines():
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if evt.get("event") == "claim_self" and evt.get("sid") == sid:
                    _log_event({"event": "fallback_jsonl_match", "sid": sid})
                    return True
    except OSError:
        pass

    # 모든 폴백 실패 — placeholder 박는 v1 동작 유지 (regression 0)
    _log_event({"event": "fallback_all_missed", "sid": sid})
    return False


def _log_event(event: dict) -> None:
    try:
        log_dir = ss.state_root() / ".logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "ralph-cross-session.jsonl"
        event["ts"] = int(time.time())
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    data = _read_stdin_json()
    sid = ss.session_id_from_stdin(data) or ss.current_session_id()
    if not sid:
        return 0

    start = Path(data.get("cwd") or os.getcwd())
    try:
        state_file = _find_state_file(start.resolve())
    except OSError:
        return 0
    if state_file is None:
        return 0

    try:
        content = state_file.read_text(encoding="utf-8")
    except OSError:
        return 0

    recorded = _parse_session_id_field(content)
    is_initiator = _is_ralph_initiator(sid)
    is_placeholder = recorded.startswith(PENDING_PREFIX)

    # Case A: state.session_id 비어있음
    if not recorded:
        if is_initiator:
            # 시작자 첫 fire — 내 SID 박음. 오피셜 정상 진행.
            new_content = _set_session_id_field(content, sid)
            if new_content != content:
                _atomic_write(state_file, new_content)
                _log_event({
                    "event": "claim_self",
                    "sid": sid,
                    "state_file": str(state_file),
                })
        else:
            # 비시작자 fire — placeholder 박아 오피셜 fall-through 차단.
            placeholder = f"{PENDING_PREFIX}{uuid.uuid4().hex[:8]}__"
            new_content = _set_session_id_field(content, placeholder)
            if new_content != content:
                _atomic_write(state_file, new_content)
                _log_event({
                    "event": "claim_block_pending",
                    "sid": sid,
                    "placeholder": placeholder,
                    "state_file": str(state_file),
                })
        return 0

    # Case B: placeholder 박혀있음
    if is_placeholder:
        if is_initiator:
            # 진짜 시작자 등장 — placeholder를 내 SID로 교체.
            new_content = _set_session_id_field(content, sid)
            if new_content != content:
                _atomic_write(state_file, new_content)
                _log_event({
                    "event": "claim_promote",
                    "sid": sid,
                    "from": recorded,
                    "state_file": str(state_file),
                })
        # 시작자 아니면 placeholder 유지. 오피셜은 STATE != HOOK이므로 exit 0.
        return 0

    # Case C: 진짜 SID가 박혀있음
    if recorded != sid:
        # 다른 세션 점유 — 오피셜이 알아서 격리. 우리는 진단만.
        _log_event({
            "event": "cross_session_state_attempt",
            "current_sid": sid,
            "recorded_sid": recorded,
            "state_file": str(state_file),
        })
        # 추가: 시작자가 아닌데 다른 세션 SID와 일치 안 하는 경우, 호환성 위해
        # 메시지도 stderr로 (기존 동작 유지).
        sys.stderr.write(
            f"⚠️  ralph-loop: state 파일이 다른 세션({recorded[:8]}…) 소유입니다. "
            f"현재 세션({sid[:8]}…)에서는 이 state를 claim하지 마세요. "
            f"필요하면 `rm {state_file}` 로 잔재를 정리하세요.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
