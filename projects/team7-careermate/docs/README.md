# CareerMate 설계 문서 인덱스 & 설계 철학

이 문서는 `docs/` 폴더 전체의 인덱스로, 각 문서의 역할과 읽는 순서를 안내합니다. CareerMate가 "무엇을 왜 이렇게 만드는가"를 처음 접하는 팀원이 30분 안에 파악할 수 있도록 작성되었습니다.

---

## 왜 이 spec인가 — 핵심 전환

원본 기획(6페이지)은 "세 개의 agent가 **선형적으로** 데이터를 전달"한다고 명시했습니다. 이는 Anthropic이 *Building Effective Agents*에서 분류한 **prompt chaining workflow** — 즉 도구 호출 0, 자율 분기 없음, 자기 검증 없음, 메모리는 1세션 저장에 그치는 고정 파이프라인입니다. 선언문("커리어 코치 역할")과 구현("입력 → 3회 LLM 호출 → 출력")이 어긋난 상태입니다.

이 spec은 그 어긋남을 세 가지 구조 변경으로 메웁니다. **(1) 모호성 라우터 노드**: 온보딩 직후 `ambiguity_score`로 ask/proceed를 분기해 자율 라우팅을 달성합니다. **(2) 스킬·학습자원 DB 조회 툴 + 웹검색 툴**: IT 직무 한정 50~150행 정적 사전을 함수 호출(`lookup_skill`)로 조회하고, DB-miss 또는 공고 부실 시 `web_search`(검색 API 호출, 크롤링 아님)로 실제 URL을 보강해 tool use 0→2, 로드맵 환각을 차단합니다(ReAct, Yao et al. 2022). **(3) 로드맵 Critic/Reflection 루프**: 4종 체크리스트로 로드맵을 자가 검증하고 위반 시 최대 2회 재생성해 reflection + guardrails를 한 노드로 구현합니다(Reflexion, Shinn et al. 2023; Self-Refine, Madaan et al. 2023).

여기에 **Gap→Job 되먹임 엣지**(일방향 파이프라인을 양방향 협업으로), **경량 episodic 메모리**(직전 로드맵+주차 진행 읽기→반영), **실행 트레이스 로그**('why-this-path' 타임라인)를 더해, "데이터를 전달하는 파이프라인"이 "상황에 따라 경로를 바꾸고 스스로 검증하는 에이전트 그래프"로 전환됩니다. 범위는 **1.5주 / IT 직무 1~2개 / 대규모 크롤링·파인튜닝 금지(검색 API 호출은 허용)**로 묶어 일정 내 완료 가능한 수준을 유지합니다.

---

## 3대 개선 요약

| # | 개선 항목 | 해결하는 원본 문제 | 에이전트 요소 | 난이도 |
|---|-----------|-------------------|--------------|--------|
| 1 | **모호성 라우터 노드** (Triage / Clarify-or-Proceed) | 자율 라우팅 부재 — 모든 사용자가 동일 직선 통과 | Autonomous Routing | 낮음 |
| 2 | **스킬·학습자원 DB 조회 툴** (`lookup_skill`) **+ 웹검색 툴** (`web_search`) | Tool Use 0 — 로드맵 강의·링크 LLM 환각. DB-miss·공고 부실 시 실제 URL 보강 불가 | Tool Use (스킬DB + 웹검색) | 중간 |
| 3 | **로드맵 Critic/Reflection 루프** | Reflection·Guardrails 부재 — 시간 초과 로드맵 자동 통과 | Reflection + Guardrails | 낮음 |

추가 보강 (낮은 비용):
- **Gap→Job 되먹임 메시지** — `needs_rerun` 엣지로 일방향→양방향 협업
- **경량 episodic 메모리** — `progress_reconciliation` 노드로 시간축 가치 실증
- **실행 트레이스** — `trace` 리스트로 에이전시(agency)를 발표·평가에서 증명

---

## 1.5주 범위 명시

**해야 할 것:**
- LangGraph 그래프 정의(노드·조건 엣지·State 스키마)
- `lookup_skill` / `list_skills_for_role` / `normalize_skill_name` 툴 함수
- `web_search` 어댑터 (검색 API 1개, 캐시 dict, MAX_SEARCH=8 가드) — 크롤링 아님
- `triage_router` conditional edge (ask / proceed)
- `roadmap_critic` 검증 체크리스트 + 재생성 루프 (max 2회)
- `gap_analysis → job_requirement` 되먹임 엣지 (max 1회)
- `progress_reconciliation` 노드 (returning_user 읽기+반영)
- `trace` append 로직 + `final_output` 조립

**하지 말아야 할 것:**
- 대규모 채용공고 크롤링(사이트 순회·HTML 수집) — 단, 검색 API 호출(쿼리→색인 결과 메타데이터 수신)은 허용(크롤링과 구분)
- 단일 페이지 직접 fetch/HTML 파싱 (1.5주 범위 외)
- 모델 파인튜닝
- IT 직무 범위 과도한 확장(2개 초과)
- 스킬 DB 150행 초과 (MVP 범위)
- 프론트엔드·백엔드 완성도보다 에이전트 그래프 우선

---

## 문서 목록 & 읽는 순서

아래 순서대로 읽으면 "왜→무엇→어떻게" 흐름이 완성됩니다.

