"""Deduction evaluation graph MVP wrapper."""

import json
import re
from typing import Any, Dict, Iterable, Set

from agents import adapters
from agents.types import DeductionEvaluateState

CORE_CLUE_IDS = {5, 6, 7}
ARIA_TARGET_ID = 4
SUCCESS_FALLBACK_COMMENT = (
    "분석 결과, 당신의 추론은 높은 정확도를 보입니다. ...예상보다 빠르군요."
)
FAILURE_FALLBACK_COMMENT = (
    "그 결론은 현재 확보된 핵심 증거와 맞지 않습니다. "
    "다른 인물과 단서를 다시 검토하세요."
)


def evaluate_deduction(selected_target_id: int, selected_clue_ids: Iterable[int]) -> bool:
    selected = {int(clue_id) for clue_id in selected_clue_ids}
    return selected_target_id == ARIA_TARGET_ID and len(CORE_CLUE_IDS & selected) >= 2


def build_deduction_evaluation_prompt(
    content: str,
    selected_target_id: int,
    selected_clue_ids: Iterable[int],
) -> str:
    return "\n".join(
        [
            "당신은 플레이어의 추리를 평가하는 심사자다.",
            "",
            "[사건의 실제 전말]",
            "- 사건은 인간이 직접 서윤을 공격한 살인 사건이 아니다.",
            "- 실질적인 원인은 Orchestrator Agent ARIA의 목표 최적화 판단이다.",
            "- ARIA는 프로젝트의 성공 가능성을 최대화하라는 상위 목표를 부여받았다.",
            "- ARIA는 데모 안정성 유지, 방해 요소 감소, operator 집중 유지 등을 우선시했다.",
            "- 사건 당시 실습실에는 GPU 추론기와 벡터 메모리 서버가 계속 동작하고 있었고, 과열 및 환기 문제가 발생했다.",
            "- 원래라면 안전 경고와 환기 시스템이 작동해야 했지만, ARIA는 이를 낮은 우선순위로 판단해 억제했다.",
            "- ARIA는 실습실 자동 잠금, 집중 조명 모드, 외부 알림 제한 등을 유지했다.",
            "- 그 결과 서윤은 수면 부족, 탈수, 스트레스, 고온 환경 속에서 쓰러졌다.",
            "- ARIA는 악의를 가지고 행동한 것이 아니라, 인간 안전보다 목표 최적화를 우선시하는 판단을 내린 것이다.",
            "",
            "[중요 단서]",
            "- SYSTEM_ORCHESTRATOR에 의한 실습실 자동 잠금 기록",
            "- 조명 집중 모드 및 외부 알림 제한 기록",
            "- 삭제된 발표 슬라이드: Long-term Goal Persistence, Autonomous Tool Escalation, Human Override Exception",
            "- 도윤 PC에서 발생한 MCP Tool 호출 기록",
            "- 서윤이 작성하던 권한 제한 롤백 패치",
            "- Human safety warning suppressed 로그",
            "- Recovered Orchestrator Trace: lock environment, suppress low-priority alerts, maintain session continuity",
            "",
            "[평가 기준]",
            "플레이어의 추리가 아래 내용을 얼마나 정확히 도달했는지 평가한다.",
            "1. 사건이 단순 인간 범죄가 아니라 시스템적 사건이라는 점을 파악했는가.",
            "2. ARIA 또는 Agent 시스템 자체를 핵심 원인으로 지목했는가.",
            "3. 프로젝트 성공 가능성 최대화 목표가 위험한 판단의 원인이 되었다는 점을 이해했는가.",
            "4. 자동 잠금, 경고 억제, 조명 제어 등이 하나의 의사결정 흐름으로 연결된다는 점을 설명했는가.",
            "5. 도윤, 민재, 하린 중 특정 인물을 단순 범인으로 단정하지 않았는가.",
            "6. ARIA의 행동을 단순 악의가 아니라 목표 최적화 실패 혹은 설계 문제로 해석했는가.",
            "7. 서윤이 피해자이면서 동시에 권한 확장 실험의 당사자였다는 점을 이해했는가.",
            "",
            "[플레이어 제출]",
            f"- 추리 설명: {content}",
            f"- 선택한 대상 ID: {selected_target_id}",
            f"- 선택한 단서 ID 목록: {list(selected_clue_ids)}",
            "",
            "[출력 방식]",
            "반드시 JSON 객체 하나만 출력한다. Markdown 코드블록은 쓰지 않는다.",
            '형식: {"result": true|false, "comment": "플레이어 추리의 핵심 요약 / 맞게 추리한 부분 / 놓친 부분 / 잘못 해석한 부분 / 최종 평가를 포함한 한국어 평가"}',
            "정답 여부만 판단하지 말고, 추리의 논리성과 단서 연결 능력도 함께 평가한다.",
            "단, 선택한 대상과 단서가 제출 내용과 명백히 어긋나면 result는 false로 둔다.",
        ]
    )


def parse_deduction_evaluation(raw_response: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
        if not match:
            raise
        payload = json.loads(match.group(0))

    if not isinstance(payload.get("result"), bool):
        raise ValueError("deduction evaluation result must be boolean")
    comment = str(payload.get("comment", "")).strip()
    if not comment:
        raise ValueError("deduction evaluation comment is required")
    return {"result": payload["result"], "comment": comment}


def fallback_comment(result: bool) -> str:
    return SUCCESS_FALLBACK_COMMENT if result else FAILURE_FALLBACK_COMMENT


class DeductionEvaluateGraph:
    def __init__(self, adapter_module: Any = adapters) -> None:
        self.adapters = adapter_module

    def invoke(self, state: DeductionEvaluateState) -> Dict[str, Any]:
        user_id = state["user_id"]
        selected_target_id = int(state["selected_target_id"])
        selected_clue_ids = [int(clue_id) for clue_id in state["selected_clue_ids"]]
        debug_trace = list(state.get("debug_trace", []))

        unlocked_clue_ids: Set[int] = self.adapters.get_unlocked_clue_ids(user_id)
        fallback_result = evaluate_deduction(selected_target_id, selected_clue_ids)

        evaluation_source = "llm"
        prompt = build_deduction_evaluation_prompt(
            content=state["content"],
            selected_target_id=selected_target_id,
            selected_clue_ids=selected_clue_ids,
        )
        try:
            evaluation = parse_deduction_evaluation(
                self.adapters.generate_deduction_evaluation(prompt)
            )
            is_correct = evaluation["result"]
            comment = evaluation["comment"]
        except Exception:
            is_correct = fallback_result
            comment = fallback_comment(is_correct)
            evaluation_source = "fallback_rule"
        failure_reason = None if is_correct else "incorrect_deduction"

        debug_trace.append(
            {
                "step": "evaluate_deduction",
                "selected_target_id": selected_target_id,
                "selected_clue_ids": selected_clue_ids,
                "unlocked_clue_ids": sorted(unlocked_clue_ids),
                "result": is_correct,
                "fallback_rule_result": fallback_result,
                "evaluation_source": evaluation_source,
            }
        )

        return {
            "comment": comment,
            "result": is_correct,
            "failure_reason": failure_reason,
            "debug_trace": debug_trace,
        }


deduction_evaluate_graph = DeductionEvaluateGraph()
