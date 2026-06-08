# CareerMate — 제품 개요 & 에이전트 전환

> 이 문서는 CareerMate가 **무엇을 만드는 제품인지**, 그리고 원본 기획의 프롬프트 체인 구조를 **어떻게 진짜 에이전트 그래프로 전환하는지**를 설명합니다.
> 비전공자도 읽을 수 있도록 새 개념은 처음 등장할 때 한 줄로 풀어 씁니다.

---

## 1. 제품 정의

**CareerMate**는 대학생·사회초년생을 위한 AI 커리어 코칭 에이전트입니다.
사용자가 자신의 전공·보유 기술·목표 직무를 입력하면, 에이전트가 역량 갭을 진단하고 주차별 실행 로드맵을 생성합니다.

### 핵심 가치

| 가치 | 설명 |
|------|------|
| **갭 기반 진단** | 목표 직무 요구역량과 현재 보유역량을 비교해 "무엇이 부족한지"를 명시 |
| **실행 가능한 로드맵** | 주당 가용 시간을 실제로 지키는 주차별 계획 (시간 예산 검증 포함) |
| **신뢰할 수 있는 자원** | 정적 스킬 DB 조회로 환각 강의·링크 차단 |
| **자기 검증** | 생성한 로드맵을 에이전트 스스로 체크리스트로 검증하고 위반 시 재생성 |
| **시간축 가치** | 재방문 시 직전 로드맵·주차 진행기록을 반영해 "오늘 어디까지 왔는지"를 이어받음 |

---

## 2. 대상 사용자 & 페르소나

### 주요 페르소나

**페르소나 A — 전공자 취준생**
- 컴퓨터공학 3~4학년, 백엔드 개발자 지망
- 보유: Python 기초, 자료구조 이론
- 고민: "Spring이 필요한지 아닌지 모르겠고, 어떤 순서로 공부해야 하는지 막막하다"
- 기대: 내 현재 실력 기준으로 빠진 스킬을 순서대로 채워 주는 로드맵

**페르소나 B — 비전공 전환자**
- 경영학과 졸업, IT 기획자·데이터 분석가 전환 희망
- 보유: Excel, 기초 SQL
- 고민: "어디서부터 시작해야 하는지, 내가 지원 가능한 직무가 뭔지 모른다"
- 기대: 직무 모호성을 해소해 주는 질문 + 현실적 기간의 로드맵

---

## 3. 원본 설계 vs. 개선 설계 — "체인 vs. 에이전트"

> **프롬프트 체인(Prompt Chaining Workflow)**: LLM 호출을 고정 순서로 연결한 직선 파이프라인. 분기·자율성·도구 호출 없음. Anthropic "Building Effective Agents"에서 agent와 구분되는 workflow 패턴으로 정의.
>
> **에이전트(Agent)**: 상황에 따라 스스로 경로를 결정하고, 도구를 호출하며, 결과를 자가 검증하는 구조. LangGraph conditional edge로 구현.

### 비교표

| 항목 | 원본 설계 (프롬프트 체인) | 개선 설계 (에이전트 그래프) |
|------|--------------------------|--------------------------|
| **제어 흐름** | 항상 동일한 8단계 직선 | 조건 엣지 기반 동적 분기 |
| **라우팅** | 없음 (모든 사용자 동일 경로) | `triage_router`: ambiguity_score로 ask/proceed 분기 |
| **도구 호출** | 0개 (LLM 학습 지식만) | `lookup_skill()` — 정적 스킬 DB 조회 + `web_search()` — 검색 API 호출 (tool use 0→2) |
| **자기 검증** | 없음 | `roadmap_critic`: 4종 체크리스트 검증 후 위반 시 재생성 |
| **에이전트 간 협업** | 일방향 직렬 전달 | Gap→Job 되먹임: `needs_rerun` 플래그로 1회 재요청 |
| **메모리** | 1세션 저장 (DB 1행) | 경량 episodic memory: 직전 로드맵 + 주차 진행기록 반영 |
| **계획 수립** | 4주/8주 고정 템플릿 채우기 | 갭 크기·가용시간으로 기간 동적 산출 후 프리셋 표시 |
| **가드레일** | 프롬프트 선언만 | Critic 노드 금칙 표현 런타임 검사 + `verified` 플래그 |
| **Anthropic 분류** | Prompt Chaining Workflow | Agent (routing + tool use + evaluator-optimizer) |

