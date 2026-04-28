"""test_plan_reviewer_scope.py — plan-reviewer 검토 범위 경계 보호.

jajang #133 reviewer 가 PRD 외 파일 (docs/impl/06, docs/impl/07, batch.md,
stories.md, audio-engine.md) 을 다 뒤져 "impl 계획 부재" 로 잘못된 CHANGES_REQUESTED
를 낸 사고 후 보강.

architect MODULE_PLAN 단계에서 만들어질 산출물을 PRD 시점에 요구하면 plan 루프가
무한 재시도에 빠진다. 본 회귀 테스트는 scope 섹션이 누락/약화되지 않도록 보호.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENT_FILE = ROOT / "agents" / "plan-reviewer.md"


@pytest.fixture(scope="module")
def agent_text() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ── REQ-001: scope 경계 섹션 존재 ────────────────────────────────

class TestREQ001ScopeSectionExists:
    def test_scope_header_at_top(self, agent_text: str):
        # frontmatter 다음의 첫 ## 섹션이 scope 섹션이어야 함
        body = agent_text.split("---\n", 2)[-1]
        first_h2 = body.lstrip().split("\n", 1)[0]
        assert "검토 범위 경계" in first_h2, f"첫 섹션에 scope 헤더 부재: {first_h2!r}"

    def test_scope_priority_marked(self, agent_text: str):
        # 🔴 + "최우선" 마킹으로 우선순위 강조
        assert "🔴" in agent_text
        assert "최우선" in agent_text


# ── REQ-002: 금지 파일 목록 명시 ────────────────────────────────

class TestREQ002ForbiddenFilesEnumerated:
    """jajang #133 reviewer 가 헤맨 실 파일 목록 박제."""

    @pytest.mark.parametrize("forbidden_path", [
        "docs/impl/",
        "docs/milestones/",
        "stories.md",
        "batch.md",
        "audio-engine.md",
        "voice-pipeline.md",
        "apps/",
        "src/",
        "trd.md",
    ])
    def test_forbidden_path_listed(self, agent_text: str, forbidden_path: str):
        assert forbidden_path in agent_text, f"금지 경로 {forbidden_path} 미명시"


# ── REQ-003: 허용 파일 명시 ─────────────────────────────────────

class TestREQ003AllowedFilesExplicit:
    @pytest.mark.parametrize("allowed_path", [
        "prd.md",
        "prd-draft.md",
        "docs/sdk.md",
        "docs/reference.md",
        "docs/architecture.md",
    ])
    def test_allowed_path_listed(self, agent_text: str, allowed_path: str):
        assert allowed_path in agent_text


# ── REQ-004: scope drift 차단 자기규율 ──────────────────────────

class TestREQ004ScopeDriftSelfDiscipline:
    def test_jajang_133_lesson_present(self, agent_text: str):
        # 이슈 본문 파일명 환각 차단 메시지
        assert "이슈 본문에 파일명" in agent_text or "파일명" in agent_text
        assert "그 파일을 열어보지 않습니다" in agent_text or "열어보지 않습니다" in agent_text

    def test_tool_call_budget_documented(self, agent_text: str):
        # Glob/Grep 호출 횟수 제한 가이드
        assert "Glob" in agent_text and "Grep" in agent_text
        assert "5회" in agent_text or "5번" in agent_text or "초과" in agent_text


# ── REQ-005: "다음 단계 책임" 명시 ──────────────────────────────

class TestREQ005NextStageResponsibility:
    def test_architect_module_plan_responsibility_stated(self, agent_text: str):
        assert "architect" in agent_text.lower()
        assert "MODULE_PLAN" in agent_text or "module_plan" in agent_text.lower() or "다음 단계" in agent_text
