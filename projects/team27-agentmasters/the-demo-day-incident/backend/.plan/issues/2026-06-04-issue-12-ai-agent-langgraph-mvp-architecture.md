# 2026-06-04 — AI Agent LangGraph MVP 구조 구현

- Date: 2026-06-04
- GitHub Issue: #12
- Status: Draft

## Goal

`main.py`에 Agent 코드를 몰아넣지 않고, AI Agent/LangGraph MVP 구현을 위한 최소 `agents/` 패키지 구조를 추가한다.

## Non-goals

- 기존 API 명세, endpoint path, response schema는 변경하지 않는다.
- DB 모델과 세션 상태 저장 구현은 변경하지 않는다.
- 실제 LangGraph dependency 추가나 LLM API 호출은 이번 단계에서 강제하지 않는다.
- 운영용 tool log 저장소는 만들지 않는다.

## Context / Constraints

- 작업 범위는 `ai-agent-plan/01-agent-langgraph-mvp-architecture.md`에 맞춘다.
- 2일 MVP 기준으로 과한 폴더 분리 없이 `graphs/`, `prompts/`, `adapters.py`, `guard.py`, `types.py` 정도만 둔다.
- Graph는 fake adapter로 단위 테스트가 가능해야 한다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m py_compile agents/__init__.py agents/adapters.py agents/guard.py agents/types.py agents/graphs/*.py agents/prompts/*.py`
- **Expected output:**
  - Python compile succeeds with no output.

## Risks & Rollback

- **Risks:**
  - 실제 DB adapter 구현이 없으므로 endpoint에 바로 연결하면 `NotImplementedError`가 발생할 수 있다.
  - Python 3.9 환경에서는 `X | Y` union syntax를 피해야 한다.
- **Rollback steps:** `git revert` 또는 `agents/` 패키지 삭제.

## Open Questions

- LangGraph dependency를 다음 구현 이슈에서 추가할지, 함수형 runner로 먼저 갈지 결정이 필요하다.
