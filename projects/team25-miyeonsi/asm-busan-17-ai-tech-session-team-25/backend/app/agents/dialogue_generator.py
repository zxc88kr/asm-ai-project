"""
대사 생성 에이전트.

단기 메모리(대화 맥락), 호감도, 챕터, 그리고 도구 호출 결과(있다면)를 종합해
Solar LLM으로 캐릭터의 최종 대사 리스트와 표정(emotion_code)을 생성한다.

LLM이 불가능하거나(키 없음) 응답 파싱에 실패해도 더미 대사로 폴백하여
게임 턴이 항상 완결되도록 보장한다.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.prompts.system_prompts import build_system_prompt, FEW_SHOT_EXAMPLES
from app.services import llm_client

# response.py의 TurnResult.emotion_code와 동일한 허용 집합
_VALID_EMOTIONS = {"idle", "smile", "sad", "surprise"}
_DEFAULT_EMOTION = "idle"


@dataclass
class DialogueResult:
    """대사 생성 결과."""

    dialogue_list: List[str] = field(default_factory=list)
    emotion_code: str = _DEFAULT_EMOTION
    is_fallback: bool = False  # True면 LLM 실패로 더미 응답 사용 → history 저장 제외용


def _build_messages(
    user_message: str,
    affinity: int,
    chapter: int,
    history: List[Dict[str, str]],
    tool_result: Optional[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
    summary: str = "",
) -> List[Dict[str, str]]:
    """LLM에 보낼 messages 배열을 조립한다."""
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": build_system_prompt(affinity, chapter, profile=profile, summary=summary),
        }
    ]
    # Few-shot 예시로 출력 포맷/말투를 고정
    messages.extend(FEW_SHOT_EXAMPLES)
    # 단기 메모리(이전 대화)
    messages.extend(history)

    # 도구 호출 결과(항공권 등)가 있으면 사실 근거로 주입
    if tool_result:
        messages.append(
            {
                "role": "system",
                "content": (
                    "[도구 조회 결과] 아래 데이터에 근거해서만 사실(가격/일정 등)을 말한다:\n"
                    + json.dumps(tool_result, ensure_ascii=False)
                ),
            }
        )

    messages.append({"role": "user", "content": user_message})
    return messages


def _extract_last_json_obj(text: str) -> Optional[str]:
    """문자열에서 마지막 완결된 JSON 오브젝트를 추출한다.

    greedy regex 대신 역방향 브레이스 매칭을 사용해
    여러 JSON 블록이 섞여 있어도 가장 마지막(완성된) 오브젝트만 반환한다.
    """
    last = text.rfind("}")
    if last == -1:
        return None
    depth = 0
    for i in range(last, -1, -1):
        if text[i] == "}":
            depth += 1
        elif text[i] == "{":
            depth -= 1
            if depth == 0:
                return text[i : last + 1]
    return None


def _parse_llm_json(raw: str) -> Optional[DialogueResult]:
    """LLM 응답 문자열에서 {dialogue, emotion} JSON을 견고하게 파싱한다.

    코드펜스·// 주석·앞뒤 잡텍스트 제거 후 마지막 유효 JSON 오브젝트를 추출한다.
    파싱 실패 시 None을 반환해 호출측이 폴백하게 한다.
    """
    text = raw.strip()
    # ```json ... ``` 같은 코드펜스 제거
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    # // 한 줄 주석 제거 (LLM이 템플릿 주석을 그대로 출력하는 경우 대비)
    text = re.sub(r"//[^\n]*", "", text)
    # 마지막 완결된 JSON 오브젝트 추출
    candidate = _extract_last_json_obj(text)
    if candidate is None:
        return None
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return None

    dialogue = data.get("dialogue")
    # 문자열 단일 응답도 허용
    if isinstance(dialogue, str):
        dialogue = [dialogue]
    if not isinstance(dialogue, list) or not dialogue:
        return None
    dialogue = [str(d) for d in dialogue if str(d).strip()]
    if not dialogue:
        return None

    emotion = data.get("emotion", _DEFAULT_EMOTION)
    if emotion not in _VALID_EMOTIONS:
        emotion = _DEFAULT_EMOTION

    return DialogueResult(dialogue_list=dialogue, emotion_code=emotion)


def _fallback(user_message: str, affinity: int) -> DialogueResult:
    """LLM 없이 동작하는 더미 대사. 호감도에 따라 톤만 약간 달리한다."""
    if affinity >= 60:
        line = "헤헤, 나도 그 기분 알아! 우리 여행 기대된다~"
        emotion = "smile"
    elif affinity >= 30:
        line = "오, 좋은데! 우리 같이 더 얘기해보자!"
        emotion = "smile"
    else:
        line = "응, 좀 더 얘기해줄래?"
        emotion = "idle"
    return DialogueResult(dialogue_list=[line], emotion_code=emotion, is_fallback=True)


def generate_dialogue(
    user_message: str,
    *,
    affinity: int = 50,
    chapter: int = 0,
    history: Optional[List[Dict[str, str]]] = None,
    tool_result: Optional[Dict[str, Any]] = None,
    profile: Optional[Dict[str, Any]] = None,
    summary: str = "",
) -> DialogueResult:
    """최종 대사와 표정을 생성한다.

    Args:
        user_message: 유저 발화.
        affinity: 현재 호감도(말투 결정).
        chapter: 현재 챕터(맥락).
        history: 단기 메모리 대화 리스트(memory.store.get_short_term 결과).
        tool_result: tool_router가 반환한 도구 결과(항공권 등). 없으면 None.
        profile: 사용자 여행 선호 프로필(store.get_profile 결과). 시스템 프롬프트에 주입.
        summary: 이전 챕터 요약 메모리(store.get_summary 결과). 시스템 프롬프트에 주입.

    Returns:
        DialogueResult(dialogue_list, emotion_code). 실패 시에도 폴백으로 항상 유효한 결과.
    """
    history = history or []

    if not llm_client.is_available():
        return _fallback(user_message, affinity)

    messages = _build_messages(
        user_message, affinity, chapter, history, tool_result, profile, summary
    )
    try:
        raw = llm_client.chat(
            messages,
            temperature=0.8,
            max_tokens=512,
            response_format={"type": "json_object"},
        )
    except llm_client.LLMUnavailableError:
        return _fallback(user_message, affinity)

    parsed = _parse_llm_json(raw)
    if parsed is None:
        return _fallback(user_message, affinity)
    return parsed


# =============================================================================
# 장기 기억 보조: 사용자 프로필 추출 / 챕터 요약 (요약 메모리)
# =============================================================================
# 추출을 허용할 프로필 키(스키마 고정). 그 외 키는 무시한다.
_PROFILE_KEYS = ("budget", "mood", "period", "companion", "destination")

_PROFILE_PROMPT = (
    "너는 여행 대화에서 사용자의 여행 선호만 뽑아내는 추출기다. "
    "아래 발화에서 '명시적으로 드러난' 선호만 JSON 으로 출력한다. 추측하지 않는다.\n"
    "키: budget(예산/가격성향), mood(여행 분위기), period(기간), companion(동행), destination(가고 싶은 도시).\n"
    "드러나지 않은 키는 아예 포함하지 않는다. 없으면 {} 만 출력한다. JSON 외 텍스트 금지."
)

_SUMMARY_PROMPT = (
    "너는 여행 미연시 게임의 대화 요약기다. 아래 대화를 한국어 2~3문장으로 압축한다. "
    "결정된 여행지·항공편, 사용자의 취향, 호감도에 영향을 준 사건 위주로 사실만 담는다. "
    "대사체가 아니라 요약 서술체로 쓴다. 요약문만 출력한다."
)


def _extract_json_obj(raw: str) -> Optional[dict]:
    """LLM 응답에서 첫 JSON 오브젝트를 추출해 dict 로 반환(실패 시 None)."""
    text = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def extract_profile(user_message: str) -> Dict[str, Any]:
    """유저 발화에서 여행 선호 프로필을 추출한다.

    명시된 선호만 담은 부분 dict 를 반환하며, 추출할 게 없거나 LLM 불가 시 빈 dict.
    호출측(routes)이 store.update_state(profile=...) 로 누적 병합하는 것을 전제로 한다.
    """
    if not llm_client.is_available() or not user_message.strip():
        return {}
    messages = [
        {"role": "system", "content": _PROFILE_PROMPT},
        {"role": "user", "content": user_message},
    ]
    try:
        raw = llm_client.chat(messages, temperature=0.0, max_tokens=200)
    except llm_client.LLMUnavailableError:
        return {}
    data = _extract_json_obj(raw)
    if not data:
        return {}
    # 허용 키 + 비어있지 않은 값만 통과시킨다.
    return {
        k: data[k]
        for k in _PROFILE_KEYS
        if data.get(k) not in (None, "", [], {})
    }


def generate_summary(
    history: List[Dict[str, str]],
    previous_summary: str = "",
) -> str:
    """단기 대화 기록을 요약 메모리 문자열로 압축한다(챕터 종료 시 호출 상정).

    LLM 불가/실패 시 기존 요약(previous_summary)을 그대로 반환해 정보 손실을 막는다.
    """
    if not history or not llm_client.is_available():
        return previous_summary

    convo = "\n".join(f"{m.get('role')}: {m.get('content', '')}" for m in history)
    context = convo if not previous_summary else f"[이전 요약]\n{previous_summary}\n\n[최근 대화]\n{convo}"
    messages = [
        {"role": "system", "content": _SUMMARY_PROMPT},
        {"role": "user", "content": context},
    ]
    try:
        raw = llm_client.chat(messages, temperature=0.3, max_tokens=256)
    except llm_client.LLMUnavailableError:
        return previous_summary
    summary = raw.strip()
    return summary or previous_summary
