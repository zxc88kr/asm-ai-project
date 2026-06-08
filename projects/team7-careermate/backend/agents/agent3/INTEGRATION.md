# Agent3 통합 협의 체크리스트

> Agent3는 현재 **독립 실행**으로 완성돼 있습니다. 입력 3개(`profile`·`job_requirement`·`weekly_hours`)는
> 요청 본문에 **직접 주입**하고, episodic memory는 **받기만 하고 저장하지 않으며**, gap→job 되먹임은
> **신호만 surface**합니다. 이 문서는 에이전트1·2·백엔드·통합 그래프와 **협의해야 할 접점**을 정리합니다.
>
> 관련 문서: [README.md](README.md)(설계) · [IMPLEMENTATION.md](IMPLEMENTATION.md)(구현 현황) · [../docs/06-data-model.md](../docs/06-data-model.md)(스키마)

---

## 한 줄 요약

> **"입력 3개는 직접 주입 중, 메모리는 받기만 하고 저장 안 함, 되먹임은 신호만 보냄"** — 이 세 가지가 통합 시 실제 연결돼야 할 핵심 접점입니다.

---

## 1. 에이전트1 (profile_diagnosis) 담당자와

✅ **스키마 정합 완료** — `feature/Agent_2`의 `ProfileDiagnosis`(`backend/agent2/profile_agent.py`)에 맞춰
Agent3의 `models.py::ProfileDiagnosis`를 일치시켰다. 온보딩 8필드(`major~concern`) 보존 + 정성 진단
(`summary/strengths/weaknesses/evidence`).

**확인된 핵심 사실 (Agent3가 의존하는 부분):**
- ✅ **`owned_skills`가 실제 보유 스킬** — Agent3의 "보유 기준"은 이것을 쓴다. `strengths`/`weaknesses`는
  스킬명이 아니라 정성 개념(`"개발 경험 부족"`, `"전공 일치도"`)이므로 갭 제외 기준으로 쓰지 않는다.
- ✅ **`weekly_hours`가 profile 안에 포함** — Agent3 요청의 `weekly_hours`는 생략 가능(생략 시 `profile.weekly_hours` 사용).
- ✅ **`target_role` 포함** — 추천 경로명 등에 활용 가능(현재는 갭 프롬프트 컨텍스트로 사용).
- `readiness_level`은 Agent1이 보내지 않음 → Agent3 모델에서 제거(과거 의존 제거 완료).

**남은 합의 사항:**
- [ ] **`owned_skills` 표기 정합**: 사용자가 고르는 보유 스킬이 스킬DB 키와 매칭되는 표기인지(예: `"리액트"` vs `"React"`).
  Agent3는 `normalize_skill_name`으로 보정하지만, 온보딩 선택지를 스킬DB 키에 맞추면 정확도가 오른다.
- [ ] **`target_role` 표기 정합**: 직무명이 스킬DB `roles` 키(`"백엔드 개발자"`, `"프론트엔드 개발자"`)와 맞는지.

> 코드 위치: `models.py::ProfileDiagnosis`, `llm.py::_build_gap_prompt`·`_fallback_gaps`(owned_skills 기준), `main.py::run_agent3`(weekly_hours 해석)

---

## 2. 에이전트2 (job_requirement) 담당자와

Agent2의 `JobRequirement`는 필드가 많고(`companies`, `postings` 등) `source="duckduckgo"`를 쓰므로,
Agent3는 `extra="ignore"`로 **그대로 받아** 핵심 필드만 사용한다.

- [ ] **`keywords` 필드 유지**: required_skills가 문장형이라 Agent3는 **`keywords`를 스킬명 추출 힌트로 의존**한다. 에이전트2가 `keywords`에 **깔끔한 기술 토큰**(`["React", "TypeScript"]`)을 계속 채워주는지 보장 필요
- [ ] **`evidence_strength` 정직성**: `"strong" / "weak"` 값이 **`needs_rerun` 트리거**다. weak 남발 시 불필요한 되먹임 발생
- [ ] **gap→job 되먹임 입력 경로**: Agent3가 `needs_rerun=true` + `rerun_reason`을 응답에 surface한다. 에이전트2가 **`rerun_reason`을 컨텍스트로 받아 재추출**하는 입력 경로 필요
- [ ] **핵심 필드명 안정성**: `required_skills / preferred_skills / required_experience / keywords / evidence_strength` 이름 변경 시 **사전 통지**

