# Agent3 — Gap Analysis & Roadmap Planner

CareerMate의 `gap_analysis` · `roadmap_plan` · `roadmap_critic`을 담당하는 백엔드 에이전트 모듈입니다.
에이전트 1(프로필 진단)·에이전트 2(직무 요구역량) 결과를 받아 **부족 역량을 진단**하고 **주차별 학습 로드맵**을 생성한 뒤, **4종 체크리스트로 자가 검증**합니다.

> **백엔드 통합 완료**: 이제 독립 서버(`:8003`)가 아니라 `backend/agents/agent3/`의 모듈입니다.
> `backend/main.py`가 `Agent3.default(request, agent1Result, agent2Result)`로 호출하고,
> 결과를 `RoadmapResponse`(recommendedPath/skillGaps/week1To2..week7To8)로 반환합니다.
> 호출 래퍼는 [Agent3.py](Agent3.py), 오케스트레이션은 [pipeline.py](pipeline.py) 참고.
>
> **실행**: `cd backend && uvicorn main:app --port 8000` (API 키는 `backend/.env`)
> **테스트**: `cd backend && PYTHONPATH=. python -m pytest agents/agent3/tests -q`
>
> 아래 본문 중 독립 서버(`uvicorn agent3.main:app :8003`) 관련 설명은 통합 전 기준이라 더 이상 유효하지 않습니다.

> 설계 근거: [docs/02-agent-graph.md](../docs/02-agent-graph.md), [docs/03-agent-contracts.md](../docs/03-agent-contracts.md), [docs/04-tools-skill-db.md](../docs/04-tools-skill-db.md), [docs/05-reflection-critic.md](../docs/05-reflection-critic.md)

---

## 위치 결정

`backend/readme.md`에는 agent 파일을 backend 내부에 두라는 지시가 없어, 기존 backend 및 `agent2/`와 충돌하지 않도록 루트에 `agent3/` 전용 폴더로 구성합니다. (Agent2와 동일한 컨벤션)

---

## 에이전트 역할 분담

```
[에이전트 1: profile_diagnosis]   현재 역량 구조화        → ProfileDiagnosis
[에이전트 2: job_requirement]     목표 직무 요구역량 추출  → JobRequirement
[에이전트 3: gap_analysis →       부족 역량 진단 +         → GapAnalysis
             roadmap_plan]        주차별 로드맵 생성        → Roadmap
[에이전트 3: roadmap_critic]      4종 체크리스트 자가 검증  → CriticReport
```

Agent3는 에이전트 1·2의 출력을 **입력으로** 받습니다.
- 에이전트 1: 아직 미개발 → 개발 중에는 목 데이터(`ProfileDiagnosis` 픽스처)로 대체
- 에이전트 2: `feat/agent2` 브랜치 참고 (`agent2/models.py`의 `JobRequirement`)

---

## Agent3가 하는 일 (3개 노드)

### 1. `gap_analysis` 노드
1. 에이전트1 `profile` vs 에이전트2 `job_requirement` 비교 → 부족 역량 도출
2. 부족 역량 우선순위 결정 (required→high, preferred→medium)
3. `normalize_skill_name` + `lookup_skill` 호출로 스킬 상태(known/unknown) 확인
4. `status="unknown"`이면 `web_search`로 실제 URL 보강
5. 에이전트2 `evidence_strength == "weak"`이면 `needs_rerun=true` (에이전트2 재실행 신호, 최대 1회)

### 2. `roadmap_plan` 노드
1. 기간 동적 산출: `sum(스킬별 typical_hours) / weekly_hours` (Plan-and-Solve)
2. `lookup_skill.prereqs`로 선후행 순서 확정
3. `status="unknown"` 스킬은 `web_search`로 자원 URL 보강
4. 재방문 사용자면 episodic memory의 이월/완료 스킬 반영
5. Critic이 `revise` 판정 시 위반 사유 받아 재생성 (최대 2회)

### 3. `roadmap_critic` 노드 (코드 기반 검증)
| # | violation_type | 검사 |
|---|----------------|------|
| ① | `uncovered_gap` | gap의 모든 스킬이 로드맵에 1개 이상 매핑되었는가 |
| ② | `time_budget_exceeded` | 각 주차 `planned_hours ≤ weekly_hours` |
| ③ | `prereq_order_violation` | `lookup_skill.prereqs` 선후행 순서 준수 |
| ④ | `forbidden_phrase` | "합격 가능", "반드시 취업" 등 금칙 표현 없음 |

---

## 폴더 구조

