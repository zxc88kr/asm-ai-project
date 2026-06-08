# calculator/ — 정산 계산 모듈

## 역할 범위

정산의 모든 산술 연산을 담당하는 순수 Python 모듈이다.
웹 서버가 아니며, ai/의 `calculation_node`가 직접 import하여 호출한다.

```python
from calculator.engine import calculate, recalculate
result = calculate(parsed_json)
```

LLM은 이 모듈에 관여하지 않으며, 이 모듈은 LLM을 호출하지 않는다.
예외 조건의 **rate는 ai/의 input_parsing_node(LLM)가 결정**하며,
이 모듈은 `parsed_json`에 담긴 `discount_rate` / `surcharge_rate` / `surcharge_amount`
값을 받아 금액으로 환산하기만 한다.

## 주요 함수 인터페이스

```python
calculate(parsed_json: dict) -> dict
# 입력: 구조화된 정산 JSON (참여자별 예외 조건 + rate 포함)
# 출력: 참여자별 부담 금액, 계산 근거 로그, 하한선 적용 내역, 총액 검증 결과

recalculate(parsed_json: dict, feedback_json: dict) -> dict
# feedback_json["name"] 참여자에 additional_exception을 추가한 뒤 calculate() 재호출
```

## 계산 처리 순서

1. **Step 1** (`_calc_step1`) — 항목(items)이 있으면 항목별 eligible 참여자 기준 1인 몫 계산:
   - `discount_rate >= 1.0` → 해당 항목에서 완전 제외 (eligible 제외)
   - `0 < discount_rate < 1.0` → 해당 항목 비용을 부분 감액
   - 감액분은 소멸하지 않고 같은 항목의 비감액 eligible 참여자에게 재분배
   - 항목이 없으면 총액 ÷ N (균등 분배)
2. **Step 2** (`_apply_steps_2_to_4`, 할증) — `surcharge_rate` 또는 `surcharge_amount` 적용:
   - `surcharge_rate: 0.2` → 할증 전 개인 부담액(step1 결과)의 20% 추가
   - `surcharge_amount: 5000` → 고정 5,000원 추가
   - 추가분은 **비할증자에게만** 균등 차감 분배 (전원 할증이면 본인 제외 전체에 분배)
3. **Step 3** — 최소 부담 하한선: 균등 분담액(총액÷N)의 30%
   - 미달 시 30%로 끌어올리고, 차액은 하한선 미적용자에게 비례 차감
   - **부담액이 정확히 0원인 참여자(완전 제외)는 하한선 면제** — 0원으로 유지
4. **Step 4** — 반올림 후 총액 검증. 합계가 총액과 다르면 소수부가 가장 큰/작은 참여자에게
   차액을 보정한다.

> 선결제자(sponsor) 처리 단계는 현재 버전에서 제거되었다.

## 예외 조건 타입

| 조건 | 키 | 예시 |
|------|----|------|
| 술 미섭취 | `discount_rate: 1.0` | `{"type": "술 미섭취", "target_items": ["주류"], "discount_rate": 1.0}` |
| 소량 섭취 | `discount_rate: 0.5~0.7` | `{"type": "소량 섭취", "target_items": ["안주"], "discount_rate": 0.5}` |
| 중도 귀가 | `discount_rate: 0.5` | `{"type": "중도 귀가", "target_items": ["주류", "안주"], "discount_rate": 0.5}` |
| 지각 (비율) | `surcharge_rate: 0.15~0.3` | `{"type": "늦은 도착", "target_items": ["안주"], "surcharge_rate": 0.2}` |
| 지각 (금액) | `surcharge_amount: 정수` | `{"type": "늦은 도착", "target_items": ["주류","안주"], "surcharge_amount": 5000}` |

## 입력 검증 (_validate에서 ValueError 발생)

| 상황 | 처리 방식 |
|------|-----------|
| 총액 or 참여자 정보 누락 | `ValueError` — ai/의 safety_check_node가 upstream에서 차단 |
| 중복 참여자 이름 | `ValueError` (중복 이름 명시) |
| 항목별 금액 합계 ≠ 총액 | `ValueError` (모순 지점 메시지 포함) |
| `discount_rate` / `surcharge_rate` 가 null 또는 0.0~1.0 범위 밖 | `ValueError` |
| `surcharge_amount` 가 null 또는 음수 | `ValueError` |

> 정상 입력 시 하한선 미달 케이스는 예외가 아니라 Step 3에서 30%로 보정 후 정상 반환된다.

## 출력 구조

```python
{
    "participants": [
        {
            "name": str,
            "final_amount": int,          # 최종 부담액 (음수면 수령)
            "breakdown": {
                "base": int,              # 균등 분담액 (총액 ÷ N)
                "step1_amount": int,      # 할증·하한선 적용 전(Step 1) 부담액
            },
        },
        ...
    ],
    "total_verified": bool,               # 합계 == total_amount 여부
    "floor_applied": list[str],           # 하한선이 강제 적용된 참여자 이름
    "rounding_adjusted": str | None,      # 반올림 차액을 보정한 참여자 이름
    # 아래 로그 필드는 해당 항목이 있을 때만 포함된다 (LLM 역산 오류 방지용 설명 문장)
    "discount_logs": dict[str, list[str]],
    "surcharge_logs": dict[str, list[str]],
    "surcharge_deductions": dict[str, dict],  # {name: {targets: [...], per_person: int}}
}
```
