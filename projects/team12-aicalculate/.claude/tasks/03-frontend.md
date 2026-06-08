# Step 3 — Frontend 구현 에이전트 브리핑

## 전제 조건

아래 두 가지가 완료된 상태다:
- `calculator/engine.py` — `calculate()`, `recalculate()` 구현 완료
- `ai/graph.py` — `graph` 객체 export 완료

시작 전 아래를 확인한다:

```python
from ai.graph import graph
result = graph.invoke({"raw_input": "테스트", "feedback_history": []})
print(result.keys())  # state 키 목록 확인
```

## 프로젝트 컨텍스트

Streamlit UI. 전체 3단계 중 **3단계** — 마지막 구현 단계.

## 작업 범위

`front/` 폴더만 구현한다. `ai/`, `calculator/`는 import만 하고 수정하지 않는다.
구체적인 역할 정의는 `front/CLAUDE.md`를 먼저 읽어라.

## 실행

```bash
streamlit run front/app.py
```

## session_state 구조

```python
# 초기화
if "state" not in st.session_state:
    st.session_state.state = {
        "raw_input": "",
        "parsed_json": {},
        "strategy": "",
        "calculation_result": {},
        "feedback_history": [],
        "final_report": "",
    }
```

## 화면 구성

### 1단계: 입력

```python
user_input = st.text_area("정산 상황을 자연어로 입력하세요", height=120)
if st.button("정산 시작") and user_input:
    with st.spinner("AI가 분석 중입니다..."):
        result = graph.invoke({
            "raw_input": user_input,
            "feedback_history": st.session_state.state["feedback_history"]
        })
        st.session_state.state.update(result)
```

### 2단계: 결과 출력

`calculation_result`가 있을 때 표시:

```python
if st.session_state.state.get("calculation_result"):
    cr = st.session_state.state["calculation_result"]
    
    # 참여자별 정산표
    st.subheader("정산 결과")
    for p in cr["participants"]:
        st.write(f"**{p['name']}**: {p['final_amount']:,}원")
    
    # 계산 근거 설명
    st.subheader("계산 근거")
    st.write(st.session_state.state["final_report"])
```

### 3단계: 피드백 재계산

```python
feedback_input = st.text_input("추가 조건이 있으면 입력하세요 (예: D는 안주도 거의 안 먹었어)")
if st.button("재계산") and feedback_input:
    # feedback_history에 추가
    st.session_state.state["feedback_history"].append(feedback_input)
    
    # FeedbackParsingNode 진입 — ai/graph.py에서 feedback 진입점 확인 후 구현
    with st.spinner("재계산 중..."):
        result = graph.invoke({
            "raw_input": st.session_state.state["raw_input"],
            "parsed_json": st.session_state.state["parsed_json"],
            "feedback_history": st.session_state.state["feedback_history"],
        })
        st.session_state.state.update(result)
    st.rerun()
```

### 4단계: 공유 메시지 복사

```python
if st.session_state.state.get("final_report"):
    st.subheader("공유용 정산 메시지")
    st.code(st.session_state.state["final_report"], language=None)
    # st.code는 우상단에 복사 버튼이 자동으로 생성됨
```

## 구현 시 주의사항

- `graph.invoke()`의 실제 반환 키 구조는 `ai/graph.py`의 `SettlementState`와 일치한다
- 피드백 재진입 방법은 `ai/graph.py` 구현 방식에 따라 달라질 수 있음 — 실제 코드 확인 후 맞게 구현
- SafetyCheckNode가 재입력 요청을 반환하는 경우 (`calculation_result` 없음) 사용자에게 메시지 표시

## 완료 기준

`streamlit run front/app.py` 실행 후 브라우저에서:

1. 시나리오 A 자연어 입력 → 참여자별 정산표 + 설명 출력 확인
2. 피드백 입력 ("D는 안주도 거의 안 먹었어") → 재계산 결과 업데이트 확인
3. 공유 메시지 복사 버튼 동작 확인
