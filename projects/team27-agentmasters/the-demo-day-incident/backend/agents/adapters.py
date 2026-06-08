"""Adapter boundary between agent graphs and backend persistence.

The functions in this module are intentionally thin placeholders. Backend
integration work can replace them with DB-backed implementations, while graph
tests can monkeypatch them with fakes.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib import request

from data.characters import get_character_by_id
from data.clues import CLUES, get_clue_by_id


DEFAULT_USER_ID = "default"
DEFAULT_UNLOCKED_CLUE_IDS = {1}


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _upstage_chat_completion(prompt: str) -> str:
    _load_dotenv()
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not configured")

    base_url = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1").rstrip("/")
    model = os.getenv("UPSTAGE_MODEL", "solar-pro3")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    encoded_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{base_url}/chat/completions",
        data=encoded_payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


class DatabaseAgentAdapter:
    """DB-backed adapter for sync FastAPI endpoints."""

    def __init__(self, db: Any, user_id: str = DEFAULT_USER_ID) -> None:
        self.db = db
        self.user_id = user_id

    def get_character(self, character_id: int) -> Dict[str, Any]:
        return get_character_by_id(character_id)

    def get_clue(self, clue_id: int) -> Dict[str, Any]:
        return get_clue_by_id(clue_id)

    def get_accessible_clues(self, character_id: int) -> List[Dict[str, Any]]:
        return [
            clue
            for clue in CLUES
            if character_id in clue.get("accessible_character_ids", [])
        ]

    def get_unlocked_clue_ids(self, user_id: str) -> Set[int]:
        import models

        interacted_ids = {
            clue_id
            for (clue_id,) in self.db.query(models.ClueState.clue_id)
            .filter(models.ClueState.user_id == user_id)
            .filter(models.ClueState.interacted == True)  # noqa: E712
            .all()
        }
        return DEFAULT_UNLOCKED_CLUE_IDS | {int(clue_id) for clue_id in interacted_ids}

    def is_clue_unlocked(self, user_id: str, clue_id: int) -> bool:
        return clue_id in self.get_unlocked_clue_ids(user_id)

    def get_recent_messages(
        self,
        user_id: str,
        character_id: int,
        limit: int = 6,
    ) -> List[Dict[str, Any]]:
        import models

        messages = (
            self.db.query(models.ChatMessage)
            .filter(models.ChatMessage.user_id == user_id)
            .filter(models.ChatMessage.character_id == character_id)
            .order_by(models.ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {"sender": message.sender, "content": message.content}
            for message in reversed(messages)
        ]

    def save_message(
        self,
        user_id: str,
        character_id: int,
        sender: str,
        content: str,
    ) -> None:
        import models

        self.db.add(
            models.ChatMessage(
                user_id=user_id,
                sender=sender,
                character_id=character_id,
                content=content,
            )
        )

    def mark_clue_interacted(self, user_id: str, clue_id: int) -> None:
        import models

        clue_state = (
            self.db.query(models.ClueState)
            .filter(models.ClueState.user_id == user_id)
            .filter(models.ClueState.clue_id == clue_id)
            .first()
        )
        if clue_state:
            clue_state.interacted = True
            return
        self.db.add(
            models.ClueState(
                user_id=user_id,
                clue_id=clue_id,
                interacted=True,
            )
        )

    def generate_character_reply(
        self,
        prompt: str,
        character: Dict[str, Any],
        user_message: str,
        context_clues: List[Dict[str, Any]],
    ) -> str:
        return _upstage_chat_completion(prompt)

    def generate_deduction_evaluation(self, prompt: str) -> str:
        return _upstage_chat_completion(prompt)


def get_character(character_id: int) -> Dict[str, Any]:
    return get_character_by_id(character_id)


def get_clue(clue_id: int) -> Dict[str, Any]:
    return get_clue_by_id(clue_id)


def get_accessible_clues(character_id: int) -> List[Dict[str, Any]]:
    return [
        clue
        for clue in CLUES
        if character_id in clue.get("accessible_character_ids", [])
    ]


def get_unlocked_clue_ids(user_id: str) -> Set[int]:
    raise NotImplementedError("get_unlocked_clue_ids adapter is not wired yet")


def is_clue_unlocked(user_id: str, clue_id: int) -> bool:
    return clue_id in get_unlocked_clue_ids(user_id)


def get_recent_messages(
    user_id: str,
    character_id: int,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    raise NotImplementedError("get_recent_messages adapter is not wired yet")


def save_message(
    user_id: str,
    character_id: int,
    sender: str,
    content: str,
) -> None:
    raise NotImplementedError("save_message adapter is not wired yet")


def generate_character_reply(
    prompt: str,
    character: Dict[str, Any],
    user_message: str,
    context_clues: List[Dict[str, Any]],
) -> str:
    return _upstage_chat_completion(prompt)


def generate_deduction_evaluation(prompt: str) -> str:
    return _upstage_chat_completion(prompt)


def mark_clue_interacted(user_id: str, clue_id: int) -> None:
    raise NotImplementedError("mark_clue_interacted adapter is not wired yet")