```
agent3/
├── README.md                 # 이 문서 (설계 + 개발 가이드)
├── __init__.py
├── requirements.txt          # 런타임 의존성
├── requirements-dev.txt      # + pytest
├── .gitignore
├── .env.example              # 환경변수 템플릿 (.env로 복사해 키 입력)
├── pytest.ini
├── constants.py              # MAX_RERUN/MAX_REVISIONS/MAX_SEARCH/FORBIDDEN_PHRASES ...
├── models.py                 # Pydantic 모델 (GapAnalysis, Roadmap, SkillRecord, FinalOutput ...)
├── state.py                  # Agent3State(공유 상태) + append_trace 헬퍼
├── skill_db.json             # 정적 스킬 사전 (7직무·53스킬 + 직무/스킬 별칭)
├── tools.py                  # lookup_skill, normalize_skill_name, list_skills_for_role, web_search
├── llm.py                    # Solar LLM (extract_gaps, generate_roadmap) + 규칙 폴백
├── gap_analysis_agent.py     # gap_analysis 노드
├── roadmap_plan_agent.py     # roadmap_plan 노드 (핵심)
├── roadmap_critic.py         # 4종 체크리스트 검증
├── main.py                   # 오케스트레이션 + finalize + FastAPI
└── tests/                    # pytest (오프라인·결정론: 키/네트워크 없이 폴백 경로)
    ├── conftest.py           # 키 제거 픽스처 + profile 픽스처
    ├── fixtures/             # 에이전트1 ProfileDiagnosis 목 JSON
    ├── test_skill_db.py      # 스킬 DB 무결성(참조·DAG)
    ├── test_tools.py
    ├── test_critic.py
    ├── test_llm_fallback.py
    ├── test_nodes.py
    ├── test_orchestration.py
    └── test_api.py
```

### 테스트

```powershell
.\.venv\Scripts\python.exe -m pip install -r agent3\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest agent3\tests -q
```

모든 테스트는 LLM/검색 키 없이(규칙 폴백) 오프라인으로 돌아간다. `conftest.py`가
`UPSTAGE_API_KEY`/`TAVILY_API_KEY`를 제거해 결정론을 보장한다.

---

## 개발 순서

| 단계 | 파일 | 내용 |
|------|------|------|
| 1 ✅ | `__init__.py`, `requirements.txt`, `.gitignore`, `README.md` | 프로젝트 초기화 (현재 단계) |
| 2 | `models.py` | Pydantic 모델 (GapItem·GapAnalysis·WeekPlan·Roadmap·SkillRecord·SearchHit·CriticReport) |
| 3 | `skill_db.json` | 스킬 사전 (선택 직무별 50~100 스킬, prereqs·resources·typical_hours·aliases) |
| 4 | `tools.py` | lookup_skill → normalize_skill_name → list_skills_for_role → web_search |
| 5 | `llm.py` | extract_gap_analysis, generate_roadmap (Agent2 llm.py 패턴 재사용) |
| 6 | `gap_analysis_agent.py` | gap_analysis 노드 (lookup_skill + web_search + needs_rerun) |
| 7 | `roadmap_plan_agent.py` | roadmap_plan 노드 (기간 산출 + 선후행 + 자원 보강) ⭐ 핵심 |
| 8 | `roadmap_critic.py` | 4종 체크리스트 |
| 9 | `main.py` | gap → roadmap → critic 통합 + FastAPI 엔드포인트 |
| 10 | `tests/` | 단위 + 통합 테스트 |

---

## 상수 (docs 기준)

```python
AMBIGUITY_THRESHOLD = 0.6   # (Agent3 범위 밖, 참고용)
MAX_RERUN = 1               # Gap→Job 되먹임 상한
MAX_REVISIONS = 2           # Critic→Roadmap 재생성 상한
MAX_SEARCH = 8              # 세션 누적 web_search API 호출 상한
```

---

## 폴백 규칙 (출처 기반 3단계 verified)

| 출처 | verified | origin | url |
|------|----------|--------|-----|
| 스킬DB known | `true` | `"db"` | DB 검수 url |
| web_search hit | `true` | `"web"` | SearchHit.url |
| LLM 순수 자체지식 | `false` | `"llm"` | `None` |

`lookup_skill`·`web_search`는 **절대 예외를 던지지 않습니다.** 실패 시 빈 결과 + 폴백 플래그.

---

## 실행 (예정)

```powershell
cd C:\workspaces\swmaestro-team07-ai-study
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r agent3\requirements.txt
$env:UPSTAGE_API_KEY="YOUR_UPSTAGE_API_KEY"
python -m uvicorn agent3.main:app --reload --port 8003
```

## API (예정)

```http
POST /agent3/roadmap
Content-Type: application/json
```

```json
{
  "profile": { "...": "에이전트1 ProfileDiagnosis" },
  "job_requirement": { "...": "에이전트2 JobRequirement" },
  "weekly_hours": 8
}
```

---

## 보안

API 키는 코드에 저장하지 않습니다. 반드시 `UPSTAGE_API_KEY` 환경변수로 주입하세요. (Agent2와 동일)
