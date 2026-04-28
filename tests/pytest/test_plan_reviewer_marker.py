"""test_plan_reviewer_marker.py — plan-reviewer.md 마커 키워드 규칙 보호.

jajang #133 사고: plan-reviewer 가 bare `---MARKER:LGTM---` emit → executor
PLAN_REVIEW_PASS 정확 매칭 실패 → 자동 CHANGES_REQUESTED 처리.

agent.md 에 마커 키워드 절대 규칙 + 5개 금지 변형 박제. 본 회귀 테스트는
규칙이 누락/약화되지 않도록 보호.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENT_FILE = ROOT / "agents" / "plan-reviewer.md"


@pytest.fixture(scope="module")
def agent_text() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ── REQ-001: 마커 절대 규칙 섹션 존재 ───────────────────────────

class TestREQ001MarkerRuleSectionExists:
    def test_marker_rule_header_present(self, agent_text: str):
        assert "마커 키워드 절대 규칙" in agent_text

    def test_priority_marked(self, agent_text: str):
        # 🔴 + "절대" 마킹으로 우선순위 강조
        rule_idx = agent_text.find("마커 키워드 절대 규칙")
        assert rule_idx >= 0
        before = agent_text[max(0, rule_idx - 50):rule_idx]
        assert "🔴" in before


# ── REQ-002: 정식 마커 명시 ─────────────────────────────────────

class TestREQ002CanonicalMarkers:
    @pytest.mark.parametrize("canonical", [
        "PLAN_REVIEW_PASS",
        "PLAN_REVIEW_CHANGES_REQUESTED",
    ])
    def test_canonical_marker_documented(self, agent_text: str, canonical: str):
        assert f"---MARKER:{canonical}---" in agent_text


# ── REQ-003: 금지 변형 박제 (jajang #133 사고 사례) ─────────────

class TestREQ003ForbiddenMarkers:
    @pytest.mark.parametrize("forbidden", [
        "MARKER:LGTM",       # jajang #133 실 사고 — pr-reviewer 마커와 충돌
        "MARKER:APPROVE",    # 일반 alias — 다른 단계와 충돌 위험
        "MARKER:PASS",       # bare PASS — 다른 단계와 동일
    ])
    def test_forbidden_marker_listed(self, agent_text: str, forbidden: str):
        # 본문에 ❌ 표기 + 금지 변형 명시
        assert forbidden in agent_text or forbidden.replace("MARKER:", "") in agent_text


# ── REQ-004: 마커 알리아스 인프라 (defense in depth) ──────────────

class TestREQ004MarkerAliasInfrastructure:
    def test_plan_review_lgtm_alias_exists_in_core(self):
        from harness import core as _core
        assert "PLAN_REVIEW_LGTM" in _core.MARKER_ALIASES
        assert _core.MARKER_ALIASES["PLAN_REVIEW_LGTM"] == "PLAN_REVIEW_PASS"

    def test_plan_review_ok_alias(self):
        from harness import core as _core
        assert _core.MARKER_ALIASES.get("PLAN_REVIEW_OK") == "PLAN_REVIEW_PASS"

    def test_plan_review_reject_alias(self):
        from harness import core as _core
        assert _core.MARKER_ALIASES.get("PLAN_REVIEW_REJECT") == "PLAN_REVIEW_CHANGES_REQUESTED"

    def test_bare_lgtm_aliased_to_plan_review_pass(self):
        # jajang 2026-04-29 실측 — plan-reviewer 가 bare LGTM emit 사고 후 alias 추가.
        # parse_marker 1차(canonical) 가 alias 보다 우선이라 pr-reviewer 호출에선
        # 1차 매치, plan-reviewer 호출에선 alias 흡수 — 양쪽 안전.
        from harness import core as _core
        assert _core.MARKER_ALIASES.get("LGTM") == "PLAN_REVIEW_PASS"
