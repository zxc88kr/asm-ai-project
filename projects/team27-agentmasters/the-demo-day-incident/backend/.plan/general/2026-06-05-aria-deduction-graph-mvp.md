# 2026-06-05 — ARIA 및 추리 Graph MVP 구현

- Date: 2026-06-05
- GitHub Issue: None
- Status: Draft

## Goal

`ai-agent-plan/03-aria-deduction-graph-mvp.md` 기준으로 ARIA 단서 설명 Graph, nextUnlock helper, DeductionEvaluateGraph를 기존 API에 연결한다.

## Non-goals

- API response shape는 변경하지 않는다.
- ARIA 자유 대화 API는 추가하지 않는다.
- 복잡한 unlock condition engine은 만들지 않는다.
- LLM으로 추리 자연어를 채점하지 않는다.

## Context / Constraints

- 기존 API 명세를 유지한다.
- `user_id` 헤더 기준으로 상태를 분리한다.
- `unlocked` 컬럼이 없으므로 현재 MVP에서는 `interacted`를 공개 상태의 근사값으로 사용한다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m py_compile main.py agents/adapters.py agents/graphs/aria_clue_explain.py agents/graphs/deduction_evaluate.py tests/test_aria_deduction_graph.py`
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m unittest tests/test_aria_deduction_graph.py tests/test_character_chat_graph.py`
- **Expected output:**
  - Compile succeeds.
  - Unit tests pass.

## Risks & Rollback

- **Risks:**
  - `unlocked` 컬럼이 없어 locked/unlocked 구분이 완전하지 않다.
  - API response shape를 유지하므로 ARIA explanation은 외부 응답에 노출하지 않는다.
- **Rollback steps:** Revert Graph/adapter/main changes for this plan.

## Open Questions

- clue 7 해금 조건은 후속 이슈에서 명확히 결정해야 한다.
