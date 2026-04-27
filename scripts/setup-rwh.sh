#!/bin/bash
# scripts/setup-rwh.sh — RealWorld Harness 프로젝트 초기화
#
# 사용법:
#   bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh"   # 플러그인 모드
#   bash ~/.claude/scripts/setup-rwh.sh                 # 개발/폴백 모드
#
# 산출물:
#   .claude/harness.config.json       (prefix + worktree 격리 + agent_tiers)
#   .claude/settings.json             (env + allowedTools 만)
#   .claude/agent-config/             (프로젝트별 에이전트 지침 디렉토리)
#   .git/hooks/pre-commit             (RealWorld Harness 거버넌스 doc-sync 게이트)
#   CLAUDE.md                         (templates/CLAUDE-base.md 에서 복사)
#
# 모드 분기:
#   - $CLAUDE_PLUGIN_ROOT set → 플러그인 모드. hooks/hooks.json 이 자동 로드되므로
#     ~/.claude/settings.json 의 hooks 섹션은 건드리지 않는다.
#   - $CLAUDE_PLUGIN_ROOT 미설정 → 개발 폴백 모드. ~/.claude/ 그대로 사용.
#
# Phase 2 (HARNESS-CHG-20260427-03 [2.8]) PLUGIN_ROOT 추상화 적용.
# 거버넌스 pre-commit 자동 설치 (scripts/hooks/pre-commit.sh).

set -e

# ── 하네스 루트 결정 ──
HARNESS_ROOT="${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude}"
if [ -n "$CLAUDE_PLUGIN_ROOT" ]; then
  echo "📦 플러그인 모드 — HARNESS_ROOT=$HARNESS_ROOT"
else
  echo "🛠  개발 폴백 모드 — HARNESS_ROOT=$HARNESS_ROOT"
fi

# 선택적 인수
# --doc-name <name>  : 핵심 설계 문서 이름 (docs/<name>.md), SPEC_GAP 신선도 체크에 사용 (기본값: domain-logic)
# --repo <owner/repo>: GitHub repo — 마일스톤/레이블 자동 생성에 사용
DOC_NAME="domain-logic"
REPO=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc-name) DOC_NAME="$2"; shift 2 ;;
    --repo)     REPO="$2";     shift 2 ;;
    *) shift ;;
  esac
done

SETTINGS_FILE=".claude/settings.json"
CONFIG_FILE=".claude/harness.config.json"
mkdir -p .claude

