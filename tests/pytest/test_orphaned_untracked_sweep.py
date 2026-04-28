"""test_orphaned_untracked_sweep.py — Issue #35 회귀 테스트.

architect/qa 가 main repo 에 떨군 untracked plan 파일이, worktree PR 머지 후
origin/<default> 의 tracked 사본과 path 충돌해 `git pull` 실패하는 시나리오 fix.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "hooks") not in sys.path:
    sys.path.insert(0, str(ROOT / "hooks"))

import worktree_sweep as wts  # noqa: E402


def _run(args, cwd=None, check=True):
    r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode != 0:
        raise RuntimeError(f"{args} → {r.stderr}")
    return r


def _setup_repo_with_origin_ahead(
    tmp_path: Path,
    new_file: str = "docs/bugfix/test.md",
    content: str = "plan content\n",
) -> Path:
    """origin 에 new_file 추가된 상태 + main repo 에 같은 path 의 untracked 사본.

    SessionStart 훅이 fetch 후 sweep 하는 시나리오를 재현 (HEAD 는 아직 untracked
    추가 전 상태, origin/main 은 tracked 사본 보유). main repo path 반환.
    """
    origin = tmp_path / "origin.git"
    main = tmp_path / "main"
    _run(["git", "init", "--bare", "-b", "main", str(origin)])
    _run(["git", "init", "-b", "main", str(main)])
    _run(["git", "-C", str(main), "config", "user.email", "t@t"])
    _run(["git", "-C", str(main), "config", "user.name", "t"])
    _run(["git", "-C", str(main), "remote", "add", "origin", str(origin)])
    (main / "README.md").write_text("seed\n")
    _run(["git", "-C", str(main), "add", "."])
    _run(["git", "-C", str(main), "commit", "-q", "-m", "seed"])
    _run(["git", "-C", str(main), "push", "-u", "origin", "main"])

    # 다른 워킹디렉토리에서 origin 에 new_file 추가 (worktree PR 머지 시뮬레이션)
    other = tmp_path / "other"
    _run(["git", "clone", "-q", str(origin), str(other)])
    _run(["git", "-C", str(other), "config", "user.email", "t@t"])
    _run(["git", "-C", str(other), "config", "user.name", "t"])
    p = other / new_file
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    _run(["git", "-C", str(other), "add", "."])
    _run(["git", "-C", str(other), "commit", "-q", "-m", "feat: add plan"])
    _run(["git", "-C", str(other), "push", "origin", "main"])

    # main repo 에는 같은 path 의 untracked 사본 (architect 가 만든 것 시뮬)
    p_main = main / new_file
    p_main.parent.mkdir(parents=True, exist_ok=True)
    p_main.write_text(content)

    return main


# ── REQ-001: untracked + origin 동일 content → 자동 삭제 ─────────

class TestREQ001AutoDelete:
    def test_identical_content_removed(self, tmp_path):
        target = "docs/bugfix/#127.md"
        main = _setup_repo_with_origin_ahead(tmp_path, target, "abc\n")

        result = wts.sweep_orphaned_untracked(cwd=str(main))

        assert target in result["removed"]
        assert not (main / target).exists()
        # pull 가능 상태 검증
        r = _run(["git", "-C", str(main), "pull", "--ff-only"], check=False)
        assert r.returncode == 0


# ── REQ-002: untracked + content 다름 → 경고만 ──────────────────

class TestREQ002DifferentContentWarn:
    def test_different_content_kept_with_warning(self, tmp_path):
        target = "docs/bugfix/#127.md"
        main = _setup_repo_with_origin_ahead(tmp_path, target, "origin\n")
        # main repo 에 다른 내용으로 덮어쓰기
        (main / target).write_text("local mods\n")

        result = wts.sweep_orphaned_untracked(cwd=str(main))

        assert (main / target).exists()
        assert result["removed"] == []
        assert any(target == w["path"] and "differs" in w["reason"]
                   for w in result["warned"])


# ── REQ-003: untracked but path NOT in origin → no-op ────────────

class TestREQ003UnrelatedUntracked:
    def test_unrelated_untracked_left_alone(self, tmp_path):
        main = _setup_repo_with_origin_ahead(tmp_path, "docs/bugfix/inOrigin.md", "x\n")
        # 별개 untracked (origin 에 없음)
        unrel = main / "docs" / "bugfix" / "purely-local.md"
        unrel.write_text("local only\n")

        result = wts.sweep_orphaned_untracked(cwd=str(main))

        # inOrigin.md 는 정리되어도 purely-local.md 는 보존
        assert unrel.exists()
        assert "docs/bugfix/purely-local.md" not in result["removed"]
        assert all(w["path"] != "docs/bugfix/purely-local.md"
                   for w in result["warned"])


# ── REQ-004: idempotent — 두 번째 호출은 no-op ──────────────────

class TestREQ004Idempotent:
    def test_second_call_noop(self, tmp_path):
        target = "docs/bugfix/x.md"
        main = _setup_repo_with_origin_ahead(tmp_path, target, "x\n")

        wts.sweep_orphaned_untracked(cwd=str(main))
        result2 = wts.sweep_orphaned_untracked(cwd=str(main), fetch=False)

        assert result2["removed"] == []
        assert result2["warned"] == []


# ── REQ-005: origin 없음 → silent skip ──────────────────────────

class TestREQ005NoOrigin:
    def test_no_origin_skips_silently(self, tmp_path):
        main = tmp_path / "main"
        _run(["git", "init", "-b", "main", str(main)])
        _run(["git", "-C", str(main), "config", "user.email", "t@t"])
        _run(["git", "-C", str(main), "config", "user.name", "t"])
        (main / "a.md").write_text("seed\n")
        _run(["git", "-C", str(main), "add", "."])
        _run(["git", "-C", str(main), "commit", "-q", "-m", "seed"])
        # untracked 파일
        (main / "untracked.md").write_text("x\n")

        result = wts.sweep_orphaned_untracked(cwd=str(main))

        assert result["removed"] == []
        assert result["warned"] == []
        assert (main / "untracked.md").exists()


# ── REQ-006: format_orphaned_report 포맷 ─────────────────────────

class TestREQ006Report:
    def test_empty(self):
        assert wts.format_orphaned_report({"removed": [], "warned": []}) == ""

    def test_removed(self):
        msg = wts.format_orphaned_report({"removed": ["a", "b"], "warned": []})
        assert "removed 2" in msg

    def test_warned(self):
        msg = wts.format_orphaned_report({
            "removed": [],
            "warned": [{"path": "a", "reason": "x"}],
        })
        assert "1 kept" in msg
