#!/bin/bash
# pre-commit.sh — RealWorld Harness 거버넌스 게이트 (git pre-commit hook 진입점)
#
# 설치 (한 줄):
#   ln -sf ../../scripts/hooks/pre-commit.sh "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit"
# 또는 복사:
#   cp scripts/hooks/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#
# 책임: scripts/check_doc_sync.py 호출. 종료 코드 0이 아니면 commit 차단.
# 우회: SKIP_DOC_SYNC=1 환경변수 set 시 게이트 통과.
#       또는 commit msg 에 'Document-Exception: <10자 이상 사유>' 명시 (스크립트가 파싱).
#
# Spec: orchestration/policies.md §2~6, docs/proposals.md §6
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# 우회 옵션
if [ "${SKIP_DOC_SYNC:-0}" = "1" ]; then
    echo "[pre-commit] SKIP_DOC_SYNC=1 — Document Sync 게이트 우회"
    exit 0
fi

# 스크립트 부재 시 skip (호환성)
if [ ! -f scripts/check_doc_sync.py ]; then
    echo "[pre-commit] scripts/check_doc_sync.py 없음 — skip"
    exit 0
fi

python3 scripts/check_doc_sync.py
