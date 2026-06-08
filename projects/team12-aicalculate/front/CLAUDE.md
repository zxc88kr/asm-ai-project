# front/ — Streamlit UI

## 역할 범위

- 사용자 자연어 입력 수신 (텍스트 영역 + `전송 →` 버튼)
- ai/ LangGraph 워크플로우를 직접 import하여 실행 (`graph.invoke(state)`)
- 채팅 인터페이스로 정산 결과 출력 (오래된 것 위 → 최신 아래)
- 전략 배지, 참여자별 부담액 카드, 계산 근거(접이식), 공유용 정산 메시지 표시

> front/, ai/, calculator/ 모두 같은 Python 프로세스에서 실행된다. HTTP 통신 없음.
> 결제자(payer) 입력은 현재 버전에서 제거되었다 — 항상 개인 부담액을 표시한다.

## 화면 구조

```
[좌측 사이드바]                 [메인 영역]
  📋 상황별 예시                # 💸 AI 정산 비서
  🗑️ 대화 초기화                ─────────────────────
  ─────────                     👤 첫 번째 질문
  🍺 술 미섭취+지각 [채우기↗]    🤖 첫 번째 결과
  👥 균등 분배   [채우기↗]       ─────────────────────
  🚪 중도 귀가   [채우기↗]       👤 두 번째 질문 (아래로 쌓임)
  🥤 소량 섭취   [채우기↗]       🤖 두 번째 결과
  🎂 생일 면제   [채우기↗]       ─────────────────────
                                [정산 상황 텍스트 영역]
                                [전송 →]
```

메시지는 오래된 것부터 위→아래 순서로 표시. 전송 후 `st.rerun()`으로 갱신.

## 세션 상태

```python
st.session_state.messages     # 대화 이력 (user/assistant 메시지 리스트)
st.session_state["input_text"] # 입력창 텍스트 (text_area의 key; 사이드바 예시로 채움)
```

- `messages` 각 항목(assistant): `{"role": "assistant", **graph_result}`
  (graph_result = parsed_json / strategy / calculation_result / calc_explanation / final_report / safety_error / error 등)
- 사이드바 예시 버튼 → `st.session_state["input_text"]`에 프롬프트 주입 후 `st.rerun()`
- `대화 초기화`는 `window.parent.document.location.reload()`로 페이지 새로고침 (session_state 전체 초기화)

## 화면 흐름

1. 정산 상황을 텍스트 영역에 입력 (좌측 예시 클릭 시 채워짐)
2. `전송 →` 클릭 → `_invoke_graph()` → 결과가 채팅 히스토리에 추가
3. 추가 조건을 다시 입력하면 자동으로 피드백(재계산) 모드로 전환
4. 공유 메시지 코드 블록 우상단 복사 버튼 제공, 계산 근거는 `📋 계산 근거 보기` expander로 확인

## 피드백 모드 자동 전환

`_invoke_graph()` 내부에서 판단:
- `messages`에 직전 assistant 메시지가 있고 그 `parsed_json.participants`가 존재 →
  이전 `parsed_json` / `strategy` / `feedback_history`를 state에 실어 피드백 모드로 invoke
- 없으면 → 초기 정산 모드 (`raw_input` + 빈 `feedback_history`)
- 별도 "재계산" 버튼 없음

## 결과 표시 (_render_result)

- `error` → 빨간 오류 박스 / `safety_error` → 노란 경고 박스 (재입력 안내)
- 전략 배지: SIMPLE("균등 분배") / EXCEPTION("⚡ 예외 조건 반영")
- 참여자 카드: 이름 · 최종 금액 (`breakdown`에 감액/할증 메모가 있으면 함께 표시)
- `floor_applied` 있으면 하한선(30%) 적용 안내 caption
- `total_verified`가 False면 검증 불일치 경고
- `calc_explanation` 있으면 접이식 코드 블록, `final_report`는 공유용 메시지 코드 블록

## 이 폴더에서 하지 않는 것

- 정산 계산 로직 구현
- LLM 직접 호출
- 세션 외부 데이터 저장