### 전환 근거

원본 기획서 6페이지는 "세 개의 agent가 **선형적으로 데이터를 전달**"이라고 직접 표현했습니다.
Anthropic "Building Effective Agents"는 이 패턴을 workflow로 분류하며, LLM이 스스로 제어 흐름·도구 사용을 결정할 때 비로소 agent라 정의합니다.

아이러니하게도 원본 7페이지 예외 처리 항목("직무 모호 → 유사 직무 제안", "정보 부족 → 추가 질문", "공고 짧음 → 샘플 안내")에는 에이전트다운 씨앗이 이미 담겨 있었습니다. 이 씨앗들을 **부록에서 그래프의 공식 노드·조건 엣지로 승격**하는 것이 이번 전환의 핵심입니다.

---

## 4. 개선된 에이전트 그래프 — 전체 흐름

```
START
  │
  ▼
[onboarding_intake]  ← 프론트 입력 구조화 + episodic_memory 조회
  │
  ▼
[progress_reconciliation]  ← returning_user면 직전 로드맵·진행기록 반영
  │
  ▼
[triage_router] ─── ambiguity_score > THRESHOLD? ──▶ [clarify] ─┐
  │ proceed                                                       │
  │ ◀─────────────────────────────────────────────────────────────┘
  ▼
[profile_diagnosis]  ← ProfileDiagnosisAgent
  │
  ▼
[job_requirement]  ← JobRequirementAgent
  │
  ▼
[gap_analysis]  ─── needs_rerun=true & rerun_count < 1? ──▶ [job_requirement]
  │ proceed                                                  (1회 되먹임)
  ▼
[roadmap_plan]  ← lookup_skill() 호출로 선후행·자원·시간 확정
  │
  ▼
[roadmap_critic] ─── verdict=revise & revision_count < 2? ──▶ [roadmap_plan]
  │ pass (또는 revision_count >= 2)                          (최대 2회 재생성)
  ▼
[finalize]  ← final_output 조립 + verified 플래그 + trace 요약
  │
  ▼
END
```

조건 엣지 정의 (LangGraph `add_conditional_edges` 기준):

```python
# 모호성 라우터 분기
graph.add_conditional_edges(
    "triage_router",
    lambda state: state["route_decision"],   # "ask" | "proceed"
    {"ask": "clarify", "proceed": "profile_diagnosis"}
)

# Gap → Job 되먹임 (최대 1회)
graph.add_conditional_edges(
    "gap_analysis",
    lambda state: (
        "rerun_job"
        if state["needs_rerun"] and state["rerun_count"] < MAX_RERUN
        else "skip_rerun"
    ),
    {"rerun_job": "job_requirement", "skip_rerun": "roadmap_plan"}
)

# Critic 반복 루프 (최대 2회)
graph.add_conditional_edges(
    "roadmap_critic",
    lambda state: (
        "revise"
        if state["critic_report"]["verdict"] == "revise"
           and state["revision_count"] < MAX_REVISIONS
        else "pass"
    ),
    {"revise": "roadmap_plan", "pass": "finalize"}
)
```

---

## 5. 3대 개선 상세 설명

### 5-1. 모호성 라우터 노드 (Triage / Clarify-or-Proceed)

> **자율 라우팅(Autonomous Routing)**: 입력 상황에 따라 에이전트가 스스로 다음 경로를 결정하는 능력. 고정 직선과 에이전트를 가르는 1차 기준.