> 코드 위치: `models.py::JobRequirement`(extra=ignore), `gap_analysis_agent.py`(needs_rerun), `main.py`(응답 surface)

---

## 3. 백엔드 담당자와

- [ ] **영속성(episodic memory)**: 현재 `episodic_memory`를 요청 본문에 받으면 반영하지만 **저장하지 않는다.** DB(SQLite/MySQL)의 `last_roadmap` / `weekly_progress` 테이블 R/W를 누가 구현? (docs/06 §6 스키마)
- [ ] **`user_id` / `session_id`**: `Agent3State`에서 **제외**(단독 실행용)했다. 사용자 식별·메모리 조회 키를 백엔드가 주입할지, State에 다시 넣을지
- [ ] **`/progress` 엔드포인트**: 미구현(주차 완료 체크박스). 진척 기록 → 다음 로드맵 반영 루프. 누가 구현? (docs/06 §7-4)
- [ ] **서비스 경계**: Agent3가 **독립 FastAPI(:8003)**. 백엔드가 모듈 import할지 / 별도 서비스 HTTP 호출할지 / 포트·CORS·인증 정책
- [ ] **시크릿 관리**: 로컬 `agent3/.env`의 `UPSTAGE_API_KEY` → 배포 환경 키 주입 방식
- [ ] **`weekly_hours` 출처**: 현재 요청에 직접 받음. 온보딩 입력의 어느 단계에서 전달되는지

> 코드 위치: `state.py::Agent3State`, `main.py`(엔드포인트·`Agent3Request`)

---

## 4. 통합(전체 LangGraph) 차원에서

- [ ] **State 통합**: `Agent3State`는 docs의 `CareerMateState`의 **부분집합**(triage/clarify 필드 없음). 전체 그래프 합칠 때 단일 State로 통일 — 필드명 정합
- [ ] **루프 카운터 증가 위치(CANON E)**: 단독 실행에선 `main.py` orchestrator가 `revision_count++`/`rerun_count++`를 담당한다. 전체 그래프에선 **conditional edge**가 담당 → **중복 증가 방지** 정리 필요
- [ ] **trace 포맷**: `TraceEntry`로 통일. 에이전트1·2·라우터도 **동일 trace 포맷**을 써야 대시보드 "why-this-path" 타임라인이 일관됨
- [ ] **노드 시그니처**: Agent3는 `state -> state`(async/sync 혼재). LangGraph 노드 규약과 맞추기

---

## 현재 입출력 계약 (참고)

### 입력 — `POST /agent3/roadmap`
```json
{
  "profile":         { "...": "에이전트1 ProfileDiagnosis" },
  "job_requirement": { "...": "에이전트2 JobRequirement (extra 필드 무시)" },
  "weekly_hours":    8,
  "episodic_memory": null,     // 선택 — 있으면 반영(저장은 안 함)
  "rerun_count":     0         // 되먹임 가드용
}
```

### 출력 — `Agent3Response`

아래는 **실제 호출 응답**(프론트엔드 지망, 주 8시간)을 가독성을 위해 일부 주차/자원만 남긴 것입니다.
**전체 응답**은 [examples/sample_response.json](examples/sample_response.json)을 참고하세요.

