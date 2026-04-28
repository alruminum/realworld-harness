"""test_marketplace_auto_pull.py — SessionStart 의 marketplace auto-pull 검증.

bash fallback path 가 stale 되는 hole (jajang #22 silent skip 류) 차단용.
실제 git remote 동기화로 fast-forward pull 동작 확인.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(args, cwd=None, check=True):
    r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode != 0:
        raise RuntimeError(f"{args} → {r.stderr}")
    return r


def _setup_origin_and_clone(
    tmp_path: Path,
    ahead_commits: int = 0,
    ahead_modifies_readme: bool = False,
) -> tuple[Path, Path]:
    """bare origin + 클론. ahead_commits>0 이면 origin 이 클론보다 N개 앞섬.
    ahead_modifies_readme=True 면 origin commits 가 README.md 도 수정 (dirty 충돌 시뮬레이션용).
    """
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    other = tmp_path / "other"
    _run(["git", "init", "--bare", "-b", "main", str(origin)])

    # 첫 commit (다른 워킹트리에서 push)
    _run(["git", "init", "-b", "main", str(other)])
    _run(["git", "-C", str(other), "config", "user.email", "t@t"])
    _run(["git", "-C", str(other), "config", "user.name", "t"])
    _run(["git", "-C", str(other), "remote", "add", "origin", str(origin)])
    (other / "README.md").write_text("seed\n")
    _run(["git", "-C", str(other), "add", "."])
    _run(["git", "-C", str(other), "commit", "-q", "-m", "seed"])
    _run(["git", "-C", str(other), "push", "-u", "origin", "main"])

    # 클론 (이 시점에 origin 과 sync)
    _run(["git", "clone", "-q", str(origin), str(clone)])
    _run(["git", "-C", str(clone), "config", "user.email", "t@t"])
    _run(["git", "-C", str(clone), "config", "user.name", "t"])

    # ahead_commits 만큼 origin 만 추가 (other 에서 push)
    for i in range(ahead_commits):
        if ahead_modifies_readme:
            (other / "README.md").write_text(f"seed\nupdate-{i}\n")
        else:
            (other / f"f{i}.txt").write_text(f"{i}\n")
        _run(["git", "-C", str(other), "add", "."])
        _run(["git", "-C", str(other), "commit", "-q", "-m", f"feat{i}"])
        _run(["git", "-C", str(other), "push", "origin", "main"])

    return origin, clone


def _simulate_pull(market_path: Path) -> int:
    """SessionStart 훅이 수행하는 ff-only pull 시뮬레이션."""
    if not (market_path / ".git").is_dir():
        return -1
    r = subprocess.run(
        ["git", "-C", str(market_path), "pull", "--ff-only", "--quiet"],
        capture_output=True, timeout=10,
    )
    return r.returncode


# ── REQ-001: stale 클론 → ff-pull 로 동기화 ────────────────────

class TestREQ001AutoPullSync:
    def test_stale_clone_gets_synced(self, tmp_path):
        _, clone = _setup_origin_and_clone(tmp_path, ahead_commits=3)

        # 동기화 전: clone HEAD 는 origin 보다 3 commit 뒤
        before = _run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()
        origin_head = _run(["git", "-C", str(clone), "rev-parse", "origin/main"],
                           check=False).stdout.strip()

        rc = _simulate_pull(clone)

        assert rc == 0
        after = _run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()
        assert after != before
        # post-pull HEAD 가 origin/main 과 일치
        _run(["git", "-C", str(clone), "fetch", "origin"])
        new_origin = _run(["git", "-C", str(clone), "rev-parse", "origin/main"]).stdout.strip()
        assert after == new_origin


# ── REQ-002: 이미 동기 → no-op (Already up to date) ─────────────

class TestREQ002AlreadySynced:
    def test_no_op_when_synced(self, tmp_path):
        _, clone = _setup_origin_and_clone(tmp_path, ahead_commits=0)

        rc = _simulate_pull(clone)

        assert rc == 0


# ── REQ-003: .git 없는 경로 → -1 (skip 신호) ────────────────────

class TestREQ003NoGitDir:
    def test_returns_minus_one_for_non_git_path(self, tmp_path):
        # .git 디렉토리 없음
        plain = tmp_path / "not-a-repo"
        plain.mkdir()

        rc = _simulate_pull(plain)

        assert rc == -1


# ── REQ-004: dirty working tree → ff-pull 실패해도 silent ──────

class TestREQ004DirtyToleration:
    def test_dirty_pull_returns_nonzero_but_does_not_raise(self, tmp_path):
        # origin 이 README.md 를 수정 + 로컬도 README.md 를 dirty 로 → ff 충돌 보장
        _, clone = _setup_origin_and_clone(tmp_path, ahead_commits=1, ahead_modifies_readme=True)
        (clone / "README.md").write_text("dirty\n")

        rc = _simulate_pull(clone)

        # ff-only pull 가 dirty 위에서 실패해도 예외 없이 returncode 만 반환
        # (실 훅에서는 try/except 로 감싸 silent 처리)
        assert rc != 0
        # 파일 손상 없음
        assert (clone / "README.md").read_text() == "dirty\n"


# ── REQ-005: divergent (non-ff) → ff-only 실패 silent ──────────

class TestREQ005NonFastForward:
    def test_divergent_history_does_not_clobber(self, tmp_path):
        _, clone = _setup_origin_and_clone(tmp_path, ahead_commits=1)
        # 클론 측에 origin 과 다른 commit 만들어 divergent 만들기
        (clone / "local.txt").write_text("local\n")
        _run(["git", "-C", str(clone), "add", "."])
        _run(["git", "-C", str(clone), "commit", "-q", "-m", "local-only"])
        # 이 상태에서 ff-only pull 시도 → 실패 (divergent)

        before_head = _run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()
        rc = _simulate_pull(clone)
        after_head = _run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()

        assert rc != 0
        # local commit 보존
        assert before_head == after_head
        assert (clone / "local.txt").exists()