**무엇을 하는가**
온보딩 직후 `triage_router` 노드가 `onboarding_input`을 읽어 `ambiguity_score`(0.0~1.0)를 산정합니다.
임계값(`AMBIGUITY_THRESHOLD`, 권장 0.6) 초과 시 `ask` 경로 → `clarify` 노드에서 2~3개 역질문 또는 유사 직무 후보 제시 후 사용자 응답을 `clarify_answers`에 수집, 다시 `triage_router`로 돌아와 재평가합니다.
미만이면 `proceed` → 바로 `profile_diagnosis`로 진행합니다.

**State 변화**

| 키 | 노드 | 값 예시 |
|----|------|---------|
| `ambiguity_score` | triage_router 쓰기 | `0.72` |
| `route_decision` | triage_router 쓰기 | `"ask"` |
| `clarify_answers` | clarify 쓰기 | `[{question: "백엔드 개발자와 풀스택 중 어느 쪽에 가깝나요?", answer: "백엔드", kind: "similar_role_pick"}]` |

**왜 에이전트다운가**
ReAct(Yao et al. 2022)의 핵심인 "상황을 읽어 행동을 결정"이 이 노드에서 처음 발현됩니다.
모든 사용자가 동일한 파이프라인을 통과하는 구조에서, 입력에 따라 경로가 달라지는 에이전트 그래프로 바뀝니다.

---

### 5-2. 스킬·학습자원 DB 조회 툴 + 웹검색 툴 (Skill/Resource Lookup & Web Search Tools)

> **도구 호출(Tool Use)**: LLM이 직접 답하는 대신 외부 함수를 호출해 정보를 가져오는 행위. 에이전트와 단순 LLM 체인을 가르는 기준 중 하나 (Anthropic "Building Effective Agents").

**툴 계약 — lookup_skill (정적 스킬 DB 캐시/보조)**

```python
def lookup_skill(name: str) -> SkillRecord:
    """
    IT 직무 한정 정적 JSON 스킬 사전 조회.
    존재하면 status="known", 없으면 status="unknown" 반환 (예외 throw 금지).
    Agent3(gap_analysis/roadmap_plan)에서 DB-hit(known)이면 검색 생략(캐시 역할).
    """
    ...

def list_skills_for_role(role: str) -> list[SkillRecord]:
    """직무명으로 관련 스킬 집합 일괄 조회. 미매핑이면 빈 리스트."""
    ...

def normalize_skill_name(raw: str) -> str:
    """'react.js' → 'React' 등 별칭 정규화. 실패 시 원문 반환."""
    ...
```

**툴 계약 — web_search (검색 API, 크롤링 아님)**

```python
from pydantic import BaseModel

class SearchHit(BaseModel):
    title: str            # 검색 결과 제목
    url: str              # 출처 URL (verified=True 근거)
    snippet: str          # 검색 API가 반환한 본문 발췌 (크롤링 아님)
    source: str           # 도메인 또는 제공자명 (예: "wanted.co.kr", "tavily")
    retrieved_at: str     # ISO 타임스탬프 (검색 시각)

def web_search(query: str, k: int = 5) -> list[SearchHit]:
    """
    검색 API 1개(Tavily 또는 Serper 택1)를 호출해 상위 k개 결과를 반환한다.
    절대 예외를 던지지 않는다(lookup_skill과 동일 철학).
    on_fail(API 오류/쿼터 초과/MAX_SEARCH 초과): 빈 리스트 [] 반환 +
      호출 노드가 state["search_degraded"]=True 설정 → LLM 자체지식 폴백(verified=False).
    캐시 히트 시 state["search_results"]에서 반환(API 재호출 없음).
    """
    ...
```

**Agent2(job_requirement) — 웹검색 기본 의존**
- 공고 텍스트가 충분(≥100자)하면 검색 생략(공고 우선).
- 부실하면 `web_search(f"{target_role} 채용공고 요구역량 필수기술", k=5)` 호출 → snippet에서 required/preferred skills 추출, 각 스킬에 `source_url` 부착.
- `list_skills_for_role`은 검색 결과 0건일 때 최후 폴백(보조).

