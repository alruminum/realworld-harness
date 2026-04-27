#!/bin/bash
# migrate-step1.sh — ~/.claude → RWHarness 플러그인 마이그레이션 1단계
#
# 작업: 백업 + settings.json 의 hooks 섹션 무력화
# 전제: Claude Code 가 완전히 quit 된 상태
# 다음: Claude Code 재시작 → /plugin marketplace add + /plugin install →
#       Claude Code 재시작 → migrate-step2.sh 실행
#
# Spec: docs/migration-from-source.md §1~3
set -e

CLAUDE_DIR="${HOME}/.claude"
DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR="${CLAUDE_DIR}.bak.${DATE}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " RWHarness Migration — Step 1 (백업 + settings 무력화)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 0. Claude Code 종료 확인 ──
if pgrep -fl "Claude Code\|claude-code" > /dev/null 2>&1; then
    echo "❌ Claude Code 가 실행 중입니다. 완전히 quit 후 다시 실행하세요."
    echo "   (Cmd+Q + 백그라운드 프로세스 확인)"
    exit 1
fi
echo "✓ Claude Code 종료 확인"

# ── 1. ~/.claude 존재 확인 ──
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ ${CLAUDE_DIR} 가 존재하지 않습니다. 마이그레이션 대상 없음."
    exit 1
fi

# ── 2. 사용자 확인 (destructive action) ──
echo ""
echo "다음 작업을 진행합니다:"
echo "  1) ${CLAUDE_DIR} 전체를 ${BACKUP_DIR} 로 백업 (cp -R)"
echo "  2) ${CLAUDE_DIR}/settings.json 의 hooks 섹션 제거 (백업: settings.json.bak)"
echo ""
read -p "진행할까요? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "중단."
    exit 0
fi

# ── 3. 백업 ──
echo ""
echo "[1/2] 백업 중... (${BACKUP_DIR})"
cp -R "$CLAUDE_DIR" "$BACKUP_DIR"
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "✓ 백업 완료 — ${BACKUP_SIZE}"

# ── 4. settings.json hooks 섹션 제거 ──
echo ""
echo "[2/2] settings.json hooks 섹션 무력화 중..."
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "⚠️  ${SETTINGS_FILE} 없음 — skip"
else
    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"
    python3 - <<PY
import json, sys
p = "${SETTINGS_FILE}"
try:
    d = json.load(open(p))
except Exception as e:
    print(f"⚠️  settings.json 파싱 실패: {e}", file=sys.stderr)
    sys.exit(0)
removed = d.pop("hooks", None)
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
if removed:
    print(f"✓ hooks 섹션 제거 완료 ({len(removed)} 이벤트 카테고리)")
else:
    print("ℹ️  hooks 섹션 없음 — skip")
PY
fi

# ── 완료 + 다음 단계 안내 ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Step 1 완료"
echo ""
echo "  백업 위치: ${BACKUP_DIR}"
echo "  settings 백업: ${SETTINGS_FILE}.bak"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "다음 단계:"
echo ""
echo "  1) Claude Code 시작"
echo "     → 새 세션에서 입력:"
echo "       /plugin marketplace add alruminum/realworld-harness"
echo "       /plugin install realworld-harness"
echo ""
echo "  2) Claude Code 완전 재시작 (플러그인 활성화)"
echo "     → 새 세션의 Bash 도구에서 검증:"
echo "       echo \$CLAUDE_PLUGIN_ROOT"
echo "       (path 가 출력되어야 함)"
echo ""
echo "  3) Claude Code quit (터미널 작업 위해)"
echo ""
echo "  4) 터미널에서 step2 실행:"
echo "       bash <RWHarness>/scripts/migrate-step2.sh"
echo ""
echo "롤백: rm -rf ${CLAUDE_DIR} && mv ${BACKUP_DIR} ${CLAUDE_DIR}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
