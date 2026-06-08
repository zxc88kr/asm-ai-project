# Agent3 구현 현황 (개발 기록)

> CareerMate Agent3(갭 분석 + 로드맵 생성 + 자가 검증) **구현 완료 기록**입니다.
> 팀원이 빠르게 이해할 수 있도록 "무엇을 / 어떻게 / 어디까지" 만들었는지 정리했습니다.
> 설계 배경은 [README.md](README.md), 원본 스펙은 [../docs](../docs)를 참고하세요.

---

## 1. 한눈에 보기

Agent3는 **에이전트1(프로필 진단)·에이전트2(직무 요구역량)의 출력을 입력으로 받아**, 부족 역량을 진단하고 주차별 학습 로드맵을 생성한 뒤 스스로 4종 체크리스트로 검증합니다.

```
[입력] profile(에이전트1) + job_requirement(에이전트2) + weekly_hours
   │
   ▼
progress_reconciliation   재방문자면 직전 로드맵의 완료/미완료 반영
   ▼
gap_analysis              (LLM) 부족 역량 추출 → lookup_skill/web_search로 확정
   ▼                      evidence_strength=weak이면 needs_rerun 신호
roadmap_plan  ⇄  roadmap_critic     (LLM) 로드맵 생성 ↔ 4종 검증 (revise 최대 2회)
   ▼
finalize                  FinalOutput 조립 (verified·disclaimer·trace)
   │
   ▼
[출력] FinalOutput(profile, gap_analysis, roadmap, verified, trace, disclaimer)
```

상태는 `Agent3State` 하나로 흐르며, 각 노드는 필요한 필드만 읽고 씁니다.

---

## 2. 에이전트 역할 분담

| 에이전트 | 노드 | 역할 | 상태 |
|----------|------|------|------|
| 1 | `profile_diagnosis` | 현재 역량 구조화 | 미개발 → 테스트는 `tests/fixtures` 목 사용 |
| 2 | `job_requirement` | 직무 요구역량 추출 | `feat/agent2` 브랜치 (별도) |
| **3** | `gap_analysis` → `roadmap_plan` → `roadmap_critic` | **부족 역량 진단 + 로드맵 + 검증** | ✅ **이 폴더** |

Agent2의 `JobRequirement`는 필드가 많고(`companies`, `postings` 등) `source="duckduckgo"`를 쓰므로, Agent3는 `extra="ignore"`로 **그대로 받아** 핵심 필드만 사용합니다.

---

## 3. 파일 맵

| 파일 | 역할 | LLM |
|------|------|:---:|
| `constants.py` | MAX_RERUN/MAX_REVISIONS/MAX_SEARCH, 금칙어, 기간 캡 | - |
| `models.py` | Pydantic 모델 전체 (입력·툴·출력·FinalOutput) | - |
| `state.py` | `Agent3State`(공유 상태) + `append_trace` | - |
| `skill_db.json` | 정적 스킬 사전 (7직무·53스킬, prereqs·resources·hours, 직무/스킬 별칭 정규화) | - |
| `tools.py` | `lookup_skill`/`normalize_skill_name`/`list_skills_for_role`/`web_search` | - |
| `llm.py` | `extract_gaps`/`generate_roadmap` (Solar) + **규칙기반 폴백** | ✅ |
| `gap_analysis_agent.py` | gap 노드: LLM 추출 + 툴 확정 + needs_rerun | ✅ |
| `roadmap_plan_agent.py` | roadmap 노드: 기간 산출 + 생성 + 자원 보강 (핵심) | ✅ |
| `roadmap_critic.py` | 4종 체크리스트 (전부 코드, 결정론적) | - |
| `main.py` | 오케스트레이션(revise 루프) + finalize + FastAPI | ✅ |
| `tests/` | pytest 42개 (오프라인·결정론) | - |

---

## 4. 두 가지 핵심 장치

### 4-1. 툴 (ReAct: 환각 차단)
- **`lookup_skill`** — 정적 JSON 사전 조회. DB-hit이면 검증된 자원 사용(검색 생략).
- **`web_search`** — DB-miss 스킬만 검색 API(DuckDuckGo, 키 불필요 / Tavily 선택)로 실제 URL 보강.
- 둘 다 **절대 예외를 던지지 않음** — 실패 시 빈/unknown 폴백.

자원 출처는 3단계로 표기됩니다.

| 출처 | verified | origin | 뱃지 |
|------|:--------:|--------|------|
| 스킬DB | ✅ | `db` | 없음 |
| 웹검색 | ✅ | `web` | "웹 출처" |
| LLM 자체지식 | ❌ | `llm` | "검증 안 됨" |

