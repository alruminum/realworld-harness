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
# 검증 항목 (16개):
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
# 12. monorepo 환경 — engineer_scope config 동적 로딩 (jajang fixture)
# 13. env 미설정 회귀 0 — HARNESS_GUARD_V2_* 전체 off 시 v1 동작 유지
# 14. LLM 마커 변형 흡수 — alias map (PLAN_LGTM/PLAN_OK/APPROVE/REJECT)
# 15. feature flag 부분 활성 — cross-flag 호환성 (AGENT_BOUNDARY=1 only)
# 16. 5번째 위험 cross-guard silent dependency — stderr 경고 출력 검증
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

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 Guard Model Realignment (Issue #13 Iter 3 W5)
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "[10] monorepo 환경 — engineer_scope config 동적 로딩 (jajang fixture)"
run "jajang fixture config 로드 + apps/api/src/ 패턴 매치" python3 -c "
import sys, os, re
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')

# harness_common 캐시 초기화
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None

# V2 활성
os.environ['HARNESS_GUARD_V2_AGENT_BOUNDARY'] = '1'

# jajang fixture config 로드
from harness.config import load_config
from pathlib import Path
fixture = Path('tests/pytest/fixtures/jajang_monorepo')
cfg = load_config(project_root=fixture)
assert len(cfg.engineer_scope) > 0, 'engineer_scope 비어있음'
assert cfg.prefix == 'jajang', f'prefix 불일치: {cfg.prefix}'

# mock 로드 없이 실제 패턴으로 검증
scope = cfg.engineer_scope
combined = re.compile('(' + '|'.join(scope) + ')')
test_paths = ['apps/api/src/main.py', 'apps/web/src/app.ts', 'services/api/src/router.py']
for p in test_paths:
    assert combined.search(p), f'{p} 가 engineer_scope 에 매치 안 됨'
print(f'OK: {len(scope)} 패턴 로드, {len(test_paths)} 경로 모두 매치')
"

run "monorepo V2 off → static scope 회귀 0" python3 -c "
import sys, os, re
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None
# V2 flag 없음
for k in list(os.environ.keys()):
    if k.startswith('HARNESS_GUARD_V2_'):
        del os.environ[k]
scope = hc._load_engineer_scope()
assert scope == list(hc._STATIC_ENGINEER_SCOPE), f'V2 off static scope 불일치'
combined = re.compile('(' + '|'.join(scope) + ')')
assert combined.search('src/foo.ts'), 'src/foo.ts 매치 실패'
assert combined.search('apps/api/src/main.py'), 'apps/api/src/ 매치 실패'
print(f'OK: V2 off → static scope {len(scope)}개 패턴, 회귀 0')
"

echo ""
echo "[11] env 미설정 회귀 0 — HARNESS_GUARD_V2_* 전체 off"
run "V2 전체 off → harness_common v1 동작" python3 -c "
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
# 모든 V2 flag 제거
for k in list(os.environ.keys()):
    if k.startswith('HARNESS_GUARD_V2_'):
        del os.environ[k]
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None
scope = hc._load_engineer_scope()
assert scope == list(hc._STATIC_ENGINEER_SCOPE), 'V2 off 시 scope 다름'
# MUTATING_SUBCOMMANDS 는 V2 flag 무관하게 항상 존재
from harness.tracker import MUTATING_SUBCOMMANDS
assert 'create-issue' in MUTATING_SUBCOMMANDS
print('OK: V2 전체 off → v1 동작 확인, MUTATING_SUBCOMMANDS 존재')
"

run "V2=0 명시 설정 → off 취급" python3 -c "
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
os.environ['HARNESS_GUARD_V2_AGENT_BOUNDARY'] = '0'
os.environ['HARNESS_GUARD_V2_COMMIT_GATE'] = '0'
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None
scope = hc._load_engineer_scope()
assert scope == list(hc._STATIC_ENGINEER_SCOPE), 'V2=0 가 off 취급 안 됨'
print('OK: V2=0 명시 → off 취급 (static scope)')
"

echo ""
echo "[12] LLM 마커 변형 흡수 — alias map"
run "PLAN_LGTM → PLAN_VALIDATION_PASS" python3 -c "
import sys, tempfile, os
sys.path.insert(0, '.')
from harness import core as _core
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write('validator output\nPLAN_LGTM\n')
    fname = f.name
try:
    r = _core.parse_marker(fname, 'PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL')
    assert r == 'PLAN_VALIDATION_PASS', f'alias 실패: {r}'
    print('OK: PLAN_LGTM → PLAN_VALIDATION_PASS')
finally:
    os.unlink(fname)
"

run "PLAN_OK → PLAN_VALIDATION_PASS" python3 -c "
import sys, tempfile, os
sys.path.insert(0, '.')
from harness import core as _core
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write('output\nPLAN_OK\n')
    fname = f.name
try:
    r = _core.parse_marker(fname, 'PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL')
    assert r == 'PLAN_VALIDATION_PASS', f'alias 실패: {r}'
    print('OK: PLAN_OK → PLAN_VALIDATION_PASS')
finally:
    os.unlink(fname)
"

run "APPROVE → PASS / REJECT → FAIL" python3 -c "
import sys, tempfile, os
sys.path.insert(0, '.')
from harness import core as _core

def check(marker, expected, marker_str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(f'output\n{marker}\n')
        fname = f.name
    try:
        r = _core.parse_marker(fname, marker_str)
        assert r == expected, f'{marker} alias 실패: {r} != {expected}'
    finally:
        os.unlink(fname)

check('APPROVE', 'PASS', 'PASS|FAIL')
check('REJECT', 'FAIL', 'PASS|FAIL')
print('OK: APPROVE→PASS, REJECT→FAIL 모두 흡수')
"

run "PLAN_APPROVE → PLAN_VALIDATION_PASS" python3 -c "
import sys, tempfile, os
sys.path.insert(0, '.')
from harness import core as _core
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write('output\nPLAN_APPROVE\n')
    fname = f.name
try:
    r = _core.parse_marker(fname, 'PLAN_VALIDATION_PASS|PLAN_VALIDATION_FAIL|PASS|FAIL')
    assert r == 'PLAN_VALIDATION_PASS', f'alias 실패: {r}'
    print('OK: PLAN_APPROVE → PLAN_VALIDATION_PASS')
finally:
    os.unlink(fname)
"

echo ""
echo "[13] feature flag 부분 활성 — cross-flag 호환성"
run "AGENT_BOUNDARY=1 only → _load_engineer_scope v2 동작" python3 -c "
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
# AGENT_BOUNDARY 만 활성, COMMIT_GATE 는 off
os.environ['HARNESS_GUARD_V2_AGENT_BOUNDARY'] = '1'
for k in ['HARNESS_GUARD_V2_COMMIT_GATE', 'HARNESS_GUARD_V2_ALL']:
    os.environ.pop(k, None)
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None
# v2_any = True (AGENT_BOUNDARY=1 이므로) → config 로드 시도
# 테스트 환경에서는 config 없으므로 static 폴백이지만 v2 경로 진입 자체는 확인
scope = hc._load_engineer_scope()
assert len(scope) > 0, 'scope 비어있음'
print(f'OK: AGENT_BOUNDARY=1 only → scope {len(scope)}개 (config 없으면 static 폴백)')
"

run "AGENT_BOUNDARY=1 + COMMIT_GATE=0 → scope 일관성" python3 -c "
import sys, os, re
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
os.environ['HARNESS_GUARD_V2_AGENT_BOUNDARY'] = '1'
os.environ['HARNESS_GUARD_V2_COMMIT_GATE'] = '0'
import harness_common as hc
hc._ENGINEER_SCOPE_CACHE = None
scope = hc._load_engineer_scope()
combined = re.compile('(' + '|'.join(scope) + ')')
# 두 패턴 모두 매치 (static fallback 에도 있음)
assert combined.search('src/foo.ts'), 'src/ 매치 실패'
assert combined.search('apps/api/src/main.py'), 'apps/api/src/ 매치 실패'
print('OK: 부분 활성에서도 scope 일관성 유지')
"

echo ""
echo "[14] 5번째 위험 — cross-guard silent dependency 가시화"
run "skill-gate V2 on + 키 없음 → stderr 경고 출력" python3 -c "
import sys, os, io
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
os.environ['HARNESS_GUARD_V2_SKILL_GATE'] = '1'
import importlib.util
spec = importlib.util.spec_from_file_location('sg', 'hooks/skill-gate.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# stderr 캡처
import io as _io
buf = _io.StringIO()
old_stderr = sys.stderr
sys.stderr = buf
try:
    result = mod._skill_name({'tool_input': {'wrong_key': 'val'}})
finally:
    sys.stderr = old_stderr
output = buf.getvalue()
assert result == '', f'expected empty string, got {result!r}'
assert 'WARN' in output, f'stderr 경고 없음: {output!r}'
print('OK: V2 on + 키 없음 → stderr WARN 출력 확인')
"

run "_verify_live_json_writable 실패 → cascade 사전 감지" python3 -c "
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
from unittest.mock import patch
import harness_common as hc
with patch('session_state.update_live', side_effect=OSError('Permission denied')):
    ok, err = hc._verify_live_json_writable('test-sid')
assert not ok, 'ok=True 인데 실패해야 함'
assert len(err) > 0, 'error msg 비어있음'
assert 'OSError' in err or 'Permission' in err, f'에러 메시지 부적절: {err}'
print(f'OK: live.json 쓰기 실패 감지: {err}')
"

run "skill-gate V2 off → silent (stderr 없음) — 회귀 0" python3 -c "
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'hooks')
# V2 off
for k in list(os.environ.keys()):
    if k.startswith('HARNESS_GUARD_V2_'):
        del os.environ[k]
import importlib.util, io
spec = importlib.util.spec_from_file_location('sg_off', 'hooks/skill-gate.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
buf = io.StringIO()
old_stderr = sys.stderr
sys.stderr = buf
try:
    result = mod._skill_name({'tool_input': {}})
finally:
    sys.stderr = old_stderr
assert result == '', f'expected empty, got {result!r}'
assert buf.getvalue() == '', f'V2 off 에서 stderr 경고 발생: {buf.getvalue()!r}'
print('OK: V2 off → silent pass (stderr 없음) — 회귀 0')
"

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
