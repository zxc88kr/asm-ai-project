# 스킬 DB + 웹검색 tool — 툴 계약 & 스킬 사전

이 문서는 **tool use 0→1**의 두 핵심 툴인 `lookup_skill`(정적 스킬 사전 조회)과 `web_search`(검색 API 호출) 계약·폴백 규칙과, 그 뒤를 받치는 정적 스킬 사전(Skill DB)의 스키마·예시·작성 가이드를 정의합니다.
LLM이 강의나 링크를 환각하는 대신 함수 호출로 검증된 자원을 가져오는 구조(ReAct, Yao et al. 2022)를 최소 비용으로 구현합니다.

---

## 1. 왜 툴이 필요한가

> "도구 호출 여부는 에이전트와 단순 LLM 호출을 가르는 1차 기준입니다." — feedback.md, 에이전트 관점에서 아쉬운 점 §1

현재 설계에서 `GapRoadmapAgent`는 "Python 배우려면 이 강의 들어라" 같은 정보를 LLM의 학습된 지식에서 바로 꺼냅니다.  
문제는 두 가지입니다.

| 문제 | 증상 |
|------|------|
| **환각(Hallucination)** | 존재하지 않는 강의명·링크가 로드맵에 삽입됨 |
| **선후행 오류** | "Docker를 배우기 전에 Linux 기초" 같은 순서를 무시한 로드맵 생성 |

**해결책**: 50~150행짜리 정적 JSON 스킬 사전을 만들고, LLM이 이 사전을 함수로 조회하게 합니다.  
조회 실패(스킬 미존재) 시에도 예외를 던지지 않고 `status='unknown'`을 반환해 LLM이 폴백하도록 설계합니다.

이 패턴은 **DB 캐시 우선 조회(lookup_skill) + unknown 스킬은 web_search로 실제 URL 보강**하는 구조이며, ReAct 논문의 핵심인 "추론(Thought) + 행동(Act = 도구 호출)"을 가장 단순한 형태로 구현합니다.  
`lookup_skill`은 사람이 URL을 직접 검수한 고품질 영구 캐시(Agent3 우선 사용), `web_search`는 DB에 없는 스킬의 실제 URL을 보강하는 신선 조회(Agent2 기본 의존 · Agent3 miss 보강)입니다.

---

## 2. 툴 계약 (Tool Contract)

### 2.1 `lookup_skill`

```python
def lookup_skill(name: str) -> SkillRecord:
    """
    IT 직무 한정 정적 스킬 사전을 조회한다.

    Args:
        name: 스킬명. normalize_skill_name()으로 전처리 권장.

    Returns:
        SkillRecord — 사전에 존재하면 status='known', 없으면 status='unknown'.
        절대 예외를 던지지 않는다(on_fail 참조).
    """
```

**반환 타입: `SkillRecord`**

```python
class ResourceItem(BaseModel):
    title: str              # 자원 제목
    url: str | None         # 링크 (사전 유래만; 폴백은 None)
    type: str               # 'course' | 'doc' | 'project'
    verified: bool          # url 출처 있으면 True (db 또는 web)
    origin: Literal["db", "web", "llm"] = "db"  # 검증 출처 종류
    source_url: str | None = None               # web origin일 때 SearchHit.url

class SkillRecord(BaseModel):
    name: str               # 표준 스킬명
    status: str             # 'known' | 'unknown'
    prereqs: list[str]      # 선행 스킬 리스트
    resources: list[ResourceItem]  # 대표 학습 자원
    typical_hours: int      # 표준 소요 시간(시간 단위)
    verified: bool          # 사전 적중 여부 (status='known'이면 True)
```

**on_fail 폴백 규칙**

사전에 스킬이 없거나 IO 오류가 발생하면 다음 객체를 반환합니다(예외 throw 금지):

```python
SkillRecord(
    name=name,
    status="unknown",
    prereqs=[],
    resources=[],
    typical_hours=0,
    verified=False
)
```

