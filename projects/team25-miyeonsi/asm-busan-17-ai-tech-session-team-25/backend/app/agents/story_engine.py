"""
스토리 엔진: 챕터 전환·이벤트 트리거·엔딩 결정 로직.

매 턴 종료 시점에 현재 챕터/호감도/유저 발화/누적 플래그를 받아
다음 챕터로 넘어갈지, 특수 이벤트가 발생했는지, 게임이 엔딩에 도달했는지를 평가한다.

LLM 비의존 룰 기반(상태 머신)이라 결정이 결정론적이고 디버깅이 쉽다.
호감도 척도(0~100)는 affinity_calculator와, 챕터 ID(int)는 schemas와 공유한다.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# 엔딩을 의미하는 특수 챕터 ID
ENDING_CHAPTER = 99

# 지연 이벤트가 발생할 수 있는 챕터(탑승 게이트). flags["flight_delayed"] 가 켜져 있어야 한다.
_GATE_CHAPTER = 4


@dataclass
class Chapter:
    """하나의 챕터(씬) 정의."""

    id: int
    name: str
    # 다음 챕터로 넘어가기 위해 유저 발화에 포함되어야 하는 트리거 키워드들
    triggers: List[str] = field(default_factory=list)
    # 전환에 필요한 최소 호감도(이 미만이면 트리거가 있어도 넘어가지 않음)
    min_affinity: int = 0
    # 챕터 진입 후 전환을 허용하기까지 필요한 최소 대화 턴 수
    min_turns: int = 2
    # 다음 챕터 ID (None이면 엔딩 분기 판정으로 진입)
    next_id: Optional[int] = None


# 메인 스토리 라인 (기획서 시나리오 8단계 기반의 선형 진행 + 마지막에 멀티 엔딩 분기)
# ① 서비스 시작·소개는 챕터 0 진입에 포함된다. ⑧ 도착 후 엔딩 분기로 마무리된다.
STORY_LINE: Dict[int, Chapter] = {
    0: Chapter(0, "공항에서의 첫 만남", triggers=["여행", "어디", "가고싶", "시작", "안녕", "만나"], next_id=1),
    1: Chapter(1, "여행지 정하기", triggers=["파리", "도쿄", "오사카", "방콕", "런던", "뉴욕", "여기로", "이걸로", "결정", "정했"], next_id=2),
    2: Chapter(2, "항공권 검색", triggers=["검색", "찾아", "항공권", "비행기", "조회", "알아봐"], next_id=3),
    3: Chapter(3, "항공권 선택", triggers=["예약", "이 항공권", "이거", "선택", "번째", "번으로", "골랐"], min_affinity=40, next_id=4),
    4: Chapter(4, "탑승 게이트", triggers=["면세점", "게이트", "대기", "탑승", "기다"], next_id=5),
    5: Chapter(5, "기내", triggers=["기내", "비행", "이륙", "출발", "떠나", "탔"], next_id=6),
    6: Chapter(6, "도착", triggers=["도착", "내려", "왔다", "끝", "마지막"], next_id=None),  # None -> 엔딩 분기
}


@dataclass
class StoryDecision:
    """스토리 평가 결과."""

    next_chapter: int          # 다음(또는 유지될) 챕터 ID
    is_transition: bool        # 이번 턴에 씬 전환이 일어났는지
    is_ending: bool = False    # 엔딩 도달 여부
    event: Optional[str] = None  # 발생한 특수 이벤트 코드(없으면 None)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _decide_ending(affinity: int) -> str:
    """출발 시점의 누적 호감도로 멀티 엔딩을 결정한다."""
    if affinity >= 70:
        return "ending_best"     # 최고의 동행 엔딩
    if affinity >= 40:
        return "ending_good"     # 무난한 여행 엔딩
    return "ending_solo"         # 혼자 떠나는 쓸쓸한 엔딩


def _check_event(chapter_id: int, affinity: int, flags: Dict[str, Any]) -> Optional[str]:
    """챕터/호감도/플래그 조합으로 발생하는 특수 이벤트를 판정한다.

    이벤트는 각각 한 번씩만 발생하며(플래그로 중복 방지), 우선순위 순으로 평가한다.
    """
    # 1) 지연 이벤트: 탑승 게이트에서 도구가 지연 항공편을 반환한 경우(flight_delayed).
    #    "지연됐대… 너랑 더 같이 있을 수 있어 싫지만은 않아" 류의 감정 대사를 유도한다.
    if (
        chapter_id == _GATE_CHAPTER
        and flags.get("flight_delayed")
        and not flags.get("event_delay")
    ):
        return "event_delay"

    # 2) 동행 고백 이벤트: 호감도가 충분히 높을 때 한 번만 발생하는 깜짝 이벤트.
    if affinity >= 75 and not flags.get("event_confession"):
        return "event_confession"
    return None


def evaluate(
    current_chapter: int,
    affinity: int,
    user_message: str,
    flags: Optional[Dict[str, Any]] = None,
) -> StoryDecision:
    """현재 상태 기준 씬 종료/전환/엔딩 조건을 평가한다.

    Args:
        current_chapter: 현재 챕터 ID.
        affinity: 현재 누적 호감도.
        user_message: 이번 턴 유저 발화(트리거 키워드 탐지용).
        flags: 장기 메모리의 이벤트 플래그.

    Returns:
        StoryDecision. 전환이 없으면 next_chapter == current_chapter.
    """
    flags = flags or {}
    chapter = STORY_LINE.get(current_chapter)

    # 정의되지 않은(또는 엔딩 이후) 챕터: 그대로 유지
    if chapter is None:
        return StoryDecision(next_chapter=current_chapter, is_transition=False)

    # 1) 특수 이벤트 우선 평가(전환과 독립적으로 메타데이터로 전달)
    event = _check_event(current_chapter, affinity, flags)

    # 2) 전환 조건: 트리거 키워드 + 최소 호감도 + 최소 대화 턴 수 충족
    triggered = any(kw in user_message for kw in chapter.triggers)
    chapter_turns = flags.get("chapter_turns", 0)
    can_advance = (
        triggered
        and affinity >= chapter.min_affinity
        and chapter_turns >= chapter.min_turns
    )

    if not can_advance:
        return StoryDecision(
            next_chapter=current_chapter,
            is_transition=False,
            event=event,
            metadata={"reason": "조건 미충족(트리거/호감도/최소턴)", "chapter_name": chapter.name},
        )

    # 3) 엔딩 분기(next_id가 None인 마지막 챕터)
    if chapter.next_id is None:
        ending_code = _decide_ending(affinity)
        return StoryDecision(
            next_chapter=ENDING_CHAPTER,
            is_transition=True,
            is_ending=True,
            event=event,
            metadata={"ending": ending_code, "final_affinity": affinity},
        )

    # 4) 일반 챕터 전환
    next_chapter = STORY_LINE[chapter.next_id]
    return StoryDecision(
        next_chapter=next_chapter.id,
        is_transition=True,
        event=event,
        metadata={"reason": "트리거 충족", "from": chapter.name, "to": next_chapter.name},
    )