```json
{
  "final_output": {
    "profile": {
      "summary": "JavaScript 기초를 보유했으나 프레임워크 실무 경험이 없습니다.",
      "strengths": ["JavaScript", "HTML/CSS"],
      "weaknesses": ["React", "TypeScript"],
      "interests": ["프론트엔드 개발"],
      "readiness_level": "mid",
      "evidence": { "JavaScript": "owned_skills에 명시" }
    },
    "gap_analysis": {
      "gaps": [
        { "skill": "React", "priority": "high", "current_level": "없음",
          "target_level": "실무", "skill_status": "known", "verified": true },
        { "skill": "TypeScript", "priority": "high", "current_level": "없음",
          "target_level": "실무", "skill_status": "known", "verified": true },
        { "skill": "상태관리", "priority": "medium", "current_level": "없음",
          "target_level": "실무", "skill_status": "known", "verified": true }
      ],
      "job_evidence_strength": "strong",
      "needs_rerun": false,
      "rerun_reason": null
    },
    "roadmap": {
      "horizon": "weeks_8",
      "total_weeks": 8,
      "weekly_hours_budget": 8,
      "rationale": "React와 TypeScript는 JavaScript 기초가 필요하며, 상태관리는 React 이해가 필요합니다. 주 8시간 기준 8주에 배치했습니다.",
      "weeks": [
        {
          "week_index": 1,
          "objectives": ["JavaScript 기초 문법 학습"],
          "covered_skills": ["JavaScript"],
          "planned_hours": 8,
          "tasks": [
            {
              "title": "JavaScript 기초 문법 학습",
              "skill": "JavaScript",
              "est_hours": 8,
              "verified": true,
              "resources": [
                {
                  "title": "MDN: JavaScript 가이드",
                  "url": "https://developer.mozilla.org/ko/docs/Web/JavaScript/Guide",
                  "type": "doc",
                  "verified": true,
                  "origin": "db",
                  "source_url": null
                }
              ]
            }
          ]
        }
        /* ... week 2~8 생략 (JavaScript→React→TypeScript→상태관리 순) ... */
      ]
    },
    "verified": true,
    "search_degraded": false,
    "disclaimer": "이 로드맵은 학습 방향 제안이며 합격이나 진로를 보장하지 않습니다.",
    "trace_summary": [
      { "node": "progress_reconciliation", "decision": "skip_reconcile",
        "tool_called": null, "output_summary": "이월/완료 컨텍스트 없음", "ts": "..." },
      { "node": "gap_analysis", "decision": "skip_rerun", "tool_called": "lookup_skill",
        "output_summary": "gaps=[React(high), TypeScript(high), 상태관리(medium)], needs_rerun=False, verified=True, search_count=0", "ts": "..." },
      { "node": "roadmap_plan", "decision": null, "tool_called": "lookup_skill",
        "output_summary": "horizon=weeks_8, weeks=8, verified=True", "ts": "..." },
      { "node": "roadmap_critic", "decision": "pass", "tool_called": null,
        "output_summary": "verdict=pass, violations=[위반 없음]", "ts": "..." },
      { "node": "finalize", "decision": null, "tool_called": null,
        "output_summary": "FinalOutput 조립 완료, weeks=8", "ts": "..." }
    ]
  },
  "needs_rerun": false,        // true면 통합 그래프가 에이전트2 재실행 필요
  "rerun_reason": null
}
```

#### 소비자가 알아둘 핵심 필드

| 필드 | 의미 |
|------|------|
| `gap_analysis.gaps[].skill_status` / `verified` | `known`=스킬DB 검증, `unknown`=DB에 없음 |
| `roadmap.weeks[].tasks[].resources[].origin` | `db`(스킬DB) / `web`(검색 보강) / `llm`(미검증) |
| `final_output.verified` | 미검증(llm origin) 자원이 섞이면 `false` |
| `final_output.search_degraded` | 검색 실패/상한 초과 시 `true` (disclaimer에 반영) |
| `trace_summary[].decision` | 분기 결정(`pass`/`revise`/`rerun_job`/`skip_rerun`…) → "why-this-path" 타임라인 |
| `needs_rerun` (최상위) | `true`면 통합 그래프가 에이전트2 재호출 필요 |

---

## UI 로드맵 카드 연동 (`roadmap.phases`)

대시보드의 **"8주 커리어 로드맵" 카드**는 `roadmap.phases`로 그립니다. `phases`는 **항상 정확히 4개 카드**이며,
주차를 균등 분할합니다(8주 → 2·2·2·2). 제목은 표준 4단계
(기초 다지기 / 핵심 역량 강화 / 프로젝트 실전 / 포트폴리오 & 준비)입니다.