호출자(`roadmap_plan` 노드)는 `status='unknown'`이면 LLM 일반지식으로 폴백하되,  
해당 `TaskItem.verified = False`로 표기하고 `State.verified = False`로 내립니다.  
프론트엔드는 `verified=False` 항목에 "검증 안 됨" 뱃지를 붙입니다.

---

### 2.2 `list_skills_for_role`

```python
def list_skills_for_role(role: str) -> list[SkillRecord]:
    """
    직무명으로 관련 스킬 집합을 일괄 조회한다.

    Args:
        role: IT 직무명 (예: 'frontend', 'backend', 'data_analyst').

    Returns:
        해당 직무에 매핑된 SkillRecord 리스트.
        role 미매핑 시 빈 리스트 반환(throw 금지).
    """
```

`JobRequirementAgent`가 직무명만 있고 공고 텍스트가 부실할 때 보조적으로 호출해  
갭 분석 후보 스킬 풀을 확보합니다.

---

### 2.3 `normalize_skill_name`

```python
def normalize_skill_name(raw: str) -> str:
    """
    사용자/LLM 자유 표기를 스킬 사전 표준 키로 정규화한다.

    예: 'react.js' -> 'React', 'JS' -> 'JavaScript', 'docker' -> 'Docker'

    매칭 실패 시 raw 원문 그대로 반환(throw 금지).
    이후 lookup_skill이 unknown 처리.
    """
```

`lookup_skill` 호출 전 항상 이 함수를 먼저 통과시켜 적중률을 높입니다.

---

### 2.4 `web_search` (신규)

검색 API 1개(Tavily 또는 Serper 택1)를 감싸는 단일 어댑터입니다. 결과 파싱(snippet→skills/resources 추출)은 호출 노드의 LLM 프롬프트가 담당합니다.

```python
# tools/web_search.py
from pydantic import BaseModel
from typing import Literal

class SearchHit(BaseModel):
    title: str            # 검색 결과 제목
    url: str              # 출처 URL (verified=true 근거)
    snippet: str          # 본문 발췌(검색 API가 준 텍스트, 크롤링 아님)
    source: str           # 도메인 또는 제공자명 (예: "wanted.co.kr", "tavily")
    retrieved_at: str     # ISO 타임스탬프 (검색 시각)

def web_search(query: str, k: int = 5) -> list[SearchHit]:
    """
    검색 API 1개를 호출해 상위 k개 결과를 SearchHit 리스트로 반환한다.

    계약(lookup_skill과 동일 철학):
      - 절대 예외를 던지지 않는다(throw 금지).
      - 성공: SearchHit 리스트(0~k개). 각 항목은 url·snippet·retrieved_at 포함.
      - on_fail(API 키 없음/타임아웃/HTTP 오류/쿼터 초과/MAX_SEARCH 초과):
          빈 리스트 [] 반환 + 호출 노드가 state["search_degraded"]=True 설정.
          호출자는 LLM 자체지식으로 폴백하되 verified=False로 표기.
      - 캐시 히트 시 API 호출 없이 캐시된 SearchHit 리스트 반환(retrieved_at은 원본 검색 시각 유지).
    """
    ...
```

**캐시 · MAX_SEARCH 상한**

- 세션 캐시: `State.search_results: dict[str, list[SearchHit]]`에 `query.strip().lower()` 키로 저장. 동일 쿼리 재요청 시 API 재호출 없이 캐시 반환(상한 소모 X).
- `MAX_SEARCH = 8` — 세션당 실제 API 호출 상한(캐시 히트 제외). 초과 시 빈 리스트 반환 + `search_degraded=True`.
- `search_count` 증가는 노드 본문(tool 호출 카운터). `MAX_RERUN=1`, `MAX_REVISIONS=2`와 동일 계열 가드 상수.

**허용 vs 금지 경계**

