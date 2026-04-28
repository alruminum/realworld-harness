"""test_worktree_sweep.py — Issue #36 회귀 테스트.

stale worktree 자동 정리 로직 검증. 임시 git repo + 실제 git worktree 명령
(test_worktree.py 컨벤션과 동일).
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
        raise RuntimeError(f"cmd {args} failed: {r.stderr}")
    return r


def _init_origin_and_clone(tmp_path: Path) -> tuple[Path, Path]:
    """bare origin + main repo clone. 반환 (origin, main)."""
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
    return origin, main


def _create_branch_and_worktree(main: Path, branch: str) -> Path:
    """branch 생성 + .worktrees/ 아래 worktree add. 반환: worktree path."""
    wt_dir = main / ".worktrees" / "test"
    wt_dir.mkdir(parents=True, exist_ok=True)
    wt_path = wt_dir / branch.replace("/", "-")
    _run(["git", "-C", str(main), "worktree", "add", "-b", branch, str(wt_path), "main"])
    return wt_path


def _commit_in_wt(wt: Path, files: dict, msg: str):
    for rel, content in files.items():
        p = wt / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    _run(["git", "-C", str(wt), "add", "-A"])
    _run(["git", "-C", str(wt), "commit", "-q", "-m", msg])


def _push(wt: Path, branch: str):
    _run(["git", "-C", str(wt), "push", "-u", "origin", branch])


def _merge_to_main(main: Path, branch: str):
    """origin 의 main 에 branch 를 머지 후 fetch."""
    # main 브랜치 체크아웃 후 merge --no-ff (squash 흉내내려면 squash 가능)
    _run(["git", "-C", str(main), "checkout", "-q", "main"])
    _run(["git", "-C", str(main), "fetch", "origin"])
    _run(["git", "-C", str(main), "merge", "--no-ff", "-m", f"merge {branch}",
          f"origin/{branch}"])
    _run(["git", "-C", str(main), "push", "origin", "main"])
    _run(["git", "-C", str(main), "fetch", "origin"])


# ── REQ-001: 머지 + clean + pushed → 제거 ────────────────────────

class TestREQ001MergedCleanPushed:
    def test_removes_stale_worktree(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        wt = _create_branch_and_worktree(main, "feat/done")
        _commit_in_wt(wt, {"a.txt": "1"}, "feat: done")
        _push(wt, "feat/done")
        _merge_to_main(main, "feat/done")

        result = wts.sweep(cwd=str(main))

        assert str(wt.resolve()) in [Path(p).resolve().__str__()
                                     for p in result["removed"]]
        assert not wt.exists()
        assert result["warned"] == []


# ── REQ-002: 미머지 → skip ──────────────────────────────────────

class TestREQ002UnmergedSkip:
    def test_unmerged_branch_left_alone(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        wt = _create_branch_and_worktree(main, "feat/wip")
        _commit_in_wt(wt, {"a.txt": "1"}, "wip")
        _push(wt, "feat/wip")
        # 머지 안 함

        result = wts.sweep(cwd=str(main))

        assert wt.exists()
        assert result["removed"] == []
        assert result["skipped"] >= 1


# ── REQ-003: 머지됐지만 unpushed commit 있음 → 경고만 ───────────

class TestREQ003UnpushedWarn:
    def test_merged_with_unpushed_keeps_worktree_with_warning(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        wt = _create_branch_and_worktree(main, "feat/orphan")
        _commit_in_wt(wt, {"a.txt": "1"}, "feat: first")
        _push(wt, "feat/orphan")
        _merge_to_main(main, "feat/orphan")
        # 머지 후 worktree 에 추가 commit (jajang 611fbb8 시나리오)
        _commit_in_wt(wt, {"b.txt": "2"}, "test: regression")

        result = wts.sweep(cwd=str(main))

        assert wt.exists(), "unpushed commit 보호 — worktree 보존되어야 함"
        assert result["removed"] == []
        assert any(
            w["branch"] == "feat/orphan" and "unpushed" in w["reason"]
            for w in result["warned"]
        )


# ── REQ-004: 머지됐지만 working tree dirty → 경고만 ─────────────

class TestREQ004DirtyWarn:
    def test_merged_with_dirty_tree_keeps_worktree(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        wt = _create_branch_and_worktree(main, "feat/dirty")
        _commit_in_wt(wt, {"a.txt": "1"}, "feat: first")
        _push(wt, "feat/dirty")
        _merge_to_main(main, "feat/dirty")
        # 머지 후 dirty 상태 만들기
        (wt / "untracked.txt").write_text("untracked\n")

        result = wts.sweep(cwd=str(main))

        assert wt.exists()
        assert result["removed"] == []
        assert any(
            w["branch"] == "feat/dirty" and "dirty" in w["reason"]
            for w in result["warned"]
        )


# ── REQ-005: main worktree 는 절대 청소 안 함 ───────────────────

class TestREQ005MainProtected:
    def test_main_worktree_never_removed(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        # main worktree 만 있는 상태에서 sweep — 아무 영향 없어야

        result = wts.sweep(cwd=str(main))

        assert main.exists()
        assert result["removed"] == []
        # main 은 is_main=True 라 skipped 카운트에도 안 들어감
        # (skipped 는 non-main 중 unmerged 케이스)


# ── REQ-006: idempotent — 두 번 호출해도 안전 ────────────────────

class TestREQ006Idempotent:
    def test_second_call_is_noop(self, tmp_path):
        _, main = _init_origin_and_clone(tmp_path)
        wt = _create_branch_and_worktree(main, "feat/done")
        _commit_in_wt(wt, {"a.txt": "1"}, "feat: done")
        _push(wt, "feat/done")
        _merge_to_main(main, "feat/done")

        wts.sweep(cwd=str(main))
        assert not wt.exists()

        # 두 번째 호출 — 이미 정리된 상태에서 에러 없이 빈 결과
        result2 = wts.sweep(cwd=str(main))
        assert result2["removed"] == []
        assert result2["warned"] == []


# ── REQ-007: format_report 빈 결과는 빈 문자열 ───────────────────

class TestREQ007Report:
    def test_empty_result_gives_empty_string(self):
        assert wts.format_report({"removed": [], "warned": [], "skipped": 0}) == ""

    def test_removed_only(self):
        msg = wts.format_report({"removed": ["/p"], "warned": [], "skipped": 0})
        assert "removed 1" in msg

    def test_warned_only(self):
        msg = wts.format_report({
            "removed": [], "skipped": 0,
            "warned": [{"path": "/p", "branch": "b", "reason": "x"}],
        })
        assert "1 kept" in msg

    def test_both(self):
        msg = wts.format_report({
            "removed": ["/p1"], "skipped": 0,
            "warned": [{"path": "/p2", "branch": "b", "reason": "x"}],
        })
        assert "removed 1" in msg and "1 kept" in msg