> **중요**: Agent3는 **구조만** 보냅니다. 체크박스 `completed`와 진행률 `%`는 **넣지 않습니다**
> (사용자 런타임 상태 → 백엔드 소유). 대신 각 항목에 안정 키 `id`를 주어 백엔드가 완료 상태를 매핑합니다.
>
> 보유 스킬(profile.strengths)은 재학습하지 않습니다 — 아래 `JavaScript 짧은 복습(2h)`처럼 가벼운 복습만.

### Agent3가 보내는 값 (실제 생성 결과, 1단계 카드 발췌)

```json
"phases": [
  {
    "index": 1,
    "title": "기초 다지기",
    "week_from": 1,
    "week_to": 2,
    "items": [
      {
        "id": "p1-i1",
        "label": "JavaScript 짧은 복습",     // 보유 스킬 → 짧은 복습(2h)만
        "skill": "JavaScript",
        "est_hours": 2,
        "resources": [
          { "title": "MDN: JavaScript 가이드", "url": "https://developer.mozilla.org/ko/docs/Web/JavaScript/Guide",
            "type": "doc", "verified": true, "origin": "db", "source_url": null }
        ]
      },
      { "id": "p1-i2", "label": "React 기초 학습",      "skill": "React",      "est_hours": 8, "resources": [ /* React 공식문서 */ ] },
      { "id": "p1-i3", "label": "React 심화 학습",      "skill": "React",      "est_hours": 3, "resources": [ /* ... */ ] },
      { "id": "p1-i4", "label": "TypeScript 기초 학습", "skill": "TypeScript", "est_hours": 3, "resources": [ /* ... */ ] }
    ]
  }
  /* [2] "핵심 역량 강화" (3-4주), [3] "프로젝트 실전" (5-6주),
     [4] "포트폴리오 & 준비" (7-8주) ... 전체는 examples/sample_roadmap_phases.json */
]
```

> ✅ **4카드 고정**: `phases`는 항상 4개, 8주면 **2·2·2·2 균등 분할**됩니다(`llm.build_phases`).
> 주차가 4 미만이면 주차 수만큼만 카드가 나옵니다(희귀).
> 전체 응답: [examples/sample_roadmap_phases.json](examples/sample_roadmap_phases.json)

### 백엔드가 진행상태를 머지한 뒤 (화면이 받는 형태)

백엔드가 `item id → completed`를 저장하고 끼워 넣어 진행률을 계산합니다(1단계 75% 예시):

```json
{
  "index": 1, "title": "기초 다지기", "week_from": 1, "week_to": 2,
  "progress": 0.75,                       // 백엔드 계산: 완료 3 / 전체 4
  "items": [
    { "id": "p1-i1", "label": "필수 개념 학습",        "completed": true  },
    { "id": "p1-i2", "label": "개발 환경 세팅",        "completed": true  },
    { "id": "p1-i3", "label": "기초 프로젝트 기획",    "completed": true  },
    { "id": "p1-i4", "label": "자료구조/알고리즘 복습", "completed": false }
  ]
}
```

### 필드 책임 경계

| 필드 | 누가 |
|------|------|
| `phases[].title` (단계명) | **Agent3** (LLM) |
| `week_from/to`, `items[].id` / `label` / `skill` / `resources` / `est_hours` | **Agent3** |
| `items[].completed` | **백엔드** (체크박스 저장) |
| `phases[].progress`, 전체 진행률 % | **백엔드/프론트** (완료수 / 전체수) |

---

## 협의 우선순위 제안

1. **에이전트2 `keywords`/`evidence_strength` 계약** — Agent3 품질에 직접 영향 (가장 시급)
2. **백엔드 영속성 + `user_id`** — 재방문 시나리오 실동작에 필요
3. **에이전트1 입도 합의** — 강점 제외 로직 정확도
4. **통합 그래프 State/카운터 통일** — 에이전트1 완성 후