> **허용 — 검색 API 호출(web_search):** 검색 엔진/검색 API(예: Tavily, Serper)에 쿼리를 보내 검색 엔진이 미리 색인해 반환하는 결과 메타데이터(title·url·snippet)만 받아 사용합니다. 우리 시스템은 대상 사이트에 직접 접속해 페이지를 내려받지 않습니다.
>
> **금지 — 대규모 사이트 크롤링(out-of-scope, 유지):** 채용 사이트 전체를 봇으로 순회하며 HTML을 대량 수집·저장·파싱하는 행위는 MVP 범위에서 제외합니다. 단일 페이지 본문을 직접 fetch해 본문을 긁는 것도 1.5주 범위에서는 하지 않습니다.
>
> 한 줄 요약: **"실시간 크롤링(사이트 직접 순회·HTML 수집)은 제외하되, 검색 API 호출(쿼리→색인된 결과 메타데이터 수신)은 도입한다. 둘은 다른 행위다."**

**호출 위치**: 기존 `lookup_skill`과 동일하게 별도 ToolNode 분기 없이 노드 내부 tool 호출로 구현합니다. 그래프 구조(8개 노드·3개 조건엣지)는 변경하지 않습니다.

---

## 3. Skill DB 스키마

스킬 사전은 단일 JSON 파일(`skill_db.json`)로 관리합니다.  
최상위는 `skills` 배열, 각 항목이 하나의 스킬 레코드입니다.

```json
{
  "version": "1.0",
  "last_updated": "2025-01-01",
  "skills": [
    {
      "name": "React",
      "aliases": ["react.js", "ReactJS", "리액트"],
      "roles": ["frontend"],
      "prereqs": ["JavaScript", "HTML/CSS"],
      "resources": [
        {
          "title": "공식 React 튜토리얼",
          "url": "https://react.dev/learn",
          "type": "doc",
          "verified": true
        },
        {
          "title": "인프런 — React 완벽 가이드",
          "url": "https://www.inflearn.com/course/react-complete-guide",
          "type": "course",
          "verified": true
        }
      ],
      "typical_hours": 60
    }
  ],
  "role_mappings": {
    "frontend": ["HTML/CSS", "JavaScript", "TypeScript", "React", "Git", "단위테스트"],
    "backend": ["Python", "REST API 설계", "SQL", "Docker", "Git", "단위테스트"],
    "data_analyst": ["Python", "SQL", "판다스/넘파이", "데이터 시각화", "Git"]
  }
}
```

**스키마 필드 설명**

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 표준 스킬 키 (대소문자 유지) |
| `aliases` | list[string] | `normalize_skill_name` 매칭용 별칭 목록 |
| `roles` | list[string] | 이 스킬이 속한 IT 직무 태그 (`role_mappings` 키와 동일) |
| `prereqs` | list[string] | 선행 스킬명 (`name` 기준, 순환 참조 금지) |
| `resources` | list[ResourceItem] | 대표 학습 자원 1~3개 권장 |
| `typical_hours` | int | 이 스킬을 입문~실무 수준으로 올리는 표준 소요 시간 |
| `role_mappings` | dict | `list_skills_for_role` 조회 테이블 |

---

## 4. 스킬 DB 예시 항목 (8~12개)

아래는 IT 직무 한정 예시 항목입니다. 실제 구현 시 이 형식 그대로 `skill_db.json`에 추가합니다.

