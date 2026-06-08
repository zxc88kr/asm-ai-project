"""
Upstage Solar LLM 통신 공통 모듈.

Upstage는 OpenAI 호환 API를 제공하므로 `openai` SDK로 접근한다.
이 모듈은 '채팅 1회 호출'이라는 단일 책임만 갖고, 프롬프트 조립이나
응답 파싱(JSON 해석)은 상위 모듈(dialogue_generator)이 담당한다.

API 키가 없으면 네트워크 호출을 시도하지 않고 LLMUnavailableError를 던져
상위 모듈이 더미(fallback) 응답으로 우아하게 폴백할 수 있게 한다.
"""

from functools import lru_cache
from typing import Dict, List

from app.core.config import settings


class LLMUnavailableError(RuntimeError):
    """LLM 호출이 불가능할 때(키 없음/네트워크 오류 등) 발생. 상위에서 폴백 처리한다."""


def is_available() -> bool:
    """실제 Solar API 호출이 가능한지(키 설정 여부) 반환한다."""
    return settings.has_upstage_key


@lru_cache
def _get_client():
    """OpenAI 호환 클라이언트를 lazy 하게 생성·캐시한다.

    키가 없으면 생성 자체를 막아 의미 없는 객체가 만들어지지 않게 한다.
    openai 패키지 import 도 이 시점에야 수행하여, 키 없는 환경의 import 비용을 줄인다.
    """
    if not settings.has_upstage_key:
        raise LLMUnavailableError("UPSTAGE_API_KEY가 설정되지 않았습니다.")
    from openai import OpenAI

    return OpenAI(
        api_key=settings.UPSTAGE_API_KEY,
        base_url=settings.UPSTAGE_BASE_URL,
    )


def chat(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.8,
    max_tokens: int = 512,
    response_format: dict | None = None,
) -> str:
    """Solar 모델에 채팅 메시지를 보내고 응답 본문(content) 문자열을 반환한다.

    Args:
        messages: [{"role": "system"|"user"|"assistant", "content": str}, ...] 형식.
        temperature: 창의성(말투 다양성). 대사 생성은 0.8 권장.
        max_tokens: 최대 응답 토큰.

    Raises:
        LLMUnavailableError: 키가 없거나 API 호출이 실패한 경우.
    """
    client = _get_client()
    try:
        create_kwargs: dict = dict(
            model=settings.SOLAR_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if response_format:
            create_kwargs["response_format"] = response_format
        resp = client.chat.completions.create(**create_kwargs)
    except Exception as exc:  # openai.APIError 등 모든 통신 오류를 폴백 신호로 변환
        raise LLMUnavailableError(f"Solar API 호출 실패: {exc}") from exc

    content = resp.choices[0].message.content
    if not content:
        raise LLMUnavailableError("Solar API가 빈 응답을 반환했습니다.")
    return content.strip()
