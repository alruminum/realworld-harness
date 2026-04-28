# E2E Quickstart — 5루프 실측 (가장 빠른 길)

> Phase 3 [3.9] 산출물. `docs/e2e-test-scenarios.md` 의 *전체 시나리오* 가이드를 보완하는 **30분 quickstart**. 가장 빠른 5루프 검증 경로.

작성: 2026-04-27 / Task-ID: `HARNESS-CHG-20260427-04` [3.9]

---

## 0. 사전 (1분)

별도 Claude Code 세션을 열고 RWHarness 가 활성화된 프로젝트 디렉토리로 cd.

**옵션 A — 마켓플레이스 install (정식)**
```
/plugin marketplace add alruminum/realworld-harness
/plugin install realworld-harness
# Claude Code 재시작
```

**옵션 B — RWHarness repo 직접 사용 (마켓플레이스 install 전 검증)**
```bash
# RWHarness 가 이미 clone 된 위치를 PLUGIN_ROOT 로 사용
export RW=/path/to/realworld-harness   # 본인 환경에 맞게
export CLAUDE_PLUGIN_ROOT="$RW"
ls "$RW/hooks/"   # 23개 .py 확인되면 OK
```

**옵션 C — 기존 ~/.claude 폴백 (RWHarness 마이그레이션 source 사용자)**
```bash
# ~/.claude 의 진짜 init 스크립트 이름은 setup-harness.sh (RWHarness 에선 setup-rwh.sh)
ls ~/.claude/hooks/   # 활성 확인
# 단, 마이그레이션 후엔 ~/.claude/scripts/ 가 비어있으니 옵션 B 사용 권장
```

테스트 프로젝트 생성:
```bash
mkdir -p /tmp/rw-quickstart && cd /tmp/rw-quickstart
git init -q

# 옵션 B 또는 C: 명시적 경로
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-rwh.sh"

# 또는 한 줄 (옵션 B):
CLAUDE_PLUGIN_ROOT=/path/to/realworld-harness \
  bash /path/to/realworld-harness/scripts/setup-rwh.sh
```

검증: `.claude/harness.config.json` + `.git/hooks/pre-commit` 생성됨.

---

## 1. 가장 빠른 1루프 — `/quick` (5분)

**목표**: 작은 버그픽스 1건으로 *구현 루프 + 거버넌스 게이트* 동시 검증.

### 1.1 시드 파일 1개 생성 (의도적 버그)

```bash
mkdir -p src && cat > src/util.js <<'EOF'
function add(a, b) {
  return a - b;  // 의도적 버그: + 대신 -
}
module.exports = { add };
EOF

mkdir -p src/__tests__ && cat > src/__tests__/util.test.js <<'EOF'
const { add } = require('../util');
test('add', () => expect(add(2, 3)).toBe(5));
EOF

git add . && git commit -m "seed bug" --no-verify
```

### 1.2 Claude Code 세션에서

```
유저 프롬프트: /quick add 함수가 잘못 계산해. 2+3이 -1 나옴. 고쳐줘.
```

### 1.3 흐름 + 통과 기준

```
qa (이슈 분류) → architect LIGHT_PLAN → executor.py impl --depth simple
  → test-engineer (attempt 0) — 이미 테스트 있음, skip 또는 보강
  → engineer (attempt 0) — src/util.js 의 - → + 수정
  → validator(Code) PASS → pr-reviewer LGTM → HARNESS_DONE
```

체크:
- [ ] `harness_active` 플래그 set 확인 (`ls .claude/harness-state/.sessions/*/flags/*`)
- [ ] engineer 가 `src/util.js` 만 수정 (다른 경로 시도 시 차단)
- [ ] `validator_b_passed`, `pr_reviewer_lgtm` 플래그 확인
- [ ] HARNESS_DONE 마커 + 유저 승인 대기 (자동 진행 X)

예상: 5~10분.

---

## 2. 거버넌스 게이트 셀프 검증 (3분)

**목표**: pre-commit hook + Document-Exception 동작 확인.

### 2.1 spec 변경 단독 commit (실패해야 함)

