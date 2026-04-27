# Migration from ~/.claude (Source) to RealWorld Harness Plugin

> ~/.claude 에 작동 중인 하네스 시스템을 RealWorld Harness 플러그인으로 전환하는 가이드.

작성: 2026-04-27 / 대상: ~/.claude 에 RWHarness 의 source 시스템(hooks/, harness/, agents/, orchestration/ 등)이 활성화돼있는 사용자

---

## ⚠️ 사전 주의

- **새 Claude Code 세션을 열어도 ~/.claude 환경은 동일** — 새 세션 = 깨끗한 컨텍스트지만 settings.json + hooks/* 는 모든 세션이 공유. 단순히 새 세션 만으로는 정리 불가.
- 진짜 안전한 흐름: **Claude Code 자체 종료(quit) → 터미널에서 백업 + settings 무력화 → Claude 재시작 → 플러그인 install → 재시작 → 나머지 정리**.
- "터미널" = 일반 셸(Mac Terminal, iTerm 등). "Claude 세션" = `/plugin` 명령 등 가능한 Claude Code 안.
- ~/.claude 전체 백업이 1단계. 5분 보호 작업.
- 활성 화이트리스트 프로젝트(`/harness-list` 로 확인)에서 *진행 중인 작업* 이 있으면 정리 후 시작.

---

## 1. Claude Code 완전 종료 (필수)

작업 중인 모든 Claude Code 창 저장 후 quit. 메뉴 → Quit Claude Code (Cmd+Q). 백그라운드 프로세스도 종료.

검증 (터미널):
```bash
pgrep -fl "Claude Code" || echo "Claude Code 종료됨"
```

---

## 2. 백업 (5분, 필수, 터미널 작업)

```bash
DATE=$(date +%Y%m%d_%H%M)
cp -R ~/.claude ~/.claude.bak.$DATE
echo "백업 위치: ~/.claude.bak.$DATE"
```

→ 문제 시 롤백: `rm -rf ~/.claude && mv ~/.claude.bak.$DATE ~/.claude`

---

## 3. settings.json hooks 섹션 무력화 (터미널 작업)

source 시스템의 23개 훅이 ~/.claude/settings.json 에 등록돼있음. 다음 Claude Code 시작 시 플러그인과 *중복* 실행 위험. 미리 제거.

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak

python3 - <<'PY'
import json, os
p = os.path.expanduser('~/.claude/settings.json')
d = json.load(open(p))
removed = d.pop('hooks', None)
json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
print("hooks 섹션 제거 완료" if removed else "hooks 섹션 없음 — skip")
PY
```

이 시점부터 다음 Claude 세션에서는 ~/.claude/hooks/* 의 훅이 발동 *안 함* → 정리 작업이 자기 발판 부수지 않음.

---

## 4. RWHarness 플러그인 install (Claude Code 재시작 후)

Claude Code 재시작 → 새 세션 (이때는 ~/.claude 훅 + 플러그인 모두 비활성 상태):

```
/plugin marketplace add alruminum/realworld-harness
/plugin install realworld-harness
```

**Claude Code 다시 한 번 완전 재시작** (플러그인 hooks/hooks.json 활성화). 검증:

```bash
# 새 Claude 세션의 Bash 도구 또는 일반 터미널에서
echo $CLAUDE_PLUGIN_ROOT
# 예: /Users/<name>/.claude/plugins/cache/.../realworld-harness/<version>
```

→ env 가 set 됐으면 플러그인 활성. 이제 RWHarness 의 23개 훅이 hooks.json 으로 발동.

---

## 5. ~/.claude 의 source 디렉토리 삭제 (터미널 작업)

이 시점에 ~/.claude/hooks 등 source 디렉토리는 *어디서도 참조 안 됨* (settings.json hooks 제거 + 플러그인이 PLUGIN_ROOT 로 작동). 안전 삭제.

```bash
rm -rf ~/.claude/hooks
rm -rf ~/.claude/harness
rm -rf ~/.claude/agents
rm -rf ~/.claude/orchestration
rm -rf ~/.claude/templates

rm -f ~/.claude/scripts/setup-harness.sh
rm -f ~/.claude/scripts/harness-review.py
rm -f ~/.claude/scripts/classify-miss-report.py
rmdir ~/.claude/scripts 2>/dev/null   # 비어있으면 삭제

rm -f ~/.claude/.harness-infra        # 인프라 프로젝트 마커
```

### 절대 보존 (사용자 데이터)

| 파일 / 디렉토리 | 역할 |
|---|---|
| `~/.claude/CLAUDE.md` | 사용자 글로벌 룰 |
| `~/.claude/MEMORY.md`, `~/.claude/memory/` | 사용자 메모리 |
| `~/.claude/projects/` | Claude Code 프로젝트 메모리 |
| `~/.claude/harness-projects.json` | 화이트리스트 (등록된 프로젝트 목록) |
| `~/.claude/harness-state/` | 프로젝트별 세션 상태 (있다면) |
| `~/.claude/harness-logs/` | 실행 로그 |
| `~/.claude/harness-memory.md` | 사용자 하네스 메모리 |
| `~/.claude/plugins/` | Claude Code 플러그인 캐시 (RWHarness 도 여기) |
| `~/.claude/settings.json` | hooks 섹션만 제거, 나머지 보존 |
| `~/.claude/commands/` 의 개인 스킬 | (예: `hardcarry.md`, `softcarry.md` 같은 개인 임시 스킬) |
| `~/.claude/dongchan-style/` 또는 개인 스타일 가이드 | 사용자 개인 자료 |

---

## 6. 검증 (10분)

### 6.1 플러그인 활성 확인

```bash
ls "$CLAUDE_PLUGIN_ROOT/hooks/" | wc -l   # 23개 .py 파일
cat "$CLAUDE_PLUGIN_ROOT/hooks/hooks.json" | python3 -m json.tool | head -5
```

### 6.2 화이트리스트 등록된 프로젝트에서 훅 동작 확인

```bash
cd /path/to/<your-active-project>
ls .claude/harness-state/ 2>/dev/null
```

활성 프로젝트에서 Claude Code 세션 열고:

```
/harness-list   # 등록된 프로젝트 목록
```

### 6.3 quickstart §1 실행 (5분)

[`docs/e2e-quickstart.md §1`](e2e-quickstart.md) 따라 `/quick` 루프 1건 통과 확인.

---

## 7. 롤백 (문제 발생 시)

```bash
# 1) 플러그인 제거
# Claude Code 세션에서:
/plugin uninstall realworld-harness

# 2) ~/.claude 백업 복원
DATE=20260427_XXXX   # 본인 백업 시점으로
rm -rf ~/.claude
mv ~/.claude.bak.$DATE ~/.claude

# 3) Claude Code 재시작
```

---

## 8. 정리 완료 (수일 사용 후 문제 없으면)

```bash
rm -rf ~/.claude.bak.<date>
rm -f ~/.claude/settings.json.bak
```

---

## 자주 묻는 질문

**Q. 플러그인 install 후에도 기존 화이트리스트 프로젝트들이 자동으로 작동하나?**
→ 응. `~/.claude/harness-projects.json` 그대로 보존되고, 플러그인 훅이 그 목록 참조.

**Q. ~/.claude/agents/ 안에 개인 에이전트 파일을 추가했었는데?**
→ 4단계 삭제 *전에* 그 파일들만 별도 디렉토리로 옮겨두기. 플러그인 모드에선 `${CLAUDE_PLUGIN_ROOT}/agents/` 가 정본이라 ~/.claude/agents/ 의 개인 추가는 작동 안 함. 대신 *프로젝트별* `.claude/agent-config/<agent-name>.md` 로 옮기는 게 권장.

**Q. ~/.claude/orchestration/ 의 업데이트 기록이 사라지면?**
→ RWHarness 의 `orchestration/upstream/` 에 source 환경의 운영 룰 + 업데이트 기록 스냅샷이 보존돼있음 (참조 전용). 본 source ~/.claude/orchestration/ 의 *새* 변경 기록은 삭제 전 별도 보관 권장.

**Q. ~/.claude/.bak* 파일들은?**
→ 모두 source 환경의 deprecated 백업. 4단계 정리 시 같이 삭제 가능.

**Q. plugins 캐시 손대면 안 되나?**
→ `~/.claude/plugins/{cache,marketplaces,data}/` 는 Claude Code 가 관리. 절대 직접 수정·삭제 X (RWHarness 자체도 그 안에 캐시됨).
