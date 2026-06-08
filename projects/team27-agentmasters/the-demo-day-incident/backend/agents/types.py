"""Typed graph state definitions for agent MVP flows."""

from typing import Any, Dict, List, Optional, Set, TypedDict


class CharacterChatState(TypedDict, total=False):
    user_id: str
    character_id: int
    user_message: str
    character: Optional[Dict[str, Any]]
    recent_messages: List[Dict[str, Any]]
    accessible_clues: List[Dict[str, Any]]
    unlocked_clue_ids: Set[int]
    context_clues: List[Dict[str, Any]]
    prompt: str
    llm_response: str
    used_clue_ids: List[int]
    suggested_questions: List[str]
    debug_trace: List[Dict[str, Any]]
    error: Optional[str]


class AriaClueExplainState(TypedDict, total=False):
    user_id: str
    clue_id: int
    clue: Optional[Dict[str, Any]]
    is_unlocked: bool
    aria_scripts: List[str]
    explanation: str
    next_unlock: Optional[Dict[str, Any]]
    debug_trace: List[Dict[str, Any]]
    error: Optional[str]


class DeductionEvaluateState(TypedDict, total=False):
    user_id: str
    content: str
    selected_target_id: int
    selected_clue_ids: List[int]
    unlocked_clue_ids: Set[int]
    is_correct: bool
    failure_reason: Optional[str]
    comment: str
    debug_trace: List[Dict[str, Any]]
