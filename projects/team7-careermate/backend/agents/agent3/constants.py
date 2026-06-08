"""Agent3 상수 중앙 정의 (docs/08-implementation-plan.md 기준).

그래프 루프 가드와 검색 예산을 한 곳에서 관리해 노드·툴·critic이 동일 값을 참조한다.
"""

from __future__ import annotations

# ── 그래프 루프 가드 ──────────────────────────────────────────
MAX_RERUN = 1          # Gap→Job 되먹임 상한 (무한 루프 방지)
MAX_REVISIONS = 2      # Critic→Roadmap 재생성 상한
AMBIGUITY_THRESHOLD = 0.6  # (Agent3 범위 밖, 참고용)

# ── 웹검색 예산 ───────────────────────────────────────────────
MAX_SEARCH = 8         # 세션 누적 web_search 실제 API 호출 상한 (캐시 히트 제외)
DEFAULT_SEARCH_K = 5   # web_search 기본 결과 수

# ── 로드맵 기간 캡 (Plan-and-Solve) ───────────────────────────
MIN_WEEKS = 4
MAX_WEEKS = 8

# ── Critic ④ 금칙 표현 (런타임 가드레일) ──────────────────────
FORBIDDEN_PHRASES = [
    "합격 가능",
    "합격할 수 있",
    "취업 보장",
    "반드시 취업",
    "100% 합격",
    "성공 보장",
    "진로 결정",
    "확실히 합격",
]
