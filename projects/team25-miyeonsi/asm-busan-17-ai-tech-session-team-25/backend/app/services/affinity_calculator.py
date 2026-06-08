"""
호감도(Affinity) 증감 연산 엔진.

유저 발화의 긍정/부정 신호와, 직전에 결정된 캐릭터 감정(emotion_code)을 종합해
이번 턴의 호감도 변동치(affinity_delta)를 계산한다.

LLM 없이 동작하는 가벼운 룰 기반 모듈이라 키가 없어도 항상 작동한다.
호감도 점수 범위는 0~100으로 가정하며, story_engine의 분기 조건도 이 척도를 공유한다.
"""

from typing import Dict, Tuple

# 호감도 점수 한계
AFFINITY_MIN = 0
AFFINITY_MAX = 100

# 캐릭터가 느낀 감정(emotion_code)이 호감도에 주는 기본 가중치.
# 캐릭터가 기뻐했다면 관계가 가까워진 것이고, 서운했다면 멀어진 것으로 본다.
_EMOTION_WEIGHT: Dict[str, int] = {
    "smile": 3,
    "surprise": 2,
    "idle": 0,
    "sad": -3,
}

# 유저 발화에서 잡아내는 긍/부정 신호 키워드(간이 휴리스틱).
_POSITIVE_KEYWORDS = (
    "좋아", "고마", "최고", "사랑", "재밌", "행복", "기대", "설레",
    "멋지", "예쁘", "귀여", "응 좋", "같이", "함께", "ㅎㅎ", "ㅋㅋ", "♥", "❤",
)
_NEGATIVE_KEYWORDS = (
    "싫어", "별로", "짜증", "그만", "관심없", "노잼", "최악", "꺼져",
    "바보", "멍청", "지겨", "귀찮",
)


def _keyword_score(user_message: str) -> int:
    """유저 발화의 긍/부정 키워드를 세어 점수화한다."""
    text = user_message.lower()
    score = 0
    for kw in _POSITIVE_KEYWORDS:
        if kw in text:
            score += 2
    for kw in _NEGATIVE_KEYWORDS:
        if kw in text:
            score -= 3
    # 한 발화의 키워드 영향력은 과도하지 않게 ±4로 제한
    return max(-4, min(4, score))


def compute_delta(user_message: str, emotion_code: str = "idle") -> int:
    """이번 턴의 호감도 증감치를 계산한다.

    Args:
        user_message: 유저가 입력한 발화.
        emotion_code: dialogue_generator가 결정한 캐릭터 감정 코드.

    Returns:
        이번 턴 호감도 변동치(정수). 통상 -7 ~ +6 범위.
    """
    delta = _EMOTION_WEIGHT.get(emotion_code, 0)
    delta += _keyword_score(user_message)
    return delta


def apply_delta(current_affinity: int, delta: int) -> int:
    """현재 호감도에 변동치를 적용하고 0~100 범위로 클램프해 반환한다."""
    return max(AFFINITY_MIN, min(AFFINITY_MAX, current_affinity + delta))


def step(current_affinity: int, user_message: str, emotion_code: str = "idle") -> Tuple[int, int]:
    """변동치 계산과 적용을 한 번에 수행하는 편의 함수.

    Returns:
        (delta, new_affinity) 튜플.
    """
    delta = compute_delta(user_message, emotion_code)
    return delta, apply_delta(current_affinity, delta)
