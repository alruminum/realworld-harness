"""test_ux_architect_identity.py — ux-architect agent.md 정체성 선언 보호.

jajang #133 plan 루프 중 ux-architect 가 동일 self-recognition 실패
("메인 Claude 세션이라 서브에이전트로 진입하지 않습니다... /ux-sync 또는
명시적인 요청 주세요") 발생. product-planner #38 에 적용한 동일 패턴 적용 후
회귀 테스트.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENT_FILE = ROOT / "agents" / "ux-architect.md"


@pytest.fixture(scope="module")
def agent_text() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ── REQ-001: 정체성 선언 섹션 존재 ───────────────────────────────

class TestREQ001IdentitySectionExists:
    def test_identity_header_at_top(self, agent_text: str):
        body = agent_text.split("---\n", 2)[-1]
        first_h2 = body.lstrip().split("\n", 1)[0]
        assert "정체성" in first_h2, f"첫 섹션에 정체성 헤더 부재: {first_h2!r}"

    def test_explicit_self_assertion(self, agent_text: str):
        assert "당신이 ux-architect 에이전트입니다" in agent_text

    def test_main_claude_clarification(self, agent_text: str):
        assert "메인 Claude" in agent_text
        assert "당신을 호출" in agent_text


# ── REQ-002: 금지 패턴 명시 ──────────────────────────────────────

class TestREQ002ForbiddenPatterns:
    def test_lists_anti_patterns(self, agent_text: str):
        # jajang 실측 사례 박제
        patterns = [
            "메인 Claude 세션이라 서브에이전트로 진입",  # 실 케이스
            "ux-architect 에이전트로 위임",
            "/ux-sync 또는 명시적인 요청 주세요",
            "당신이 이미 ux-architect",
        ]
        missing = [p for p in patterns if p not in agent_text]
        assert not missing, f"금지 패턴 누락: {missing}"

    def test_marker_requirement_explicit(self, agent_text: str):
        assert "마커 없이 질문" in agent_text or "마커 없이 끝" in agent_text


# ── REQ-003: 모드 마커 인식 가이드 ───────────────────────────────

class TestREQ003ModeMarkerHandling:
    def test_three_modes_documented(self, agent_text: str):
        for mode in ("UX_FLOW", "UX_SYNC", "UX_REFINE"):
            assert f"@MODE:UX_ARCHITECT:{mode}" in agent_text, f"{mode} 모드 마커 누락"

    def test_mode_treated_as_task(self, agent_text: str):
        assert "당신이 지금 즉시 수행할" in agent_text or "당신이 지금" in agent_text


# ── REQ-004: 출력 마커 안내 보존 ────────────────────────────────

class TestREQ004OutputMarkers:
    def test_ux_flow_ready_marker_documented(self, agent_text: str):
        assert "UX_FLOW_READY" in agent_text

    def test_ux_refine_ready_marker_documented(self, agent_text: str):
        assert "UX_REFINE_READY" in agent_text

    def test_ux_flow_escalate_marker_documented(self, agent_text: str):
        assert "UX_FLOW_ESCALATE" in agent_text
