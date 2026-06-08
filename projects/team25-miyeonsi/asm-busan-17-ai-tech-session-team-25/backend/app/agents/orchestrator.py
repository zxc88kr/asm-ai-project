"""
오케스트레이터: 한 번의 게임 턴을 처리하는 파이프라인 총괄 모듈.

routes.py 에서 호출되며, 아래 에이전트·서비스를 순서대로 실행한다.
    1. 메모리 로드  (단기 대화 + 장기 요약/프로필/플래그)
    2. 의도 분류   (IntentClassifier)
    3. 도구 호출   (ToolRouter)
    4. 대사·표정 생성 (dialogue_generator)
    5. 호감도 증감 연산 (affinity_calculator)
    6. 스토리 평가  (story_engine)
    7. 메모리 갱신  (단기 턴 저장 + 프로필 추출 + 챕터 전환 시 요약 압축)
    8. TurnResult 반환
"""

from typing import Any, Dict, Optional

from app.schemas.request import ChatRequest
from app.schemas.response import TurnResult
from app.memory import store
from app.agents import dialogue_generator, story_engine
from app.services import affinity_calculator


class Orchestrator:
    def __init__(self):
        # 외부 SDK·네트워크에 의존하는 객체는 첫 호출 시 지연 생성한다.
        self._classifier = None
        self._tool_router = None

    def _classify_intent(self, user_message: str, chapter: int, affinity: int) -> Dict[str, Any]:
        """발화 의도를 분류한다. 사용 불가 시 'dialogue' 로 폴백."""
        try:
            if self._classifier is None:
                from app.agents.intent_classifier import IntentClassifier
                self._classifier = IntentClassifier()
            return self._classifier.classify(user_message, chapter, affinity)
        except Exception:
            return {"intent": "dialogue", "params": {}, "reason": "의도 분류기 사용 불가"}

    def _route_tool(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """의도에 맞는 도구를 호출한다. 사용 불가 시 빈 결과로 폴백."""
        try:
            if self._tool_router is None:
                from app.agents.tool_router import ToolRouter
                self._tool_router = ToolRouter()
            return self._tool_router.route(intent, params)
        except Exception:
            return {"tool_name": "none", "results": [], "summary": ""}

    def run_turn(self, request: ChatRequest) -> TurnResult:
        """유저의 한 턴 입력을 받아 전체 파이프라인을 실행하고 TurnResult 를 반환한다."""

        # ------------------------------------------------------------------ #
        # 1. 메모리 로드
        # ------------------------------------------------------------------ #
        history = store.get_short_term(request.session_id)
        summary = store.get_summary(request.session_id)
        profile = store.get_profile(request.session_id)
        flags: Dict[str, Any] = dict(
            store.load_session(request.session_id)["long_term"]["flags"]
        )

        # ------------------------------------------------------------------ #
        # 2. 의도 분류 (대화 / 도구 / 선택)
        # ------------------------------------------------------------------ #
        intent_obj = self._classify_intent(
            request.user_message, request.current_chapter, request.current_affinity
        )
        intent = intent_obj.get("intent", "dialogue")

        # ------------------------------------------------------------------ #
        # 2-b. 챕터 내 턴 카운터 증가 (story_engine 전환 조건 판정용)
        # ------------------------------------------------------------------ #
        chapter_turns = flags.get("chapter_turns", 0) + 1
        flags["chapter_turns"] = chapter_turns

        # ------------------------------------------------------------------ #
        # 3. 도구 호출 (intent == "tool" 일 때만)
        # ------------------------------------------------------------------ #
        tool_result: Optional[Dict[str, Any]] = None
        if intent == "tool":
            routed = self._route_tool("tool", intent_obj.get("params", {}))
            if routed.get("results") or routed.get("summary"):
                tool_result = routed
            # 지연 항공편이 조회되면 플래그를 켠다 (story_engine 이 탑승 게이트에서 사용).
            if any(r.get("delayed") for r in routed.get("results", [])):
                flags["flight_delayed"] = True

        # ------------------------------------------------------------------ #
        # 4. 대사·표정 생성
        # ------------------------------------------------------------------ #
        dialogue = dialogue_generator.generate_dialogue(
            request.user_message,
            affinity=request.current_affinity,
            chapter=request.current_chapter,
            history=history,
            tool_result=tool_result,
            profile=profile,
            summary=summary,
        )

        # ------------------------------------------------------------------ #
        # 5. 호감도 증감 연산
        # ------------------------------------------------------------------ #
        affinity_delta, new_affinity = affinity_calculator.step(
            request.current_affinity,
            request.user_message,
            dialogue.emotion_code,
        )

        # ------------------------------------------------------------------ #
        # 6. 스토리 평가 (씬 전환 / 엔딩 / 이벤트)
        # ------------------------------------------------------------------ #
        decision = story_engine.evaluate(
            current_chapter=request.current_chapter,
            affinity=new_affinity,
            user_message=request.user_message,
            flags=flags,
        )

        # ------------------------------------------------------------------ #
        # 7. 메모리 갱신
        # ------------------------------------------------------------------ #
        # fallback 응답은 history에 저장하지 않는다.
        # 저장하면 LLM이 fallback 패턴을 학습해 반복 생성하는 악순환이 발생한다.
        if not dialogue.is_fallback:
            store.append_turn(request.session_id, request.user_message, dialogue.dialogue_list)

        extracted_profile = dialogue_generator.extract_profile(request.user_message)

        new_summary: Optional[str] = None
        if decision.is_transition:
            updated_history = store.get_short_term(request.session_id)
            new_summary = dialogue_generator.generate_summary(updated_history, summary)

        flag_updates: Dict[str, Any] = {}
        if decision.event:
            flag_updates[decision.event] = True
        if flags.get("flight_delayed"):
            flag_updates["flight_delayed"] = True
        # 챕터 전환 시 턴 카운터 리셋, 아니면 증가된 값을 저장한다.
        flag_updates["chapter_turns"] = 0 if decision.is_transition else chapter_turns

        store.update_state(
            request.session_id,
            affinity=new_affinity,
            chapter=decision.next_chapter,
            flags=flag_updates or None,
            summary=new_summary,
            profile=extracted_profile or None,
        )

        # ------------------------------------------------------------------ #
        # 8. TurnResult 반환
        # ------------------------------------------------------------------ #
        return TurnResult(
            next_chapter=decision.next_chapter,
            affinity_delta=affinity_delta,
            agent_dialogue_list=dialogue.dialogue_list,
            emotion_code=dialogue.emotion_code,
            metadata={
                "is_transition": decision.is_transition,
                "is_ending": decision.is_ending,
                "event": decision.event,
                "current_affinity": new_affinity,
                "intent": intent,
                "tool_result": tool_result,
                **decision.metadata,
            },
        )