```json
[
  {
    "name": "HTML/CSS",
    "aliases": ["html", "css", "html5", "css3"],
    "roles": ["frontend"],
    "prereqs": [],
    "resources": [
      {
        "title": "MDN Web Docs — HTML 기초",
        "url": "https://developer.mozilla.org/ko/docs/Learn/HTML",
        "type": "doc",
        "verified": true
      },
      {
        "title": "MDN Web Docs — CSS 첫걸음",
        "url": "https://developer.mozilla.org/ko/docs/Learn/CSS",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 30
  },
  {
    "name": "JavaScript",
    "aliases": ["JS", "javascript", "자바스크립트"],
    "roles": ["frontend", "backend"],
    "prereqs": ["HTML/CSS"],
    "resources": [
      {
        "title": "모던 JavaScript 튜토리얼 (ko.javascript.info)",
        "url": "https://ko.javascript.info/",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 60
  },
  {
    "name": "TypeScript",
    "aliases": ["TS", "typescript", "타입스크립트"],
    "roles": ["frontend", "backend"],
    "prereqs": ["JavaScript"],
    "resources": [
      {
        "title": "TypeScript 공식 핸드북",
        "url": "https://www.typescriptlang.org/ko/docs/handbook/intro.html",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 30
  },
  {
    "name": "React",
    "aliases": ["react.js", "ReactJS", "리액트"],
    "roles": ["frontend"],
    "prereqs": ["JavaScript", "HTML/CSS"],
    "resources": [
      {
        "title": "공식 React 튜토리얼",
        "url": "https://react.dev/learn",
        "type": "doc",
        "verified": true
      },
      {
        "title": "미니 프로젝트 — Todo 앱 만들기",
        "url": null,
        "type": "project",
        "verified": true
      }
    ],
    "typical_hours": 60
  },
  {
    "name": "Python",
    "aliases": ["python3", "파이썬"],
    "roles": ["backend", "data_analyst"],
    "prereqs": [],
    "resources": [
      {
        "title": "점프 투 파이썬",
        "url": "https://wikidocs.net/book/1",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 50
  },
  {
    "name": "REST API 설계",
    "aliases": ["REST API", "RESTful", "rest api"],
    "roles": ["backend"],
    "prereqs": ["Python"],
    "resources": [
      {
        "title": "FastAPI 공식 튜토리얼",
        "url": "https://fastapi.tiangolo.com/ko/tutorial/",
        "type": "doc",
        "verified": true
      },
      {
        "title": "미니 프로젝트 — Todo REST API 구현",
        "url": null,
        "type": "project",
        "verified": true
      }
    ],
    "typical_hours": 40
  },
  {
    "name": "SQL",
    "aliases": ["sql", "MySQL", "PostgreSQL", "데이터베이스"],
    "roles": ["backend", "data_analyst"],
    "prereqs": [],
    "resources": [
      {
        "title": "프로그래머스 SQL 고득점 Kit",
        "url": "https://school.programmers.co.kr/learn/challenges?tab=sql_practice_kit",
        "type": "course",
        "verified": true
      }
    ],
    "typical_hours": 25
  },
  {
    "name": "Linux 기초",
    "aliases": ["linux", "리눅스", "bash", "shell", "터미널"],
    "roles": ["backend"],
    "prereqs": [],
    "resources": [
      {
        "title": "The Linux Command Line (무료 공개본)",
        "url": "https://linuxcommand.org/tlcl.php",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 10
  },
  {
    "name": "Docker",
    "aliases": ["docker", "도커", "컨테이너"],
    "roles": ["backend"],
    "prereqs": ["Linux 기초"],
    "resources": [
      {
        "title": "Docker 공식 Getting Started",
        "url": "https://docs.docker.com/get-started/",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 15
  },
  {
    "name": "Git",
    "aliases": ["git", "github", "깃", "깃헙", "버전관리"],
    "roles": ["frontend", "backend", "data_analyst"],
    "prereqs": [],
    "resources": [
      {
        "title": "Pro Git (공식 한국어)",
        "url": "https://git-scm.com/book/ko/v2",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 10
  },
  {
    "name": "단위테스트",
    "aliases": ["unit test", "unittest", "pytest", "jest", "테스트"],
    "roles": ["frontend", "backend"],
    "prereqs": ["Python"],
    "resources": [
      {
        "title": "pytest 공식 문서",
        "url": "https://docs.pytest.org/en/stable/",
        "type": "doc",
        "verified": true
      },
      {
        "title": "미니 프로젝트 — 기존 코드에 테스트 추가하기",
        "url": null,
        "type": "project",
        "verified": true
      }
    ],
    "typical_hours": 15
  },
  {
    "name": "판다스/넘파이",
    "aliases": ["pandas", "numpy", "판다스", "넘파이"],
    "roles": ["data_analyst"],
    "prereqs": ["Python"],
    "resources": [
      {
        "title": "pandas 공식 Getting Started",
        "url": "https://pandas.pydata.org/docs/getting_started/index.html",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 30
  },
  {
    "name": "데이터 시각화",
    "aliases": ["matplotlib", "seaborn", "plotly", "시각화"],
    "roles": ["data_analyst"],
    "prereqs": ["판다스/넘파이"],
    "resources": [
      {
        "title": "Matplotlib 튜토리얼 (공식)",
        "url": "https://matplotlib.org/stable/tutorials/index.html",
        "type": "doc",
        "verified": true
      }
    ],
    "typical_hours": 20
  }
]
```

