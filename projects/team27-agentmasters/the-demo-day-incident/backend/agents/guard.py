"""Spoiler guard helpers shared by agent graphs."""

from typing import Any, Dict, Iterable, List, Set


def _accessible_character_ids(clue: Dict[str, Any]) -> Set[int]:
    raw_ids = (
        clue.get("accessible_character_ids")
        or clue.get("accessableCharacters")
        or clue.get("accessibleCharacters")
        or []
    )
    return {int(character_id) for character_id in raw_ids}


def filter_context_clues(
    character_id: int,
    clues: Iterable[Dict[str, Any]],
    unlocked_ids: Set[int],
) -> List[Dict[str, Any]]:
    """Return clues the character can access and the session has unlocked."""
    return [
        clue
        for clue in clues
        if int(clue["id"]) in unlocked_ids
        and character_id in _accessible_character_ids(clue)
    ]


def filter_locked_clues(
    clues: Iterable[Dict[str, Any]],
    unlocked_ids: Set[int],
) -> List[Dict[str, Any]]:
    """Return clues that are not unlocked for the current session."""
    return [clue for clue in clues if int(clue["id"]) not in unlocked_ids]


def find_locked_clue_leaks(
    response: str,
    locked_clues: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Detect simple clue-name leaks in an LLM response.

    This is intentionally a lightweight keyword check for the MVP. A stronger
    LLM judge can replace it later.
    """
    leaks: List[Dict[str, Any]] = []
    for clue in locked_clues:
        name = str(clue.get("name", "")).strip()
        if name and name in response:
            leaks.append(clue)
    return leaks


def safe_response_for_spoiler_leak() -> str:
    return "지금 확인된 정보만으로는 그 부분을 단정할 수 없어."
