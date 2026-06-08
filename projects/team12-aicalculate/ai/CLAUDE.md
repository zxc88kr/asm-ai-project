# ai/ — Agentic Workflow (LangGraph + Upstage)

## 역할 범위

- 자연어 입력 파싱 → 구조화 JSON 생성
- 예외 조건별 감액률/할증률 결정 (맥락 기반, LLM 판단)
- 정산 전략 분기 결정 (SIMPLE / EXCEPTION)
- 피드백 조건 구조화 (기존 parsed_json에 반영)
- 계산 근거 설명(calc_explanation) 및 공유 메시지(final_report) 생성

## 이 폴더에서 절대 하지 않는 것

- 감액률/할증률을 금액으로 환산하는 산술 연산 (calculator/에서만 수행)
- 30% 하한선 적용, 총액 검증, 반올림 보정 (calculator/ 내부에서 처리됨)
- Streamlit UI 렌더링

## LangGraph 노드 목록 및 흐름

```
START
  │
  ├─ [parsed_json 없음] ──► input_parsing ──┐
  │                                          ▼
  ├─ [parsed_json 있음] ──► feedback_parsing ─► safety_check
  │                                                  │
  │                                       [safety_error 있음] ──► END
  │                                                  │
  │                                          route_request (전략 결정)
  │                                                  │
  │                                            calculation (calculator/ 호출)
  │                                                  │
  │                                          report_generation
  │                                                  │
  │                                                 END
```

1. `input_parsing_node` : 자연어 → 구조화 JSON + 예외 조건 rate 결정 (Upstage LLM).
   호출 후 `_post_validate_exceptions()`로 분류 오류를 코드 레벨에서 보정한다.
2. `safety_check_node` : 총액 누락/모순, 중복 참여자, items 없는데 target_items 지정,
   `discount_rate` null, 할증 rate/amount 미지정 등을 감지해 `safety_error` 반환 (LLM 미사용).
3. `route_request_node` : 전략 분기 결정 — SIMPLE / EXCEPTION (Upstage LLM).
4. `calculation_node` : `from calculator.engine import calculate` 직접 호출.
5. `report_generation_node` : `_build_explanation()`으로 계산 근거 텍스트(calc_explanation)를
   코드로 조립하고, 공유 메시지(final_report)는 LLM이 최종 금액 목록만 보고 작성한다.
6. `feedback_parsing_node` : 피드백 입력 시 수정 조건만 반영 → **safety_check로 재진입**.

> 초기 흐름과 피드백 흐름 모두 safety_check를 거친 뒤 route_request → calculation → report_generation으로 진행된다.
> FairnessAdjust/Validator 같은 별도 노드는 두지 않는다 — 하한선·검증 로직은 calculator/ 내부에 있다.

## 입력 후처리 (_post_validate_exceptions)

LLM 분류 오류를 코드 레벨에서 보정한다:
- 지각/늦은 도착 키워드인데 `discount_rate`로 분류된 경우 → `surcharge_rate`로 전환
- 할증인데 비율/금액이 없으면 `surcharge_rate: null` 주입 (이후 safety_check가 재입력 요청)
- 모호한 `discount_rate: null` → 타입 키워드로 rate 추론 (미섭취 1.0, 거의 안 0.7, 소량 0.5 등)
- 한 참여자에 할증 예외가 둘 이상이면 `_merge_surcharge_exceptions()`가 가장 구체적인 것
  하나로 병합 (우선순위: surcharge_amount > surcharge_rate > null)

## 프롬프트 작성 규칙

- input_parsing : 산술 계산 금지. 예외를 `discount_rate` / `surcharge_rate` / `surcharge_amount`로 분류.
  - 감액 조건(소비 감소) → `discount_rate` (미섭취 1.0 / 거의 안 0.7 / 소량·절반 0.5 / 잠깐 0.3 / 모호 null)
  - 할증 조건(지각 등): 비율 명시 → `surcharge_rate`, 금액 명시 → `surcharge_amount`, 미명시 → `surcharge_rate: null`
- route_request : "단어 기반이 아닌 문맥 기반으로 판단하라". 예외 하나라도 있으면 EXCEPTION, 없으면 SIMPLE.
- feedback_parsing : "기존 정산 정보를 임의로 덮어쓰지 말고, 새로 말한 조건만 추가/수정. 언급 없는 참여자는 건드리지 말라."
- 공유 메시지(SHARE_MESSAGE) : 계산 근거·예외 이유 언급 금지, 산술 계산 금지, 최종 금액 나열만 허용.

## LLM 설정

- 모델 : `solar-pro` (Upstage), `base_url=https://api.upstage.ai/v1`
- API Key : 환경변수 `UPSTAGE_API_KEY`
- LangSmith : `wrap_openai`로 클라이언트를 감싸 트레이싱을 자동 기록한다.
  `LANGSMITH_TRACING=false`면 오버헤드 없이 동작.

## LangGraph State 스키마 (공유 인터페이스)

```python
class SettlementState(TypedDict, total=False):
    raw_input          : str   # 사용자 원문 (피드백 시에는 피드백 텍스트)
    parsed_json        : dict   # 구조화 결과 — discount_rate/surcharge_rate/surcharge_amount 포함
    strategy           : str   # SIMPLE | EXCEPTION
    calculation_result : dict   # calculator/ 반환값 (하한선·검증·설명 로그 포함)
    feedback_history   : list   # 피드백 이력
    calc_explanation   : str   # 코드로 조립한 계산 근거 텍스트
    final_report       : str   # 공유용 메시지 (LLM 생성)
    safety_error       : str   # safety_check 오류 메시지 (없으면 빈 문자열)
```

> payer/sponsor 필드 및 `_inject_payer` 로직은 현재 버전에서 제거되었다.

## parsed_json 구조 예시

```json
{
  "total_amount": 80000,
  "items": [
    {"name": "주류", "amount": 30000},
    {"name": "안주", "amount": 50000}
  ],
  "participants": [
    {"name": "A", "exceptions": []},
    {"name": "B", "exceptions": []},
    {"name": "C", "exceptions": [
      {"type": "늦은 도착", "target_items": ["주류", "안주"], "surcharge_amount": 5000}
    ]},
    {"name": "D", "exceptions": [
      {"type": "술 미섭취", "target_items": ["주류"], "discount_rate": 1.0}
    ]}
  ]
}
```

`discount_rate`는 해당 항목에서 제외되는 비율이다 (`1.0` = 전액 제외, `0.5` = 50% 감액).
`surcharge_rate`는 비율 할증, `surcharge_amount`는 고정 금액 할증이다.