# 프로젝트 prefix 유도: 디렉토리명 → 소문자 → 영숫자만 → 최대 6자
RAW=$(basename "$PWD")
PREFIX=$(echo "$RAW" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9' | cut -c1-6)
if [ -z "$PREFIX" ]; then
  PREFIX="proj"
fi

echo "📌 프로젝트 prefix: ${PREFIX}_"
echo "📄 설정 파일: $SETTINGS_FILE"
echo "📋 핵심 설계 문서: docs/${DOC_NAME}.md"

# harness.config.json 생성 (없으면)
# isolation="worktree" 기본 활성: 이슈별 git worktree로 동시 작업 격리.
# 기존 파일이 있고 isolation 필드가 없으면 자동 추가하지 않고 안내만
# (유저가 의도적으로 비활성한 경우 존중).
if [ ! -f "$CONFIG_FILE" ]; then
  echo "{\"prefix\": \"${PREFIX}\", \"test_command\": \"\", \"lint_command\": \"\", \"build_command\": \"\", \"isolation\": \"worktree\"}" > "$CONFIG_FILE"
  echo "📄 $CONFIG_FILE 생성 완료 (worktree 격리 기본 활성)"
else
  HAS_ISOLATION=$(python3 -c "
import json
try:
  d = json.load(open('$CONFIG_FILE'))
  print('1' if 'isolation' in d else '0')
except Exception:
  print('0')
" 2>/dev/null || echo "0")
  if [ "$HAS_ISOLATION" = "0" ]; then
    # isolation 필드가 없으면 기본값 "worktree" 로 자동 추가 (RealWorld Harness 기본 정책).
    # 의도적으로 비활성하려면 본 스크립트 실행 후 "isolation": "" 로 수동 설정.
    python3 - <<PY
import json
p = "$CONFIG_FILE"
d = json.load(open(p))
d["isolation"] = "worktree"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
PY
    echo "📄 $CONFIG_FILE — isolation 필드 누락 → \"worktree\" 자동 추가"
  else
    echo "ℹ️  $CONFIG_FILE 이미 존재 — 유지 (isolation 필드 감지됨)"
  fi
fi

# .gitignore 자동 등록 (git repo 이고 미등록일 때만)
# .worktrees/             — 이슈별 worktree 격리 디렉토리
# .claude/harness-state/  — 세션·플래그·디버그 로그 (절대 commit 금지)
_GITIGNORE_ENTRIES=(".worktrees/" ".claude/harness-state/")

if [ -d .git ]; then
  if [ ! -f .gitignore ]; then
    printf '%s\n' "${_GITIGNORE_ENTRIES[@]}" > .gitignore
    echo "📄 .gitignore 생성 (.worktrees/ + .claude/harness-state/ 등록)"
  else
    for _entry in "${_GITIGNORE_ENTRIES[@]}"; do
      _pattern="^$(echo "$_entry" | sed 's|/|\\/|g')\\?$"
      if ! grep -qE "$_pattern" .gitignore; then
        echo "$_entry" >> .gitignore
        echo "📄 .gitignore에 $_entry 추가"
      fi
    done
  fi
fi

# 기존 settings.json 에서 allowedTools 보존
EXISTING_ALLOWED="[]"
if [ -f "$SETTINGS_FILE" ]; then
  EXISTING_ALLOWED=$(python3 -c "
import json, sys
with open('$SETTINGS_FILE') as f:
    d = json.load(f)
print(json.dumps(d.get('allowedTools', [])))
" 2>/dev/null || echo "[]")
  echo "⚠️  기존 settings.json 감지 — allowedTools 보존, hooks 덮어씀"
fi

# Python으로 settings.json 생성
python3 << PYEOF
import json

prefix = "${PREFIX}"
p = prefix
doc_name = "${DOC_NAME}"

import os
settings_path = "$SETTINGS_FILE"
existing_allowed = ${EXISTING_ALLOWED}

# ⚠️ 훅은 프로젝트 settings.json에 쓰지 않는다.
#    모든 훅은 ~/.claude/settings.json(전역)에서 관리.
#    프로젝트에는 env + allowedTools만 작성.
output = {
    "env": {
        "HARNESS_DOC_NAME": doc_name,
    },
    "allowedTools": existing_allowed,
}

# 기존 settings.json에 hooks 섹션이 있으면 제거 (마이그레이션)
if os.path.exists(settings_path):
    try:
        with open(settings_path) as f:
            old = json.load(f)
        if "hooks" in old:
            print("⚠️  기존 프로젝트 hooks 섹션 발견 — 제거 (전역으로 이관)")
    except Exception:
        pass

with open(settings_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ {settings_path} 생성 완료 (prefix: {prefix}_)")
PYEOF

# harness-*.sh — 글로벌 전용 (프로젝트에 복사하지 않음)
# 실행 인프라는 ~/.claude/ 에서만 관리. 프로젝트엔 설정(harness.config.json)만 둔다.
# 기존 프로젝트에 낡은 복사본이 있으면 삭제
for old_file in ".claude/harness-loop.sh" ".claude/harness/executor.sh"; do
  if [ -f "$old_file" ]; then
    rm -f "$old_file"
    echo "  🗑 낡은 $old_file 삭제 (글로벌 전용으로 전환)"
  fi
done

# ── 낡은 .claude/agents/ 복사본 정리 (마이그레이션) ─────────────────────
# 에이전트는 전역(~/.claude/agents/)에서 직접 로드. 프로젝트 복사본 불필요.
# 프로젝트별 컨텍스트는 .claude/agent-config/ 에 저장.
if [ -d ".claude/agents" ]; then
  AGENT_COUNT=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "$AGENT_COUNT" -gt 0 ]; then
    echo "⚠️  낡은 .claude/agents/ 감지 (${AGENT_COUNT}개 파일)"
    echo "    에이전트는 전역(~/.claude/agents/)에서 직접 로드됩니다."
    echo "    프로젝트별 지침은 .claude/agent-config/에 옮겨주세요."
    echo "    (자동 삭제하지 않음 — 수동 확인 후 삭제)"
  fi
fi

# ── .claude/agent-config/ 디렉토리 생성 ──────────────────────────────
mkdir -p .claude/agent-config
echo "📁 .claude/agent-config/ 준비 완료 (프로젝트별 에이전트 지침)"

# ── CLAUDE.md 베이스 복사 (없을 때만) ─────────────────────────────────
if [ ! -f "CLAUDE.md" ]; then
  if [ -f "${HARNESS_ROOT}/templates/CLAUDE-base.md" ]; then
    cp "${HARNESS_ROOT}/templates/CLAUDE-base.md" CLAUDE.md
    if [ -n "$REPO" ]; then
      sed -i '' "s|\[채우기: owner/repo\]|${REPO}|g" CLAUDE.md 2>/dev/null || true
    fi
    echo "📄 CLAUDE.md 생성 (베이스 템플릿에서 복사)"
  fi
else
  echo "ℹ️  CLAUDE.md 이미 존재 — 건너뜀"
fi

# ── GitHub 마일스톤/레이블 자동 생성 ──────────────────────────────────
if [ -n "$REPO" ]; then
  echo ""
  echo "🏷️  GitHub 마일스톤 생성 중 (${REPO})..."
  for M in "Story" "Bugs" "Epics" "Feature"; do
    RESULT=$(gh api "repos/${REPO}/milestones" -f title="$M" -f state="open" 2>&1)
    if echo "$RESULT" | grep -q '"number"'; then
      echo "  ✅ $M"
    elif echo "$RESULT" | grep -qF 'already_exists'; then
      echo "  ⚠️  $M (이미 존재)"
    else
      echo "  ❌ $M 실패 — gh auth login 확인 필요"
    fi
  done

  echo ""
  echo "🏷️  GitHub 레이블 생성 중..."
  for LABEL_INFO in "v01:0075ca" "bug:d73a4a" "feat:a2eeef"; do
    LABEL_NAME="${LABEL_INFO%%:*}"
    LABEL_COLOR="${LABEL_INFO##*:}"
    RESULT=$(gh api "repos/${REPO}/labels" -f name="$LABEL_NAME" -f color="$LABEL_COLOR" 2>&1)
    if echo "$RESULT" | grep -q '"name"'; then
      echo "  ✅ $LABEL_NAME"
    elif echo "$RESULT" | grep -qF 'already_exists'; then
      echo "  ⚠️  $LABEL_NAME (이미 존재)"
    else
      echo "  ❌ $LABEL_NAME 실패"
    fi
  done
fi

# ── 전역 settings.json 훅 관리 ──────────────────────────────────────
# _meta: "harness" 태그가 붙은 훅만 프레임워크가 관리.
# _meta가 없거나 "user"인 훅은 사용자 훅으로 보존.
# 새 프레임워크 훅 추가 시 이 스크립트에서 _meta: harness로 등록.
GLOBAL_SETTINGS="${HOME}/.claude/settings.json"
INJECT_HOOK_MARKER="harness-review-inject.py"

if [ -f "$GLOBAL_SETTINGS" ]; then
  if grep -qF "$INJECT_HOOK_MARKER" "$GLOBAL_SETTINGS" 2>/dev/null; then
    echo "ℹ️  harness-review-inject.py 훅 이미 등록됨 — 스킵"
  else
    python3 << 'INJECT_PYEOF'
import json, sys, os

settings_path = os.path.expanduser("~/.claude/settings.json")
hook_cmd = "python3 ~/.claude/hooks/harness-review-inject.py 2>/dev/null || true"

try:
    with open(settings_path) as f:
        cfg = json.load(f)
except Exception as e:
    print(f"❌ 전역 settings.json 읽기 실패: {e}", flush=True)
    sys.exit(0)

ups = cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])

# 이미 등록됐는지 확인
already = any(
    any(h.get("command", "") == hook_cmd for h in block.get("hooks", []))
    for block in ups
)
if already:
    print("ℹ️  harness-review-inject.py 이미 등록됨", flush=True)
    sys.exit(0)

# 새 블록 추가 (_meta: harness 태그 포함)
ups.append({
    "_meta": "harness",
    "hooks": [
        {
            "type": "command",
            "command": hook_cmd,
            "timeout": 10
        }
    ]
})

with open(settings_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print("✅ 전역 settings.json에 harness-review-inject.py 훅 등록 완료 (_meta: harness)", flush=True)
INJECT_PYEOF
  fi
else
  echo "⚠️  전역 settings.json 없음 — harness-review-inject.py 훅 수동 등록 필요"
fi

# ── session-agent-cleanup 훅 등록 (UserPromptSubmit 체인 맨 앞) ────────────
# agent-gate.py(PreToolUse Agent)가 live.json.agent를 기록한 뒤 유저가 tool use를 reject하면
# PostToolUse(post-agent-flags.py)가 돌지 않아 agent 필드가 고아로 남는 버그 방어.
# 새 유저 프롬프트가 들어오는 시점엔 이전 Agent tool은 종료 상태이므로 agent 필드를 무조건 해제.
CLEANUP_HOOK_MARKER="session-agent-cleanup.py"

if [ -f "$GLOBAL_SETTINGS" ]; then
  if grep -qF "$CLEANUP_HOOK_MARKER" "$GLOBAL_SETTINGS" 2>/dev/null; then
    echo "ℹ️  session-agent-cleanup.py 훅 이미 등록됨 — 스킵"
  else
    python3 << 'CLEANUP_PYEOF'
import json, sys, os

settings_path = os.path.expanduser("~/.claude/settings.json")
hook_cmd = "python3 ~/.claude/hooks/session-agent-cleanup.py 2>/dev/null || true"

try:
    with open(settings_path) as f:
        cfg = json.load(f)
except Exception as e:
    print(f"❌ 전역 settings.json 읽기 실패: {e}", flush=True)
    sys.exit(0)

ups = cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])