**Agent3(gap_analysis/roadmap_plan) — DB 캐시 우선, miss 시 검색 보강**
- `lookup_skill` 먼저 → `status="known"`이면 DB 사용(검색 생략).
- `status="unknown"`이면 `web_search(f"{skill} 학습 강의 튜토리얼 공식문서", k=3)` 호출 → 실제 url을 가진 ResourceItem 생성.
- 검색도 실패하면 LLM 폴백(verified=False, origin="llm").

**SkillRecord 스키마 (반환 예시)**

```json
{
  "name": "FastAPI",
  "status": "known",
  "prereqs": ["Python", "HTTP 기초"],
  "resources": [
    {
      "title": "FastAPI 공식 튜토리얼",
      "url": "https://fastapi.tiangolo.com/tutorial/",
      "type": "doc",
      "verified": true
    }
  ],
  "typical_hours": 20,
  "verified": true
}
```

**폴백 규칙 (출처 기반 3단계)**

| 출처 | `verified` | `origin` | url | 비고 |
|------|-----------|---------|-----|------|
| 스킬DB known | `true` | `"db"` | DB 검수 url | 최고 신뢰, 뱃지 없음 |
| web_search (SearchHit.url 존재) | `true` | `"web"` | SearchHit.url | "웹 출처" 뱃지 + 링크 노출 |
| LLM 순수 자체지식 (url 없음) | `false` | `"llm"` | `None` | "검증 안 됨" 뱃지 |

기존 2단계(known=verified / unknown=unverified)에서 확장: web_search로 url 보강에 성공하면 `verified=True`(단 `origin="web"` 명시). 검색까지 실패한 경우에만 `origin="llm"` → `verified=False`.

**스킬 DB 예시 구조 (50~150행 JSON)**

```json
{
  "skills": {
    "Python": {
      "prereqs": [],
      "resources": [{"title": "점프 투 파이썬", "url": "https://wikidocs.net/book/1", "type": "doc", "verified": true}],
      "typical_hours": 40
    },
    "FastAPI": {
      "prereqs": ["Python", "HTTP 기초"],
      "resources": [{"title": "FastAPI 공식 튜토리얼", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "doc", "verified": true}],
      "typical_hours": 20
    },
    "React": {
      "prereqs": ["JavaScript", "HTML/CSS"],
      "resources": [{"title": "React 공식 문서", "url": "https://react.dev/learn", "type": "doc", "verified": true}],
      "typical_hours": 30
    }
  },
  "roles": {
    "백엔드 개발자": ["Python", "FastAPI", "SQL", "Docker", "Git"],
    "프론트엔드 개발자": ["JavaScript", "HTML/CSS", "React", "TypeScript", "Git"]
  },
  "aliases": {
    "react.js": "React",
    "fastapi": "FastAPI",
    "py": "Python"
  }
}
```

**왜 에이전트다운가**
ReAct 패턴에서 Act = 도구 호출입니다. tool use 0 → 1로 전환되며 Anthropic 분류상 "에이전트"가 됩니다.
동시에 로드맵 강의·링크 환각을 차단해 신뢰도를 높입니다(RAG-lite, 검색 대상을 웹에서 로컬 사전으로 한정).

---

### 5-3. 로드맵 Critic/Reflection 루프

> **Reflection / Self-Correction**: 에이전트가 자신의 출력을 기준에 비추어 스스로 평가하고, 위반이 있으면 재생성하는 자기 검증 루프. Reflexion(Shinn et al. 2023), Self-Refine(Madaan et al. 2023)의 핵심 개념.

**4종 체크리스트**

| 번호 | `violation_type` | 검사 내용 |
|------|-----------------|-----------|
| ① | `uncovered_gap` | `gap_analysis.gaps`의 모든 스킬이 `roadmap.weeks` 어딘가에 1개 이상 매핑됐는가 |
| ② | `time_budget_exceeded` | 각 주차의 `planned_hours` ≤ `weekly_hours_budget` (가용 시간 초과 금지) |
| ③ | `prereq_order_violation` | `lookup_skill`의 `prereqs` 순서대로 스킬이 배치됐는가 (예: Python 전에 FastAPI 금지) |
| ④ | `forbidden_phrase` | "합격 가능", "보장", "반드시 취업" 등 금칙 표현 없음 |

