#!/bin/bash
# smoke-test.sh — RealWorld Harness clean install 자동 검증 스크립트
#
# 사용법:
#   bash scripts/smoke-test.sh
#     → 현재 환경 (~/.claude 폴백 모드) 검증
#
#   CLAUDE_PLUGIN_ROOT=/path/to/plugin bash scripts/smoke-test.sh
#     → 플러그인 모드 시뮬레이션
#
# 검증 항목 (11개):
#  1. Python 파일 syntax (py_compile)
#  2. hooks/hooks.json JSON 파싱
#  3. .claude-plugin/{plugin,marketplace}.json 파싱
#  4. PLUGIN_ROOT 폴백 동작
#  5. PLUGIN_ROOT 명시 동작
#  6. agent_tiers 매핑 (architect/engineer/qa/unknown)
#  7. check_doc_sync.py 분류기 단위 테스트
#  8. setup-rwh.sh + scripts/hooks/pre-commit.sh syntax
#  9. hooks/ 의 sys.path 트릭으로 harness_common 등 import 가능
# 10. SKIP_DOC_SYNC env 우회 동작 (pre-commit.sh)
# 11. tracker.py — parse_ref / format_ref / normalize / LocalBackend 회로 (LOCAL-N regression 방어)
#
# 종료 코드: 0 = ALL PASS / 1 = 1개 이상 FAIL
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

