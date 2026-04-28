#!/usr/bin/env python3
"""
executor.py — executor.sh 대체.
CLI 진입점: python3 executor.py <mode> [--impl PATH] [--issue N] ...
Python 3.9+ stdlib only.
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

# Plugin root resolution — env > __file__ self-detect > legacy fallback.
# 자세한 사유는 harness/core.py _resolve_plugin_root 도 참조.
def _resolve_plugin_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    # __file__ = ${PLUGIN_ROOT}/harness/executor.py
    here = Path(__file__).resolve()
    if here.parent.name == "harness":
        return here.parent.parent
    return Path.home() / ".claude"


PLUGIN_ROOT = _resolve_plugin_root()


def main() -> None:
    parser = argparse.ArgumentParser(description="하네스 워크플로우 라우터")
    parser.add_argument("mode", choices=["impl", "plan"], help="실행 모드")
    parser.add_argument("--impl", dest="impl_file", default="", help="impl 파일 경로")
    parser.add_argument("--issue", dest="issue_num", default="", help="이슈 번호")
    parser.add_argument("--prefix", default="", help="프로젝트 prefix")
    parser.add_argument("--depth", default="auto", choices=["auto", "simple", "std", "deep"])
    parser.add_argument("--context", default="", help="추가 컨텍스트")
    parser.add_argument("--branch-type", default="feat", help="브랜치 타입 (feat|fix)")
    parser.add_argument("--force-retry", action="store_true",
                        help="stale state 일괄 청소 후 재실행 — merge_cooldown + escalate_history "
                             "(false failure 누적 시, 예: 마커 파서 mismatch 후 alias map 도입 등)")

    args = parser.parse_args()

    # config + state_dir 초기화
    try:
        from .config import load_config
        from .core import StateDir, RunLogger, Flag, find_main_repo_root
        from .tracker import format_ref, normalize_issue_num
    except ImportError:
        from config import load_config
        from core import StateDir, RunLogger, Flag, find_main_repo_root
        from tracker import format_ref, normalize_issue_num

    # L2 방어: cwd가 worktree 내부로 persist된 상태면 main repo root로 복귀.
    # Claude Code Bash tool은 세션 간 cwd를 유지하므로 `cd .worktrees/...` 이후 호출 시
    # StateDir/WorktreeManager가 중첩 경로로 오염된다. 여기서 한 번 복귀하면 이후 모든
    # cwd 의존 코드(StateDir, agent handoff, flag 파일 등)가 안전해짐.
    _main_root = find_main_repo_root()
    if _main_root != Path.cwd().resolve():
        print(f"[HARNESS] ⚠️ cwd가 worktree 내부 감지 → main repo 복귀")
        print(f"  이전: {Path.cwd()}")
        print(f"  복귀: {_main_root}")
        os.chdir(_main_root)

    config = load_config()
    prefix = args.prefix or config.prefix
    # 진입점에서 normalize — 디렉토리·flag·env 안전한 internal 형식으로 변환.
    # "#42" → "42", "LOCAL-7" 보존, 빈 문자열은 그대로.
    issue_num = normalize_issue_num(getattr(args, "issue_num", "") or "")

    # Phase 3: 세션 ID 부팅 — HARNESS_SESSION_ID env → .session-id 파일
    sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
    try:
        import session_state as ss  # type: ignore
    except ImportError:
        ss = None  # type: ignore
    session_id = ""
    if ss is not None:
        session_id = ss.current_session_id()
        if session_id:
            os.environ["HARNESS_SESSION_ID"] = session_id
            # W4 — live.json round-trip canary (always-on).
            # silent-cascade 사전 차단: live.json 쓰기 불가 시 즉시 ESCALATE.
            # §2.4: executor 진입 직후 1회 검증 — downstream 가드 오염 방지.
            try:
                sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))
                from harness_common import _verify_live_json_writable  # type: ignore
            except ImportError:
                _verify_live_json_writable = None  # type: ignore
            if _verify_live_json_writable is not None:
                _canary_ok, _canary_err = _verify_live_json_writable(session_id)
                if not _canary_ok:
                    print(
                        f"[HARNESS] \u274c ESCALATE \u2014 live.json round-trip \uc2e4\ud328: {_canary_err}\n"
                        f"  downstream guards (agent-boundary/issue-gate/commit-gate/ralph-session-stop) \uac00\n"
                        f"  silent-cascade \ud569\ub2c8\ub2e4. \uc9c4\ub2e8:\n"
                        f"  ls -la .claude/harness-state/.sessions/{session_id}/\n"
                        f"  df -h .claude/harness-state/  # \ub514\uc2a4\ud06c \ud480 \ud655\uc778\n",
                        file=sys.stderr,
                    )
                    sys.exit(1)

    state_dir = StateDir(Path.cwd(), prefix, issue_num=issue_num)

    # HARNESS_ISSUE_NUM env var — hooks가 이슈별 플래그 디렉토리 참조
    if issue_num:
        os.environ["HARNESS_ISSUE_NUM"] = issue_num

    # ── Merge cooldown 가드 — 직전 MERGE_CONFLICT_ESCALATE 재진입 차단 ──
    if issue_num and args.mode == "impl" and not args.force_retry:
        try:
            from .core import get_merge_cooldown, clear_merge_cooldown
        except ImportError:
            from core import get_merge_cooldown, clear_merge_cooldown
        cooldown = get_merge_cooldown(Path.cwd(), prefix, issue_num)
        if cooldown:
            from datetime import datetime
            ts = datetime.fromtimestamp(cooldown.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"[HARNESS] ⚠️ 이슈 {format_ref(issue_num)} cooldown 중 — {cooldown.get('reason')} ({ts})")
            print(f"  branch: {cooldown.get('branch','?')}")
            if cooldown.get("stderr_tail"):
                print(f"  사유: {cooldown['stderr_tail'][:200]}")
            print("")
            print("  반복 재진입이 같은 실패를 반복합니다. 수동 해결 후 재시도하세요:")
            print("    1) gh pr list --head <branch> 로 PR 상태 확인")
            print("    2) 충돌 해결 또는 PR 수동 merge/close")
            print("    3) --force-retry 플래그로 재실행")
            sys.exit(1)
    elif args.force_retry:
        # --force-retry: stale state 일괄 청소 (cooldown + escalate_history)
        # cooldown 청소는 issue_num 필요. escalate_history 청소는 impl_file 필요.
        try:
            from .core import clear_merge_cooldown, clear_escalate_count
        except ImportError:
            from core import clear_merge_cooldown, clear_escalate_count
        if issue_num:
            clear_merge_cooldown(Path.cwd(), prefix, issue_num)
            print(f"[HARNESS] cooldown 우회: 이슈 {format_ref(issue_num)}")
        if args.impl_file:
            # 동일 impl 의 누적 ESCALATE 기록 청소 → _maybe_auto_spec_gap 자동 발동 차단.
            # 이전 ESCALATE 가 false failure 였던 경우(예: 마커 파서 mismatch) 재시도
            # 시 historical fail count 무시하고 fresh start.
            clear_escalate_count(state_dir, args.impl_file)
            print(f"[HARNESS] escalate history 청소: {args.impl_file}")

    # Phase 3: 이슈 lock 획득 — 두 세션이 같은 이슈 동시 작업 방지
    if ss is not None and session_id and issue_num:
        try:
            ok, holder = ss.claim_issue_lock(prefix, issue_num, session_id, mode=args.mode)
            if not ok and holder:
                print(f"[HARNESS] 오류: 이슈 {format_ref(issue_num)}은 세션 {holder.get('session_id','')[:8]}…가 "
                      f"PID {holder.get('pid')}로 이미 작업 중입니다.")
                print("동시 작업은 지원하지 않습니다. /harness-kill 또는 세션 완료를 기다리세요.")
                sys.exit(1)
            # 세션 live.json에 하네스/이슈 상태 기록
            ss.update_live(session_id, harness_active=True, issue_num=issue_num,
                           prefix=prefix, mode=args.mode)
        except Exception as e:
            print(f"[HARNESS] session_state 초기화 경고: {e}")

    # ── 병렬 실행 가드 (이슈별 잠금 — 다른 이슈는 동시 실행 가능) ──
    if issue_num:
        lock_file = state_dir.path / f"{prefix}_{issue_num}_harness_active"
    else:
        lock_file = state_dir.path / f"{prefix}_harness_active"
    if lock_file.exists():
        try:
            data = json.loads(lock_file.read_text())
            existing_pid = data.get("pid", 0)
            if existing_pid:
                try:
                    os.kill(existing_pid, 0)  # 살아있는지 확인
                    print(f"[HARNESS] 오류: 같은 PREFIX({prefix})로 이미 실행 중 (PID={existing_pid})")
                    print("동시 실행은 지원하지 않습니다. /harness-kill로 기존 실행을 중단하거나 완료를 기다리세요.")
                    sys.exit(1)
                except OSError:
                    # PID 죽었음 — stale lock 정리. 외부 SIGKILL/세션 종료 후 재진입 케이스.
                    # 상태 추적 가시성 (HARNESS-CHG-20260428-06): 이전엔 silent unlink 라
                    # AI 가 "왜 막혀있지?" 패닉으로 우회 시도 → 본 메시지로 정상 복구임을 명시.
                    _started = data.get("started", 0)
                    _hb = data.get("heartbeat", 0)
                    _stale_secs = int(time.time()) - max(_started, _hb)
                    print(f"[HARNESS] 직전 실행 PID={existing_pid} 죽음 — stale lock 자동 정리 "
                          f"(마지막 heartbeat {_stale_secs}초 전). 재진행합니다.")
                    lock_file.unlink(missing_ok=True)
        except (json.JSONDecodeError, OSError):
            print(f"[HARNESS] lock 파일 손상 — 자동 정리 후 재진행: {lock_file}")
            lock_file.unlink(missing_ok=True)

    lock_started = int(time.time())
    os.environ["HARNESS_RESULT"] = "unknown"

    def write_lease() -> None:
        try:
            lock_file.write_text(json.dumps({
                "pid": os.getpid(),
                "mode": args.mode,
                "started": lock_started,
                "heartbeat": int(time.time()),
            }))
        except OSError:
            pass
        # W2 §1.3 heartbeat — HARNESS_ACTIVE flag mtime touch.
        # agent-gate.py 의 _is_active_flag_fresh() TTL=6h 이 false-GC 하지 않도록
        # 매 write_lease() 호출(15초 간격)마다 flag mtime 갱신.
        try:
            _harness_active_flag = state_dir.flags_dir / f"{prefix}_{Flag.HARNESS_ACTIVE}"
            if _harness_active_flag.exists():
                _harness_active_flag.touch(exist_ok=True)
        except Exception:
            pass

    write_lease()

    # ── Heartbeat (15초마다) ──
    hb_stop = threading.Event()

    def heartbeat_loop() -> None:
        while not hb_stop.is_set():
            hb_stop.wait(15)
            if not hb_stop.is_set():
                write_lease()
                # Phase 3: 이슈 lock heartbeat도 갱신 — 장시간 루프가 stale 판정되지 않도록
                if ss is not None and session_id and issue_num:
                    try:
                        ss.heartbeat_issue_lock(prefix, issue_num, session_id)
                    except Exception:
                        pass

    hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    hb_thread.start()

    # ── EXIT 정리 ──
    run_logger_ref: list = [None]  # mutable container for atexit closure
    _run_end_written = [False]

    def cleanup() -> None:
        hb_stop.set()
        lock_file.unlink(missing_ok=True)
        state_dir.flag_rm(Flag.HARNESS_KILL)
        # *_active 정리 (레거시 폴백 경로)
        for f in state_dir.flags_dir.glob(f"{prefix}_*_active"):
            f.unlink(missing_ok=True)
        # Phase 3: 이슈 lock 해제 + live.json 정리
        if ss is not None and session_id:
            try:
                if issue_num:
                    ss.release_issue_lock(prefix, issue_num, session_id)
                ss.update_live(session_id, harness_active=None, agent=None)
            except Exception:
                pass
        # write_run_end — 루프 함수에서 이미 호출했으면 스킵 (이중 호출 방지)
        if run_logger_ref[0] and not _run_end_written[0]:
            result = os.environ.get("HARNESS_RESULT", "unknown")
            branch = os.environ.get("HARNESS_BRANCH", "")
            run_logger_ref[0].write_run_end(result, branch, args.issue_num)

    atexit.register(cleanup)

    # SIGTERM/SIGINT 핸들러 — bash trap EXIT가 SIGTERM에도 반응한 것과 동일
    def _signal_cleanup(signum: int, frame: object) -> None:
        cleanup()
        sys.exit(128 + signum)
    signal.signal(signal.SIGTERM, _signal_cleanup)
    signal.signal(signal.SIGINT, _signal_cleanup)

    # ── 모드 라우터 ──
    if args.mode == "impl":
        try:
            from .impl_router import run_impl
        except ImportError:
            from impl_router import run_impl
        run_logger = RunLogger(prefix, "impl", args.issue_num)
        run_logger_ref[0] = run_logger
        result = run_impl(
            impl_file=args.impl_file,
            issue_num=args.issue_num,
            prefix=prefix,
            depth=args.depth,
            context=args.context,
            branch_type=args.branch_type,
            run_logger=run_logger,
            config=config,
            state_dir=state_dir,
        )
        os.environ["HARNESS_RESULT"] = result
        _run_end_written[0] = True  # run_impl 내부에서 write_run_end 호출됨

    elif args.mode == "plan":
        try:
            from .plan_loop import run_plan
        except ImportError:
            from plan_loop import run_plan
        run_logger = RunLogger(prefix, "plan", args.issue_num)
        run_logger_ref[0] = run_logger
        result = run_plan(
            issue_num=args.issue_num,
            prefix=prefix,
            context=args.context,
            config=config,
            state_dir=state_dir,
            run_logger=run_logger,
        )
        os.environ["HARNESS_RESULT"] = result
        _run_end_written[0] = True


if __name__ == "__main__":
    main()
