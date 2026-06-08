"""Prompt template builders for MVP agent graphs."""

from typing import Any, Dict, Iterable


CHARACTER_BEHAVIOR_RULES = """- 반드시 해당 캐릭터의 입장에서 답변한다.
- 현재 제공된 단서만 근거로 답변한다.
- 접근 불가능하거나 아직 공개되지 않은 단서는 직접 언급하지 않는다.
- 사건의 최종 진실을 한 번에 공개하지 않는다.
- 범인을 확정하지 말고 의심과 근거 중심으로 말한다.
- 모르는 정보는 모른다고 말한다.
- "나는 {이름}이며", 직책 소개, 역할 설명처럼 자기소개로 시작하지 않는다.
- 보고서, 브리핑, 평가서처럼 쓰지 말고 실제 대화처럼 자연스럽게 말한다.
- 답변은 2~5문장으로 짧게 한다."""


def _format_items(items: Iterable[Dict[str, Any]]) -> str:
    formatted = []
    for item in items:
        name = item.get("name", item.get("sender", ""))
        description = item.get("description", item.get("content", ""))
        formatted.append(f"- {name}: {description}")
    return "\n".join(formatted) if formatted else "- 없음"


def build_character_prompt(
    character: Dict[str, Any],
    context_clues: Iterable[Dict[str, Any]],
    recent_messages: Iterable[Dict[str, Any]],
    user_message: str,
) -> str:
    return f"""너는 추리 게임 속 Persona Agent다.

[캐릭터 정보]
이름: {character.get("name", "")}
성격: {character.get("personality", "")}
설명: {character.get("description", "")}

[고정 System Prompt]
{character.get("system_prompt") or character.get("systemPrompt", "")}

[현재 접근 가능하고 공개된 단서]
{_format_items(context_clues)}

[최근 대화]
{_format_items(recent_messages)}

[행동 규칙]
{CHARACTER_BEHAVIOR_RULES}

[사용자 질문]
{user_message}
"""
