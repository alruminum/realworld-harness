"""test_worktree.py — WorktreeManager 회귀 테스트.

Issue #26: reuse 분기에서 untracked plan 파일이 복사되지 않던 hole.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.core import WorktreeManager  # noqa: E402


def _init_repo(repo: Path) -> None:
    """임시 git repo 초기화 + 더미 commit."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "README.md").write_text("seed\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "seed"], check=True)


def _write_untracked_plan(repo: Path, rel: str, content: str) -> Path:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


class TestREQ001ReusePlanCopy:
    """REQ-001: reuse worktree + main 의 untracked plan → 복사된다."""

    def test_reuse_copies_untracked_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)  # _git() 는 cwd 기반

        wm = WorktreeManager(repo, prefix="test")
        # 1차: fresh 생성
        wt1 = wm.create_or_reuse("test/issue-42", "42")
        assert wt1.exists()

        # main 에 untracked plan 추가 (commit 안 함)
        _write_untracked_plan(repo, "docs/impl/26-foo.md", "PLAN BODY\n")

        # 2차: 같은 이슈 재호출 → reuse 분기
        wt2 = wm.create_or_reuse("test/issue-42", "42")
        assert wt2 == wt1

        copied = wt2 / "docs/impl/26-foo.md"
        assert copied.exists(), "reuse 분기에서 untracked plan 이 복사되어야 함"
        assert copied.read_text() == "PLAN BODY\n"


class TestREQ002ReusePreserveExisting:
    """REQ-002: reuse worktree 에 이미 존재하는 동일 경로 파일은 보존."""

    def test_reuse_does_not_overwrite_existing_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        wm = WorktreeManager(repo, prefix="test")
        wt = wm.create_or_reuse("test/issue-42", "42")

        # main 과 worktree 양쪽에 같은 경로 파일을 다른 내용으로 작성
        _write_untracked_plan(repo, "docs/impl/26-foo.md", "MAIN VERSION\n")
        wt_plan = wt / "docs/impl/26-foo.md"
        wt_plan.parent.mkdir(parents=True, exist_ok=True)
        wt_plan.write_text("WORKTREE LOCAL EDIT\n")

        # reuse 호출
        wm.create_or_reuse("test/issue-42", "42")

        # worktree 본 보존되어야 함 (덮어쓰기 금지)
        assert wt_plan.read_text() == "WORKTREE LOCAL EDIT\n"


class TestREQ003FreshPathRegression:
    """REQ-003: [14.2] fresh 생성 path 동작 회귀 없음 — 신규 worktree 에 untracked plan 그대로 복사."""

    def test_fresh_create_still_copies_plan(self, tmp_path, monkeypatch):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        monkeypatch.chdir(repo)

        _write_untracked_plan(repo, "docs/bugfix/#42-bug.md", "BUG NOTE\n")

        wm = WorktreeManager(repo, prefix="test")
        wt = wm.create_or_reuse("test/issue-42", "42")

        assert (wt / "docs/bugfix/#42-bug.md").read_text() == "BUG NOTE\n"
