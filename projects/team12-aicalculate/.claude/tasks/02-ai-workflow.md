# Step 2 — AI Workflow 구현 에이전트 브리핑

## 전제 조건

`calculator/engine.py` 구현이 완료된 상태다.
`from calculator.engine import calculate, recalculate` import가 동작함을 확인하고 시작한다.

## 프로젝트 컨텍스트

Upstage Solar LLM + LangGraph StateGraph로 자연어 입력을 구조화하고 정산 전략을 결정한다.
전체 3단계 중 **2단계** — 완료 후 front/ 에이전트가 이어받는다.

## 작업 범위

`ai/` 폴더만 구현한다. `calculator/`는 import만 하고, `front/`에는 접근하지 않는다.
구체적인 역할 정의는 `ai/CLAUDE.md`를 먼저 읽어라.

## 환경변수

`UPSTAGE_API_KEY` — `.env` 파일에서 로드. `python-dotenv` 사용.

## LangGraph State

```python
from typing import TypedDict

class SettlementState(TypedDict):
    raw_input: str          # 사용자 원문
    parsed_json: dict       # InputParsingNode 출력 (discount_rate 포함)
    strategy: str           # SIMPLE | EXCEPTION | SPONSOR
    calculation_result: dict
    feedback_history: list[str]
    final_report: str
```

## 노드 구현 가이드

### 1. InputParsingNode (Upstage LLM)

역할: 자연어 → 구조화 JSON + 예외 조건별 discount_rate 결정

```python
SYSTEM_PROMPT = """
당신은 정산 데이터 파서입니다.
산술 계산은 수행하지 말고, 다음을 수행하라:
1. 참여자, 총 금액, 비용 항목, 예외 조건을 JSON으로 추출하라.
2. 각 예외 조건에 대해 상황의 심각도에 비례한 감액률(discount_rate: 0.0~1.0)을 결정하라.
   - 술 미섭취: 주류 항목 discount_rate 1.0
   - 10분 지각: 안주 discount_rate 0.1~0.2
   - 1시간 지각: 안주 discount_rate 0.4~0.6
   - 중도 귀가 (절반 이상): discount_rate 0.5
   - 소량 섭취: discount_rate 0.3~0.5
반드시 유효한 JSON만 반환하라.
"""
```

출력은 `calculator/engine.py`의 `calculate()` 입력과 동일한 구조여야 한다.

### 2. SafetyCheckNode (LLM 호출 없음)

```python
def safety_check(state: SettlementState) -> SettlementState:
    pj = state["parsed_json"]
    if not pj.get("total_amount") or not pj.get("participants"):
        # 재입력 요청 → graph 종료 또는 interrupt
        ...
    items_sum = sum(i["amount"] for i in pj.get("items", []))
    if items_sum and abs(items_sum - pj["total_amount"]) > 1:
        # 모순 감지
        ...
```

### 3. RouteRequestNode (Upstage LLM)

출력: `{"strategy": "SIMPLE" | "EXCEPTION" | "SPONSOR"}`

프롬프트 핵심: "단어 기반이 아닌 문맥 기반으로 판단하라. 예외 조건이 하나라도 있으면 EXCEPTION, 선결제가 있으면 SPONSOR."

### 4. CalculationNode (LLM 호출 없음)

```python
from calculator.engine import calculate

def calculation_node(state: SettlementState) -> SettlementState:
    result = calculate(state["parsed_json"])
    return {**state, "calculation_result": result}
```

### 5. ReportGenerationNode (Upstage LLM)

입력: `calculation_result` + `parsed_json`
출력: 자연어 설명 + 복사용 공유 메시지

프롬프트 핵심: "특정 참여자를 비난하지 말고, 항목 참여 여부 기준으로 중립적으로 설명하라."

### 6. FeedbackParsingNode (Upstage LLM)

입력: 피드백 텍스트 + 기존 `parsed_json` + `feedback_history`
출력: 수정된 `parsed_json` (변경된 조건만 반영, 기존 정보 덮어쓰지 않음)

프롬프트 핵심: "기존 정산 정보를 임의로 덮어쓰지 말고, 사용자가 새로 말한 조건만 추가 또는 수정하라."

이후 CalculationNode로 재진입한다.

## 그래프 엣지 구성

```
InputParsing → SafetyCheck → RouteRequest → Calculation → ReportGeneration

피드백 경로:
FeedbackParsing → Calculation → ReportGeneration
```

`ai/graph.py`에서 `graph` 객체를 export한다:
```python
graph = builder.compile()
```

## 완료 기준

```python
from ai.graph import graph

result = graph.invoke({
    "raw_input": "총 8만원이고 A, B, C, D 있어. 주류 3만원 / 안주 5만원. C는 늦게 왔고 D는 술 안 마셨어.",
    "feedback_history": []
})

assert result["strategy"] == "EXCEPTION"
assert result["parsed_json"]["participants"]  # discount_rate 포함 확인
assert result["calculation_result"]["total_verified"] == True
assert len(result["final_report"]) > 0
```