already = any(
    any(h.get("command", "") == hook_cmd for h in block.get("hooks", []))
    for block in ups
)
if already:
    print("ℹ️  session-agent-cleanup.py 이미 등록됨", flush=True)
    sys.exit(0)

# 체인 맨 앞에 삽입 — router보다 먼저 돌아야 stale agent 제거 후 router가 올바른 context로 동작
ups.insert(0, {
    "_meta": "harness",
    "hooks": [
        {
            "type": "command",
            "command": hook_cmd,
            "timeout": 5
        }
    ]
})

with open(settings_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print("✅ 전역 settings.json에 session-agent-cleanup.py 훅 등록 완료 (UserPromptSubmit 체인 맨 앞)", flush=True)
CLEANUP_PYEOF
  fi
fi

# ── 거버넌스 pre-commit hook 설치 (RealWorld Harness Document Sync 게이트) ──
# scripts/hooks/pre-commit.sh 를 .git/hooks/pre-commit 으로 심볼릭 링크 또는 append.
# orchestration/policies.md §2~6 룰 자동 강제 (Task-ID, Change-Type, Document-Exception).
PRECOMMIT_HOOK=".git/hooks/pre-commit"
DOC_SYNC_MARKER="# realworld-harness: document sync gate"
HARNESS_PRECOMMIT="${HARNESS_ROOT}/scripts/hooks/pre-commit.sh"

if [ -d ".git/hooks" ]; then
  if ! grep -qF "$DOC_SYNC_MARKER" "$PRECOMMIT_HOOK" 2>/dev/null; then
    if [ -x "$HARNESS_PRECOMMIT" ]; then
      cat >> "$PRECOMMIT_HOOK" <<HOOKEOF

${DOC_SYNC_MARKER}
# scripts/check_doc_sync.py 호출. 실패 시 commit 차단.
# 우회: SKIP_DOC_SYNC=1 또는 commit msg 에 'Document-Exception: <사유>' 명시.
if [ -x "${HARNESS_PRECOMMIT}" ]; then
  bash "${HARNESS_PRECOMMIT}" || exit 1
fi
HOOKEOF
      chmod +x "$PRECOMMIT_HOOK"
      echo "✅ pre-commit hook에 RealWorld Harness Document Sync 게이트 추가"
    else
      echo "ℹ️  $HARNESS_PRECOMMIT 없음 — pre-commit hook 스킵 (플러그인 미설치 또는 파일 부재)"
    fi
  else
    echo "ℹ️  pre-commit hook에 Document Sync 게이트 이미 등록됨 — 스킵"
  fi
else
  echo "ℹ️  .git/hooks 디렉토리 없음 — pre-commit hook 스킵 (git init 후 재실행)"
fi

# ── 화이트리스트 자동 등록 (하네스 훅 활성화) ──
# 전역 훅은 `~/.claude/harness-projects.json`에 등록된 프로젝트에서만 동작한다.
# setup-harness.sh 실행 = 하네스 사용 의도이므로 자동 등록.
PROJECT_ROOT_ABS=$(python3 -c "import os; print(os.path.realpath('$PWD'))")
python3 - <<PY
import json, os
from pathlib import Path
wl = Path.home() / ".claude" / "harness-projects.json"
data = {"projects": []}
if wl.exists():
    try: data = json.loads(wl.read_text())
    except Exception: pass
projects = data.get("projects", [])
here = "$PROJECT_ROOT_ABS"
for p in projects:
    root = os.path.realpath(os.path.expanduser(p))
    if here == root or here.startswith(root + os.sep):
        print(f"ℹ️  화이트리스트 이미 등록됨: {root}")
        raise SystemExit(0)
projects.append(here)
data["projects"] = sorted(set(projects))
wl.parent.mkdir(parents=True, exist_ok=True)
wl.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print(f"✅ 하네스 화이트리스트 등록: {here}")
PY

# ── MCP 서버 등록 안내 (GitHub + Pencil) ───────────────────────────
# 에이전트들이 사용하는 MCP 도구는 서버 등록 없으면 silently 실패한다.
# 도구 선언(agents/*.md frontmatter)과 권한(settings.json allowedTools)이 있어도
# 서버 자체가 없으면 호출 무효 — 데드락 발생 위험.
#
# 자동 등록은 토큰/경로를 다루므로 보안상 하지 않는다. 안내만 출력.
if command -v claude >/dev/null 2>&1; then
  MCP_LIST=$(claude mcp list 2>/dev/null)

  # GitHub MCP — qa/designer/architect/product-planner 이슈 생성·수정용
  if ! echo "$MCP_LIST" | grep -qE '^github:'; then
    echo ""
    echo "⚠️  GitHub MCP 서버 미등록 — 에이전트가 이슈를 만들지 못합니다."
    if command -v gh >/dev/null 2>&1 && gh auth token >/dev/null 2>&1; then
      echo "    아래 명령으로 등록 (gh 로그인 토큰 자동 사용):"
      echo ""
      echo "      TOKEN=\$(gh auth token) && claude mcp add github -s user \\"
      echo "        -e GITHUB_PERSONAL_ACCESS_TOKEN=\"\$TOKEN\" \\"
      echo "        -- npx -y @modelcontextprotocol/server-github"
      echo ""
      echo "    등록 후 Claude Code 세션을 재시작해야 도구가 로드됩니다."
    else
      echo "    먼저 \`gh auth login\` 으로 GitHub 로그인 후 위 명령 실행 필요."
    fi
  else
    echo "ℹ️  GitHub MCP 서버 등록 확인됨"
  fi

  # Pencil MCP — designer/ux-architect 디자인 시안 생성·읽기용 (UI 프로젝트만)
  if ! echo "$MCP_LIST" | grep -qE '^pencil:'; then
    echo ""
    echo "ℹ️  Pencil MCP 서버 미등록 — UI 프로젝트면 designer 에이전트 작동 안 함."
    PENCIL_BIN="/Applications/Pencil.app/Contents/Resources/app.asar.unpacked/out/mcp-server-darwin-arm64"
    if [ -f "$PENCIL_BIN" ]; then
      echo "    Pencil 앱은 설치됨 — 아래 명령으로 등록:"
      echo ""
      echo "      claude mcp add pencil -s user -- $PENCIL_BIN --app desktop"
      echo ""
      echo "    등록 후 Claude Code 세션을 재시작해야 도구가 로드됩니다."
    else
      echo "    UI 없는 프로젝트면 무시. UI 프로젝트라면:"
      echo "      1) Pencil 앱 설치 (https://pencil.do)"
      echo "      2) claude mcp add pencil -s user -- $PENCIL_BIN --app desktop"
      echo "      3) Claude Code 세션 재시작"
    fi
  else
    echo "ℹ️  Pencil MCP 서버 등록 확인됨"
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Harness 프로젝트 설정 완료"
echo ""
echo "  플래그 prefix : /tmp/${PREFIX}_*"
echo "  설정 파일     : $SETTINGS_FILE (env + allowedTools만)"
echo "  config 파일   : $CONFIG_FILE"
echo ""
echo "⚠️  훅은 전역 ~/.claude/settings.json에서만 관리."
echo "    프로젝트 settings.json에 hooks 섹션 추가 금지."
echo ""
echo "다음 단계:"
echo "  1. CLAUDE.md의 [채우기] 항목을 프로젝트에 맞게 작성"
echo "  2. .claude/agent-config/ 에 프로젝트별 에이전트 지침 추가 (선택)"
echo "     예: .claude/agent-config/engineer.md — SDK 래퍼 패턴, 의존성 규칙 등"
echo "  3. product-planner와 PRD/TRD 작성 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
