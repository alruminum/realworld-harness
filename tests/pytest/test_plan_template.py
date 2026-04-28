"""test_plan_template.py — light-plan 산출물 형식 회귀 (Issue #31).

[14.2] hole (#26) retroactive 사례:
  light-plan 작성자가 수정 함수의 reuse 분기를 enumerate 안 함 → 회귀 테스트 누락 → 머지 후 발현.
본 테스트는 "분기 enumeration 섹션이 없거나 비어있는" light-plan 을
정규식 검사로 거부한다. LLM 의 enumeration 의미적 정확성은 비목표 (사람 영역).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ── 검증 정규식 ──────────────────────────────────────────────────────────
# §"분기 enumeration" 섹션이 존재해야 한다.
SECTION_HEADER = re.compile(r"^##\s+분기\s*enumeration\s*$", re.MULTILINE)

# 헤더 다음~다음 §## 헤더 직전까지를 섹션 본문으로 추출.
SECTION_BODY = re.compile(
    r"^##\s+분기\s*enumeration\s*$(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

# 표의 데이터 행 ("|" 로 시작 + 셀 4개 이상, 헤더/구분자 제외).
TABLE_DATA_ROW = re.compile(
    r"^\|(?!\s*[-:|\s]+\|\s*$)(?!\s*분기\b).+\|.+\|.+\|.+\|\s*$",
    re.MULTILINE,
)

# single-branch 라벨 (단일 분기 함수 명시 escape hatch).
SINGLE_BRANCH_LABEL = re.compile(r"single-branch", re.IGNORECASE)


def _has_branch_enumeration(text: str) -> tuple[bool, str]:
    """광범위 검사. (passed, reason) 반환."""
    if not SECTION_HEADER.search(text):
        return False, "§분기 enumeration 섹션 누락"

    m = SECTION_BODY.search(text)
    if not m:
        return False, "§분기 enumeration 섹션 본문 추출 실패"

    body = m.group(1)
    rows = TABLE_DATA_ROW.findall(body)
    has_single_label = bool(SINGLE_BRANCH_LABEL.search(body))

    if not rows and not has_single_label:
        return False, "분기 enumeration 표가 비어있고 single-branch 라벨도 없음"
    if len(rows) < 2 and not has_single_label:
        return False, f"분기 행 {len(rows)}개 — 최소 2행 또는 single-branch 라벨 필요"
    return True, "OK"


# ── 합성 픽스처 — light-plan 산출물 형식 검사 ─────────────────────────────

VALID_TWO_BRANCH = """
# Sample

## 변경 대상
- 파일: `foo.py`

## 분기 enumeration

| 분기 / 호출 사이트 | 위치 | fix 적용 여부 | 회귀 가능성 |
|---|---|---|---|
| fresh path | `foo.py:10` | YES | 본 fix 1차 대상 |
| reuse path | `foo.py:20` | YES | [14.2] hole 메우기 |

## 수정 내용
"""

VALID_SINGLE_BRANCH = """
## 분기 enumeration

| 분기 | 위치 | fix 적용 | 사유 |
|---|---|---|---|
| 단일 진입점 (single-branch) | `bar.py:5` | YES | 단일 분기 함수 — enumeration 불필요 |

## 수정 내용
"""

INVALID_NO_SECTION = """
# Sample

## 변경 대상
## 수정 내용
"""

INVALID_EMPTY_SECTION = """
## 분기 enumeration

(아직 작성 안 함)

## 수정 내용
"""

INVALID_SINGLE_ROW_NO_LABEL = """
## 분기 enumeration

| 분기 | 위치 | fix 적용 | 사유 |
|---|---|---|---|
| only path | `x.py:1` | YES | 본 fix |

## 수정 내용
"""


class TestBranchEnumerationRegex:
    """light-plan 산출물 형식 회귀 — 정규식만 (LLM 의미 검증은 비목표)."""

    def test_two_branch_table_passes(self):
        ok, reason = _has_branch_enumeration(VALID_TWO_BRANCH)
        assert ok, reason

    def test_single_branch_label_passes(self):
        ok, reason = _has_branch_enumeration(VALID_SINGLE_BRANCH)
        assert ok, reason

    def test_missing_section_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_NO_SECTION)
        assert not ok
        assert "누락" in reason

    def test_empty_section_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_EMPTY_SECTION)
        assert not ok
        assert "비어있" in reason or "행" in reason

    def test_single_row_without_label_fails(self):
        ok, reason = _has_branch_enumeration(INVALID_SINGLE_ROW_NO_LABEL)
        assert not ok
        assert "1개" in reason or "최소" in reason


class TestActualLightPlanArtifacts:
    """현재 repo 의 light-plan 산출물이 형식 게이트를 통과하는지 회귀 검사.

    docs/impl/*.md 중 frontmatter 에 `depth: simple` 인 파일만 대상.
    (module-plan / deep depth 는 §"핵심 로직" 의사코드가 등가 역할 — 본 게이트 면제)
    """

    def _light_plan_files(self) -> list[Path]:
        out = []
        for p in (ROOT / "docs" / "impl").glob("*.md"):
            text = p.read_text(encoding="utf-8")
            if re.search(r"^depth:\s*simple\s*$", text, re.MULTILINE):
                out.append(p)
        return out

    def test_self_apply_branch_enumeration(self):
        """이 impl 자체 (#31) 가 자기 게이트를 통과해야 한다 — meta-recursive 검증."""
        target = ROOT / "docs" / "impl" / "31-light-plan-branch-enumeration.md"
        if not target.exists():
            pytest.skip("self impl not yet committed")
        ok, reason = _has_branch_enumeration(target.read_text(encoding="utf-8"))
        assert ok, f"self-apply violation: {reason}"
