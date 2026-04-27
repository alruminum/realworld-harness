# Smoke Test 가이드 — Clean Install 검증

> Phase 3 [3.5] 산출물. 외부 머신/컨테이너에서 RealWorld Harness 가 정상 설치·동작하는지 검증.

---

## 1. 목적

`~/.claude/` 가 *없는* 환경(또는 사용자가 다른 환경)에서 RealWorld Harness 를 install 후 다음을 확인한다:

1. `${CLAUDE_PLUGIN_ROOT}` 환경변수가 set되면 PLUGIN_ROOT 가 그 경로를 사용
2. 모든 Python 파일이 syntax 통과 + import 가능
3. JSON 파일(hooks.json, plugin.json, marketplace.json) 파싱 가능
4. `agent_tiers` 매핑 + 사용자 override 동작
5. `setup-rwh.sh` 신규 프로젝트 적용 시 정상 산출
6. 거버넌스 자동 게이트 (pre-commit hook + check_doc_sync.py) 동작

---

## 2. 자동 검증 (현재 머신에서 즉시 가능)

```bash
bash scripts/smoke-test.sh
```

10개 검증 영역, 50개 단위 케이스. PASS=50/FAIL=0 이면 코어 정상.

플러그인 모드 시뮬레이션:

```bash
CLAUDE_PLUGIN_ROOT=/some/other/path bash scripts/smoke-test.sh
```

→ PLUGIN_ROOT 가 그 경로를 가리키는지 확인.

---

## 3. 외부 머신/컨테이너 검증 (수동 단계)

### 3.1 Docker 컨테이너 (권장)

```bash
# RWHarness repo 루트에서
docker run --rm -it \
  -v "$(pwd):/plugin" \
  -e CLAUDE_PLUGIN_ROOT=/plugin \
  python:3.11-slim \
  bash -c "apt-get update -qq && apt-get install -qq -y git && cd /plugin && bash scripts/smoke-test.sh"
```

기대 결과: `✅ ALL PASS`

### 3.2 별도 머신 (다른 macOS/Linux)

```bash
# 1) repo clone
git clone https://github.com/alruminum/realworld-harness.git
cd realworld-harness

# 2) 자동 검증
bash scripts/smoke-test.sh

# 3) 신규 프로젝트 셋업 시뮬레이션
mkdir /tmp/test-project && cd /tmp/test-project
git init
CLAUDE_PLUGIN_ROOT=$OLDPWD bash "$CLAUDE_PLUGIN_ROOT/scripts/setup-rwh.sh"

# 4) 산출물 확인
ls -la .claude/ .git/hooks/pre-commit
cat .claude/harness.config.json   # prefix + isolation: worktree 등
```

### 3.3 Claude Code 마켓플레이스 install (실제 시나리오)

```
/plugin marketplace add alruminum/realworld-harness
/plugin install realworld-harness
# Claude Code 재시작 (hooks/hooks.json 자동 활성화)

# 새 세션에서:
/init-rwh   # → setup-rwh.sh 호출
```

검증:
- `${CLAUDE_PLUGIN_ROOT}` 자동 set 확인 (`echo $CLAUDE_PLUGIN_ROOT`)
- `~/.claude/settings.json` hooks 섹션 *건드리지 않음* (플러그인 모드 분기 미구현 상태에선 잠재 부채 — 플러그인 install 후 hooks 중복 가능성 있음, Phase 3+ 정리 대상)
- `.git/hooks/pre-commit` 자동 설치
- `.claude/harness.config.json` 생성

---

## 4. 통과 기준

| 항목 | 통과 조건 |
|---|---|
| smoke-test.sh | PASS=50/FAIL=0 |
| Docker 컨테이너 | ALL PASS |
| 별도 머신 | ALL PASS + .claude/harness.config.json 생성 |
| 마켓플레이스 install | hooks/hooks.json 자동 활성화 + setup-rwh.sh 정상 동작 |

---

## 5. 알려진 부채 (Phase 3+ 정리 대상)

1. **`setup-rwh.sh` 의 글로벌 settings.json hooks 등록 영역** — 플러그인 모드에선 hooks/hooks.json 자동 로드되므로 글로벌 settings.json 수정이 *중복*. 플러그인 모드 분기 추가 필요.
2. **PLUGIN_ROOT 폴백 검증의 cross-platform** — 현재 macOS 기준만 검증. Linux 컨테이너에선 `Path.home()` 동작 확인 필요 (Docker smoke test로 자동 검증).
3. **GitHub Actions doc-sync workflow** — 첫 PR 발생 시 가동 확인 필요 (현재는 코드만, 실행 검증 미완).

---

## 6. 자동 검증 결과 (셀프 실행)

마지막 셀프 실행: 2026-04-27 (Phase 3 [3.5])
- 환경: macOS Darwin 24.6.0, Python 3.11
- CLAUDE_PLUGIN_ROOT: 미설정 (~/.claude 폴백 모드)
- 결과: **PASS=50 / FAIL=0** ✅

추후 실행 시 본 섹션에 결과 기록 권장.
