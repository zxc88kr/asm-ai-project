# Step 1 — Calculator 구현 에이전트 브리핑

## 프로젝트 컨텍스트

AI 정산 비서. 모임 정산 상황을 자연어로 입력하면 공정한 정산안을 계산해주는 시스템.
전체 3단계 중 **1단계** — 이 작업이 완료되어야 ai/, front/를 구현할 수 있다.

## 작업 범위

`calculator/` 폴더만 구현한다. `ai/`, `front/`에는 접근하지 않는다.
구체적인 역할 정의는 `calculator/CLAUDE.md`를 먼저 읽어라.

## 구현 목표

`calculator/engine.py`에 두 함수를 구현한다.

### 함수 시그니처

```python
def calculate(parsed_json: dict) -> dict: ...
def recalculate(parsed_json: dict, feedback_json: dict) -> dict: ...
```

### 입력 구조 (`parsed_json`)

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
      {"type": "늦은 도착", "target_items": ["안주"], "discount_rate": 0.3}
    ]},
    {"name": "D", "exceptions": [
      {"type": "술 미섭취", "target_items": ["주류"], "discount_rate": 1.0}
    ]}
  ]
}
```

`discount_rate`: 해당 항목에서 제외되는 비율. `1.0` = 전액 제외, `0.3` = 30% 감액.
감액된 금액은 예외 조건이 없는 나머지 참여자에게 재분배한다.

### 출력 구조 (`calculate` 반환값)

```json
{
  "participants": [
    {
      "name": "A",
      "final_amount": 23750,
      "breakdown": {"base": 20000, "redistributed": 3750, "discounted": 0}
    }
  ],
  "total_verified": true,
  "floor_applied": ["C"],
  "rounding_adjusted": "A"
}
```

### 계산 처리 순서

1. 균등 분담액 = 총액 ÷ 참여자 수
2. 각 예외 조건의 감액액 = 항목금액 × discount_rate ÷ (해당 항목 참여자 수)
3. 감액액을 해당 참여자에서 차감, 나머지에게 재분배
4. 최소 부담 하한선: 균등 분담액의 30% — 미달 시 강제 적용
5. 총액 검증: 합계 ↔ total_amount 비교
6. 반올림 오차 자동 보정 (차액을 한 명에게 가산)

### SPONSOR 전략 처리

선결제자가 있을 경우: 각자 납부액 계산 후 선결제 금액을 선결제자의 납부액에서 차감.
결과가 음수면 해당 금액을 나머지 참여자로부터 환급받아야 함을 표시.

## 예외 처리

| 상황 | 처리 |
|------|------|
| 총액 또는 참여자 정보 누락 | `ValueError` |
| 항목별 합계 ≠ total_amount | `ValueError` + 모순 지점 메시지 |
| `discount_rate` 범위 초과 (0.0~1.0 외) | `ValueError` |
| 하한선 미달 | 강제 적용 후 정상 반환 |

## 검증 시나리오 (3개 모두 통과해야 완료)

### 시나리오 A

```python
input_a = {
    "total_amount": 80000,
    "items": [{"name": "주류", "amount": 30000}, {"name": "안주", "amount": 50000}],
    "participants": [
        {"name": "A", "exceptions": []},
        {"name": "B", "exceptions": []},
        {"name": "C", "exceptions": [{"type": "늦은 도착", "target_items": ["안주"], "discount_rate": 0.3}]},
        {"name": "D", "exceptions": [{"type": "술 미섭취", "target_items": ["주류"], "discount_rate": 1.0}]}
    ]
}
result = calculate(input_a)
assert result["total_verified"] == True
assert sum(p["final_amount"] for p in result["participants"]) == 80000
```

### 시나리오 B

```python
input_b = {
    "total_amount": 120000,
    "items": [
        {"name": "주류", "amount": 50000},
        {"name": "안주", "amount": 50000},
        {"name": "공통비", "amount": 20000}
    ],
    "sponsor": {"name": "A", "prepaid": 50000},
    "participants": [
        {"name": "A", "exceptions": []},
        {"name": "B", "exceptions": []},
        {"name": "C", "exceptions": []},
        {"name": "D", "exceptions": [{"type": "술 미섭취", "target_items": ["주류"], "discount_rate": 1.0}]},
        {"name": "E", "exceptions": [{"type": "늦은 도착 + 소량 섭취", "target_items": ["안주"], "discount_rate": 0.5}]}
    ]
}
result = calculate(input_b)
assert result["total_verified"] == True
```

### 시나리오 C (재계산)

```python
feedback = {"name": "D", "additional_exception": {"type": "소량 섭취", "target_items": ["안주"], "discount_rate": 0.5}}
result_c = recalculate(input_b, feedback)
assert result_c["total_verified"] == True
# D의 안주 감액이 추가 반영되어야 함
```

## 작업 방식

TDD로 진행한다 — 테스트 먼저 작성, 구현 후 통과 확인.
`calculator/tests/test_engine.py`에 테스트를 작성하고 `pytest`로 실행한다.
