"""conftest.py — pytest fixtures for guard tests.

공유 fixture:
- tmp_state_dir: 임시 harness-state 디렉토리
- tmp_config_dir: 임시 .claude/harness.config.json 포함 프로젝트 루트
- v2_env_all_on: HARNESS_GUARD_V2_* 전체 활성 (monkeypatch)
- v2_env_all_off: HARNESS_GUARD_V2_* 전체 비활성 (monkeypatch)
- live_json_setup: live.json 초기화 + 정리

환경 격리: 모든 HARNESS_GUARD_V2_* env var 는 각 테스트 후 자동 복원.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# 프로젝트 루트 (RWHarness/) — sys.path 에 없으면 추가
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HOOKS_DIR = ROOT / "hooks"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# harness_common 의 per-process 캐시를 테스트 간 초기화하기 위한 헬퍼
def _reset_engineer_scope_cache():
    """harness_common._ENGINEER_SCOPE_CACHE 를 None 으로 리셋 (테스트 격리)."""
    try:
        import harness_common as _hc
        _hc._ENGINEER_SCOPE_CACHE = None
    except ImportError:
        pass


# ── V2 flag 환경변수 목록 ────────────────────────────────────────────────────
V2_FLAGS = [
    "HARNESS_GUARD_V2_AGENT_BOUNDARY",
    "HARNESS_GUARD_V2_COMMIT_GATE",
    "HARNESS_GUARD_V2_AGENT_GATE",
    "HARNESS_GUARD_V2_SKILL_GATE",
    "HARNESS_GUARD_V2_SKILL_STOP_PROTECT",
    "HARNESS_GUARD_V2_ISSUE_GATE",
    "HARNESS_GUARD_V2_PLUGIN_WRITE_GUARD",
    "HARNESS_GUARD_V2_RALPH_FALLBACK",
    "HARNESS_GUARD_V2_ALL",
    "HARNESS_GUARD_V2_FLAG_TTL_SEC",
]


@pytest.fixture(autouse=True)
def _isolate_v2_env(monkeypatch):
    """모든 테스트에서 HARNESS_GUARD_V2_* env var 를 자동 격리.
    테스트 시작 시 전부 제거 → 개별 테스트에서 명시적 설정.
    """
    for flag in V2_FLAGS:
        monkeypatch.delenv(flag, raising=False)
    _reset_engineer_scope_cache()
    yield
    _reset_engineer_scope_cache()


@pytest.fixture(autouse=True)
def _isolate_harness_env(monkeypatch):
    """HARNESS_* env var 격리 (HARNESS_SESSION_ID, HARNESS_PREFIX 등)."""
    for key in list(os.environ.keys()):
        if key.startswith("HARNESS_") and key not in V2_FLAGS:
            monkeypatch.delenv(key, raising=False)
    monkeypatch.delenv("RALPH_SESSION_INITIATOR", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    yield


@pytest.fixture()
def tmp_state_dir(tmp_path):
    """임시 harness-state 디렉토리 (세션 구조 포함)."""
    state = tmp_path / ".claude" / "harness-state"
    logs = state / ".logs"
    sessions = state / ".sessions"
    logs.mkdir(parents=True)
    sessions.mkdir(parents=True)
    return state


@pytest.fixture()
def tmp_config_dir(tmp_path):
    """임시 프로젝트 루트 + .claude/harness.config.json 기본값."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    config = claude_dir / "harness.config.json"
    config.write_text(json.dumps({"prefix": "test"}), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def tmp_config_with_scope(tmp_path):
    """jajang 모노레포 스타일 engineer_scope 포함 config."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    config = claude_dir / "harness.config.json"
    config.write_text(json.dumps({
        "prefix": "jajang",
        "engineer_scope": [
            r"(^|/)src/",
            r"(^|/)apps/[^/]+/src/",
            r"(^|/)apps/[^/]+/app/",
            r"(^|/)services/[^/]+/src/",
        ],
    }), encoding="utf-8")
    return tmp_path


@pytest.fixture()
def v2_all_on(monkeypatch):
    """HARNESS_GUARD_V2_ALL=1 + 개별 flag 전체 활성."""
    for flag in V2_FLAGS:
        if flag != "HARNESS_GUARD_V2_FLAG_TTL_SEC":
            monkeypatch.setenv(flag, "1")
    _reset_engineer_scope_cache()
    yield
    _reset_engineer_scope_cache()


@pytest.fixture()
def v2_all_off(monkeypatch):
    """모든 HARNESS_GUARD_V2_* 를 명시적으로 off."""
    for flag in V2_FLAGS:
        monkeypatch.delenv(flag, raising=False)
    _reset_engineer_scope_cache()
    yield
    _reset_engineer_scope_cache()


@pytest.fixture()
def live_json_session(tmp_state_dir):
    """임시 세션 live.json 반환. (sid, live_path, state_dir) 튜플."""
    sid = "test-session-0001-abcd-efgh"
    session_dir = tmp_state_dir / ".sessions" / sid
    session_dir.mkdir(parents=True)
    live_path = session_dir / "live.json"
    live_path.write_text(json.dumps({}), encoding="utf-8")
    return sid, live_path, tmp_state_dir


@pytest.fixture()
def jajang_fixture_path():
    """jajang_monorepo fixture 루트 경로."""
    return ROOT / "tests" / "pytest" / "fixtures" / "jajang_monorepo"
