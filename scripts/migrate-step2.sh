#!/bin/bash
# migrate-step2.sh — ~/.claude → RWHarness 플러그인 마이그레이션 2단계
#
# 작업: ~/.claude 의 source 디렉토리/파일 삭제 (RWHarness 플러그인이 대체)
# 전제:
#   - migrate-step1.sh 가 이미 실행됨 (백업 + settings 정리)
#   - RWHarness 플러그인이 install 됨
#   - Claude Code 가 완전히 quit 된 상태
#
# Spec: docs/migration-from-source.md §5
set -e

CLAUDE_DIR="${HOME}/.claude"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " RWHarness Migration — Step 2 (source 정리)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 0. Claude Code 종료 확인 ──
if pgrep -fl "Claude Code\|claude-code" > /dev/null 2>&1; then
    echo "❌ Claude Code 가 실행 중입니다. 완전히 quit 후 다시 실행하세요."
    exit 1
fi
echo "✓ Claude Code 종료 확인"

# ── 1. step1 백업 존재 확인 ──
LATEST_BAK=$(ls -dt "${CLAUDE_DIR}".bak.* 2>/dev/null | head -1)
if [ -z "$LATEST_BAK" ]; then
    echo "❌ ${CLAUDE_DIR}.bak.* 백업 없음. step1 먼저 실행하세요."
    exit 1
fi
echo "✓ step1 백업 발견 — ${LATEST_BAK}"

# ── 2. 플러그인 설치 확인 (~/.claude/plugins/cache 에 realworld-harness 존재) ──
PLUGIN_CACHE_GLOB="${CLAUDE_DIR}/plugins/cache/*/realworld-harness/*"
PLUGIN_FOUND=$(ls -d $PLUGIN_CACHE_GLOB 2>/dev/null | head -1)
if [ -z "$PLUGIN_FOUND" ]; then
    echo "❌ RWHarness 플러그인이 install 되지 않음 (${CLAUDE_DIR}/plugins/cache/.../realworld-harness/ 없음)."
    echo "   Claude Code 에서 다음 명령 실행 후 재시도:"
    echo "     /plugin marketplace add alruminum/realworld-harness"
    echo "     /plugin install realworld-harness"
    exit 1
fi
echo "✓ 플러그인 install 확인 — ${PLUGIN_FOUND}"

# ── 3. 사용자 확인 ──
echo ""
echo "다음 항목을 ${CLAUDE_DIR} 에서 삭제합니다:"
echo "  디렉토리: hooks/, harness/, agents/, orchestration/, templates/, docs/"
echo "  파일: setup-harness.sh, setup-agents.sh, orchestration-rules.md,"
echo "        agent-score.md, harness-improvement-plan.md, harness-watch.sh,"
echo "        README.md, .harness-infra (있다면)"
echo "  scripts/ 의 RWHarness 가져간 .py: harness-review.py, classify-miss-report.py"
echo "  commands/ 의 16개 (hardcarry/softcarry 는 commands.personal/ 로 이동 후 보존)"
echo ""
echo "보존: CLAUDE.md, harness-memory.md, harness-projects.json, harness-state/,"
echo "      harness-logs/, memory/, dongchan-style/, backups/, settings.json,"
echo "      plugins/, projects/, sessions/, etc (Claude Code 자체 사용 영역)"
echo ""
read -p "진행할까요? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "중단."
    exit 0
fi

# ── 4. 삭제 실행 ──
echo ""
echo "[1/4] 디렉토리 삭제 중..."
for dir in hooks harness agents orchestration templates docs; do
    target="${CLAUDE_DIR}/${dir}"
    if [ -d "$target" ]; then
        rm -rf "$target"
        echo "  ✓ ${target}"
    else
        echo "  - ${target} (이미 없음)"
    fi
done

echo ""
echo "[2/4] 루트 source 파일 삭제 중..."
for f in setup-harness.sh setup-agents.sh orchestration-rules.md agent-score.md \
         harness-improvement-plan.md harness-watch.sh README.md .harness-infra; do
    target="${CLAUDE_DIR}/${f}"
    if [ -f "$target" ]; then
        rm -f "$target"
        echo "  ✓ ${target}"
    fi
done

echo ""
echo "[3/4] scripts/ 의 RWHarness 가져간 .py 삭제 중..."
for py in harness-review.py classify-miss-report.py; do
    target="${CLAUDE_DIR}/scripts/${py}"
    if [ -f "$target" ]; then
        rm -f "$target"
        echo "  ✓ ${target}"
    fi
done
rmdir "${CLAUDE_DIR}/scripts" 2>/dev/null && echo "  ✓ ${CLAUDE_DIR}/scripts (empty, removed)" || true

echo ""
echo "[4/4] commands/ 정리 중..."
COMMANDS_DIR="${CLAUDE_DIR}/commands"
PERSONAL_DIR="${CLAUDE_DIR}/commands.personal"
if [ -d "$COMMANDS_DIR" ]; then
    # 개인 스킬 보존 (hardcarry, softcarry)
    for personal in hardcarry softcarry; do
        if [ -f "${COMMANDS_DIR}/${personal}.md" ]; then
            mkdir -p "$PERSONAL_DIR"
            mv "${COMMANDS_DIR}/${personal}.md" "${PERSONAL_DIR}/"
            echo "  ✓ ${personal}.md → commands.personal/ (보존)"
        fi
    done
    # 나머지 commands/ 삭제
    rm -rf "$COMMANDS_DIR"
    echo "  ✓ ${COMMANDS_DIR} 삭제"
fi

# ── 검증 ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Step 2 완료"
echo ""
echo "정리 후 ${CLAUDE_DIR} 의 모습:"
ls "${CLAUDE_DIR}" | grep -v "^\." | sort | column -c 80 || ls "${CLAUDE_DIR}" | grep -v "^\."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "다음 단계 (검증):"
echo ""
echo "  1) Claude Code 재시작"
echo "  2) 화이트리스트 등록된 프로젝트 디렉토리에서 Claude 세션 열기"
echo "  3) /harness-list 로 등록 프로젝트 확인"
echo "  4) /quick (또는 docs/e2e-quickstart.md §1) 으로 동작 검증"
echo ""
echo "롤백 (문제 시):"
echo "  rm -rf ${CLAUDE_DIR}"
echo "  mv ${LATEST_BAK} ${CLAUDE_DIR}"
echo "  Claude Code 재시작 + /plugin uninstall realworld-harness"
echo ""
echo "정리 완료 (수일 사용 후 문제 없으면):"
echo "  rm -rf ${LATEST_BAK}"
echo "  rm -f ${CLAUDE_DIR}/settings.json.bak"
echo "  rm -rf ${CLAUDE_DIR}/commands.personal  # 개인 스킬 더 안 쓰면"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