### 4-2. Critic 4종 (Reflexion: 자가 검증)
| # | 검사 | 위반 시 |
|---|------|---------|
| ① uncovered_gap | 모든 갭이 로드맵에 매핑 | revise |
| ② time_budget_exceeded | 각 주차 ≤ weekly_hours | revise |
| ③ prereq_order_violation | **선행의 첫 등장 ≤ 후행의 첫 등장** | revise |
| ④ forbidden_phrase | "합격 가능" 등 금칙 표현 없음 | revise |

위반이 있으면 `roadmap_plan`으로 되돌아가 위반 사유를 주입해 재생성합니다(최대 2회, `revision_count` 가드).

---

## 5. 동작을 보장하는 설계

- **키 없어도 동작**: `UPSTAGE_API_KEY`가 없으면 `llm.py`가 규칙기반 폴백으로 전환. 폴백 패커는 토폴로지 정렬 + 시간예산 분할로 **Critic 4종을 구조적으로 만족**합니다.
- **무한 루프 방지**: `MAX_RERUN=1`(Gap→Job), `MAX_REVISIONS=2`(Critic→Roadmap), `MAX_SEARCH=8`(웹검색).
- **트레이스**: 모든 노드가 `TraceEntry`를 남겨 "why-this-path" 타임라인을 만듭니다.
- **선행 자원 보강**: gap 단계에서 갭 스킬의 **선행(prereq)까지** `skill_records`에 미리 확보해, LLM이 추가한 기초 주차에도 검증 자원이 붙습니다.

---

## 6. 실행 & 테스트

### 환경 준비
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r agent3\requirements.txt
```

### API 키 (선택 — 없으면 폴백)
`agent3\.env.example`을 `agent3\.env`로 복사한 뒤 키 입력:
```
UPSTAGE_API_KEY=...        # Solar LLM (gap/roadmap 품질)
# TAVILY_API_KEY=...       # (선택) 없으면 DuckDuckGo 사용
```
`.env`는 `.gitignore`로 제외되어 커밋되지 않습니다.

### 서버
```powershell
.\.venv\Scripts\python.exe -m uvicorn agent3.main:app --reload --port 8003
```

### 호출 예시
```http
POST http://127.0.0.1:8003/agent3/roadmap
Content-Type: application/json

{
  "profile": { "strengths": ["JavaScript"], "weaknesses": ["React"], "readiness_level": "mid" },
  "job_requirement": { "required_skills": ["React 구현"], "keywords": ["React","TypeScript"], "evidence_strength": "strong" },
  "weekly_hours": 8
}
```
응답: `final_output`(profile·gap_analysis·roadmap·verified·trace·disclaimer) + `needs_rerun`.

> **실제 응답 예시**: [examples/sample_response.json](examples/sample_response.json) (전체) ·
> [INTEGRATION.md](INTEGRATION.md#출력--agent3response) (필드 설명 포함 요약)

### 테스트
```powershell
.\.venv\Scripts\python.exe -m pip install -r agent3\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest agent3\tests -q
```
→ **42 passed** (LLM/네트워크 없이 오프라인·결정론).

---

## 7. 검증 완료 항목

- ✅ 실제 Solar LLM 경로 (gap 추출·로드맵 생성)
- ✅ 규칙 폴백 경로 (키 없이 Critic 4종 만족)
- ✅ web_search 보강 (DB-miss → origin=web, 실제 검색 확인)
- ✅ revise 루프 (종료 보장: pass 또는 2회 소진)
- ✅ episodic memory (이월/완료 반영)
- ✅ FastAPI 엔드포인트 (agent2 풍부 JSON 호환)
- ✅ 스킬 DB 무결성 (참조·DAG)

---

## 8. 알려진 한계 / 향후

- **horizon 라벨**: `RoadmapHorizon`은 4/6/8주 버킷이라, 갭 총량이 많으면(예: 주8h에 77h) **실제 10주**여도 라벨은 `weeks_8`로 근사됩니다. 주간 예산(하드 제약)을 우선하기 때문이며, 필요 시 enum 확장 가능.
- **gap→job 되먹임**: `needs_rerun`은 신호만 surface합니다. 실제 job 재실행은 에이전트2가 외부 입력이므로 **통합 그래프(전체 LangGraph)**에서 연결해야 합니다.
- **에이전트1 연동**: 현재 목 픽스처 사용. 실제 `profile_diagnosis` 완성 시 입력만 교체하면 됩니다.
- **프론트/대시보드**: trace 타임라인 시각화는 미구현(데이터는 `FinalOutput.trace_summary`로 제공).