---

## 5. 어느 노드가 언제 호출하는가 (ReAct 패턴)

ReAct(Yao et al. 2022)는 **Thought(추론) → Act(도구 호출) → Observation(결과 반영)** 사이클을 반복합니다.  
CareerMate에서는 다음 두 노드가 이 사이클을 구현합니다.

```
[job_requirement 노드]
  Thought: "공고 텍스트가 부실하면 웹 검색으로 요구역량 보강"
  Act:     web_search(f"{target_role} 채용공고 요구역량 필수기술", k=5)  ← 공고 없을 때
  Obs:     SearchHit.snippet → required/preferred skills 추출, source_url 부착

[gap_analysis 노드]
  Thought: "profile.weaknesses vs job_requirement.required_skills 비교"
  Act:     normalize_skill_name(raw_skill) → lookup_skill(normalized)
           → unknown이면 web_search(f"{skill} 학습 강의 튜토리얼 공식문서", k=3)
  Obs:     prereqs, typical_hours → GapItem.skill_status, GapItem.verified 설정

[roadmap_plan 노드]
  Thought: "high priority gap부터 주차 배치 결정"
  Act:     lookup_skill(gap.skill) → known이면 DB 사용(검색 생략)
           → unknown이면 web_search로 실제 url 보강 → prereqs·resources 채우기
  Obs:     typical_hours → WeekPlan.planned_hours & weekly_hours_budget 주차별 비교
           (시간초과 위험 감지 시 critic에서 time_budget_exceeded 위반으로 잡힘)
```

**전체 호출 흐름 다이어그램**

```
onboarding_intake
      |
      v
triage_router ──(ask)──> clarify ──> triage_router
      |
   (proceed)
      |
      v
profile_diagnosis
      |
      v
job_requirement ◄──────────────────────────┐
      |  [공고 부실 시]                     │ needs_rerun=true
      |  [web_search → snippet 추출]        │ (rerun_count < 1)
      v                                    │
gap_analysis ──► [normalize_skill_name]    │
      |          [lookup_skill] × N        │
      |          [unknown → web_search] × M│
      |               │                   │
      |          GapItem 생성              │
      └─── needs_rerun? ──────────────────┘
      |
   (proceed)
      v
roadmap_plan ──► [lookup_skill] × N
      |          [known → DB 사용, unknown → web_search 보강]
      |          (prereqs·resources·hours)
      v
roadmap_critic  ←──────────────────────────┐
      |                                    │ verdict=revise
      │  verdict=pass                      │ (revision_count < 2)
      └──────────────────────────────────┐ │
                                         v │
                                      finalize
                                         |
                                        END
```

> **참고**: `roadmap_critic`이 `time_budget_exceeded` 위반을 잡는 조건은  
> **주차별** `week.planned_hours > weekly_hours_budget`입니다(주차 단위 초과 여부를 각각 검사).  
> `lookup_skill`이 반환한 `typical_hours`를 로드맵 생성 시 주차 배치에 사용했기 때문에, 사전 값이 정확할수록 Critic의 검증도 정확해집니다.

