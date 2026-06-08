# 에이전트 I/O 계약 (Agent I/O Contracts)

이 문서는 CareerMate 그래프를 구성하는 4개 에이전트의 **입력·출력·프롬프트 전략·실패 처리**를 계약 수준으로 명세합니다.
"계약"이란 에이전트끼리 주고받는 데이터의 형태와 규칙을 코드로 옮길 수 있을 만큼 구체적으로 정의한 것입니다.
에이전트 그래프 전체 구조는 [에이전트 그래프](02-agent-graph.md)를 참고하세요.

---

## 목차

1. [TriageRouter — 모호성 라우터](#1-triagerouter--모호성-라우터)
2. [ProfileDiagnosisAgent — 프로필 진단](#2-profilediagnosisagent--프로필-진단)
3. [JobRequirementAgent — 직무 요구역량 추출](#3-jobrequirementagent--직무-요구역량-추출)
4. [GapRoadmapAgent — 갭 분석 & 로드맵 생성](#4-gaproadmapagent--갭-분석--로드맵-생성)

---

## 1. TriageRouter — 모호성 라우터

### 역할

온보딩 직후 **가장 먼저** 실행되는 분기 에이전트입니다.
사용자 입력의 모호도(ambiguity_score)를 0.0~1.0으로 산정한 뒤, 임계값(`AMBIGUITY_THRESHOLD = 0.6`)을 초과하면 역질문(ask) 경로로, 미만이면 바로 진단(proceed) 경로로 나눕니다.
원본 기획 7페이지의 "직무 모호 → 유사 직무 제안", "정보 부족 → 추가 질문" 예외처리를 워크플로우의 **정식 라우터 노드**로 승격한 것입니다 (피드백 제안1, Anthropic Building Effective Agents — routing 패턴).

```
온보딩 입력
    │
    ▼
┌──────────────┐    ambiguity_score > 0.6    ┌─────────────┐
│ triage_router│ ──────────────────────────▶ │   clarify   │
│  (이 노드)   │                              └──────┬──────┘
│              │    ambiguity_score ≤ 0.6           │ 역질문 응답 수집 후 재산정
│              │ ──────────────────────────▶  profile_diagnosis
└──────────────┘         proceed
```

### 입력 (State에서 읽는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `onboarding_input` | `OnboardingInput` | 온보딩 원본 입력 전체 |
| `clarify_answers` | `list[ClarifyAnswer]` | 이전 clarify 경로에서 수집된 보강 응답 (최초 진입 시 빈 리스트) |

**프롬프트 컨텍스트로 전달하는 정보:**
- `onboarding_input.target_role` — 목표 직무명
- `onboarding_input.owned_skills` — 보유 기술 리스트
- `onboarding_input.concern` — 현재 고민 (있으면)
- `clarify_answers` 전체 — 보강 응답이 있으면 재산정에 반영

### 출력 (State에 쓰는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `ambiguity_score` | `float` | 0.0~1.0 모호도 점수 |
| `route_decision` | `RouteDecision` | `"ask"` 또는 `"proceed"` |
| `trace` | `list[TraceEntry]` | 이 노드 실행 기록 append |

**conditional_edge 조건:**

```python
def triage_edge(state: CareerMateState) -> str:
    if state["route_decision"] == "ask":
        return "clarify"
    return "profile_diagnosis"
```

### Pydantic 스케치

```python
class TriageResult(BaseModel):
    ambiguity_score: float          # 0.0~1.0, LLM 자체 산정
    route_decision: Literal["ask", "proceed"]
    ask_reason: str | None          # ask 경로일 때 모호한 이유 (trace용)
    similar_roles: list[str]        # ask 경로 + 직무 모호일 때 유사직무 후보 (최대 3개)
    clarify_questions: list[str]    # ask 경로일 때 던질 역질문 (최대 3개)
```

### 프롬프트 전략 요지

**모호도 판단 기준 (LLM에게 제시하는 채점 기준):**

```
다음 항목 중 해당되는 수를 세어 ambiguity_score를 0.0~1.0으로 산출하라.
하나당 약 0.2점을 부여하되, 전체적 맥락을 고려해 최종 조정한다.

□ target_role이 직무명이 아닌 분야명이거나 너무 광범위 (예: "IT", "개발자")
□ owned_skills가 0개이거나 직무와 연관성이 없는 기술만 나열
□ major와 target_role이 전혀 관련 없고 이직 배경 설명 없음
□ weekly_hours가 0 또는 비현실적으로 낮음 (2시간 미만)
□ concern이 "모르겠다", "없다" 등 정보가 없는 수준
```

**ask 경로 응답 형식:**
- 직무 모호: 유사직무 후보 2~3개 + 각 직무가 어떤 일을 하는지 한 줄 설명
- 정보 부족: 구체적 역질문 2~3개 (Yes/No 불가, 서술형)

**proceed 경로:** 별도 응답 없이 route_decision만 설정하고 다음 노드로 진행.

### 실패·폴백

| 상황 | 처리 |
|---|---|
| LLM이 ambiguity_score를 0~1 범위 밖으로 반환 | `min(max(score, 0.0), 1.0)` 클리핑 |
| LLM 응답이 JSON 파싱 실패 | ambiguity_score=0.5, route_decision="ask"로 보수적 폴백 |
| clarify 루프가 2회 이상 반복돼도 score > 0.6 | 3회째에 강제 proceed (무한 역질문 방지) |

### 출력 JSON 예시

```json
{
  "ambiguity_score": 0.75,
  "route_decision": "ask",
  "ask_reason": "target_role='개발자'는 직무 범위가 너무 넓고, owned_skills=['Python']만으로는 어떤 개발 직군인지 판단 불가",
  "similar_roles": ["백엔드 개발자", "데이터 엔지니어", "ML 엔지니어"],
  "clarify_questions": [
    "어떤 종류의 개발 업무를 하고 싶으신가요? (예: 서버/API 개발, 데이터 파이프라인, AI 모델 서빙 등)",
    "Python 외에 다루어본 기술이나 프레임워크가 있다면 알려주세요.",
    "희망 직무와 관련해 이전에 해본 프로젝트나 공부 경험이 있나요?"
  ]
}
```

---

## 2. ProfileDiagnosisAgent — 프로필 진단

### 역할

사용자가 제공한 정보만으로 현재 역량을 객관적으로 구조화합니다.
**핵심 원칙:** "입력 외 추론 금지" — 사용자가 명시하지 않은 스킬, 경험, 수준을 LLM이 임의로 추가하거나 상향/하향 조정하지 않습니다.
원본 기획 6페이지의 ProfileDiagnosisAgent에 해당하며, clarify 경로 보강 응답과 episodic 메모리를 함께 반영합니다.

### 입력 (State에서 읽는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `onboarding_input` | `OnboardingInput` | 온보딩 원본 입력 |
| `clarify_answers` | `list[ClarifyAnswer]` | 역질문 보강 응답 (proceed 경로면 빈 리스트) |
| `episodic_memory` | `EpisodicMemory \| None` | 재방문 사용자의 직전 기록 |

**프롬프트 컨텍스트로 전달하는 정보:**

```python
context = {
    "major": onboarding_input.major,
    "current_status": onboarding_input.current_status,
    "interests": onboarding_input.interests,
    "owned_skills": onboarding_input.owned_skills,   # 사용자 자유 표기 그대로
    "target_role": onboarding_input.target_role,
    "concern": onboarding_input.concern,
    # clarify 보강이 있으면 추가
    "clarify_supplements": [
        a.answer for a in clarify_answers if a.kind == "info_supplement"
    ],
    # episodic: 완료된 스킬은 보유로 간주
    "completed_skills": completed_skills_from_memory,  # progress_reconciliation이 추출
}
```

### 출력 (State에 쓰는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `profile` | `ProfileDiagnosis` | 역량 진단 결과 |
| `trace` | `list[TraceEntry]` | 이 노드 실행 기록 append |

### Pydantic 모델

```python
class ProfileDiagnosis(BaseModel):
    summary: str                     # 현재 역량 1~2문장 요약
    strengths: list[str]             # 강점 (입력 근거 있는 것만)
    weaknesses: list[str]            # 약점 (입력 근거 있는 것만)
    interests: list[str]             # 관심 분야 (입력에서 추출)
    readiness_level: Literal["low", "mid", "high"]  # 준비 수준

    # 각 항목의 입력 근거 (검증용)
    evidence: dict[str, str]         # {"강점명": "근거 입력문장", ...}
```

### 프롬프트 전략 요지

**"입력 외 추론 금지" 강제 규칙 (프롬프트에 명시):**

```
규칙 1. strengths와 weaknesses의 각 항목은 반드시 사용자 입력에서
        직접 확인 가능한 근거가 있어야 한다. 근거 없으면 해당 항목을 포함하지 않는다.
규칙 2. owned_skills에 없는 기술을 보유 기술로 기재하지 않는다.
규칙 3. 사용자가 언급하지 않은 경험/자격증/프로젝트를 추론하여 기재하지 않는다.
규칙 4. readiness_level은 아래 기준으로만 판정한다:
        - high: 목표 직무 관련 스킬 3개 이상 보유 + 관련 경험 명시
        - mid : 관련 스킬 1~2개 보유 또는 관련 전공/수업 이수
        - low : 관련 스킬 없거나 완전 비전공 전환
규칙 5. evidence 필드에 각 strengths/weaknesses 항목의 근거 입력 문장을 반드시 기재한다.
```

**재방문 사용자 처리:**
- `episodic_memory.weekly_progress`에서 `completed=true`인 주차의 `covered_skills`를 owned_skills에 합산
- `completed=true` 스킬은 weaknesses에서 제외하거나 우선순위 낮춤
- trace에 `"episodic_merge: [스킬명 목록]"` 기록

**가드레일 (출력 후 스키마 검증 — Anthropic Building Effective Agents, guardrail 패턴):**

```python
def validate_profile(profile: ProfileDiagnosis, onboarding: OnboardingInput) -> bool:
    """입력 외 추론 금지 검증: strengths/weaknesses가 owned_skills 또는
    clarify_answers에 근거를 두는지 확인."""
    allowed_sources = set(onboarding.owned_skills + onboarding.interests)
    for strength in profile.strengths:
        if strength not in profile.evidence:
            return False  # 근거 없는 강점 → 재생성 요청
    return True
```

### 실패·폴백

| 상황 | 처리 |
|---|---|
| evidence 필드 누락 또는 빈 딕셔너리 | 해당 노드 재실행 1회 (최대 2회 시도) |
| strengths/weaknesses가 각각 5개 초과 | 상위 5개만 유지, 나머지 truncate |
| 재실행 2회 후에도 근거 없는 항목 | verified=false로 내리고 진행 (사용자에게 '검증 안 됨' 노출) |
| LLM JSON 파싱 실패 | summary만 채운 최소 ProfileDiagnosis 반환 |

### 출력 JSON 예시

```json
{
  "summary": "컴퓨터공학 전공 재학생으로 Python과 SQL 기초는 보유하나, 백엔드 실무 프레임워크 경험은 없는 입문~초급 수준입니다.",
  "strengths": [
    "Python 기초 코딩 능력",
    "SQL 기초 쿼리 작성"
  ],
  "weaknesses": [
    "웹 프레임워크(FastAPI/Django) 미경험",
    "REST API 설계 및 구현 경험 없음",
    "Docker/배포 환경 지식 부재"
  ],
  "interests": ["백엔드 개발", "데이터 처리"],
  "readiness_level": "low",
  "evidence": {
    "Python 기초 코딩 능력": "owned_skills: ['Python', 'SQL']",
    "SQL 기초 쿼리 작성": "owned_skills: ['Python', 'SQL']",
    "웹 프레임워크(FastAPI/Django) 미경험": "owned_skills에 웹 프레임워크 없음",
    "REST API 설계 및 구현 경험 없음": "owned_skills에 API 관련 기술 없음",
    "Docker/배포 환경 지식 부재": "owned_skills에 인프라/배포 기술 없음"
  }
}
```

---

## 3. JobRequirementAgent — 직무 요구역량 추출

### 역할

목표 직무 공고 텍스트(또는 샘플 공고)에서 **필수·우대 역량**과 요구 경험을 구조화 추출합니다.
채용 홍보성 문구("우리는 글로벌 기업입니다", "최고의 복지")를 걸러내고, 실제 역량 요구만 추출합니다.
추출 결과의 **근거 강도(evidence_strength)**를 자가 평기하고, `needs_rerun` 트리거를 위한 신호를 제공합니다.
`rerun_reason`이 있으면 (Gap→Job 되먹임) 해당 사유를 반영해 재추출합니다.

**에이전트 간 되먹임 설명:**
GapRoadmapAgent가 "직무 요구역량 근거가 너무 약하다"고 판단하면 `needs_rerun=true`와 `rerun_reason`을 State에 설정하고, 이 에이전트를 1회 다시 실행합니다.
이것이 원본 기획 6페이지 "선형 전달"을 **양방향 협업**으로 바꾸는 핵심 장치입니다 (피드백 제안4, LangGraph conditional edge).

### 입력 (State에서 읽는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `onboarding_input` | `OnboardingInput` | 목표 직무명 + 공고 텍스트 |
| `rerun_reason` | `str \| None` | Gap→Job 되먹임 시 재추출 사유 |

**공고 텍스트 소스 선택 로직 + web_search 보강 경로:**

```python
def select_posting_text(onboarding: OnboardingInput) -> tuple[str, str]:
    """(공고 텍스트, source 라벨) 반환"""
    if onboarding.job_posting_text and len(onboarding.job_posting_text) >= 100:
        return onboarding.job_posting_text, "user_posting"
    elif onboarding.job_posting_text and len(onboarding.job_posting_text) < 100:
        # 공고가 너무 짧으면 샘플과 병합 + source 표기
        sample = load_sample_posting(onboarding.target_role)
        return onboarding.job_posting_text + "\n\n[샘플 보강]\n" + sample, "user_posting"
    else:
        return load_sample_posting(onboarding.target_role), "sample_posting"
```

**web_search 보강 경로 (공고 부실 시 검색→snippet 추출):**

`job_posting_text`가 없거나 100자 미만인 경우, 샘플 공고 로드와 함께 `web_search`를 병행 호출해 요구역량을 보강합니다.
검색은 노드 내부 tool 호출로 처리하며(별도 ToolNode 추가 없음), ReAct 패턴의 Act=`web_search` 호출 / Observe=snippet 파싱입니다.

```python
# job_requirement_node 본문 내부
def enrich_with_web_search(
    state: CareerMateState,
    posting_text: str,
    target_role: str,
) -> tuple[str, list[SearchHit]]:
    """공고 텍스트가 부실할 때 web_search로 요구역량 snippet 보강.
    반환: (보강된 컨텍스트 문자열, 사용된 SearchHit 리스트)
    """
    if len(posting_text) >= 100:
        return posting_text, []   # 충분한 공고 → 검색 생략

    # Act: web_search 호출
    hits: list[SearchHit] = web_search(
        f"{target_role} 채용공고 요구역량 필수기술", k=5
    )
    if not hits:
        # on_fail → 폴백 없음, 기존 텍스트 그대로
        state["search_degraded"] = True
        return posting_text, []

    # Observe: snippet을 LLM 컨텍스트로 주입할 텍스트 블록 조합
    # (search_count는 web_search() 내부에서 실제 API 호출 1건당 += 1 로 관리한다.
    #  여기서 별도로 증가시키지 않는다 — 02-agent-graph.md:442 카운터 규율과 일치)
    snippet_block = "\n\n".join(
        f"[출처: {h.url}]\n{h.snippet}" for h in hits
    )
    return posting_text + "\n\n[웹검색 보강]\n" + snippet_block, hits
```

추출된 각 필수·우대 스킬에는 근거 `source_url`(SearchHit.url)을 부착합니다.
검색 경로로 추출된 스킬은 `source="web_search"`로 기록됩니다.

**rerun 시 추가 컨텍스트:**

```python
if rerun_reason:
    prompt_context["rerun_instruction"] = f"""
이전 추출 결과에 대해 Gap 분석 에이전트가 다음 문제를 보고했습니다:
{rerun_reason}

이를 반영해 필수 역량을 더 구체적으로 추출하거나,
부족한 공고 근거는 직무 일반 지식을 보완해 evidence_strength를 높이세요.
단, 공고에 없는 내용을 임의로 추가하는 것은 금지합니다.
"""
```

### 출력 (State에 쓰는 키)

| State 키 | 타입 | 설명 |
|---|---|---|
| `job_requirement` | `JobRequirement` | 추출된 직무 요구역량 |
| `trace` | `list[TraceEntry]` | 이 노드 실행 기록 append |

### Pydantic 모델

```python
class JobRequirement(BaseModel):
    required_skills: list[str]       # 필수 기술 (공고에 명시된 것)
    preferred_skills: list[str]      # 우대 기술 (있으면 가점)
    required_experience: list[str]   # 요구 경험 (기간, 프로젝트 등)
    keywords: list[str]              # 핵심 키워드 (역할 요약용)
    evidence_strength: Literal["strong", "weak"]  # 근거 강도 자가 평가
    source: Literal["user_posting", "sample_posting", "role_inference", "web_search"]
    # web_search: 공고 부실 시 검색 API snippet에서 추출한 경우
    source_urls: list[str] = []   # web_search 경로 시 SearchHit.url 목록
```

### evidence_strength 판정 기준 (프롬프트에 명시)

```
evidence_strength = "strong" 조건 (모두 충족 시):
  ① required_skills가 3개 이상 공고 원문에서 직접 추출됨
  ② 공고 텍스트 길이 ≥ 200자
  ③ 홍보성 문구를 제외한 실질 역량 기술이 전체의 50% 이상

evidence_strength = "weak" 조건 (하나라도 해당 시):
  ① 공고가 없거나 100자 미만 (샘플/추론으로 보완한 경우)
  ② required_skills를 공고가 아닌 직무 일반 지식으로만 추론
  ③ 필수/우대 구분이 공고에 없어 전부 추론
  ④ web_search 경로로 추출했으나 검색 결과가 2건 미만이거나 snippet이 30자 미만인 경우
     (검색 결과 충실도 부족 → strong 자가 판정 금지)
```

### 프롬프트 전략 요지

**추출 지시:**

```
1. 공고에서 기술 스택명(언어/프레임워크/도구)을 그대로 추출한다.
   약어와 정식명이 혼재하면 둘 다 포함한다 (예: "JS", "JavaScript").
2. "적극적인 자세", "팀플레이어" 같은 태도/소프트스킬은 required_experience에만
   포함하고, required_skills에는 넣지 않는다.
3. 채용 홍보 문구는 모두 제거한다.
   판별 기준: 회사/복지 소개, "최고/글로벌/도전" 등 수식어, 직무 외 안내.
4. evidence_strength를 위의 판정 기준에 따라 반드시 기재한다.
5. source를 정확히 기재한다 (user_posting / sample_posting / role_inference).
```

### 실패·폴백

| 상황 | 처리 |
|---|---|
| 공고 텍스트 없음 (job_posting_text=None) | 샘플 공고 로드 후 source="sample_posting" |
| 샘플 공고도 없는 직무 | required_skills를 직무 일반 지식으로 추론 후 source="role_inference", evidence_strength="weak" |
| LLM JSON 파싱 실패 | required_skills=[], evidence_strength="weak", source="role_inference" 최소 결과 반환 |
| rerun 2회 이상 요청 | rerun_count >= MAX_RERUN(=1) 도달 시 현재 결과 유지하고 gap_analysis 진행 |

### 출력 JSON 예시

```json
{
  "required_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "REST API 설계",
    "Git"
  ],
  "preferred_skills": [
    "Docker",
    "Redis",
    "AWS (EC2/S3)"
  ],
  "required_experience": [
    "API 서버 개발 경험 (인턴/프로젝트 포함)",
    "협업 도구 사용 경험 (Jira, Notion 등)"
  ],
  "keywords": ["백엔드", "Python", "FastAPI", "REST API", "서버 개발"],
  "evidence_strength": "strong",
  "source": "user_posting",
  "source_urls": []
}
```

**web_search 경로 출력 예시** (공고 부실 → 검색으로 보강한 경우):

```json
{
  "required_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "REST API 설계",
    "Git"
  ],
  "preferred_skills": ["Docker", "Redis"],
  "required_experience": ["API 서버 개발 경험"],
  "keywords": ["백엔드", "Python", "FastAPI", "REST API"],
  "evidence_strength": "strong",
  "source": "web_search",
  "source_urls": [
    "https://www.wanted.co.kr/wd/12345",
    "https://www.jumpit.co.kr/position/67890"
  ]
}
```

**rerun 시 출력 예시** (Gap이 "공고 근거 약함"으로 되먹임한 경우):

```json
{
  "required_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "REST API 설계",
    "Git",
    "단위 테스트 (pytest)",
    "비동기 프로그래밍 (asyncio)"
  ],
  "preferred_skills": ["Docker", "Redis", "AWS"],
  "required_experience": [
    "API 서버 개발 경험",
    "DB 스키마 설계 경험"
  ],
  "keywords": ["백엔드", "Python", "FastAPI", "비동기", "REST API"],
  "evidence_strength": "strong",
  "source": "user_posting",
  "source_urls": []
}
```

---

## 4. GapRoadmapAgent — 갭 분석 & 로드맵 생성

### 역할

두 단계로 구성된 복합 에이전트입니다.

**단계 1 — gap_analysis (갭 분석 노드):**
ProfileDiagnosis vs JobRequirement를 비교해 부족 역량 목록과 우선순위를 도출합니다.
직무 근거가 약하면 `needs_rerun=true`를 설정해 JobRequirementAgent 재요청 신호를 보냅니다.

**단계 2 — roadmap_plan (로드맵 계획 노드):**
`lookup_skill` 툴을 호출해 선후행 관계·학습 자원·표준 소요시간을 확인한 뒤, **동적 기간**을 스스로 산출해 주차별 로드맵을 생성합니다.
"4주 또는 8주 고정 템플릿 채우기"가 아니라 갭 점수와 주당 가용시간으로 기간을 먼저 결정하는 **Plan-and-Solve** 방식입니다 (Wang et al. 2023).

`lookup_skill` 호출은 ReAct (Yao et al. 2022)의 Act 단계에 해당합니다 — LLM이 환각하는 대신 외부 사전을 실제로 조회하는 도구 호출로 신뢰도를 확보합니다.

### 입력 (State에서 읽는 키)

#### gap_analysis 노드

| State 키 | 타입 | 설명 |
|---|---|---|
| `profile` | `ProfileDiagnosis` | 프로필 진단 결과 |
| `job_requirement` | `JobRequirement` | 직무 요구역량 |
| `rerun_count` | `int` | 현재까지의 Job 재요청 횟수 (무한 루프 방지) |

#### roadmap_plan 노드

| State 키 | 타입 | 설명 |
|---|---|---|
| `gap_analysis` | `GapAnalysis` | 갭 분석 결과 |
| `onboarding_input.weekly_hours` | `int` | 주당 가용 시간 (시간예산 계산 기준) |
| `episodic_memory` | `EpisodicMemory \| None` | 미완료 이월·직전 로드맵 rationale |
| `critic_report` | `CriticReport \| None` | roadmap_critic revise 시 위반 사유 |
| `revision_count` | `int` | 현재까지 재생성 횟수 |

### 출력 (State에 쓰는 키)

#### gap_analysis 노드

| State 키 | 타입 | 설명 |
|---|---|---|
| `gap_analysis` | `GapAnalysis` | 갭 분석 결과 |
| `needs_rerun` | `bool` | Job 재요청 필요 여부 |
| `rerun_reason` | `str \| None` | 재요청 사유 |
| `verified` | `bool` | 스킬 사전 검증 여부 (폴백 포함 시 false) |
| `trace` | `list[TraceEntry]` | 이 노드 실행 기록 append |

#### roadmap_plan 노드

| State 키 | 타입 | 설명 |
|---|---|---|
| `roadmap` | `Roadmap` | 생성된 주차별 로드맵 |
| `verified` | `bool` | 모든 스킬이 사전 조회됐으면 유지, 폴백 있으면 false |
| `trace` | `list[TraceEntry]` | 이 노드 실행 기록 append |

### Pydantic 모델 (핵심 모델만 발췌)

```python
class GapItem(BaseModel):
    skill: str                          # normalize_skill_name() 정규화 후 스킬명
    priority: Literal["high", "medium", "low"]
    current_level: str                  # 사용자 현재 수준 (입력 근거 기반)
    target_level: str                   # 직무 요구 수준
    skill_status: Literal["known", "unknown"]  # lookup_skill 결과
    verified: bool                      # 사전 적중 여부

class GapAnalysis(BaseModel):
    gaps: list[GapItem]
    job_evidence_strength: Literal["strong", "weak"]
    needs_rerun: bool
    rerun_reason: str | None

class WeekPlan(BaseModel):
    week_index: int                     # 1-base
    objectives: list[str]
    tasks: list[TaskItem]
    covered_skills: list[str]           # 이 주차가 커버하는 GapItem.skill 목록
    planned_hours: int                  # <= weekly_hours 검증 대상

class Roadmap(BaseModel):
    horizon: Literal["weeks_4", "weeks_6", "weeks_8"]
    # weeks_custom 제거 — total_weeks는 항상 max(4, min(8, min_weeks))로 4~8 범위
    total_weeks: int
    weeks: list[WeekPlan]
    weekly_hours_budget: int            # onboarding_input.weekly_hours 복사
    rationale: str                      # 기간 산출 근거 (Plan-and-Solve)
```

### needs_rerun 신호 생성 규칙

```python
def should_rerun_job(gap_analysis: GapAnalysis, rerun_count: int) -> bool:
    """
    Gap→Job 되먹임 조건:
      1. job_evidence_strength == "weak"
      2. rerun_count < MAX_RERUN (=1)  ← 무한 루프 방지
    """
    return (
        gap_analysis.job_evidence_strength == "weak"
        and rerun_count < MAX_RERUN
    )

# conditional_edge — route 함수는 읽기만(CANON E: 카운터 증가 금지)
# rerun_count += 1 은 job_requirement_node 본문 진입 시 처리
def gap_to_next_edge(state: CareerMateState) -> str:
    if state["needs_rerun"] and state["rerun_count"] < MAX_RERUN:
        return "rerun_job"    # → job_requirement 노드 (라벨: rerun_job)
    return "skip_rerun"       # → roadmap_plan 노드 (라벨: skip_rerun)
```

### 동적 기간 산출 규칙 (Plan-and-Solve, Wang et al. 2023)

"4주 또는 8주" 고정 템플릿 대신 아래 알고리즘으로 기간을 먼저 결정합니다.
**기간이 로드맵을 결정하는 것이 아니라, 갭·시간이 기간을 결정합니다.**

```python
def calculate_horizon(gaps: list[GapItem], weekly_hours: int) -> tuple[int, str]:
    """
    Returns: (total_weeks, rationale)

    Plan 단계: 각 갭 스킬의 typical_hours를 lookup_skill로 조회해 총 소요시간 산출.
    Solve 단계: 총 소요시간 / 주당 가용시간으로 최소 주차 계산.
    """
    total_hours = 0
    for gap in gaps:
        normalized = normalize_skill_name(gap.skill)
        record = lookup_skill(normalized)
        if record.status == "known":
            # 우선순위 가중: high=100%, medium=70%, low=50%
            weight = {"high": 1.0, "medium": 0.7, "low": 0.5}[gap.priority]
            total_hours += int(record.typical_hours * weight)
        else:
            # unknown 폴백: 직무 일반 평균 사용 (20시간/스킬)
            total_hours += 20

    # 최소 주차 = ceil(총 소요시간 / 주당 가용시간)
    import math
    min_weeks = math.ceil(total_hours / max(weekly_hours, 1))

    # 4주 미만은 4주로 올림, 8주 초과는 8주로 내림 (MVP 범위)
    total_weeks = max(4, min(8, min_weeks))

    # weeks_custom 제거 — 항상 4~8 범위로 캡
    horizon = (
        "weeks_4" if total_weeks <= 4 else
        "weeks_6" if total_weeks <= 6 else
        "weeks_8"
    )

    rationale = (
        f"고우선순위 갭 {len([g for g in gaps if g.priority == 'high'])}개 포함 "
        f"총 예상 소요 {total_hours}시간 ÷ 주당 {weekly_hours}시간 = "
        f"최소 {min_weeks}주 → {total_weeks}주 로드맵 결정"
    )
    return total_weeks, rationale
```

### lookup_skill 호출 흐름 (ReAct 패턴)

```
[Thought] "FastAPI 학습에 선후행 스킬이 있는지, 표준 소요시간이 얼마인지 확인 필요"
[Act]     record = lookup_skill(normalize_skill_name("FastAPI"))
[Observe] record = {name:"FastAPI", status:"known", prereqs:["Python","HTTP 기초"],
                    typical_hours:30, resources:[...], verified:true}
[Thought] "Python과 HTTP 기초가 선행 필요. 로드맵에서 Python 주차를 FastAPI 주차 앞에 배치"
```

**unknown 스킬 web_search 보강 (3단계 처리):**

```python
record = lookup_skill(normalize_skill_name(skill))
if record.status == "known":
    # 1단계: DB 캐시 히트 → 검색 생략, verified=True (origin="db")
    task_item.verified = True
    task_item.origin = "db"
else:
    # 2단계: DB miss → web_search로 실제 url 보강
    hits: list[SearchHit] = web_search(
        f"{skill} 학습 강의 튜토리얼 공식문서", k=3
    )
    if hits:
        # 검색 성공 → SearchHit.url 기반 ResourceItem 생성 (환각 대신 실제 url)
        task_item.resources = [
            ResourceItem(
                title=h.title,
                url=h.url,
                type="doc",
                verified=True,
                origin="web",
                source_url=h.url,
            )
            for h in hits
        ]
        task_item.verified = True
        # 전역 verified는 낮추지 않음 (url 출처 확보 = verified=True)
    else:
        # 3단계: 검색도 실패(빈 리스트) → LLM 폴백(verified=False, origin="llm")
        state["search_degraded"] = True
        task_item.verified = False
        task_item.origin = "llm"
        state["verified"] = False  # 전역 verified 내림 → 프론트 "검증 안 됨" 배지
```

### roadmap_critic 검증 후 재생성 (Reflexion / Self-Refine)

critic revise 판정 시 위반 사유를 컨텍스트로 받아 재생성합니다 (Shinn et al. 2023, Madaan et al. 2023).

```python
if critic_report and critic_report.verdict == "revise":
    # 위반 사유를 프롬프트에 주입
    revision_context = "\n".join([
        f"- [{v.type}] {v.detail} (위치: {v.location})"
        for v in critic_report.violations
    ])
    prompt_context["revision_instruction"] = f"""
이전 로드맵이 다음 검증을 통과하지 못했습니다. 아래 위반을 모두 수정하세요:
{revision_context}

수정 시 다른 검증 항목을 새로 위반하지 않도록 주의하세요.
"""
```

**conditional_edge (critic 결과 → 다음 노드):**

```python
# route 함수는 읽기만(CANON E: 카운터 증가 금지)
# revision_count += 1 은 roadmap_plan_node 본문 진입 시 처리
def critic_edge(state: CareerMateState) -> str:
    report = state["critic_report"]
    if report.verdict == "pass" or state["revision_count"] >= MAX_REVISIONS:
        # pass이거나 최대 재생성 횟수(2회) 도달 시 강제 finalize
        return "pass"     # → finalize 노드 (라벨: pass)
    return "revise"       # → roadmap_plan 노드 (라벨: revise)
```

### 출력 JSON 예시

#### gap_analysis 출력 (needs_rerun=false 정상 경로)

```json
{
  "gaps": [
    {
      "skill": "FastAPI",
      "priority": "high",
      "current_level": "미경험",
      "target_level": "실무 수준 REST API 개발",
      "skill_status": "known",
      "verified": true
    },
    {
      "skill": "PostgreSQL",
      "priority": "high",
      "current_level": "SQL 기초 (SELECT/JOIN 수준)",
      "target_level": "스키마 설계 + 트랜잭션 관리",
      "skill_status": "known",
      "verified": true
    },
    {
      "skill": "Docker",
      "priority": "medium",
      "current_level": "미경험",
      "target_level": "컨테이너 기본 운용",
      "skill_status": "known",
      "verified": true
    }
  ],
  "job_evidence_strength": "strong",
  "needs_rerun": false,
  "rerun_reason": null
}
```

#### gap_analysis 출력 (needs_rerun=true, Job 되먹임 발생)

```json
{
  "gaps": [
    {
      "skill": "Python",
      "priority": "high",
      "current_level": "기초",
      "target_level": "불명확 (공고 근거 부족)",
      "skill_status": "known",
      "verified": true
    }
  ],
  "job_evidence_strength": "weak",
  "needs_rerun": true,
  "rerun_reason": "공고 텍스트가 50자 미만으로 필수 역량을 직접 추출할 수 없음. 직무 일반 지식으로만 구성되어 갭 우선순위 산정 근거 부족."
}
```

#### roadmap 출력 (6주 동적 기간 산출 예시)

```json
{
  "horizon": "weeks_6",
  "total_weeks": 6,
  "weekly_hours_budget": 10,
  "rationale": "고우선순위 갭 2개 포함 총 예상 소요 58시간 ÷ 주당 10시간 = 최소 6주 → 6주 로드맵 결정",
  "weeks": [
    {
      "week_index": 1,
      "objectives": ["Python 비동기 프로그래밍(asyncio) 기초 완성"],
      "tasks": [
        {
          "title": "asyncio 공식 문서 + 실습 예제 5개",
          "skill": "Python",
          "resources": [
            {
              "title": "Python asyncio 공식 문서",
              "url": "https://docs.python.org/3/library/asyncio.html",
              "type": "doc",
              "verified": true,
              "origin": "db",
              "source_url": null
            }
          ],
          "est_hours": 8,
          "verified": true
        }
      ],
      "covered_skills": ["Python"],
      "planned_hours": 8
    },
    {
      "week_index": 2,
      "objectives": ["FastAPI 기초 — 라우터·의존성 주입·Pydantic 모델"],
      "tasks": [
        {
          "title": "FastAPI 공식 튜토리얼 완주 (Todo API 구현)",
          "skill": "FastAPI",
          "resources": [
            {
              "title": "FastAPI 공식 튜토리얼",
              "url": "https://fastapi.tiangolo.com/tutorial/",
              "type": "doc",
              "verified": true,
              "origin": "db",
              "source_url": null
            }
          ],
          "est_hours": 10,
          "verified": true
        }
      ],
      "covered_skills": ["FastAPI"],
      "planned_hours": 10
    }
  ]
}
```

---

## 공통 사항: TraceEntry 기록 예시

모든 에이전트는 실행 종료 시 다음 형식으로 `trace`에 append합니다.

```json
[
  {
    "node": "triage_router",
    "input_summary": "target_role='개발자', owned_skills=['Python']",
    "decision": "ask",
    "tool_called": null,
    "output_summary": "ambiguity_score=0.75, similar_roles=[백엔드, 데이터엔지니어, ML엔지니어]",
    "ts": "2025-01-15T10:23:01Z"
  },
  {
    "node": "job_requirement",
    "input_summary": "target_role='백엔드 개발자', posting_length=340자, rerun_reason=null",
    "decision": null,
    "tool_called": null,
    "output_summary": "required_skills=5개, evidence_strength=strong",
    "ts": "2025-01-15T10:24:15Z"
  },
  {
    "node": "gap_analysis",
    "input_summary": "gaps 후보 8개, job_evidence_strength=strong",
    "decision": "skip_rerun",
    "tool_called": null,
    "output_summary": "gaps=3개(high:2, medium:1), needs_rerun=false",
    "ts": "2025-01-15T10:24:32Z"
  },
  {
    "node": "job_requirement",
    "input_summary": "target_role='백엔드 개발자', posting_length=45자(부실), rerun_reason=null",
    "decision": null,
    "tool_called": "web_search('백엔드 개발자 채용공고 요구역량 필수기술')",
    "output_summary": "hits=5개, required_skills=6개, source=web_search, evidence_strength=strong",
    "ts": "2025-01-15T10:24:05Z"
  },
  {
    "node": "roadmap_plan",
    "input_summary": "gaps=3개, weekly_hours=10, revision_count=0",
    "decision": null,
    "tool_called": "lookup_skill(FastAPI), lookup_skill(PostgreSQL), web_search('Docker 학습 강의 튜토리얼 공식문서')",
    "output_summary": "total_weeks=6, horizon=weeks_6, 6주×10시간 로드맵",
    "ts": "2025-01-15T10:25:10Z"
  },
  {
    "node": "roadmap_critic",
    "input_summary": "revision_count=0, violations 체크 4종",
    "decision": "pass",
    "tool_called": null,
    "output_summary": "verdict=pass, violations=[]",
    "ts": "2025-01-15T10:25:18Z"
  }
]
```

이 trace는 대시보드 "why-this-path" 타임라인으로 노출되어, 발표·평가 시 "이게 왜 에이전트인가"를 직관적으로 증명합니다 (피드백 제안6).

---

## 참고 문헌

| 논문/문서 | 적용 지점 |
|---|---|
| Anthropic, *Building Effective Agents* (2024) | TriageRouter (routing 패턴), ProfileDiagnosis (guardrail 패턴) |
| Yao et al., *ReAct* (2022) | roadmap_plan의 lookup_skill Thought-Act-Observe 루프 |
| Shinn et al., *Reflexion* (2023) | roadmap_critic → roadmap_plan 재생성 루프 |
| Madaan et al., *Self-Refine* (2023) | 단일 에이전트 자기 교정 (경량 반영 구현 근거) |
| Wang et al., *Plan-and-Solve Prompting* (2023) | 동적 기간 산출 (갭→시간→주차 역방향 인과) |
| LangGraph 공식 문서 — Conditional Edges | `triage_edge`, `gap_to_next_edge`, `critic_edge` 구현 |
