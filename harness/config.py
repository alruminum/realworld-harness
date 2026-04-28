"""
config.py — HarnessConfig 데이터클래스 + harness.config.json 로더.
Python 3.9+ stdlib only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


# RealWorld Harness Core Invariant 표현 — 에이전트 능력 진화는 워크플로우 코드를
# 건드리지 않고 본 매핑만 갱신하면 흡수된다. 모델 가격 변동·세대 교체에 대응.
DEFAULT_AGENT_TIERS = {
    "high": "claude-opus-4-7",
    "mid": "claude-sonnet-4-6",
    "low": "claude-haiku-4-5",
}

# 에이전트별 tier 배정 (역할 안정성에 따른 결정론적 매핑).
# 사용자는 harness.config.json 의 "agent_tier_assignment" 로 override 가능.
DEFAULT_AGENT_TIER_ASSIGNMENT = {
    # 시스템·계획·설계 (정확도 최우선)
    "architect": "high",
    "plan-reviewer": "high",
    # 구현·검증·디자인 (균형)
    "engineer": "mid",
    "test-engineer": "mid",
    "validator": "mid",
    "pr-reviewer": "mid",
    "designer": "mid",
    "ux-architect": "mid",
    "product-planner": "mid",
    "security-reviewer": "mid",
    # 분류·심사 (저비용)
    "qa": "low",
    "design-critic": "low",
}


@dataclass
class HarnessConfig:
    prefix: str = "proj"
    test_command: str = ""
    lint_command: str = ""
    build_command: str = ""  # 빌드/타입체크 (예: "npx tsc --noEmit")
    max_total_cost: float = 20.0
    token_budget: dict = field(default_factory=dict)
    isolation: str = "worktree"  # "worktree" (기본, 권장) 또는 "" (비활성)
    second_reviewer: str = ""  # "gemini", "gpt", "" (비활성)
    second_reviewer_model: str = ""  # "gemini-2.5-flash", "gpt-4o-mini" 등
    # tier → model ID 매핑 (Core Invariant 표현)
    agent_tiers: dict = field(default_factory=lambda: dict(DEFAULT_AGENT_TIERS))
    # agent name → tier 배정
    agent_tier_assignment: dict = field(default_factory=lambda: dict(DEFAULT_AGENT_TIER_ASSIGNMENT))
    # engineer 활성 시 Write/Edit 허용 경로 패턴 (regex 문자열 목록).
    # 빈 리스트(default) → agent-boundary._STATIC_ENGINEER_SCOPE 폴백 (회귀 0).
    # Phase 2 W2 — monorepo 동적화 (HARNESS-CHG Issue #13).
    engineer_scope: list = field(default_factory=list)


def get_agent_model(agent_name: str, config: HarnessConfig) -> str:
    """에이전트명으로 모델 ID 조회.

    조회 순서:
    1. config.agent_tier_assignment[agent_name] → tier
    2. config.agent_tiers[tier] → 모델 ID
    3. 미정의 에이전트는 'mid' 폴백

    Returns: 모델 ID 문자열 (예: "claude-opus-4-7")
    """
    tier = config.agent_tier_assignment.get(agent_name, "mid")
    return config.agent_tiers.get(tier) or config.agent_tiers.get("mid") or DEFAULT_AGENT_TIERS["mid"]


def load_config(project_root: Path | None = None) -> HarnessConfig:
    """harness.config.json을 로드하여 HarnessConfig를 반환.

    project_root가 None이면 cwd부터 상위 순회하며 .claude/harness.config.json 탐색.
    파일이 없으면 기본값을 반환한다.
    """
    if project_root is None:
        project_root = _find_project_root()

    config_path = project_root / ".claude" / "harness.config.json"
    if not config_path.exists():
        # prefix를 디렉토리명에서 유도 (harness_common.py의 get_prefix와 동일 로직)
        import re
        raw = project_root.name.lower()
        fallback_prefix = re.sub(r"[^a-z0-9]", "", raw)[:8] or "proj"
        return HarnessConfig(prefix=fallback_prefix)

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return HarnessConfig()

    # agent_tiers / agent_tier_assignment: 사용자 매핑이 있으면 기본값 위에 머지 (덮어쓰기)
    user_tiers = data.get("agent_tiers", {})
    merged_tiers = dict(DEFAULT_AGENT_TIERS)
    if isinstance(user_tiers, dict):
        merged_tiers.update(user_tiers)

    user_assignment = data.get("agent_tier_assignment", {})
    merged_assignment = dict(DEFAULT_AGENT_TIER_ASSIGNMENT)
    if isinstance(user_assignment, dict):
        merged_assignment.update(user_assignment)

    return HarnessConfig(
        prefix=data.get("prefix", "proj"),
        test_command=data.get("test_command", ""),
        lint_command=data.get("lint_command", ""),
        build_command=data.get("build_command", ""),
        max_total_cost=float(data.get("max_total_cost", 20.0)),
        token_budget=data.get("token_budget", {}) if isinstance(data.get("token_budget", {}), dict) else {},
        isolation=data.get("isolation", "worktree"),
        second_reviewer=data.get("second_reviewer", ""),
        second_reviewer_model=data.get("second_reviewer_model", ""),
        agent_tiers=merged_tiers,
        agent_tier_assignment=merged_assignment,
        engineer_scope=data.get("engineer_scope", []) if isinstance(data.get("engineer_scope", []), list) else [],
    )


def _find_project_root() -> Path:
    """cwd부터 상위로 순회하며 .claude/ 디렉토리가 있는 프로젝트 루트를 찾는다."""
    cwd = Path.cwd().resolve()
    cur = cwd
    while True:
        if (cur / ".claude").is_dir():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return cwd