---

## 6. 환각 차단 논리

출처 URL 유무를 기준으로 verified를 3단계로 판정합니다.

| 출처 | verified | origin | url | 비고 |
|------|----------|--------|-----|------|
| 스킬DB known | `true` | `"db"` | DB의 검수된 url | 최고 신뢰 |
| web_search 결과 (SearchHit.url 존재) | `true` | `"web"` | `SearchHit.url` | url 출처 있음 → verified=true, 단 'web' 표시 |
| LLM 순수 자체지식 (출처 url 없음) | `false` | `"llm"` | `None` | 검색도 실패한 폴백의 폴백. "검증 안 됨" 뱃지 |

```
lookup_skill → known
  → verified=True, origin="db", url=사전 링크
  → 프론트: 정상 표시

lookup_skill → unknown → web_search 성공(url 있음)
  → verified=True, origin="web", url=SearchHit.url
  → 프론트: "웹 출처" 뱃지 + 링크 노출

lookup_skill → unknown → web_search 실패(빈 리스트)
  → verified=False, origin="llm", url=None
  → 프론트: "검증 안 됨" 뱃지
```

구체적 판단 트리:

```python
record = lookup_skill(normalize_skill_name(skill_name))

if record.status == "known":
    # 1단계: DB 캐시 사용 (최고 신뢰)
    task_item.resources = record.resources      # verified=True, origin="db"
    task_item.verified = True
    # State.verified는 건드리지 않음 (기존 True 유지)
else:
    # 2단계: web_search로 실제 url 보강
    hits = web_search(f"{skill_name} 학습 강의 튜토리얼 공식문서", k=3)
    if hits:
        task_item.resources = [
            ResourceItem(title=h.title, url=h.url, type="doc",
                         verified=True, origin="web", source_url=h.url)
            for h in hits
        ]
        task_item.verified = True
        # State.verified는 건드리지 않음 (web origin으로 verified 유지)
        # trace에 tool_called="web_search(query)" 기록
    else:
        # 3단계: 검색도 실패 → LLM 일반지식 폴백
        task_item.resources = llm_suggest_resources(skill_name)  # url=None
        for r in task_item.resources:
            r.verified = False
            r.url = None
            r.origin = "llm"
        task_item.verified = False
        state["verified"] = False   # 전역 플래그 내림
        state["search_degraded"] = True
        # trace에 tool_called="lookup_skill(fallback)" 기록
```

`State.verified = False`가 되면 `FinalOutput.verified = False`로 전파되어  
사용자에게 "일부 학습 자원은 검증되지 않은 정보를 포함할 수 있습니다" 고지가 붙습니다.  
`search_degraded=True` 시에는 추가로 "일부 자원은 웹검색 출처" 고지가 함께 표시됩니다.

---

## 7. Skill DB 작성 가이드 (50~150행 권장 규모)

1.5주 범위에서 **IT 직무 1~2개**로 한정해 작성하는 것이 핵심입니다.

### 7.1 우선순위 기준

| 우선도 | 포함할 스킬 | 예시 |
|--------|------------|------|
| 필수 | `role_mappings`에 등재된 직무별 핵심 스킬 | React, Python, SQL, Git |
| 권장 | 필수 스킬의 `prereqs`에 등장하는 선행 스킬 | HTML/CSS → JavaScript 관계 |
| 선택 | 자주 언급되는 우대 스킬 | Docker, TypeScript |

### 7.2 작성 체크리스트

- [ ] `prereqs`는 반드시 동일 파일 내 `name`으로만 참조 (순환 참조 금지)
- [ ] `resources`는 1~3개 이하, URL은 직접 접속해 존재 확인 후 기재
- [ ] `typical_hours`는 입문자 기준, 과소평가보다 여유 있게 설정 (Critic의 시간예산 검증 정확도에 직결)
- [ ] `aliases`에 한글 표기·소문자·약어 모두 등록 (`normalize_skill_name` 적중률 향상)
- [ ] 같은 스킬이 중복 등재되지 않도록 `name` 유일성 유지

