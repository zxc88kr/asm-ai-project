# 06. 데이터 모델 · 메모리 · API

이 문서는 CareerMate 에이전트 그래프가 주고받는 **모든 데이터 구조**(Pydantic 모델), **경량 episodic 메모리 설계**, **저장소 테이블 스케치**, 그리고 **FastAPI 엔드포인트 계약**을 한 곳에 정리합니다.  
에이전트 그래프 흐름은 [에이전트 그래프](02-agent-graph.md)를, 노드별 에이전트 계약은 [에이전트 계약](03-agent-contracts.md)을 참고하세요.

---

## 목차

1. [그래프 State 스키마](#1-그래프-state-스키마)
2. [Pydantic 모델 전체 정의](#2-pydantic-모델-전체-정의)
3. [Enum 정의](#3-enum-정의)
4. [스킬 DB 툴 계약](#4-스킬-db-툴-계약)
5. [경량 Episodic 메모리](#5-경량-episodic-메모리)
6. [저장소 테이블 스케치](#6-저장소-테이블-스케치)
7. [FastAPI 엔드포인트 계약](#7-fastapi-엔드포인트-계약)

---

## 1. 그래프 State 스키마

> **State(상태)**란 LangGraph 그래프가 노드 사이를 이동하며 공유하는 "단일 공유 메모리"입니다. 모든 노드는 이 State를 읽고 일부 키만 덮어씁니다.

```python
# agent/state.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class CareerMateState(BaseModel):
    # ── 식별자 ──────────────────────────────────────────
    user_id:          str
    session_id:       str

    # ── 온보딩 입력 ──────────────────────────────────────
    onboarding_input: OnboardingInput

    # ── 모호성 라우터 ─────────────────────────────────────
    clarify_answers:  list[ClarifyAnswer]     = []
    ambiguity_score:  float                   = 0.0
    route_decision:   RouteDecision           = RouteDecision.proceed

    # ── 에이전트 출력 ─────────────────────────────────────
    profile:          Optional[ProfileDiagnosis]   = None
    job_requirement:  Optional[JobRequirement]     = None
    gap_analysis:     Optional[GapAnalysis]        = None
    roadmap:          Optional[Roadmap]            = None
    critic_report:    Optional[CriticReport]       = None

    # ── 되먹임 제어 (Gap→Job) ────────────────────────────
    needs_rerun:      bool                    = False
    rerun_reason:     Optional[str]           = None
    rerun_count:      int                     = 0        # MAX_RERUN = 1

    # ── reflection 루프 제어 ─────────────────────────────
    revision_count:   int                     = 0        # MAX_REVISIONS = 2

    # ── episodic 메모리 ───────────────────────────────────
    episodic_memory:  Optional[EpisodicMemory] = None

    # ── 실행 트레이스 ─────────────────────────────────────
    trace:            list[TraceEntry]        = []

    # ── 웹 검색 ───────────────────────────────────────────
    search_results:   dict[str, list[SearchHit]] = {}   # query→SearchHit 리스트 캐시(세션 내)
    search_count:     int                    = 0        # 실제 API 호출 누적(캐시 히트 제외)
    search_degraded:  bool                   = False    # 검색 실패/MAX_SEARCH 초과 시 True

    # ── 전역 검증 / 최종 출력 ──────────────────────────────
    verified:         bool                    = True
    final_output:     Optional[FinalOutput]   = None
    error:            Optional[str]           = None
```

### 키별 역할 요약

| 키 | 타입 | 쓰는 노드 | 설명 |
|----|------|-----------|------|
| `user_id` | `str` | `onboarding_intake` | episodic 메모리 조회/저장 키 |
| `session_id` | `str` | `onboarding_intake` | trace 로그 그룹핑 |
| `onboarding_input` | `OnboardingInput` | `onboarding_intake` | 전공·목표직무·주당가용시간 등 원본 입력 |
| `clarify_answers` | `list[ClarifyAnswer]` | `clarify` | ask 경로 역질문 응답 |
| `ambiguity_score` | `float` | `triage_router` | 0.0~1.0 모호도 (임계값: `AMBIGUITY_THRESHOLD = 0.6`) |
| `route_decision` | `RouteDecision` | `triage_router` | `ask` \| `proceed` — conditional_edge 조건 |
| `profile` | `ProfileDiagnosis` | `profile_diagnosis` | 강점/약점/준비수준 |
| `job_requirement` | `JobRequirement` | `job_requirement` | 필수·우대 기술, 근거강도 |
| `gap_analysis` | `GapAnalysis` | `gap_analysis` | 부족역량 + 재요청 필요 여부 |
| `roadmap` | `Roadmap` | `roadmap_plan` | 주차별 학습 계획 |
| `critic_report` | `CriticReport` | `roadmap_critic` | 4종 체크리스트 통과/위반 |
| `needs_rerun` | `bool` | `gap_analysis` | `True` → Job 재요청 트리거 |
| `rerun_count` | `int` | `gap_analysis` | 최대 1회 제한(무한루프 방지) |
| `revision_count` | `int` | `roadmap_critic` | 최대 2회 재생성 제한 |
| `episodic_memory` | `EpisodicMemory \| None` | `onboarding_intake` | 재방문자 직전 로드맵+진행기록 |
| `trace` | `list[TraceEntry]` | 모든 노드 (append) | why-this-path 타임라인 |
| `search_results` | `dict[str, list[SearchHit]]` | `job_requirement`, `roadmap_plan`, `gap_analysis` | query→SearchHit 캐시(세션 내). 동일 쿼리 재호출 방지. |
| `search_count` | `int` | 검색 호출 노드 전부 | 실제 API 호출 누적(캐시 히트 제외). `MAX_SEARCH=8` 가드. |
| `search_degraded` | `bool` | 검색 호출 노드 전부 | 검색 실패/상한 초과 1회라도 발생 시 True. finalize disclaimer에 반영. |
| `verified` | `bool` | `roadmap_plan`, `finalize` | 출처 없는 llm origin 항목 존재 시 `False`로 내림 |
| `final_output` | `FinalOutput \| None` | `finalize` | 사용자 전달 최종 산출물 |
| `error` | `str \| None` | 모든 노드 | 복구 불가 오류 → finalize 우회 |

---

## 2. Pydantic 모델 전체 정의

> 아래 모델들은 의사코드 수준의 **스케치**입니다. 실제 구현 시 `pydantic v2` (`from pydantic import BaseModel, Field`) 기준으로 작성하세요.

### 2-1. OnboardingInput — 사용자 온보딩 원본 입력

```python
class OnboardingInput(BaseModel):
    major:            str            # 전공 / 직무 배경 (예: "컴퓨터공학과 3학년")
    current_status:   str            # 현재 상태 (예: "재학 중", "취업 준비 중")
    interests:        list[str]      # 관심 분야 (예: ["백엔드", "AI"])
    owned_skills:     list[str]      # 보유 기술 자유 표기 (예: ["Python 기초", "React"])
    target_role:      str            # 목표 직무 IT 한정 (예: "백엔드 엔지니어")
    company_type:     Optional[str]  # 희망 기업 유형 (예: "스타트업", "대기업")
    weekly_hours:     int            # 주당 가용 학습 시간 (시간예산 검증 기준)
    concern:          Optional[str]  # 현재 고민 (예: "포트폴리오가 없어요")
    job_posting_text: Optional[str]  # 붙여넣은 채용공고 원문 (없으면 샘플 적용)
```

**JSON 예시:**

```json
{
  "major": "컴퓨터공학과 3학년",
  "current_status": "재학 중",
  "interests": ["백엔드 개발", "클라우드"],
  "owned_skills": ["Python 기초", "SQL 기초"],
  "target_role": "백엔드 엔지니어",
  "company_type": "스타트업",
  "weekly_hours": 10,
  "concern": "프로젝트 경험이 없어요",
  "job_posting_text": null
}
```

---

### 2-2. ClarifyAnswer — 역질문 응답

> `clarify` 노드가 역질문을 던지고, 사용자가 답하면 이 형식으로 `clarify_answers`에 쌓입니다.

```python
class ClarifyAnswer(BaseModel):
    question: str  # 에이전트가 던진 역질문
    answer:   str  # 사용자 응답
    kind:     str  # "info_supplement" | "similar_role_pick"
    #   info_supplement  : 정보 보완 질문 (예: "어느 언어를 주로 쓰시나요?")
    #   similar_role_pick: 유사 직무 선택 (예: "데이터 엔지니어 vs 백엔드 엔지니어")
```

---

### 2-3. ProfileDiagnosis — 역량 진단 결과

```python
class ProfileDiagnosis(BaseModel):
    summary:         str               # 현재 역량 요약 (1~2문장)
    strengths:       list[str]         # 강점 스킬/경험
    weaknesses:      list[str]         # 약점 (부족역량 후보)
    interests:       list[str]         # 에이전트가 확인한 관심 분야
    readiness_level: str               # "low" | "mid" | "high"
    evidence:        dict[str, str]    # 강점/약점 → 근거 원문 (validate_profile에서 활용)
    # 예: {"Python 기초": "owned_skills에 명시", "FastAPI": "job 요구사항에 포함"}
```

**JSON 예시:**

```json
{
  "summary": "Python 기초와 SQL 기초를 보유하고 있으나 실무 프레임워크 경험이 없습니다.",
  "strengths": ["Python 기초", "SQL 기초"],
  "weaknesses": ["FastAPI", "Docker", "REST API 설계"],
  "interests": ["백엔드 개발", "클라우드"],
  "readiness_level": "low",
  "evidence": {
    "Python 기초": "owned_skills에 명시",
    "SQL 기초": "owned_skills에 명시",
    "FastAPI": "job 요구사항 required_skills에 포함",
    "Docker": "job 요구사항 required_skills에 포함"
  }
}
```

---

### 2-4. JobRequirement — 직무 요건 추출 결과

> `evidence_strength`는 JobRequirementAgent가 **스스로** 판정합니다. 공고가 짧거나 추론에 의존했으면 `weak`, 상세 공고에서 추출하면 `strong`입니다. (Reflexion — 자기 평가의 경량 적용)

```python
class JobRequirement(BaseModel):
    required_skills:    list[str]        # 필수 기술 (예: ["FastAPI", "PostgreSQL"])
    preferred_skills:   list[str]        # 우대 기술 (예: ["Kubernetes", "Redis"])
    required_experience: list[str]       # 요구 경험 (예: ["REST API 설계 경험"])
    keywords:           list[str]        # 핵심 키워드 (예: ["MSA", "CI/CD"])
    evidence_strength:  EvidenceStrength # "strong" | "weak"
    source:             str              # "user_posting" | "sample_posting" | "role_inference" | "web_search"
```

**JSON 예시 (evidence_strength=weak → Gap이 needs_rerun 설정):**

```json
{
  "required_skills": ["Python", "REST API"],
  "preferred_skills": [],
  "required_experience": ["백엔드 개발 경험"],
  "keywords": ["백엔드", "서버"],
  "evidence_strength": "weak",
  "source": "role_inference"
}
```

---

### 2-5. GapItem · GapAnalysis — 역량 갭 분석

```python
class GapItem(BaseModel):
    skill:         str             # 정규화된 부족 스킬명 (normalize_skill_name 통과 후)
    priority:      PriorityLevel   # "high" | "medium" | "low"
    current_level: str             # 사용자 현재 수준 (예: "없음", "기초")
    target_level:  str             # 목표 요구 수준 (예: "중급", "실무")
    skill_status:  SkillStatus     # lookup_skill 결과 "known" | "unknown"
    verified:      bool            # known=True, unknown=False

class GapAnalysis(BaseModel):
    gaps:                  list[GapItem]    # 부족역량 리스트 (우선순위 정렬)
    job_evidence_strength: EvidenceStrength # 비교에 쓴 job 근거 강도
    needs_rerun:           bool             # True → job_requirement 재요청
    rerun_reason:          Optional[str]    # 재요청 사유 (예: "공고 너무 짧아 근거 약함")
```

**JSON 예시:**

```json
{
  "gaps": [
    {
      "skill": "FastAPI",
      "priority": "high",
      "current_level": "없음",
      "target_level": "실무",
      "skill_status": "known",
      "verified": true
    },
    {
      "skill": "Docker",
      "priority": "medium",
      "current_level": "없음",
      "target_level": "기초",
      "skill_status": "known",
      "verified": true
    }
  ],
  "job_evidence_strength": "strong",
  "needs_rerun": false,
  "rerun_reason": null
}
```

---

### 2-6. ResourceItem · TaskItem · WeekPlan · Roadmap — 주차별 로드맵

> `lookup_skill`이 반환한 `resources`가 `ResourceItem`으로 들어갑니다. `origin="db"`이면 DB 검수 url(verified=true), `origin="web"`이면 `web_search` 결과 url(verified=true, "웹 출처" 뱃지), `origin="llm"`이면 검색까지 실패한 폴백(verified=false, "검증 안 됨" 뱃지). (ReAct — 도구 호출로 환각 방지)

```python
class ResourceItem(BaseModel):
    title:      str                                    # 자원 제목 (예: "FastAPI 공식 튜토리얼")
    url:        Optional[str]                          # 링크 (db/web 유래; llm 폴백은 None)
    type:       str                                    # "course" | "doc" | "project"
    verified:   bool                                   # url 출처 있으면 True (db 또는 web)
    origin:     Literal["db", "web", "llm"] = "db"    # 신규: 검증 출처 종류
    source_url: Optional[str] = None                  # 신규: web origin일 때 SearchHit.url

class TaskItem(BaseModel):
    title:     str               # 과제명 (예: "간단한 CRUD API 구현")
    skill:     str               # 연결 부족스킬
    resources: list[ResourceItem] # lookup_skill 유래 학습자원
    est_hours: int               # 예상 소요 시간
    verified:  bool              # 자원 검증 여부

class WeekPlan(BaseModel):
    week_index:     int          # 주차 (1-base)
    objectives:     list[str]    # 학습 목표
    tasks:          list[TaskItem]
    covered_skills: list[str]    # 이 주차가 커버하는 부족스킬
    planned_hours:  int          # 주차 계획 시간 (≤ weekly_hours 검증)

class Roadmap(BaseModel):
    horizon:             RoadmapHorizon  # "weeks_4" | "weeks_6" | "weeks_8"
    total_weeks:         int             # 산출된 총 주차
    weeks:               list[WeekPlan]
    weekly_hours_budget: int             # 사용자 가용 시간 (검증 기준 복사)
    rationale:           str             # 기간 산출 근거 (Plan-and-Solve)
    # 예: "갭 5개·고우선순위 3개·주 10시간 → 8주 산출"
```

> **Plan-and-Solve 적용** (Wang et al. 2023): `roadmap_plan` 노드는 "4주/8주 중 선택"이 아니라 갭 개수·우선순위·`weekly_hours`를 먼저 계산해 `total_weeks = max(4, min(8, min_weeks))`를 도출하고, 결과에 따라 `weeks_4`(4주) / `weeks_6`(6주, 선택) / `weeks_8`(8주) 프리셋을 붙입니다. `rationale` 필드가 이 계산 근거를 저장합니다.

---

### 2-7. Violation · CriticReport — 자기 검증 결과

> Reflexion (Shinn et al. 2023) + Self-Refine (Madaan et al. 2023) 아이디어: 로드맵 출력 직후 `roadmap_critic` 노드가 4종 체크리스트를 돌리고 위반이 있으면 `roadmap_plan`으로 되돌립니다(최대 2회).

```python
class Violation(BaseModel):
    type:     ViolationType  # 아래 4종 참조
    detail:   str            # 위반 상세 (예: "FastAPI가 로드맵에 매핑되지 않음")
    location: str            # 위반 위치 (예: "week 3" | "FastAPI" | "week 2 19h>10h")

class CriticReport(BaseModel):
    verdict:              CriticVerdict    # "pass" | "revise"
    violations:           list[Violation]  # pass면 빈 리스트
    checked_at_revision:  int              # 검증 시점 revision_count
```

**4종 체크리스트 (ViolationType):**

| 위반 유형 | 검사 조건 | 예시 |
|-----------|-----------|------|
| `uncovered_gap` | 모든 `gap_analysis.gaps`가 어느 주차의 `covered_skills`에 1개 이상 포함 | FastAPI가 어느 주차에도 없음 |
| `time_budget_exceeded` | 각 주차 `planned_hours ≤ weekly_hours_budget` | 주 10시간 예산에 19시간 계획 |
| `prereq_order_violation` | `lookup_skill.prereqs` 선행 스킬이 해당 스킬보다 앞 주차에 배치됨 | Docker(선행: Linux 기초)가 Linux 기초보다 먼저 배치 |
| `forbidden_phrase` | 금칙 표현 목록에 해당하는 단어 없음 | "합격 가능", "취업 보장", "확실히" 등 |

---

### 2-8. SkillRecord — 스킬 DB 조회 결과

```python
class SkillRecord(BaseModel):
    name:          str              # 표준 스킬명 (예: "FastAPI")
    status:        SkillStatus      # "known" | "unknown"
    prereqs:       list[str]        # 선행 스킬 (예: ["Python", "HTTP 기초"])
    resources:     list[ResourceItem]  # 대표 학습 자원
    typical_hours: int              # 표준 소요 시간 (시간)
    verified:      bool             # known=True, unknown=False
```

**JSON 예시 (known):**

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
    },
    {
      "title": "FastAPI로 REST API 만들기 실습",
      "url": null,
      "type": "project",
      "verified": true
    }
  ],
  "typical_hours": 20,
  "verified": true
}
```

**JSON 예시 (unknown — LLM 폴백, verified=false):**

```json
{
  "name": "MyObscureLib",
  "status": "unknown",
  "prereqs": [],
  "resources": [],
  "typical_hours": 0,
  "verified": false
}
```

---

### 2-9. WeeklyProgress · EpisodicMemory — 경량 episodic 메모리

```python
class WeeklyProgress(BaseModel):
    week_index: int           # 주차 (1-base)
    completed:  bool          # 완료 여부 (대시보드 체크박스)
    note:       Optional[str] # 메모 (선택)

class EpisodicMemory(BaseModel):
    status:          MemoryStatus            # "new_user" | "returning_user"
    last_roadmap:    Optional[Roadmap]       # 직전 로드맵 (없으면 None)
    weekly_progress: list[WeeklyProgress]   # 주차 진행 기록
    last_updated:    str                     # ISO 타임스탬프
```

---

### 2-10. TraceEntry — 실행 트레이스

> 각 노드가 종료할 때 `trace_log` 헬퍼 함수를 통해 `State.trace`에 **append** 합니다. 대시보드 "why-this-path" 타임라인의 원본 데이터입니다.

```python
class TraceEntry(BaseModel):
    node:           str                     # 노드명 (예: "triage_router")
    input_summary:  str                     # 입력 요약 (1줄)
    decision:       Optional[NodeDecision]  # 분기 결정 (라우터·critic·되먹임만)
    tool_called:    Optional[str]           # 호출 툴명 (예: "lookup_skill")
    output_summary: str                     # 출력 요약 (1줄)
    ts:             str                     # ISO 타임스탬프
```

**JSON 예시 (triage_router가 ask 경로 선택):**

```json
{
  "node": "triage_router",
  "input_summary": "target_role='개발자', owned_skills=2개",
  "decision": "ask",
  "tool_called": null,
  "output_summary": "ambiguity_score=0.75 → ask 경로, 역질문 2개 생성",
  "ts": "2025-06-01T10:23:44Z"
}
```

**JSON 예시 (roadmap_plan이 lookup_skill 호출):**

```json
{
  "node": "roadmap_plan",
  "input_summary": "gaps=[FastAPI, Docker, PostgreSQL], weekly_hours=10",
  "decision": null,
  "tool_called": "lookup_skill(FastAPI)",
  "output_summary": "FastAPI known, prereqs=[Python,HTTP기초], 20h → week1~2 배치",
  "ts": "2025-06-01T10:24:01Z"
}
```

---

### 2-11. SearchHit — 웹 검색 결과 단건

> `web_search()` 툴이 반환하는 검색 결과 단건 모델입니다. `State.search_results`의 값 타입이며, `ResourceItem(origin="web")`을 생성할 때 `url`과 `source_url`의 원본이 됩니다. snippet은 검색 API가 제공한 발췌이며 사이트 HTML 크롤링 결과가 아닙니다.

```python
class SearchHit(BaseModel):
    title:        str   # 검색 결과 제목
    url:          str   # 출처 URL (verified=true 근거)
    snippet:      str   # 본문 발췌 (검색 API 반환값, 크롤링 아님)
    source:       str   # 도메인 또는 제공자명 (예: "wanted.co.kr", "tavily")
    retrieved_at: str   # ISO 타임스탬프 (검색 시각)
```

**JSON 예시:**

```json
{
  "title": "FastAPI 공식 튜토리얼",
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "snippet": "FastAPI는 Python 3.7+ 기반의 현대적이고 빠른 웹 프레임워크입니다...",
  "source": "fastapi.tiangolo.com",
  "retrieved_at": "2025-06-01T10:24:00Z"
}
```

---

### 2-12. FinalOutput — 사용자 전달 최종 산출물

```python
class FinalOutput(BaseModel):
    profile:          ProfileDiagnosis
    gap_analysis:     GapAnalysis
    roadmap:          Roadmap
    verified:         bool               # False(llm origin 항목 존재)면 UI에서 "일부 미검증 항목" 안내
    trace_summary:    list[TraceEntry]   # why-this-path 타임라인
    disclaimer:       str                # 가드레일 고지 (합격/진로 단정 아님)
    # 예: "이 로드맵은 학습 방향 제안이며 합격을 보장하지 않습니다."
    # search_degraded=True 시 disclaimer에 "일부 자원은 웹검색 출처이며 DB 검수를 거치지 않았습니다." 추가
    search_degraded:  bool = False       # True면 disclaimer에 웹검색 출처 고지 포함
```

---

## 3. Enum 정의

```python
from enum import Enum

class RouteDecision(str, Enum):
    ask     = "ask"      # 모호도 높아 역질문/유사직무 제안
    proceed = "proceed"  # 충분해 바로 진단 진행

class SkillStatus(str, Enum):
    known   = "known"    # 스킬 DB 존재 → verified=True
    unknown = "unknown"  # 미존재 → LLM 폴백 + verified=False

class CriticVerdict(str, Enum):
    pass_   = "pass"     # 4종 체크리스트 전부 통과 → finalize
    revise  = "revise"   # 위반 존재 → roadmap_plan 루프백

class ViolationType(str, Enum):
    uncovered_gap          = "uncovered_gap"
    time_budget_exceeded   = "time_budget_exceeded"
    prereq_order_violation = "prereq_order_violation"
    forbidden_phrase       = "forbidden_phrase"

class EvidenceStrength(str, Enum):
    strong = "strong"
    weak   = "weak"

class MemoryStatus(str, Enum):
    new_user       = "new_user"
    returning_user = "returning_user"

class NodeDecision(str, Enum):
    ask             = "ask"
    proceed         = "proceed"
    rerun_job       = "rerun_job"
    skip_rerun      = "skip_rerun"
    revise          = "revise"
    pass_           = "pass"
    reconcile       = "reconcile"
    skip_reconcile  = "skip_reconcile"

class RoadmapHorizon(str, Enum):
    weeks_4 = "weeks_4"
    weeks_6 = "weeks_6"   # 필요 시 사용
    weeks_8 = "weeks_8"
    # weeks_custom 제거 — calculate_horizon은 max(4, min(8, min_weeks))로 캡

class SourceOrigin(str, Enum):
    db  = "db"   # 스킬DB 검수 url (최고 신뢰)
    web = "web"  # web_search 결과 url (SearchHit.url 출처, "웹 출처" 뱃지)
    llm = "llm"  # LLM 순수 자체지식 (url 없음, "검증 안 됨" 뱃지)

class PriorityLevel(str, Enum):
    high   = "high"
    medium = "medium"
    low    = "low"
```

---

## 4. 스킬 DB 툴 계약

> **ReAct** (Yao et al. 2022) 패턴: 에이전트가 추론(Thought) 중간에 외부 함수(Act)를 호출해 사실을 가져옴으로써 LLM 환각을 차단합니다. 여기서 "외부 함수"가 정적 JSON/CSV 스킬 사전 조회입니다.

### 4-1. 툴 시그니처

```python
# tools/skill_lookup.py

def normalize_skill_name(raw: str) -> str:
    """
    사용자/LLM이 쓴 자유 표기를 스킬 사전 표준 키로 정규화.
    매칭 실패 시 raw 그대로 반환 (throw 금지).
    예: "react.js" → "React", "fast api" → "FastAPI"
    """
    ...

def lookup_skill(name: str) -> SkillRecord:
    """
    IT 직무 한정 정적 스킬 사전 조회.
    미존재 시: status=unknown, prereqs=[], resources=[], typical_hours=0, verified=False 반환.
    IO 오류도 동일 unknown 폴백 (throw 금지).
    """
    normalized = normalize_skill_name(name)
    # JSON 파일(data/skill_db.json)에서 normalized 키 조회
    ...

def list_skills_for_role(role: str) -> list[SkillRecord]:
    """
    직무명으로 관련 SkillRecord 일괄 조회.
    role 미매핑 시 빈 리스트 반환 (throw 금지).
    JobRequirement 보강 및 gap 후보군 확보용.
    """
    ...
```

### 4-2. 스킬 DB JSON 구조 스케치 (`data/skill_db.json`)

IT 직무 **1~2개** 한정, **50~150행** 유지(1.5주 범위).

```json
{
  "FastAPI": {
    "prereqs": ["Python", "HTTP 기초"],
    "resources": [
      {
        "title": "FastAPI 공식 튜토리얼",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 20
  },
  "Linux 기초": {
    "prereqs": [],
    "resources": [
      {
        "title": "Linux 커맨드라인 기초",
        "url": "https://linuxcommand.org/lc3_learning_the_shell.php",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 10
  },
  "Docker": {
    "prereqs": ["Linux 기초"],
    "resources": [
      {
        "title": "Docker 입문 실습",
        "url": "https://docs.docker.com/get-started/",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 15
  },
  "PostgreSQL": {
    "prereqs": ["SQL 기초"],
    "resources": [
      {
        "title": "PostgreSQL 공식 튜토리얼",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 12
  }
}
```

### 4-3. 직무-스킬 매핑 (`data/role_skill_map.json`)

```json
{
  "백엔드 엔지니어": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API 설계", "Git"],
  "데이터 엔지니어": ["Python", "SQL 기초", "PostgreSQL", "Airflow", "Docker", "Spark 기초"]
}
```

### 4-4. 호출 패턴 (roadmap_plan 노드 내 의사코드)

```python
# roadmap_plan 노드 내부 - lookup_skill → web_search 3단계 호출 패턴
for gap_item in state.gap_analysis.gaps:
    normalized = normalize_skill_name(gap_item.skill)
    record = lookup_skill(normalized)

    if record.status == SkillStatus.known:
        # 1순위: DB 캐시 히트 — 검색 생략
        resources = record.resources  # origin="db", verified=True
    else:
        # 2순위: DB miss → web_search로 실제 url 보강
        if state.search_count < MAX_SEARCH:
            hits = web_search(f"{normalized} 학습 강의 튜토리얼 공식문서", k=3)
            state.search_count += 1
        else:
            hits = []
            state.search_degraded = True

        if hits:
            # web origin — SearchHit.url을 source_url로 부착
            resources = [
                ResourceItem(
                    title=h.title, url=h.url, type="doc",
                    verified=True, origin="web", source_url=h.url
                ) for h in hits
            ]
        else:
            # 3순위(폴백의 폴백): 검색도 실패 → LLM 자체지식, verified=False
            state.verified = False
            resources = []   # LLM이 직접 제안 (환각 위험 고지, origin="llm")

    # prereqs 순서 검증은 roadmap_critic 노드가 담당
```

---

## 5. 경량 Episodic 메모리

> **MVP 원칙**: 세션 간 "읽기 + 반영"만 구현합니다. "쓰기"는 최종 로드맵 저장(finalize 후 1회)과 주차 체크박스 토글만 허용합니다. 무한 성장 방지를 위해 `last_roadmap`은 1개만 유지합니다.

### 5-1. 데이터 흐름

```
[onboarding_intake 노드]
    │  user_id로 DB 조회
    ▼
EpisodicMemory 적재 → State.episodic_memory
    │
    ▼
[progress_reconciliation 노드]
    │  returning_user인 경우에만 동작
    ▼
  ① weekly_progress에서 completed=false 주차의 covered_skills → "이월 대상" 목록
  ② completed=true 주차의 스킬 → ProfileDiagnosis 약점에서 제외 / 우선순위 낮춤
  ③ last_roadmap.rationale → 새 로드맵 생성 참고 맥락으로 전달
    │
    ▼
[roadmap_plan 노드]  ← 이월 대상 + 진척 정보 주입된 컨텍스트로 로드맵 생성

[finalize 노드 이후 — 저장 핸들러]
    ├─ users 테이블의 last_roadmap 컬럼 덮어쓰기
    └─ weekly_progress 테이블에 새 주차 completed=false로 시드
```

### 5-2. progress_reconciliation 노드 의사코드

```python
def progress_reconciliation(state: CareerMateState) -> CareerMateState:
    mem = state.episodic_memory

    if mem is None or mem.status == MemoryStatus.new_user:
        state.trace.append(TraceEntry(
            node="progress_reconciliation",
            input_summary="새 사용자",
            decision=NodeDecision.skip_reconcile,
            tool_called=None,
            output_summary="episodic_memory 없음, 반영 건너뜀",
            ts=now_iso()
        ))
        return state

    # 미완료 스킬 이월
    incomplete_skills = [
        skill
        for wp in mem.weekly_progress if not wp.completed
        for skill in (get_covered_skills_for_week(mem.last_roadmap, wp.week_index) or [])
    ]

    # 완료 스킬 → ProfileDiagnosis 약점 제거 후보
    completed_skills = [
        skill
        for wp in mem.weekly_progress if wp.completed
        for skill in (get_covered_skills_for_week(mem.last_roadmap, wp.week_index) or [])
    ]

    # State에 컨텍스트 주입 (별도 보조 필드 또는 프롬프트 컨텍스트로 전달)
    state._reconcile_context = {
        "incomplete_skills": incomplete_skills,
        "completed_skills":  completed_skills,
        "prev_rationale":    mem.last_roadmap.rationale if mem.last_roadmap else None,
    }

    state.trace.append(TraceEntry(
        node="progress_reconciliation",
        input_summary=f"미완료 {len(incomplete_skills)}개, 완료 {len(completed_skills)}개",
        decision=NodeDecision.reconcile,
        tool_called=None,
        output_summary="이월/진척 컨텍스트 주입 완료",
        ts=now_iso()
    ))
    return state
```

---

## 6. 저장소 테이블 스케치

> MVP에서는 **MySQL 2개 테이블**로 운영합니다. JSON 파일 기반(SQLite)으로 시작해도 동일한 스키마가 적용됩니다.

### 6-1. `users` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `user_id` | `VARCHAR(64) PK` | 사용자 식별자 |
| `email` | `VARCHAR(255)` | 이메일 (선택) |
| `created_at` | `DATETIME` | 가입 시각 |
| `last_roadmap` | `JSON` | 직전 `Roadmap` 객체 JSON (1개만 유지) |
| `last_updated` | `DATETIME` | 마지막 로드맵 갱신 시각 |

```sql
CREATE TABLE users (
    user_id      VARCHAR(64)  PRIMARY KEY,
    email        VARCHAR(255),
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    last_roadmap JSON,
    last_updated DATETIME
);
```

### 6-2. `weekly_progress` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | `INT AUTO_INCREMENT PK` | |
| `user_id` | `VARCHAR(64) FK` | `users.user_id` |
| `session_id` | `VARCHAR(64)` | 로드맵 생성 세션 |
| `week_index` | `INT` | 주차 (1-base) |
| `completed` | `BOOLEAN` | 완료 여부 (체크박스) |
| `note` | `TEXT` | 메모 (선택) |
| `updated_at` | `DATETIME` | 마지막 체크박스 갱신 |

```sql
CREATE TABLE weekly_progress (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    week_index INT         NOT NULL,
    completed  BOOLEAN     DEFAULT FALSE,
    note       TEXT,
    updated_at DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 6-3. `sessions` 테이블 (선택 — trace 아카이브용)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `session_id` | `VARCHAR(64) PK` | |
| `user_id` | `VARCHAR(64) FK` | |
| `trace` | `JSON` | `list[TraceEntry]` 전체 로그 |
| `final_output` | `JSON` | `FinalOutput` 스냅샷 |
| `created_at` | `DATETIME` | |

```sql
CREATE TABLE sessions (
    session_id   VARCHAR(64) PRIMARY KEY,
    user_id      VARCHAR(64) NOT NULL,
    trace        JSON,
    final_output JSON,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## 7. FastAPI 엔드포인트 계약

> 아래는 의사코드 수준의 계약입니다. 실제 구현 시 FastAPI `@app.post`/`@app.get` 데코레이터와 Pydantic 모델을 그대로 연결하면 됩니다.

### 엔드포인트 전체 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/onboard` | 온보딩 입력 제출 → 그래프 실행 시작 |
| `POST` | `/diagnose` | 역질문 응답 제출 → triage_router 재실행 |
| `GET` | `/roadmap/{user_id}` | 최신 로드맵 조회 |
| `POST` | `/progress` | 주차 완료 여부 체크박스 업데이트 |
| `GET` | `/trace/{session_id}` | 실행 트레이스 조회 |

---

### 7-1. `POST /onboard` — 온보딩 입력 제출

**요청:**

```json
{
  "user_id": "user_abc123",
  "onboarding_input": {
    "major": "컴퓨터공학과 3학년",
    "current_status": "재학 중",
    "interests": ["백엔드 개발", "클라우드"],
    "owned_skills": ["Python 기초", "SQL 기초"],
    "target_role": "백엔드 엔지니어",
    "company_type": "스타트업",
    "weekly_hours": 10,
    "concern": "프로젝트 경험이 없어요",
    "job_posting_text": null
  }
}
```

**응답 (200 — route_decision=proceed, 그래프 완료):**

```json
{
  "session_id": "sess_xyz789",
  "status": "completed",
  "route_decision": "proceed",
  "final_output": {
    "profile": { "summary": "...", "readiness_level": "low", "..." : "..." },
    "gap_analysis": { "gaps": ["..."], "needs_rerun": false, "..." : "..." },
    "roadmap": { "horizon": "weeks_8", "total_weeks": 8, "..." : "..." },
    "verified": true,
    "trace_summary": ["..."],
    "disclaimer": "이 로드맵은 학습 방향 제안이며 합격을 보장하지 않습니다."
  }
}
```

**응답 (202 — route_decision=ask, 역질문 대기):**

```json
{
  "session_id": "sess_xyz789",
  "status": "awaiting_clarification",
  "route_decision": "ask",
  "clarify_questions": [
    {
      "kind": "info_supplement",
      "question": "목표 직무 '개발자'가 다소 넓습니다. 백엔드/프론트엔드/풀스택 중 어느 쪽에 더 관심 있으신가요?"
    },
    {
      "kind": "similar_role_pick",
      "question": "아래 직무 중 가장 가까운 것을 선택해 주세요.",
      "options": ["백엔드 엔지니어", "데이터 엔지니어", "DevOps 엔지니어"]
    }
  ]
}
```

**FastAPI 핸들러 스케치:**

```python
@app.post("/onboard")
async def onboard(req: OnboardRequest) -> OnboardResponse:
    state = CareerMateState(
        user_id=req.user_id,
        session_id=generate_session_id(),
        onboarding_input=req.onboarding_input
    )
    result = await run_graph(state)  # LangGraph 그래프 실행

    if result.route_decision == RouteDecision.ask:
        return OnboardResponse(status="awaiting_clarification", ...)
    return OnboardResponse(status="completed", final_output=result.final_output, ...)
```

---

### 7-2. `POST /diagnose` — 역질문 응답 제출

> `status=awaiting_clarification`인 세션에 사용자가 답한 경우 호출합니다.

**요청:**

```json
{
  "session_id": "sess_xyz789",
  "clarify_answers": [
    {
      "question": "백엔드/프론트엔드/풀스택 중 어느 쪽에 더 관심 있으신가요?",
      "answer": "백엔드",
      "kind": "info_supplement"
    },
    {
      "question": "아래 직무 중 가장 가까운 것을 선택해 주세요.",
      "answer": "백엔드 엔지니어",
      "kind": "similar_role_pick"
    }
  ]
}
```

**응답 (200 — clarify 후 proceed로 수렴, 그래프 완료):**

```json
{
  "session_id": "sess_xyz789",
  "status": "completed",
  "final_output": { "..." : "..." }
}
```

---

### 7-3. `GET /roadmap/{user_id}` — 최신 로드맵 조회

**응답 (200):**

```json
{
  "user_id": "user_abc123",
  "session_id": "sess_xyz789",
  "roadmap": {
    "horizon": "weeks_8",
    "total_weeks": 8,
    "weekly_hours_budget": 10,
    "rationale": "고우선순위 갭 3개·주 10시간 → 8주 산출",
    "weeks": [
      {
        "week_index": 1,
        "objectives": ["Python HTTP 기초 완성", "FastAPI 환경 세팅"],
        "tasks": [
          {
            "title": "FastAPI Hello World 작성",
            "skill": "FastAPI",
            "resources": [
              {
                "title": "FastAPI 공식 튜토리얼",
                "url": "https://fastapi.tiangolo.com/tutorial/",
                "type": "doc",
                "verified": true
              }
            ],
            "est_hours": 4,
            "verified": true
          }
        ],
        "covered_skills": ["FastAPI"],
        "planned_hours": 8
      }
    ]
  },
  "verified": true,
  "weekly_progress": [
    { "week_index": 1, "completed": false, "note": null },
    { "week_index": 2, "completed": false, "note": null }
  ]
}
```

**응답 (404 — 로드맵 없음):**

```json
{ "detail": "로드맵이 없습니다. /onboard를 먼저 호출하세요." }
```

---

### 7-4. `POST /progress` — 주차 완료 체크박스 업데이트

**요청:**

```json
{
  "user_id": "user_abc123",
  "session_id": "sess_xyz789",
  "week_index": 1,
  "completed": true,
  "note": "FastAPI 튜토리얼 완료, CRUD API 구현함"
}
```

**응답 (200):**

```json
{
  "updated": true,
  "week_index": 1,
  "completed": true,
  "message": "1주차 완료 기록이 저장되었습니다."
}
```

**FastAPI 핸들러 스케치:**

```python
@app.post("/progress")
async def update_progress(req: ProgressUpdateRequest) -> ProgressUpdateResponse:
    # weekly_progress 테이블에서 (user_id, session_id, week_index) 레코드 업데이트
    await db.update_weekly_progress(
        user_id=req.user_id,
        session_id=req.session_id,
        week_index=req.week_index,
        completed=req.completed,
        note=req.note
    )
    return ProgressUpdateResponse(updated=True, ...)
```

---

### 7-5. `GET /trace/{session_id}` — 실행 트레이스 조회

> 대시보드 "why-this-path" 타임라인 원본 데이터. 에이전트가 어떤 분기를 선택했는지, Critic이 몇 번 재생성을 요청했는지, 어떤 툴을 불렀는지를 타임라인으로 보여줍니다.

**응답 (200):**

```json
{
  "session_id": "sess_xyz789",
  "trace": [
    {
      "node": "onboarding_intake",
      "input_summary": "user_id=user_abc123, target_role=백엔드 엔지니어",
      "decision": null,
      "tool_called": null,
      "output_summary": "OnboardingInput 구조화 완료, new_user",
      "ts": "2025-06-01T10:23:40Z"
    },
    {
      "node": "triage_router",
      "input_summary": "target_role=백엔드 엔지니어, owned_skills=2개",
      "decision": "proceed",
      "tool_called": null,
      "output_summary": "ambiguity_score=0.35 → proceed 경로",
      "ts": "2025-06-01T10:23:42Z"
    },
    {
      "node": "roadmap_plan",
      "input_summary": "gaps=[FastAPI,Docker,PostgreSQL], weekly_hours=10",
      "decision": null,
      "tool_called": "lookup_skill(FastAPI)",
      "output_summary": "FastAPI known(prereqs=[Python,HTTP기초],20h) → week1~2 배치",
      "ts": "2025-06-01T10:24:01Z"
    },
    {
      "node": "roadmap_critic",
      "input_summary": "revision_count=0, roadmap 8주",
      "decision": "revise",
      "tool_called": null,
      "output_summary": "위반 1건: week3 planned_hours=14 > budget=10 → revise",
      "ts": "2025-06-01T10:24:08Z"
    },
    {
      "node": "roadmap_plan",
      "input_summary": "revision_count=1, violations=[time_budget_exceeded week3]",
      "decision": null,
      "tool_called": "lookup_skill(Docker)",
      "output_summary": "week3 재분배 → planned_hours=9, 위반 해소",
      "ts": "2025-06-01T10:24:15Z"
    },
    {
      "node": "roadmap_critic",
      "input_summary": "revision_count=1, roadmap 8주",
      "decision": "pass",
      "tool_called": null,
      "output_summary": "4종 체크리스트 전부 통과 → finalize",
      "ts": "2025-06-01T10:24:22Z"
    },
    {
      "node": "finalize",
      "input_summary": "verified=true, revision_count=1",
      "decision": null,
      "tool_called": null,
      "output_summary": "FinalOutput 조립 완료",
      "ts": "2025-06-01T10:24:25Z"
    }
  ]
}
```

---

## 부록 — 모델 의존 관계 다이어그램

```
OnboardingInput
    │
    ▼
TriageRouter ──ask──► ClarifyAnswer
    │proceed
    ▼
ProfileDiagnosis ◄── EpisodicMemory (returning_user)
    │
    ▼
JobRequirement ◄─────────────────────────────────────┐
    │                                                 │ needs_rerun=true
    ▼                                                 │ (MAX 1회)
GapAnalysis ─────────────────────────────────────────┘
    │ gap 목록
    ▼
RoadmapPlan ──lookup_skill(스킬명)──► SkillRecord
    │ Roadmap
    ▼
RoadmapCritic ──revise──► RoadmapPlan (MAX 2회)
    │ pass
    ▼
FinalOutput
    └─ ProfileDiagnosis
    └─ GapAnalysis
    └─ Roadmap (WeekPlan → TaskItem → ResourceItem)
    └─ verified 플래그
    └─ TraceEntry 목록
    └─ disclaimer
```

---

> **참고 자료**: Anthropic *Building Effective Agents* (2024), ReAct (Yao et al. 2022), Reflexion (Shinn et al. 2023), Self-Refine (Madaan et al. 2023), Plan-and-Solve Prompting (Wang et al. 2023), LangGraph 공식 문서.
