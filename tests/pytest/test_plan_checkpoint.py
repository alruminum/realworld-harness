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
from harness.plan_loop import (  # noqa: E402
    compute_file_hash,
    load_plan_checkpoint,
    save_plan_checkpoint,
)


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


# ── REQ-007: hash 계산 helper ──────────────────────────────────────

class TestREQ007FileHash:
    def test_existing_file_returns_sha256(self, tmp_path: Path):
        f = tmp_path / "x.md"
        f.write_text("hello\n")
        h = compute_file_hash(f)
        # sha256("hello\n") = 5891b5b...
        assert len(h) == 64
        assert h == "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"

    def test_missing_file_returns_empty(self, tmp_path: Path):
        assert compute_file_hash(tmp_path / "nope.md") == ""

    def test_content_changes_change_hash(self, tmp_path: Path):
        f = tmp_path / "x.md"
        f.write_text("v1")
        h1 = compute_file_hash(f)
        f.write_text("v2")
        h2 = compute_file_hash(f)
        assert h1 != h2
        assert len(h1) == 64 and len(h2) == 64


# ── REQ-008: hash 기반 무효화 — plan_review_passed_for ──────────────

class TestREQ008PlanReviewHashCheckpoint:
    def test_save_then_load_preserves_hash(self, state_dir: StateDir, tmp_path: Path):
        prd = tmp_path / "prd.md"
        prd.write_text("v1")
        prd_hash = compute_file_hash(prd)

        save_plan_checkpoint(
            state_dir, "jajang", str(prd), "133",
            plan_review_passed_for=prd_hash,
        )

        meta = load_plan_checkpoint(state_dir, "jajang")
        assert meta["plan_review_passed_for"] == prd_hash
        assert meta["prd_hash"] == prd_hash  # 자동 기록도 됨

    def test_prd_change_invalidates_match(self, state_dir: StateDir, tmp_path: Path):
        prd = tmp_path / "prd.md"
        prd.write_text("v1")
        h1 = compute_file_hash(prd)
        save_plan_checkpoint(state_dir, "jajang", str(prd), "133",
                             plan_review_passed_for=h1)

        # PRD 수정
        prd.write_text("v2 — 큰 변경")
        h2 = compute_file_hash(prd)
        assert h1 != h2

        # save 다시 호출 (다음 실행 진입 시)
        save_plan_checkpoint(state_dir, "jajang", str(prd), "133")
        meta = load_plan_checkpoint(state_dir, "jajang")

        # plan_review_passed_for 는 이전 값 보존 (merge), prd_hash 는 갱신
        assert meta["plan_review_passed_for"] == h1  # 이전 PASS hash
        assert meta["prd_hash"] == h2  # 현재 PRD hash
        # plan_loop 이 비교 시 불일치 → reviewer 재실행


# ── REQ-009: hash 기반 무효화 — ux_validation_passed_for ────────────

class TestREQ009UxValidationHashCheckpoint:
    def test_save_then_load_preserves_ux_hash(self, state_dir: StateDir, tmp_path: Path):
        prd = tmp_path / "prd.md"
        prd.write_text("prd")
        ux = tmp_path / "ux.md"
        ux.write_text("ux v1")
        ux_hash = compute_file_hash(ux)

        save_plan_checkpoint(
            state_dir, "jajang", str(prd), "133", str(ux),
            plan_review_passed_for=compute_file_hash(prd),
            ux_validation_passed_for=ux_hash,
        )
        meta = load_plan_checkpoint(state_dir, "jajang")
        assert meta["ux_validation_passed_for"] == ux_hash
        assert meta["ux_flow_hash"] == ux_hash


# ── REQ-010: merge=True default 보존 ───────────────────────────────

class TestREQ010MergeBehavior:
    def test_merge_preserves_unrelated_keys(self, state_dir: StateDir, tmp_path: Path):
        prd = tmp_path / "prd.md"
        prd.write_text("p")
        h = compute_file_hash(prd)

        # 1차 — plan_review_passed_for 기록
        save_plan_checkpoint(state_dir, "jajang", str(prd), "133",
                             plan_review_passed_for=h)
        # 2차 — issue_num 만 갱신 (다른 키 명시 X)
        save_plan_checkpoint(state_dir, "jajang", str(prd), "133-v2")

        meta = load_plan_checkpoint(state_dir, "jajang")
        # plan_review_passed_for 보존, issue_num 갱신
        assert meta["plan_review_passed_for"] == h
        assert meta["issue_num"] == "133-v2"