| 순서 | 파일 | 한 줄 요약 |
|------|------|-----------|
| 1 | **이 문서** `README.md` | 전체 인덱스 + 설계 철학 (여기서 시작) |
| 2 | [시스템 개요](00-overview.md) | 요구사항·자율성 범위·비기능 요건·폴백 규칙. 프로젝트 목표와 MVP 경계 기술 |
| 3 | [아키텍처](01-architecture.md) | 컴포넌트 책임·인터페이스·State 스키마 개요. 웹검색 API 컴포넌트 포함 상위 구조 |
| 4 | [에이전트 그래프](02-agent-graph.md) | LangGraph 노드·엣지·조건 분기 전체 구조. State TypedDict·Pydantic 모델·trace 규칙 포함 |
| 5 | [에이전트 계약](03-agent-contracts.md) | 각 에이전트 입출력·의사코드·프롬프트 계약. `web_search` 보강 경로·되먹임 엣지 상세 |
| 6 | [툴·스킬DB](04-tools-skill-db.md) | `lookup_skill` / `web_search` 시그니처·계약·폴백 규칙. 스킬 DB JSON 예시·환각차단 트리 |
| 7 | [Critic·Reflection](05-reflection-critic.md) | Critic 4종 체크리스트, `violation_type` enum, `verified` 플래그 전파 규칙, 금칙 표현 목록 |
| 8 | [데이터 모델](06-data-model.md) | Pydantic 모델 전체(CareerMateState·ResourceItem·SearchHit 등), enum, FinalOutput 스키마 |
| 9 | [평가·KPI](07-evaluation-kpi.md) | 7대 KPI 정의·측정 방법, 데모 시나리오, 에이전트 증거표. Tool Hit율·웹 보강율 포함 |
| 10 | [구현 계획](08-implementation-plan.md) | 마일스톤·태스크 분해, 상수(MAX_RERUN/MAX_REVISIONS/MAX_SEARCH), 의사코드 참조 |

> 처음 구현을 시작한다면: **6(툴·스킬DB) → 4(에이전트 그래프) → 5(에이전트 계약) → 8(데이터 모델)** 순서를 권장합니다. 툴 계약과 State 스키마를 먼저 잡아야 노드 구현이 흔들리지 않습니다.

---

## 핵심 용어 빠른 참조

처음 보는 개념이 나오면 아래 용어 설명을 먼저 확인하세요.

| 용어 | 한 줄 풀이 |
|------|-----------|
| `ambiguity_score` | TriageRouter가 온보딩 입력의 모호함을 0.0~1.0으로 자체 산정한 점수. 임계값 초과 시 ask 경로로 분기 |
| `route_decision` (ask\|proceed) | 라우터가 내리는 두 갈래 결정. ask=역질문, proceed=바로 진단 진행 |
| `lookup_skill` | IT 스킬 사전을 함수 호출로 조회. 선행지식·학습자원·표준시간 반환. LLM 환각 방지 |
| `needs_rerun` / 되먹임 | Gap 분석 중 "Job 근거 약함"을 감지하면 Job Agent를 1회 재호출하는 양방향 협업 신호 |
| `critic_verdict` (pass\|revise) | Critic 노드의 판정. revise면 roadmap_plan으로 되돌려 재생성(최대 2회) |
| `violation_type` | Critic이 잡는 위반 종류. 부족역량 미매핑·시간 초과·선후행 위반·금칙 표현 |
| `verified` 플래그 | 정보 출처에 따라 3단계(db/web/llm)로 표시. DB known=verified, 웹검색 URL 보강=verified(web), LLM 순수 자체지식=false → '검증 안 됨' 노출 |
| `episodic_memory` | 재방문 시 직전 로드맵+주차 진행기록을 읽어 다음 계획에 반영하는 경량 기억 |
| `trace` | 각 노드 실행 메타를 append 누적하는 로그. 대시보드 'why-this-path' 타임라인 원본 |
| `progress_reconciliation` | 미완료 주차는 이월, 완료 주차는 진척 반영하는 episodic 메모리 반영 노드 |
| `web_search` | 검색 API(Tavily 또는 Serper)를 호출해 쿼리→SearchHit 리스트를 반환하는 툴. 크롤링 아님. DB-miss 또는 공고 부실 시 실제 URL 보강에 사용 |
| `search_count` | 세션 누적 `web_search` 실제 API 호출 횟수. `MAX_SEARCH=8` 상한 초과 시 빈 리스트 폴백 |
| `search_degraded` | 검색 실패 또는 MAX_SEARCH 초과가 1회라도 발생하면 True. `finalize` 출력의 disclaimer에 반영 |
| `SearchHit` | 검색 결과 1건의 Pydantic 모델. title·url·snippet·source·retrieved_at 포함. url 존재 시 verified=true(web origin) 근거 |

전체 용어집은 [에이전트 계약](03-agent-contracts.md) 및 [데이터 모델](06-data-model.md) 문서를 참조하세요.

---

## 참고 자료

| 자료 | 관련 지점 |
|------|----------|
| Anthropic, *Building Effective Agents* (2024) | workflow vs agent 분류 기준. 라우터·evaluator 패턴 근거 |
| Yao et al., *ReAct* (2022) | 추론+행동 번갈아 수행. `lookup_skill` tool use 제안 근거 |
| Shinn et al., *Reflexion* (2023) | 언어적 self-reflection 루프. `roadmap_critic` 재생성 루프 근거 |
| Madaan et al., *Self-Refine* (2023) | 단일 모델 자기 개선. 경량 reflection 구현(1.5주) 근거 |
| Wang et al., *Plan-and-Solve* (2023) | 하위 과제 분해 후 단계 실행. 동적 로드맵 기간 산출 근거 |
| LangGraph 공식 문서 (LangChain) | conditional edges·Graph State. 라우터·되먹임·재생성 루프 구현 수단 |