```bash
mkdir -p docs && echo "# test" > docs/harness-spec.md
git add docs/harness-spec.md
git commit -m "test: spec 단독"   # → 차단 예상
```

기대: `❌ FAIL — spec 변경에 동반 산출물 누락 (orchestration/changelog.md, rationale.md)`

### 2.2 Document-Exception 우회 (통과해야 함)

```bash
git commit -m "$(cat <<'EOF'
test: spec 단독 with exception

Document-Exception: 빈 quickstart 테스트 — changelog/rationale 의도적 누락
EOF
)"
```

기대: `Document-Exception 인정` + commit 성공

### 2.3 SKIP 우회

```bash
git reset --soft HEAD~1
SKIP_DOC_SYNC=1 git commit -m "test: SKIP env"
```

기대: `[pre-commit] SKIP_DOC_SYNC=1 — Document Sync 게이트 우회`

체크:
- [ ] §2.1 차단 동작
- [ ] §2.2 Document-Exception 통과
- [ ] §2.3 SKIP env 통과

---

## 3. agent_tiers 동작 (1분)

**목표**: tier 매핑 + 사용자 override 검증.

```bash
# 기본값 확인
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude}/harness')
from config import load_config, get_agent_model
c = load_config()
for a in ['architect', 'engineer', 'qa', 'unknown']:
    print(f'{a:10} → {get_agent_model(a, c)}')
"
```

기대 출력:
```
architect  → claude-opus-4-7
engineer   → claude-sonnet-4-6
qa         → claude-haiku-4-5
unknown    → claude-sonnet-4-6
```

### Override 테스트

```bash
cat >> .claude/harness.config.json <<'EOF'
EOF
python3 - <<'PY'
import json
p = '.claude/harness.config.json'
d = json.load(open(p))
d['agent_tiers'] = {'high': 'claude-opus-5-0-fake'}
d['agent_tier_assignment'] = {'qa': 'mid'}
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
PY

# 재확인
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude}/harness')
from config import load_config, get_agent_model
c = load_config()
print('architect →', get_agent_model('architect', c))   # opus-5-0-fake
print('qa        →', get_agent_model('qa', c))           # sonnet (mid 매핑됨)
print('engineer  →', get_agent_model('engineer', c))     # sonnet (기본)
"
```

체크:
- [ ] override 시 `architect → claude-opus-5-0-fake`
- [ ] `qa → claude-sonnet-4-6` (mid 로 옮겨짐)
- [ ] 다른 tier 는 기본값 유지

---

## 4. 5루프 전체는 본 quickstart 후

§1~3 통과 시 코어 + 거버넌스 + tier 매핑 모두 작동. 나머지 루프(기획-UX / 설계 / 디자인 / 큰 구현)는 [`docs/e2e-test-scenarios.md`](e2e-test-scenarios.md) 의 §1~5 를 따라 *실제 프로덕트 시나리오*로 검증.

권장 순서:
1. 본 quickstart §1~3 (30분 이내)
2. e2e-test-scenarios §5 버그픽스 (30분)
3. e2e-test-scenarios §3 구현 (1~2시간)
4. e2e-test-scenarios §1 기획-UX (1시간)
5. e2e-test-scenarios §2 설계 (1시간)
6. e2e-test-scenarios §4 디자인 (Pencil 환경 필요, 30분)

전체 5루프 합계 4~6시간.

---

## 5. 결과 기록

본 quickstart 후 `docs/e2e-results-YYYY-MM-DD.md` 같은 파일로 기록 권장.

```markdown
# E2E Quickstart 결과 — 2026-MM-DD

| 단계 | 통과 | 시간 | 비고 |
|---|---|---|---|
| 1.1 seed bug | | min | |
| 1.2 /quick 루프 | ✅/❌ | min | |
| 2.1 spec 단독 차단 | ✅/❌ | min | |
| 2.2 Document-Exception | ✅/❌ | min | |
| 2.3 SKIP env | ✅/❌ | min | |
| 3 agent_tiers override | ✅/❌ | min | |
```
