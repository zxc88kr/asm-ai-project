"""Character chat graph MVP wrapper.

This module keeps the graph boundary separate from FastAPI. It does not depend
on LangGraph yet; the public `invoke` shape is compatible with moving to a
LangGraph implementation later.
"""

from typing import Any, Callable, Dict, List

from agents import adapters
from agents.guard import (
    filter_context_clues,
    filter_locked_clues,
    find_locked_clue_leaks,
    safe_response_for_spoiler_leak,
)
from agents.prompts.templates import build_character_prompt
from agents.types import CharacterChatState


class AgentGenerationError(RuntimeError):
    """Raised when an external model call fails after the user turn is saved."""


class CharacterChatGraph:
    def __init__(
        self,
        adapter_module: Any = adapters,
        reply_generator: Callable[
            [str, Dict[str, Any], str, List[Dict[str, Any]]],
            str,
        ] = None,
    ) -> None:
        self.adapters = adapter_module
        self.reply_generator = reply_generator

    def _generate_reply(
        self,
        prompt: str,
        character: Dict[str, Any],
        user_message: str,
        context_clues: List[Dict[str, Any]],
        state: CharacterChatState,
    ) -> str:
        if state.get("llm_response"):
            return state["llm_response"]
        if self.reply_generator is not None:
            return self.reply_generator(prompt, character, user_message, context_clues)
        return self.adapters.generate_character_reply(
            prompt,
            character,
            user_message,
            context_clues,
        )

    @staticmethod
    def _extract_used_clue_ids(
        response: str,
        context_clues: List[Dict[str, Any]],
    ) -> List[int]:
        used_clue_ids = []
        for clue in context_clues:
            clue_name = str(clue.get("name", "")).strip()
            if clue_name and clue_name in response:
                used_clue_ids.append(int(clue["id"]))
        return used_clue_ids

    def invoke(self, state: CharacterChatState) -> Dict[str, Any]:
        user_id = state["user_id"]
        character_id = int(state["character_id"])
        user_message = state["user_message"]
        debug_trace = list(state.get("debug_trace", []))

        character = self.adapters.get_character(character_id)
        recent_messages = self.adapters.get_recent_messages(user_id, character_id)
        accessible_clues = self.adapters.get_accessible_clues(character_id)
        unlocked_clue_ids = self.adapters.get_unlocked_clue_ids(user_id)
        context_clues = filter_context_clues(
            character_id=character_id,
            clues=accessible_clues,
            unlocked_ids=unlocked_clue_ids,
        )
        locked_clues = filter_locked_clues(accessible_clues, unlocked_clue_ids)
        prompt = build_character_prompt(
            character=character,
            context_clues=context_clues,
            recent_messages=recent_messages,
            user_message=user_message,
        )
        debug_trace.append(
            {
                "step": "build_character_prompt",
                "character_id": character_id,
                "context_clue_ids": [clue["id"] for clue in context_clues],
            }
        )

        self.adapters.save_message(user_id, character_id, "me", user_message)

        try:
            llm_response = self._generate_reply(
                prompt,
                character,
                user_message,
                context_clues,
                state,
            )
        except Exception as exc:
            debug_trace.append({"step": "llm_generation_failed"})
            raise AgentGenerationError("character reply generation failed") from exc

        leaked_clues = find_locked_clue_leaks(llm_response, locked_clues)
        if leaked_clues:
            debug_trace.append(
                {
                    "step": "spoiler_guard_replaced_response",
                    "leaked_clue_ids": [clue["id"] for clue in leaked_clues],
                }
            )
            llm_response = safe_response_for_spoiler_leak()
        used_clue_ids = self._extract_used_clue_ids(llm_response, context_clues)

        self.adapters.save_message(
            user_id,
            character_id,
            str(character.get("name", character_id)),
            llm_response,
        )

        return {
            "content": llm_response,
            "prompt": prompt,
            "used_clue_ids": used_clue_ids,
            "suggested_questions": [],
            "debug_trace": debug_trace,
        }


character_chat_graph = CharacterChatGraph()
