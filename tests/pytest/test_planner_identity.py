"""test_planner_identity.py — product-planner agent.md 정체성 선언 보호.

jajang 에서 5회 연속 self-recognition 실패 (planner 가 자기를 메인 Claude 로
착각하고 product-planner 에게 위임 권고) 사고 후 보강된 identity 섹션이
누락되거나 약화되지 않도록 회귀 테스트.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENT_FILE = ROOT / "agents" / "product-planner.md"


@pytest.fixture(scope="module")
def agent_text() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ── REQ-001: 정체성 선언 섹션 존재 ───────────────────────────────

class TestREQ001IdentitySectionExists:
    def test_identity_header_at_top(self, agent_text: str):
        # frontmatter 다음의 첫 ## 섹션이 정체성 섹션이어야 함
        body = agent_text.split("---\n", 2)[-1]  # frontmatter 분리
        first_h2 = body.lstrip().split("\n", 1)[0]
        assert "정체성" in first_h2, f"첫 섹션에 정체성 헤더 부재: {first_h2!r}"

    def test_explicit_self_assertion(self, agent_text: str):
        assert "당신이 product-planner 에이전트입니다" in agent_text

    def test_main_claude_clarification(self, agent_text: str):
        # "메인 Claude 는 당신을 호출한 상위 오케스트레이터" 류 문구
        assert "메인 Claude" in agent_text
        assert "당신을 호출" in agent_text


# ── REQ-002: 금지 패턴 명시 ──────────────────────────────────────

class TestREQ002ForbiddenPatterns:
    def test_lists_anti_patterns(self, agent_text: str):
        # 5개 사고 패턴이 모두 명시되어야 미래 회귀 시 비교 가능
        patterns = [
            "product-planner 에이전트로 전달되어야",  # case 5
            "에이전트로 위임",                       # case 5/4
            "이대로 plan 루프 시작",                  # case 4
            "product-planner 를 직접 호출",          # case 5
        ]
        missing = [p for p in patterns if p not in agent_text]
        assert not missing, f"금지 패턴 누락: {missing}"

    def test_marker_requirement_explicit(self, agent_text: str):
        # 마커 없이 끝내지 말라는 명시
        assert "마커 없이 질문" in agent_text or "마커 없이 끝" in agent_text


# ── REQ-003: 모드 마커 인식 가이드 ───────────────────────────────

class TestREQ003ModeMarkerHandling:
    def test_mode_prompt_treated_as_task(self, agent_text: str):
        assert "@MODE:PLANNER" in agent_text
        # "그것이 당신이 지금 즉시 수행할 작업" 류 문구
        assert "당신이 지금 즉시 수행할" in agent_text or "당신이 지금" in agent_text


# ── REQ-004: 출력 마커 안내 보존 ────────────────────────────────

class TestREQ004OutputMarkers:
    def test_product_plan_ready_marker_documented(self, agent_text: str):
        assert "PRODUCT_PLAN_READY" in agent_text

    def test_clarity_insufficient_marker_documented(self, agent_text: str):
        assert "CLARITY_INSUFFICIENT" in agent_text