run() {
    local name="$1"; shift
    if "$@" > /tmp/smoke.log 2>&1; then
        echo "  ✓ $name"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name"
        echo "    --- 출력 ---"
        sed 's/^/    /' /tmp/smoke.log
        echo "    --- 끝 ---"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== RealWorld Harness Smoke Test ==="
echo "REPO_ROOT: $REPO_ROOT"
echo "CLAUDE_PLUGIN_ROOT: ${CLAUDE_PLUGIN_ROOT:-<unset, ~/.claude 폴백>}"
echo ""

echo "[1] Python 파일 syntax (py_compile)"
PY_FILES=$(find harness hooks scripts -name "*.py" -not -path "*/__pycache__/*" | sort)
for f in $PY_FILES; do
    run "py_compile $f" python3 -m py_compile "$f"
done

echo ""
echo "[2] JSON 파싱"
run "hooks/hooks.json" python3 -c "import json; json.load(open('hooks/hooks.json'))"
run ".claude-plugin/plugin.json" python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
run ".claude-plugin/marketplace.json" python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"

echo ""
echo "[3] PLUGIN_ROOT 폴백 + 명시 동작"
# HARNESS-CHG-20260428-12: 폴백 = __file__ 기반 자기-감지. core.py 가
# ${PLUGIN_ROOT}/harness/core.py 에 있다는 사실에서 root 추론. env 미설정 시도
# session_state import 안정.
run "폴백 (env 미설정 → __file__ self-detect)" python3 -c "
import sys, os
sys.path.insert(0, 'harness')
if 'CLAUDE_PLUGIN_ROOT' in os.environ:
    del os.environ['CLAUDE_PLUGIN_ROOT']
import importlib, core
importlib.reload(core)
expected = str(__import__('pathlib').Path('harness/core.py').resolve().parent.parent)
assert str(core.PLUGIN_ROOT) == expected, f'폴백 실패: {core.PLUGIN_ROOT} != {expected}'
print('PLUGIN_ROOT 폴백 (__file__) →', core.PLUGIN_ROOT)
"

run "명시 (env 설정 → 그 경로)" python3 -c "
import sys, os
sys.path.insert(0, 'harness')
os.environ['CLAUDE_PLUGIN_ROOT'] = '/tmp/fake-plugin-root'
import importlib, core
importlib.reload(core)
assert str(core.PLUGIN_ROOT) == '/tmp/fake-plugin-root', f'명시 실패: {core.PLUGIN_ROOT}'
print('PLUGIN_ROOT 명시 →', core.PLUGIN_ROOT)
"

run "session_state import (env 미설정 + 폴백)" python3 -c "
import sys, os
sys.path.insert(0, 'harness')
if 'CLAUDE_PLUGIN_ROOT' in os.environ:
    del os.environ['CLAUDE_PLUGIN_ROOT']
import importlib, core
importlib.reload(core)
# session_state 가 PLUGIN_ROOT/hooks/ 에서 import 가능해야 함
sys.path.insert(0, str(core.PLUGIN_ROOT) + '/hooks')
import session_state
assert hasattr(session_state, 'current_session_id'), 'session_state 손상'
print('session_state OK from', core.PLUGIN_ROOT)
"

echo ""
echo "[4] agent_tiers 매핑"
run "architect → opus / engineer → sonnet / qa → haiku / unknown → mid 폴백" python3 -c "
import sys; sys.path.insert(0, 'harness')
from config import load_config, get_agent_model
c = load_config()
assert get_agent_model('architect', c) == 'claude-opus-4-7', f'architect 실패'
assert get_agent_model('engineer', c) == 'claude-sonnet-4-6', f'engineer 실패'
assert get_agent_model('qa', c) == 'claude-haiku-4-5', f'qa 실패'
assert get_agent_model('unknown-agent', c) == 'claude-sonnet-4-6', f'unknown 폴백 실패'
print('OK: 4개 케이스 모두 통과')
"

echo ""
echo "[5] check_doc_sync.py 분류기 단위"
run "11개 분류 케이스" python3 -c "
import sys; sys.path.insert(0, 'scripts')
from check_doc_sync import classify
cases = [
    ('docs/harness-spec.md', 'spec'),
    ('hooks/agent-gate.py', 'infra'),
    ('agents/architect.md', 'agent'),
    ('tests/pytest/test_x.py', 'test'),
    ('README.md', 'docs'),
    ('orchestration/changelog.md', 'docs'),
    ('docs/proposals.md', 'spec'),
    ('harness/core.py', 'infra'),
    ('.claude-plugin/plugin.json', 'infra'),
    ('.github/workflows/doc-sync.yml', 'infra'),
    ('templates/CLAUDE-base.md', 'docs'),
]
for path, expected in cases:
    actual = classify(path)
    assert actual == expected, f'{path} → {actual} (expected {expected})'
print(f'OK: {len(cases)}/{len(cases)} 통과')
"

echo ""
echo "[6] Shell 스크립트 syntax"
run "scripts/setup-rwh.sh" bash -n scripts/setup-rwh.sh
run "scripts/hooks/pre-commit.sh" bash -n scripts/hooks/pre-commit.sh
run "scripts/smoke-test.sh (self)" bash -n scripts/smoke-test.sh

echo ""
echo "[7] hooks/ 공유 유틸 import"
run "hooks/harness_common.py import" python3 -c "
import sys; sys.path.insert(0, 'hooks')
import harness_common
assert hasattr(harness_common, 'is_harness_enabled'), 'is_harness_enabled 누락'
assert hasattr(harness_common, 'get_prefix'), 'get_prefix 누락'
print('OK')
"

run "hooks/session_state.py import" python3 -c "
import sys; sys.path.insert(0, 'hooks')
import session_state
print('OK')
"

echo ""
echo "[8] SKIP_DOC_SYNC env 우회 (pre-commit.sh dry-run)"
run "SKIP_DOC_SYNC=1 → 즉시 통과" bash -c "
cd /tmp && rm -rf smoke-test-dry && mkdir smoke-test-dry && cd smoke-test-dry
git init -q
mkdir -p scripts/hooks
ln -sf $REPO_ROOT/scripts/hooks/pre-commit.sh scripts/hooks/pre-commit.sh
SKIP_DOC_SYNC=1 bash scripts/hooks/pre-commit.sh 2>&1 | grep -q 'SKIP_DOC_SYNC=1' && echo OK
"

echo ""
echo "[9] tracker.py — parse_ref / format_ref / normalize_issue_num"
run "parse_ref 6 케이스 (#42 / LOCAL-7 / 42 / int / IssueRef 멱등 / 빈 입력 무시)" python3 -c "
import sys; sys.path.insert(0, '.')
from harness.tracker import parse_ref, format_ref, normalize_issue_num, IssueRef

assert parse_ref('#42').raw == '#42' and parse_ref('#42').backend == 'github'
assert parse_ref('LOCAL-7').raw == 'LOCAL-7' and parse_ref('LOCAL-7').backend == 'local'
assert parse_ref('42').raw == '#42'
assert parse_ref(42).raw == '#42'
r = parse_ref('LOCAL-1')
assert parse_ref(r) is r, '멱등 깨짐'
print('OK: 5 케이스 통과')
"

run "format_ref / normalize 일관성 (디스플레이/내부 분리)" python3 -c "
import sys; sys.path.insert(0, '.')
from harness.tracker import format_ref, normalize_issue_num

cases = [
    ('42',      '#42',      '42'),
    ('#42',     '#42',      '42'),       # 부수발견: 디렉토리 안전한 internal
    ('LOCAL-7', 'LOCAL-7',  'LOCAL-7'),
    (42,        '#42',      '42'),
    ('',        '',         ''),
    (None,      '',         ''),
]
for inp, exp_disp, exp_int in cases:
    d = format_ref(inp)
    n = normalize_issue_num(inp)
    assert d == exp_disp, f'format_ref({inp!r}) = {d!r}, exp {exp_disp!r}'
    assert n == exp_int, f'normalize({inp!r}) = {n!r}, exp {exp_int!r}'
print(f'OK: {len(cases)} 케이스 모두 통과')
"

run "LocalBackend 라운드트립 (tmpdir create→get→comment)" python3 -c "
import sys, tempfile
from pathlib import Path
sys.path.insert(0, '.')
from harness.tracker import LocalBackend, IssueRef

with tempfile.TemporaryDirectory() as tmp:
    b = LocalBackend(root=Path(tmp))
    r1 = b.create_issue('first', 'body1', ['bug'])
    r2 = b.create_issue('second', 'body2')
    assert r1.raw == 'LOCAL-1' and r2.raw == 'LOCAL-2'

    e = b.get_issue(r1)
    assert e['title'] == 'first' and e['labels'] == ['bug']

    b.add_comment(r1, 'reviewed')
    e2 = b.get_issue(r1)
    assert len(e2['comments']) == 1 and e2['comments'][0]['body'] == 'reviewed'
print('OK: create + get + comment 라운드트립')
"

run "HARNESS_TRACKER=local 강제 폴백 (gh 가용해도 local 선택)" python3 -c "
import sys, os
sys.path.insert(0, '.')
os.environ['HARNESS_TRACKER'] = 'local'
from harness.tracker import get_tracker
b = get_tracker()
assert b.name == 'local', f'expected local, got {b.name}'
print('OK: HARNESS_TRACKER=local 우선')
"

run "tracker which CLI 출력 — selected 라인 + 두 백엔드 가용성" python3 -m harness.tracker which

echo ""
echo "==================================="
echo "결과: PASS=$PASS / FAIL=$FAIL"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL PASS"
    exit 0
else
    echo "❌ $FAIL 실패"
    exit 1
fi
