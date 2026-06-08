"""
세션별 단기/장기 메모리를 로컬 JSON 파일로 관리하는 저장소.

- 단기 메모리(short_term): 최근 대화 N턴. LLM 컨텍스트 윈도우에 직접 주입된다.
- 장기 메모리(long_term): 호감도, 챕터, 누적 플래그(이벤트 달성 여부 등) 같은 영속 상태.

세션 1개 = `<MEMORY_DATA_DIR>/<session_id>.json` 파일 1개로 대응한다.
파일 쓰기는 임시 파일 + 원자적 교체(os.replace)로 중간에 깨진 JSON이 남지 않도록 한다.
"""

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings

# 단기 메모리로 유지할 최대 대화 턴 수 (user/assistant 메시지 기준).
# 한 턴이 user 1 + assistant 1 이므로 메시지 개수로는 약 2배가 보존된다.
SHORT_TERM_MAX_TURNS = 8

# session_id 로 파일명을 만들 때 허용할 안전한 문자(경로 조작 방지).
_SAFE_ID = re.compile(r"[^a-zA-Z0-9_-]")


def _data_dir() -> Path:
    """메모리 데이터 디렉토리를 보장(없으면 생성)하고 반환한다."""
    d = Path(settings.MEMORY_DATA_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _session_path(session_id: str) -> Path:
    """session_id 를 안전한 파일명으로 변환해 JSON 경로를 만든다.

    '../' 같은 경로 조작 문자를 제거하여 데이터 디렉토리 밖으로 새는 것을 막는다.
    """
    safe = _SAFE_ID.sub("_", session_id).strip("_") or "anonymous"
    return _data_dir() / f"{safe}.json"


def _empty_session(session_id: str) -> Dict[str, Any]:
    """신규 세션의 기본 메모리 구조."""
    return {
        "session_id": session_id,
        # 기획서 기준 시작 호감도는 50점(중립/탐색기). 0이 아님에 유의.
        "affinity": 50,
        "chapter": 0,
        "short_term": [],   # [{"role": "user"|"assistant", "content": str}, ...]
        "long_term": {
            "flags": {},     # 이벤트/미션 달성 플래그 (예: {"booked_flight": True})
            "summary": "",   # 이전 챕터 종료 시 LLM 으로 압축한 과거 대화 요약(요약 메모리)
            "profile": {},   # 사용자 여행 선호 프로필 (예: {"budget": "가성비", "mood": "힐링", "companion": "혼자"})
        },
    }


def load_session(session_id: str) -> Dict[str, Any]:
    """세션 메모리를 로드한다. 파일이 없거나 손상되면 빈 세션을 반환한다."""
    path = _session_path(session_id)
    if not path.exists():
        return _empty_session(session_id)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # 손상된 파일은 무시하고 새 세션으로 복구한다(게임이 멈추지 않도록).
        return _empty_session(session_id)

    # 구버전/누락 필드 방어: 기본 구조와 병합한다.
    base = _empty_session(session_id)
    base.update({k: data.get(k, base[k]) for k in base})
    # long_term 하위 키(flags/summary/profile)도 누락 시 기본값으로 채운다.
    loaded_long = data.get("long_term") or {}
    if isinstance(loaded_long, dict):
        long_term = _empty_session(session_id)["long_term"]
        long_term.update({k: loaded_long.get(k, long_term[k]) for k in long_term})
        base["long_term"] = long_term
    return base


def save_session(session_id: str, data: Dict[str, Any]) -> None:
    """세션 메모리를 원자적으로 저장한다."""
    path = _session_path(session_id)
    # 같은 디렉토리에 임시 파일을 만든 뒤 교체해야 os.replace 가 원자적으로 동작한다.
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        # 실패 시 임시 파일 정리
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def append_turn(
    session_id: str,
    user_message: str,
    agent_dialogue_list: List[str],
) -> Dict[str, Any]:
    """한 턴의 대화를 단기 메모리에 추가하고, 윈도우 크기를 넘으면 오래된 것을 잘라낸다.

    여러 개의 agent 말풍선은 하나의 assistant 메시지로 합쳐서 보존한다.
    저장까지 수행한 뒤 갱신된 세션 데이터를 반환한다.
    """
    data = load_session(session_id)
    short = data["short_term"]
    short.append({"role": "user", "content": user_message})
    if agent_dialogue_list:
        short.append({"role": "assistant", "content": " ".join(agent_dialogue_list)})

    # 최근 SHORT_TERM_MAX_TURNS 턴(= 2배 메시지)만 유지
    max_messages = SHORT_TERM_MAX_TURNS * 2
    if len(short) > max_messages:
        data["short_term"] = short[-max_messages:]

    save_session(session_id, data)
    return data


def get_short_term(session_id: str) -> List[Dict[str, str]]:
    """LLM 컨텍스트에 넣을 최근 대화 메시지 리스트를 반환한다."""
    return load_session(session_id)["short_term"]


def update_state(
    session_id: str,
    *,
    affinity: int | None = None,
    chapter: int | None = None,
    flags: Dict[str, Any] | None = None,
    summary: str | None = None,
    profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """장기 상태(호감도/챕터/플래그/요약/프로필)를 부분 갱신하고 저장한다.

    flags/profile 은 부분 병합(update), summary 는 통째로 교체한다.
    """
    data = load_session(session_id)
    if affinity is not None:
        data["affinity"] = affinity
    if chapter is not None:
        data["chapter"] = chapter
    if flags:
        data["long_term"]["flags"].update(flags)
    if summary is not None:
        data["long_term"]["summary"] = summary
    if profile:
        data["long_term"]["profile"].update(profile)
    save_session(session_id, data)
    return data


def get_summary(session_id: str) -> str:
    """장기 요약 메모리(이전 챕터 압축본)를 반환한다. 없으면 빈 문자열."""
    return load_session(session_id)["long_term"].get("summary", "")


def get_profile(session_id: str) -> Dict[str, Any]:
    """사용자 여행 선호 프로필을 반환한다. 없으면 빈 dict."""
    return load_session(session_id)["long_term"].get("profile", {})


def reset_session(session_id: str) -> Dict[str, Any]:
    """세션을 초기화한다(파일 삭제 후 빈 세션 반환). 게임 다시 시작용."""
    path = _session_path(session_id)
    if path.exists():
        path.unlink()
    return _empty_session(session_id)
