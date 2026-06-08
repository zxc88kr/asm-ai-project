# AI 정산 비서 — 프로젝트 개요

## 서비스 정의

모임 정산 시 자연어로 입력된 예외 조건(술 미섭취, 소량 섭취, 중도 귀가, 지각 등)을
LLM 맥락 추론 + 규칙 기반 계산 엔진으로 처리하는 Agentic Workflow 프로젝트.

## 폴더 구조

- front/ : Streamlit UI, session_state 세션 관리
- ai/ : LangGraph StateGraph, Upstage LLM 호출, 노드 체인
- calculator/ : 순수 Python 정산 계산 모듈 (웹 서버 없음)

세 폴더 모두 하나의 프로세스에서 실행된다.
front/ → ai/ → calculator/ 순서로 직접 import하여 호출한다. HTTP 통신 없음.

## 서비스 실행

```bash
# 1. .env 파일 생성 후 UPSTAGE_API_KEY 값 입력
cp .env.example .env

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행 (루트에서 실행해야 .env를 올바르게 로드함)
streamlit run front/app.py
```

- Streamlit : http://localhost:8501
- `.env`는 git에 커밋하지 않는다 (`.gitignore`에 포함됨)
- `.env.example`은 커밋한다 — 팀원이 참고하는 키 목록

## 핵심 설계 원칙

1. 금액의 산술 계산은 LLM이 수행하지 않는다.
   → LLM 담당: 자연어 파싱, 예외 조건별 rate 결정(0.0~1.0), 전략 분기, 공유 메시지 생성
   → calculator/ 담당: rate를 실제 금액으로 환산하는 연산 전체
   → 구분 기준: "얼마나 적용할지 판단"은 LLM, "그 비율로 계산"은 calculator/
2. 정산 전략은 SIMPLE / EXCEPTION 2가지로만 분기된다.
3. 최소 부담 하한선: 균등 분담액의 30% (단, 완전 제외자는 면제 — 아래 참고)
4. 세션은 브라우저 종료 시 초기화되며 장기 저장소는 없다.

## 예외 조건 분류 규칙

예외 조건은 성격에 따라 두 가지 rate(또는 고정 금액)로 분류한다:

| 구분 | 키 | 대상 조건 | 효과 |
|------|----|-----------|------|
| 감액 | `discount_rate` (0.0~1.0) | 술 미섭취, 소량 섭취, 중도 귀가 | 해당 항목 비용에서 차감, 나머지에게 재분배 |
| 할증(비율) | `surcharge_rate` (0.0~1.0) | 지각/늦은 도착 (비율 명시) | 할증 전 부담액의 N% 추가 부담, 나머지에게 차감 배분 |
| 할증(고정) | `surcharge_amount` (0 이상 정수) | 지각비 (금액 명시) | 고정 금액 추가 부담, 나머지에게 차감 배분 |

- `discount_rate: 1.0` = 해당 항목 전액 제외
- `surcharge_rate: 0.2` = 할증 전 개인 부담액의 20% 추가 부담
- `surcharge_amount: 5000` = 고정 5,000원 추가 부담 (예: "지각비 5000원")
- 한 예외에 `surcharge_rate`와 `surcharge_amount`를 동시에 쓰지 않는다.

## 최소 부담 하한선 규칙

- 기본: 어떤 참여자의 부담액이 균등 분담액(총액÷N)의 30% 미만이면 30%로 끌어올린다.
  끌어올린 차액은 하한선에 걸리지 않은 나머지 참여자에게 비례 차감한다.
- **예외(면제):** 부담액이 정확히 0원인 참여자(= 유일 항목을 `discount_rate: 1.0`으로
  완전 제외해 실제로 소비한 비용이 없는 경우)는 하한선을 적용하지 않고 0원으로 둔다.

## 구현 제외 항목 (MVP 범위 밖)

- 실제 계좌 송금 및 금융 트랜잭션
- 선결제자(payer) 송금 정산 — 현재 버전에서 제거됨
- OCR, 카드 내역/계좌 연동
- 회원가입/로그인, 장기 데이터 저장

## 환경변수

- `UPSTAGE_API_KEY` : Upstage Solar LLM API 키 (필수). .env로 관리, 코드 하드코딩 금지
- `LANGSMITH_TRACING` / `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` : LangSmith 트레이싱(선택).
  `LANGSMITH_TRACING=false`면 오버헤드 없이 일반 OpenAI 클라이언트처럼 동작

## 테스트 시나리오

시나리오 A: 술 미섭취 + 지각 (4명, 8만원, 주류 3만/안주 5만, D 미섭취, C 지각)
시나리오 B: 복합 예외 (5명, 12만원, 술 미섭취 + 소량 섭취 등 예외 조건 다중)
시나리오 C: 피드백 재계산 (기존 세션 유지 + 조건 추가)

```bash
pytest calculator/tests/
```
