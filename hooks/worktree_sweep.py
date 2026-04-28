"""worktree_sweep.py — stale worktree 자동 정리.

SessionStart 훅에서 호출되어, main 에 머지된 브랜치의 worktree 를 청소한다.
머지가 harness 의 `merge_to_main()` 이 아니라 사용자 수동 `gh pr merge` 로 처리된
경우 `WorktreeManager.remove()` 가 호출되지 않아 worktree 가 stale 상태로 누적되는
문제 (#36) 해결.

청소 조건 (모두 만족해야 제거):
1. branch 가 origin/<default> 에 머지됨 (`git branch -r --merged`)
2. working tree clean (`git -C <wt> status --porcelain` empty)
3. unpushed commit 없음 (`git -C <wt> rev-list origin/<branch>..HEAD` empty)

unpushed commit 이 있으면 stderr 경고만 — stranded commit 보호 (#34 류 사고 방지).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def _run(args: list[str], cwd: Optional[str] = None, timeout: int = 5) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd)


def _default_branch(cwd: str) -> str:
    """origin/HEAD 가리키는 default branch (보통 main)."""
    r = _run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=cwd)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().replace("refs/remotes/origin/", "")
    return "main"


def _list_worktrees(cwd: str) -> list[dict]:
    """git worktree list --porcelain 파싱.

    반환: [{"path": str, "branch": str|None, "is_main": bool}, ...]
    첫 worktree 가 main repo (is_main=True). 나머지가 격리 worktree.
    """
    r = _run(["git", "worktree", "list", "--porcelain"], cwd=cwd)
    if r.returncode != 0:
        return []

    worktrees = []
    current: dict = {}
    for line in r.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[len("worktree "):].strip(), "branch": None}
        elif line.startswith("branch "):
            ref = line[len("branch "):].strip()
            current["branch"] = ref.replace("refs/heads/", "")
        elif line == "":
            if current:
                worktrees.append(current)
                current = {}
    if current:
        worktrees.append(current)

    if worktrees:
        worktrees[0]["is_main"] = True
        for wt in worktrees[1:]:
            wt["is_main"] = False
    return worktrees


def _is_branch_merged(branch: str, default: str, cwd: str) -> bool:
    """origin/<branch> 가 origin/<default> 에 머지됐는지."""
    r = _run(
        ["git", "branch", "-r", "--merged", f"origin/{default}"],
        cwd=cwd,
    )
    if r.returncode != 0:
        return False
    target = f"origin/{branch}"
    for line in r.stdout.splitlines():
        if line.strip() == target:
            return True
    return False


def _is_working_tree_clean(wt_path: str) -> bool:
    """worktree 의 working tree 가 clean 한지."""
    r = _run(["git", "-C", wt_path, "status", "--porcelain"])
    return r.returncode == 0 and not r.stdout.strip()


def _has_unpushed_commits(branch: str, wt_path: str) -> bool:
    """worktree branch 에 origin 보다 앞선 commit 이 있는지.

    True: unpushed commit 있음 (cleanup skip — stranded 방지).
    False: 푸시 완료 또는 origin ref 없음.
    """
    # origin/<branch> 존재 확인
    r_ref = _run(
        ["git", "-C", wt_path, "rev-parse", "--verify", "--quiet",
         f"refs/remotes/origin/{branch}"],
    )
    if r_ref.returncode != 0:
        # origin 에 없는 브랜치 = 로컬만 → unpushed 로 간주
        return True

    r = _run(
        ["git", "-C", wt_path, "rev-list",
         f"origin/{branch}..HEAD", "--count"],
    )
    if r.returncode != 0:
        return True  # 안전 기본값
    try:
        return int(r.stdout.strip()) > 0
    except ValueError:
        return True


def _remove_worktree(wt_path: str, branch: str, cwd: str) -> bool:
    """worktree + 로컬 branch 제거. 반환: True=성공."""
    r = _run(["git", "worktree", "remove", "--force", wt_path], cwd=cwd, timeout=10)
    if r.returncode != 0:
        # prune 으로 marker 만이라도 정리
        _run(["git", "worktree", "prune"], cwd=cwd)
        return False
    # 머지된 로컬 branch 도 제거 (origin 머지 후 잔존 시 dangling)
    _run(["git", "branch", "-D", branch], cwd=cwd)
    return True


def sweep(cwd: Optional[str] = None) -> dict:
    """stale worktree sweep 메인 진입점.

    cwd: main repo root. None 이면 Path.cwd().
    반환: {"removed": [path...], "warned": [{"path", "branch", "reason"}, ...], "skipped": int}
    """
    cwd_str = str(Path(cwd).resolve()) if cwd else str(Path.cwd().resolve())
    result = {"removed": [], "warned": [], "skipped": 0}

    worktrees = _list_worktrees(cwd_str)
    if not worktrees:
        return result

    default = _default_branch(cwd_str)

    for wt in worktrees:
        if wt.get("is_main"):
            continue
        branch = wt.get("branch")
        path = wt["path"]
        if not branch:
            # detached HEAD worktree — 건드리지 않음
            result["skipped"] += 1
            continue

        # 1차 필터: 머지 여부
        if not _is_branch_merged(branch, default, cwd_str):
            result["skipped"] += 1
            continue

        # 2차 필터: working tree clean
        if not _is_working_tree_clean(path):
            result["warned"].append({
                "path": path, "branch": branch,
                "reason": "working tree dirty",
            })
            continue

        # 3차 필터: unpushed commit 없음 (stranded 보호)
        if _has_unpushed_commits(branch, path):
            result["warned"].append({
                "path": path, "branch": branch,
                "reason": "unpushed commits present (manual review needed)",
            })
            continue

        # 모든 안전장치 통과 → 제거
        if _remove_worktree(path, branch, cwd_str):
            result["removed"].append(path)
        else:
            result["warned"].append({
                "path": path, "branch": branch,
                "reason": "git worktree remove failed",
            })

    return result


def format_report(result: dict) -> str:
    """사람이 읽는 한 줄 보고. 빈 결과면 빈 문자열."""
    if not result["removed"] and not result["warned"]:
        return ""
    parts = []
    if result["removed"]:
        parts.append(f"removed {len(result['removed'])} stale worktree(s)")
    if result["warned"]:
        parts.append(f"{len(result['warned'])} kept (manual review)")
    return "[HARNESS] worktree sweep: " + ", ".join(parts)


# ── #35: Orphaned untracked sweep — pull-conflict 방지 ─────────────────
#
# architect/qa 가 main repo working dir 에 plan 파일을 untracked 로 떨궈두면,
# HARNESS-CHG-26 가 해당 파일을 worktree 로 복사 → PR squash merge 후
# main repo 의 untracked 사본이 origin/main 의 tracked 사본과 path 충돌 →
# `git pull` fast-forward 실패. harness merge / 사용자 수동 merge 둘 다 발생.
#
# 해법: SessionStart 에서 git fetch 후, untracked 중 origin/<default> 의 신규
# tracked 파일과 path 일치하면 *content 동일 시* 자동 삭제. content 다르면
# 경고만 (사용자 수정 보호).


def _fetch_default(cwd: str, default: str) -> bool:
    """origin/<default> 갱신. 실패 시 silent (오프라인/원격 없음)."""
    r = _run(["git", "fetch", "--quiet", "origin", default], cwd=cwd, timeout=15)
    return r.returncode == 0


def _untracked_paths(cwd: str) -> list[str]:
    r = _run(["git", "ls-files", "--others", "--exclude-standard"], cwd=cwd)
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines() if line.strip()]


def _newly_added_in_origin(default: str, cwd: str) -> set[str]:
    """origin/<default> 에는 있는데 local HEAD 엔 없는 파일 (Added)."""
    r = _run(
        ["git", "diff", "--name-only", "--diff-filter=A",
         f"HEAD..origin/{default}"],
        cwd=cwd,
    )
    if r.returncode != 0:
        return set()
    return {line for line in r.stdout.splitlines() if line.strip()}


def _content_matches_origin(path: str, default: str, cwd: str) -> bool:
    """untracked 파일 내용 == origin/<default>:<path> 내용?"""
    r = _run(["git", "show", f"origin/{default}:{path}"], cwd=cwd)
    if r.returncode != 0:
        return False
    try:
        local_content = (Path(cwd) / path).read_text(encoding="utf-8")
    except OSError:
        return False
    return r.stdout == local_content


def sweep_orphaned_untracked(cwd: Optional[str] = None, fetch: bool = True) -> dict:
    """origin/<default> 에 머지된 path 의 untracked 사본 정리.

    cwd: main repo root.
    fetch: True 면 git fetch 선행 (default). False 면 기존 origin ref 사용.
    반환: {"removed": [path...], "warned": [{"path", "reason"}, ...]}
    """
    cwd_str = str(Path(cwd).resolve()) if cwd else str(Path.cwd().resolve())
    result = {"removed": [], "warned": []}

    default = _default_branch(cwd_str)

    if fetch:
        _fetch_default(cwd_str, default)  # 실패 silent

    untracked = _untracked_paths(cwd_str)
    if not untracked:
        return result

    newly_added = _newly_added_in_origin(default, cwd_str)
    if not newly_added:
        return result

    for path in untracked:
        if path not in newly_added:
            continue
        if _content_matches_origin(path, default, cwd_str):
            try:
                (Path(cwd_str) / path).unlink()
                result["removed"].append(path)
            except OSError as e:
                result["warned"].append({"path": path, "reason": f"unlink failed: {e}"})
        else:
            result["warned"].append({
                "path": path,
                "reason": "local content differs from origin (manual review)",
            })

    return result


def format_orphaned_report(result: dict) -> str:
    """untracked sweep 한 줄 보고."""
    if not result["removed"] and not result["warned"]:
        return ""
    parts = []
    if result["removed"]:
        parts.append(f"removed {len(result['removed'])} orphaned untracked")
    if result["warned"]:
        parts.append(f"{len(result['warned'])} kept (manual review)")
    return "[HARNESS] untracked sweep: " + ", ".join(parts)