**CriticReport 스키마**

```python
class Violation(BaseModel):
    type: violation_type          # uncovered_gap | time_budget_exceeded | prereq_order_violation | forbidden_phrase
    detail: str                   # 위반 상세 설명
    location: str                 # "week 3" | "FastAPI" | "week 2 objectives[1]"

class CriticReport(BaseModel):
    verdict: critic_verdict       # "pass" | "revise"
    violations: list[Violation]   # pass면 빈 리스트
    checked_at_revision: int      # 검증 시점 revision_count
```

**루프 제어**

```python
MAX_REVISIONS = 2  # 최대 2회 재생성 후 위반 남아도 강제 finalize

# roadmap_plan 호출 시 위반 사유 주입
if state["critic_report"] and state["critic_report"]["verdict"] == "revise":
    revision_context = {
        "violations": state["critic_report"]["violations"],
        "revision_count": state["revision_count"]
    }
    # → roadmap_plan 프롬프트에 "아래 위반 사항을 수정해서 재생성하세요:" 주입
```

**왜 에이전트다운가**
Reflexion(Shinn et al. 2023)과 Self-Refine(Madaan et al. 2023)의 핵심인 "자기 출력을 평가해 재시도"가 이 노드에서 구현됩니다.
동시에 4페이지 가드레일 선언("합격 단정 금지")을 런타임 강제로 연결합니다 — 선언만 있는 프롬프트 지시에서 출력 후 검증 노드로 격상됩니다.

---

## 6. 에이전트 간 되먹임 (Gap → Job Re-query)

> **되먹임(Feedback Loop)**: 하류 에이전트가 상류 에이전트에게 "다시 해 달라"고 요청하는 양방향 협업. 에이전트 수가 아니라 상호작용이 multi-agent를 만든다.

**동작**

1. `gap_analysis` 노드가 `job_requirement.evidence_strength == "weak"`를 감지
2. `State.needs_rerun = true`, `State.rerun_reason = "공고 너무 짧아 필수역량 근거 약함"` 설정
3. 조건 엣지가 `job_requirement` 노드를 1회 재실행 → `rerun_reason`을 컨텍스트로 주입해 재추출
4. `rerun_count`가 `MAX_RERUN(=1)` 도달 시 추가 재요청 없이 진행 (무한 루프 방지)

```python
# gap_analysis 노드 내 의사코드 (읽기만 — 카운터 증가는 conditional edge route 함수에서)
if job_requirement.evidence_strength == "weak" and state["rerun_count"] < MAX_RERUN:
    return {
        "needs_rerun": True,
        "rerun_reason": "job_requirement evidence_strength=weak: 공고가 짧아 필수역량 근거 부족"
        # rerun_count += 1 은 여기서 하지 않음 — edge route 함수에서만 증가
    }
```

---

## 7. 자율성 범위 표

무엇을 에이전트가 자율적으로 처리하는지, 무엇이 사람의 판단인지, 무엇을 시스템이 절대 하지 않는지를 명시합니다.