### 7.3 규모 가이드

| IT 직무 수 | 목표 스킬 수 | JSON 행 수 (대략) |
|-----------|------------|-----------------|
| 1개 (예: frontend) | 6~8개 | 50~80행 |
| 2개 (예: frontend + backend) | 10~15개 | 80~130행 |
| 3개 이상 | 1.5주 범위 초과 위험 — 지양 | — |

> "IT 직무 1~2개로 좁혀 스킬 DB를 작게(50~150행) 유지하면 1.5주 안에 충분히 구현 가능합니다." — feedback.md, 1.5주 개발 범위 조언

---

## 8. 구현 파일 구조 제안

```
careermate/
├── tools/
│   ├── skill_db.json          # 스킬 사전 (이 문서 §4 예시 형식)
│   ├── skill_lookup.py        # lookup_skill, list_skills_for_role, normalize_skill_name 구현
│   └── __init__.py
├── agents/
│   ├── gap_analysis.py        # lookup_skill 호출 지점 (§5 참조)
│   └── roadmap_plan.py        # lookup_skill 호출 지점 (§5 참조)
└── ...
```

`skill_lookup.py` 의사코드:

```python
import json
from pathlib import Path
from models import SkillRecord, ResourceItem  # Pydantic 모델

# 모듈 로드 시 1회 파싱 (매 호출마다 파일 읽기 금지)
_DB_PATH = Path(__file__).parent / "skill_db.json"
_db: dict = json.loads(_DB_PATH.read_text(encoding="utf-8"))
_skills_by_name: dict[str, dict] = {s["name"]: s for s in _db["skills"]}
_alias_map: dict[str, str] = {
    alias.lower(): s["name"]
    for s in _db["skills"]
    for alias in s.get("aliases", [])
}


def normalize_skill_name(raw: str) -> str:
    return _alias_map.get(raw.lower(), raw)


def lookup_skill(name: str) -> SkillRecord:
    data = _skills_by_name.get(name)
    if data is None:
        return SkillRecord(
            name=name, status="unknown",
            prereqs=[], resources=[], typical_hours=0, verified=False
        )
    return SkillRecord(
        name=data["name"],
        status="known",
        prereqs=data.get("prereqs", []),
        resources=[ResourceItem(**r) for r in data.get("resources", [])],
        typical_hours=data.get("typical_hours", 0),
        verified=True
    )


def list_skills_for_role(role: str) -> list[SkillRecord]:
    names = _db.get("role_mappings", {}).get(role, [])
    return [lookup_skill(n) for n in names]
```

---

## 9. 관련 문서

- [에이전트 그래프 & 노드 설계](02-agent-graph.md) — `roadmap_plan`, `gap_analysis` 노드의 전체 흐름
- [에이전트 I/O · State 스키마 & 프롬프트 전략](03-agent-contracts.md) — `GapItem.verified`, `TaskItem.verified`, `State.verified` 필드 정의
- [로드맵 Critic & Reflection 루프](05-reflection-critic.md) — `time_budget_exceeded` 위반 검증 시 `typical_hours` 활용

---

## 참고 문헌

| 문헌 | 이 문서와의 연관 |
|------|----------------|
| Yao et al. (2022) **ReAct** | `lookup_skill` 호출이 Thought→Act→Observation 사이클의 Act 단계 |
| Anthropic, **Building Effective Agents** (2024) | tool use 0→1이 'workflow → agent' 분류 전환의 1차 조건 |
| Wang et al. (2023) **Plan-and-Solve** | `typical_hours` 기반 동적 기간 산출(고정 4/8주 탈피)의 근거 |
| Shinn et al. (2023) **Reflexion** | `roadmap_critic`이 `time_budget_exceeded` 감지 시 재생성하는 reflection 루프 (Skill DB의 `typical_hours` 정확도에 의존) |
