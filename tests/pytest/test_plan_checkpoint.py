"""test_plan_checkpoint.py — plan_loop.save_plan_checkpoint 회귀 테스트.

jajang #133 시나리오: product-planner PASS + plan-reviewer PASS 후 ux-architect
실패 → 옛 코드는 metadata 미저장 → 재실행 시 PRD 체크포인트 손실 → planner
처음부터 재실행. helper 추출 + plan-reviewer PASS 직후 호출 + ux 실패 분기에서도
부분 저장 보장.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.core import StateDir  # noqa: E402
from harness.plan_loop import save_plan_checkpoint  # noqa: E402


@pytest.fixture
def state_dir(tmp_path: Path) -> StateDir:
    sd_path = tmp_path / "state"
    sd_path.mkdir()
    sd = StateDir.__new__(StateDir)  # __init__ 우회 (project_root 의존성)
    sd.path = sd_path
    return sd


# ── REQ-001: partial checkpoint (prd_path 만) ─────────────────────

class TestREQ001PartialCheckpoint:
    def test_writes_prd_only_when_ux_flow_doc_empty(self, state_dir: StateDir, tmp_path: Path):
        ok = save_plan_checkpoint(state_dir, "jajang", "/p/prd.md", "133")
        assert ok is True
        meta_file = state_dir.path / "jajang_plan_metadata.json"
        assert meta_file.exists()
        meta = json.loads(meta_file.read_text())
        assert meta == {"prd_path": "/p/prd.md", "issue_num": "133"}
        assert "ux_flow_doc" not in meta

    def test_returns_false_when_prd_path_missing(self, state_dir: StateDir):
        ok = save_plan_checkpoint(state_dir, "jajang", "")
        assert ok is False
        # 파일 자체가 만들어지지 않아야 함
        assert not (state_dir.path / "jajang_plan_metadata.json").exists()


# ── REQ-002: full checkpoint (prd_path + ux_flow_doc) ─────────────

class TestREQ002FullCheckpoint:
    def test_writes_both_keys_when_ux_flow_doc_present(self, state_dir: StateDir):
        ok = save_plan_checkpoint(
            state_dir, "jajang", "/p/prd.md", "133", "/p/docs/ux-flow.md")
        assert ok is True
        meta = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())
        assert meta == {
            "prd_path": "/p/prd.md",
            "issue_num": "133",
            "ux_flow_doc": "/p/docs/ux-flow.md",
        }


# ── REQ-003: 부분→완전 업그레이드 시나리오 ──────────────────────

class TestREQ003UpgradeScenario:
    def test_partial_then_full_overwrites(self, state_dir: StateDir):
        # 1차: plan-reviewer PASS 직후 partial
        save_plan_checkpoint(state_dir, "jajang", "/p/prd.md", "133")
        meta1 = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())
        assert "ux_flow_doc" not in meta1

        # 2차: ux-validation 까지 통과 후 full
        save_plan_checkpoint(
            state_dir, "jajang", "/p/prd.md", "133", "/p/docs/ux-flow.md")
        meta2 = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())
        assert meta2["ux_flow_doc"] == "/p/docs/ux-flow.md"
        assert meta2["prd_path"] == "/p/prd.md"


# ── REQ-004: prefix 별 파일 분리 ──────────────────────────────────

class TestREQ004PrefixIsolation:
    def test_different_prefixes_write_separate_files(self, state_dir: StateDir):
        save_plan_checkpoint(state_dir, "jajang", "/p1/prd.md", "133")
        save_plan_checkpoint(state_dir, "memoryBattle", "/p2/prd.md", "44")

        ja_meta = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())
        mb_meta = json.loads((state_dir.path / "memoryBattle_plan_metadata.json").read_text())

        assert ja_meta["prd_path"] == "/p1/prd.md"
        assert mb_meta["prd_path"] == "/p2/prd.md"


# ── REQ-005: int issue_num 도 문제없이 직렬화 ─────────────────────

class TestREQ005IssueNumTypes:
    def test_int_issue_num_serializes(self, state_dir: StateDir):
        ok = save_plan_checkpoint(state_dir, "jajang", "/p/prd.md", 133)
        assert ok is True
        meta = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())
        assert meta["issue_num"] == 133


# ── REQ-006: jajang #133 회귀 시나리오 — full E2E semantic ──────

class TestREQ006Jajang133Regression:
    """plan-reviewer PASS 후 ux-architect 실패 → metadata 보존되어야 한다."""

    def test_partial_checkpoint_survives_ux_failure(self, state_dir: StateDir):
        # 1단계: plan-reviewer PASS 직후 — partial 저장
        ok1 = save_plan_checkpoint(state_dir, "jajang", "/proj/prd.md", "133")
        assert ok1 is True

        # 2단계: ux-architect 실패하면 *추가 저장 없음*. 기존 파일 보존.
        # (재호출 없이 시뮬레이션)
        meta = json.loads((state_dir.path / "jajang_plan_metadata.json").read_text())

        # 재실행 시 plan_loop 이 이 metadata 를 읽어 prd_path 발견 → planner 스킵
        assert meta.get("prd_path") == "/proj/prd.md"
        # ux_flow_doc 은 아직 없으므로 ux-architect 부터 재시도 가능
        assert "ux_flow_doc" not in meta