| 구분 | 항목 | 담당 |
|------|------|------|
| **에이전트 자율** | 모호성 점수 산정 및 ask/proceed 분기 | `triage_router` |
| **에이전트 자율** | 부족 역량 우선순위 결정 | `gap_analysis` 노드 |
| **에이전트 자율** | 로드맵 기간 동적 산출 (갭 크기 + 가용시간 기반) | `roadmap_plan` |
| **에이전트 자율** | 로드맵 자기 검증 및 재생성 | `roadmap_critic` |
| **에이전트 자율** | Job 에이전트 재요청 여부 판단 | `gap_analysis` → 조건 엣지 |
| **에이전트 자율** | 검색 쿼리 생성·호출 여부 판단 (공고 충분 시 생략, DB-hit 시 생략) | `job_requirement`, `gap_analysis`, `roadmap_plan` |
| **사람 결정** | 목표 직무 최종 선택 (유사 직무 후보 중 선택은 사용자) | 사용자 입력 |
| **사람 결정** | 주차 완료 여부 체크 (weekly_progress 업데이트) | 대시보드 체크박스 |
| **사람 결정** | 생성된 로드맵 채택·수정 여부 | 사용자 판단 |
| **절대 안 함 (Guardrail)** | 합격 가능성 단정, "반드시 취업된다" 류 표현 | Critic 금칙 검사 + 프롬프트 |
| **절대 안 함 (Guardrail)** | 진로 최종 결정 ("이 직무만이 정답") | 프롬프트 + disclaimer |
| **절대 안 함 (범위 외)** | 실시간 채용공고 크롤링 | 미구현 (범위 외) |
| **절대 안 함 (범위 외)** | 모델 파인튜닝, 대규모 데이터 수집 | 미구현 (범위 외) |
| **절대 안 함 (범위 외)** | IT 직무 외 도메인 지원 (의료·법률 등) | 미구현 (범위 외) |

---

## 8. 비기능 요구사항

| 항목 | 제약 | 근거 |
|------|------|------|
| **개발 기간** | 1.5주 | 남은 일정 |
| **대상 직무** | IT 직무 1~2개 (백엔드·프론트엔드 권장) | 스킬 DB를 50~150행으로 유지하기 위한 범위 한정 |
| **공고 수집** | 대규모 크롤링 금지(채용사이트 순회·HTML 수집), 사용자 붙여넣기 또는 샘플 공고 | 원본 기획 유지 + 1.5주 범위 |
| **검색 API** | 허용 — 검색 API 1개(Tavily 또는 Serper 택1) 호출(쿼리→색인된 결과 메타데이터 수신). 크롤링(사이트 직접 순회·HTML 수집)과 구분. `MAX_SEARCH=8`(세션 누적 호출 상한) | 웹검색 전면 도입, 과설계 방지 |
| **모델 파인튜닝** | 금지 | 범위 초과 |
| **스킬 DB 크기** | 50~150행 JSON/CSV | 크게 만들수록 유지 비용 증가, 작아도 IT 1~2개 직무 커버 가능 |
| **되먹임 횟수** | Gap→Job 최대 1회 (`MAX_RERUN=1`) | 무한 루프 방지 |
| **재생성 횟수** | Critic→Roadmap 최대 2회 (`MAX_REVISIONS=2`) | 무한 루프 방지 |
| **메모리 범위** | 읽기+반영 우선 (직전 로드맵 + 주차 완료 여부) / 쓰기는 체크박스 수준 | MVP 범위 내 경량 episodic memory |
| **프론트·인프라** | 에이전트 그래프·툴·검증 로직 이후 우선순위 | 에이전트 핵심 요소가 일정에서 누락되지 않도록 |

---

## 9. Anthropic "Workflow vs. Agent" 구분 인용

Anthropic "Building Effective Agents (2024)"는 LLM 기반 시스템을 두 가지로 명확히 구분합니다:

> **Workflow**: LLM과 도구가 미리 정해진 코드 경로를 따라 동작하는 시스템.
> **Agent**: LLM이 자신의 프로세스와 도구 사용을 스스로 지시하며, 목표 달성 방법을 직접 결정하는 시스템.

원본 CareerMate(6페이지 "선형적으로 데이터를 전달")는 **Prompt Chaining Workflow**입니다.
개선 CareerMate는 다음 세 가지를 추가해 **Agent**로 전환됩니다:

1. **Routing** — `triage_router`의 조건 분기 (자율 경로 결정)
2. **Tool Use** — `lookup_skill()` 정적 스킬 DB 조회 + `web_search()` 검색 API 호출 (외부 함수로 정보 획득, tool use 0→2)
3. **Evaluator-Optimizer** — `roadmap_critic` 검증 후 재생성 루프 (자기 교정)

