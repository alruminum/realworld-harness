"""test_session_state_fallback.py — current_session_id() 글로벌 폴백 단위 테스트.

Issue #19 / HARNESS-CHG-20260428-19:
  RWHarness dogfooding 환경에서 프로젝트 .session-id 미생성 시
  ~/.claude/harness-state/.session-id 를 신선도·자기참조 가드로 채택.

TC1: HARNESS_SESSION_ID env 있으면 즉시 반환 (글로벌 폴백 안 가짐)
TC2: project pointer 있으면 즉시 반환 (글로벌 폴백 안 가짐)
TC3: env + project 모두 없고 글로벌 pointer 신선 → 글로벌 sid 반환
TC4: 글로벌 pointer 6h 초과 stale → 빈 문자열 (false-positive 차단)
TC5: project_root 가 ~/.claude (자기참조) → 글로벌 폴백 skip → 빈 문자열
보너스: 글로벌 pointer 형식 invalid (path traversal 시도) → 빈 문자열

테스트 격리:
  monkeypatch.setattr(Path, "home", lambda: tmp_path) 로 ~/.claude 격리.
  실제 ~/.claude 를 절대 건드리지 않음.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

# conftest.py 가 sys.path 에 hooks/ 를 추가하므로 직접 import 가능
import session_state as ss


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────

def _make_global_pointer(fake_home: Path, sid: str, written_at: int) -> None:
    """fake_home/.claude/harness-state/ 에 신선한 글로벌 pointer 환경을 구성한다."""
    home_state = fake_home / ".claude" / "harness-state"
    sessions_dir = home_state / ".sessions" / sid
    sessions_dir.mkdir(parents=True, exist_ok=True)
    # .session-id pointer
    (home_state / ".session-id").write_text(sid, encoding="utf-8")
    # live.json (_meta 포함)
    live = sessions_dir / "live.json"
    live.write_text(json.dumps({
        "session_id": sid,
        "_meta": {
            "written_at": written_at,
            "mode": "session",
            "sessionId": sid,
        },
    }), encoding="utf-8")


def _make_project_root_without_pointer(parent: Path, name: str = "project-no-pointer") -> Path:
    """프로젝트 pointer 없는 project_root 구성.

    .claude 디렉토리는 존재하지만 harness-state/.session-id 없음.
    이렇게 해야 _find_project_root 가 해당 프로젝트를 찾고 home 으로 폴백하지 않는다.
    (home 폴백이 발동하면 read_session_pointer 가 글로벌 pointer 를 읽어버림.)
    """
    project_root = parent / name
    (project_root / ".claude" / "harness-state").mkdir(parents=True, exist_ok=True)
    return project_root


# ── TC1: env 우선순위 ─────────────────────────────────────────────────────────

def test_env_takes_priority_over_global_fallback(monkeypatch, tmp_path):
    """TC1: HARNESS_SESSION_ID env 있으면 글로벌 폴백 발동 안 함."""
    env_sid = "env-session-id-abc123"
    monkeypatch.setenv("HARNESS_SESSION_ID", env_sid)

    # 글로벌 pointer 도 신선하게 구성 (폴백 발동 여부 확인)
    global_sid = "global-session-id-xyz789"
    _make_global_pointer(tmp_path, global_sid, int(time.time()))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # project_root 는 .claude 있지만 pointer 없는 구성
    project_root = _make_project_root_without_pointer(tmp_path, "project")

    result = ss.current_session_id(project_root)
    assert result == env_sid, f"env sid 반환 기대, got {result!r}"


# ── TC2: project pointer 우선순위 ────────────────────────────────────────────

def test_project_pointer_takes_priority_over_global_fallback(monkeypatch, tmp_path):
    """TC2: 프로젝트 .session-id 있으면 글로벌 폴백 발동 안 함."""
    # env 없음 (conftest autouse _isolate_harness_env 가 HARNESS_SESSION_ID 제거)

    # 프로젝트 pointer 구성
    project_sid = "project-session-id-proj01"
    project_root = tmp_path / "project"
    state = project_root / ".claude" / "harness-state"
    state.mkdir(parents=True, exist_ok=True)
    (state / ".session-id").write_text(project_sid, encoding="utf-8")

    # 글로벌 pointer 도 신선하게 구성 (폴백 발동 여부 확인)
    global_sid = "global-session-id-xyz789"
    _make_global_pointer(tmp_path, global_sid, int(time.time()))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = ss.current_session_id(project_root)
    assert result == project_sid, f"project sid 반환 기대, got {result!r}"


# ── TC3: 글로벌 폴백 활성 (신선한 pointer) ──────────────────────────────────

def test_global_fallback_fresh_pointer(monkeypatch, tmp_path):
    """TC3: env + project 모두 없고 글로벌 pointer 신선 → 글로벌 sid 반환."""
    global_sid = "global-session-fresh-abc1"
    _make_global_pointer(tmp_path, global_sid, int(time.time()))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # project_root: .claude 있지만 pointer 없음
    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == global_sid, f"글로벌 sid 반환 기대, got {result!r}"


# ── TC4: stale pointer 거부 ───────────────────────────────────────────────────

def test_global_fallback_stale_rejected(monkeypatch, tmp_path):
    """TC4: 글로벌 pointer 6h 초과 stale → 빈 문자열."""
    global_sid = "global-session-stale-xyz2"
    stale_time = int(time.time()) - (6 * 3600 + 1)  # 6h + 1초 초과
    _make_global_pointer(tmp_path, global_sid, stale_time)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == "", f"stale → 빈 문자열 기대, got {result!r}"


# ── TC5: 자기참조 회피 ────────────────────────────────────────────────────────

def test_self_reference_avoidance(monkeypatch, tmp_path):
    """TC5: project_root 가 ~/.claude → 글로벌 폴백 헬퍼가 skip → 빈 문자열.

    _read_global_session_pointer_safely 를 직접 호출해 자기참조 가드를 검증.
    (current_session_id 경로에서는 _find_project_root 가 home 폴백으로 2단계가
    이미 처리하므로, 헬퍼 레벨 가드를 직접 검증한다.)
    """
    global_sid = "global-session-self-ref1"
    _make_global_pointer(tmp_path, global_sid, int(time.time()))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # project_root = ~/.claude (자기참조) — 헬퍼 직접 호출
    self_ref_root = tmp_path / ".claude"
    self_ref_root.mkdir(exist_ok=True)

    result = ss._read_global_session_pointer_safely(self_ref_root)
    assert result == "", f"자기참조 → 빈 문자열 기대, got {result!r}"


# ── 보너스: 형식 invalid pointer ─────────────────────────────────────────────

def test_global_fallback_invalid_format_rejected(monkeypatch, tmp_path):
    """보너스: 글로벌 pointer 형식 invalid (path traversal 시도) → 빈 문자열."""
    home_state = tmp_path / ".claude" / "harness-state"
    home_state.mkdir(parents=True, exist_ok=True)
    # path traversal 시도
    (home_state / ".session-id").write_text("../../etc/passwd", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == "", f"invalid 형식 → 빈 문자열 기대, got {result!r}"


# ── 추가: 글로벌 pointer 부재 → 빈 문자열 (회귀 0) ─────────────────────────

def test_no_pointer_returns_empty(monkeypatch, tmp_path):
    """REQ-005: 글로벌 pointer 부재 시 빈 문자열 반환 (v1 동작 유지)."""
    # ~/.claude/harness-state/.session-id 없음
    home_state = tmp_path / ".claude" / "harness-state"
    home_state.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == "", f"pointer 부재 → 빈 문자열 기대, got {result!r}"


# ── 추가: _meta.sessionId 불일치 → 거부 ────────────────────────────────────

def test_global_fallback_meta_mismatch_rejected(monkeypatch, tmp_path):
    """REQ-003: _meta.sessionId != sid (다른 세션 leftover) → 빈 문자열."""
    sid = "global-session-abc00001"
    other_sid = "other-session-xyz99999"
    home_state = tmp_path / ".claude" / "harness-state"
    sessions_dir = home_state / ".sessions" / sid
    sessions_dir.mkdir(parents=True, exist_ok=True)
    (home_state / ".session-id").write_text(sid, encoding="utf-8")
    # live.json 의 _meta.sessionId 를 다른 sid 로 설정 (불일치)
    live = sessions_dir / "live.json"
    live.write_text(json.dumps({
        "session_id": sid,
        "_meta": {
            "written_at": int(time.time()),
            "mode": "session",
            "sessionId": other_sid,  # 의도적 불일치
        },
    }), encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == "", f"meta mismatch → 빈 문자열 기대, got {result!r}"


# ── 추가: live.json 부재 → 거부 ─────────────────────────────────────────────

def test_global_fallback_no_live_json_rejected(monkeypatch, tmp_path):
    """글로벌 pointer 존재하지만 live.json 없음 → 빈 문자열."""
    sid = "global-session-nolive01"
    home_state = tmp_path / ".claude" / "harness-state"
    # .session-id 만 작성, sessions 디렉토리는 미생성
    home_state.mkdir(parents=True, exist_ok=True)
    (home_state / ".session-id").write_text(sid, encoding="utf-8")
    # sid 형식은 valid 지만 live.json 없음
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    project_root = _make_project_root_without_pointer(tmp_path)

    result = ss.current_session_id(project_root)
    assert result == "", f"live.json 없음 → 빈 문자열 기대, got {result!r}"