이 세 요소는 Anthropic이 열거한 에이전트 핵심 패턴과 1:1 대응됩니다.

---

## 10. 구현 우선순위 (1.5주 일정)

```
Week 1 (전반)
  1. LangGraph State 스키마 + 그래프 뼈대 (노드·엣지 정의)
  2. 스킬 DB JSON 작성 (IT 1~2직무, 50~100행)
  3. lookup_skill / normalize_skill_name / list_skills_for_role 구현

Week 1 (후반)
  4. triage_router + clarify 노드 + 조건 엣지
  5. profile_diagnosis / job_requirement 노드 (원본 프롬프트 재활용)
  6. gap_analysis 노드 + needs_rerun 되먹임 엣지

Week 2 (전반)
  7. roadmap_plan 노드 (lookup_skill 통합 + 동적 기간 산출)
  8. roadmap_critic 노드 (4종 체크리스트 + 재생성 루프)
  9. progress_reconciliation + episodic_memory 읽기
  10. finalize + trace_log + verified 플래그

Week 2 (후반)
  11. 통합 테스트 (백엔드·프론트 연결)
  12. 대시보드 trace 타임라인 ("why-this-path")
```

---

## 관련 문서

- [에이전트 그래프 & State 스키마](02-agent-graph.md) — 노드·엣지·Pydantic 모델 전체 정의
- [에이전트 I/O·계약·프롬프트 전략](03-agent-contracts.md) — JobRequirement/GapRoadmap 에이전트 상세
- [스킬 DB & 툴 계약](04-tools-skill-db.md) — lookup_skill·web_search 구현 가이드 + DB 예시
- [Critic/Reflection 루프 & 가드레일](05-reflection-critic.md) — 4종 체크리스트 상세 + 재생성 프롬프트
- [Pydantic 데이터 모델 & Episodic Memory](06-data-model.md) — SearchHit·ResourceItem·CareerMateState 스키마
- [평가 & KPI](07-evaluation-kpi.md) — Tool Hit율·웹 보강율 측정 지표

---

## 용어 빠른 참조

| 용어 | 한 줄 풀이 |
|------|-----------|
| `ambiguity_score` | 입력이 얼마나 모호한지 0~1로 표현한 점수. 높을수록 역질문 필요 |
| `route_decision` | 모호성 라우터의 결정: `ask`(역질문) 또는 `proceed`(바로 진단) |
| `needs_rerun` | 갭 분석이 "직무 요구역량 근거 약함"을 감지하면 `true`로 설정해 Job 에이전트 재호출 |
| `critic_verdict` | Critic 노드 판정: `pass`(finalize 진행) 또는 `revise`(로드맵 재생성) |
| `violation_type` | Critic이 잡는 위반 종류: 역량 미매핑·시간 초과·선후행 위반·금칙 표현 |
| `lookup_skill` | 정적 스킬 DB 캐시/보조 조회 함수. DB-hit(known)이면 검색 생략. LLM 환각 차단 |
| `web_search` | 검색 API 호출 함수(크롤링 아님). Agent2 기본 의존, Agent3 DB-miss 시 보강. `MAX_SEARCH=8` 상한 |
| `SearchHit` | web_search 반환 단위. `title·url·snippet·source·retrieved_at` 포함 |
| `search_degraded` | 검색 실패/상한 초과 발생 시 `true`. finalize disclaimer에 반영 |
| `verified` | 출처 기반 3단계: DB known→`true`(origin="db"), web url 있음→`true`(origin="web"), LLM 폴백→`false`(origin="llm") |
| `origin` | 검증 출처 종류: `"db"`(스킬DB), `"web"`(웹검색), `"llm"`(LLM 자체지식) |
| `episodic memory` | 재방문 사용자의 직전 로드맵 + 주차 진행기록. 미완료 이월·완료 진척 반영에 사용 |
| `trace` | 각 노드가 무슨 결정을 내렸는지 시계열로 쌓는 실행 로그. 대시보드 타임라인 원본 |
