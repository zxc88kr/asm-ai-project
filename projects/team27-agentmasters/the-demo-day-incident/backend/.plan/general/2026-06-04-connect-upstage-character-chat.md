# 2026-06-04 — Upstage CharacterChatGraph 연결

- Date: 2026-06-04
- GitHub Issue: None
- Status: Draft

## Goal

`POST /api/characters/{character_id}/messages`에서 CharacterChatGraph를 실행하고, adapter를 기존 DB/정적 데이터/Upstage LLM 호출에 연결한다.

## Non-goals

- API path와 response schema는 변경하지 않는다.
- DB schema migration은 하지 않는다.
- 세션별 상태 저장은 구현하지 않는다.
- 외부 패키지를 새로 설치하지 않는다.

## Context / Constraints

- 현재 API와 SQLAlchemy session은 동기 방식이다.
- 현재 DB 모델에는 `unlocked`가 없다.
- `.env`는 gitignore에 포함되어 있으며, 키 값은 출력하지 않는다.
- Upstage 호출은 표준 라이브러리 HTTP client로 구현한다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m py_compile main.py agents/*.py agents/graphs/*.py agents/prompts/*.py tests/test_character_chat_graph.py`
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m unittest tests/test_character_chat_graph.py`
- **Expected output:**
  - Compile succeeds.
  - Existing CharacterChatGraph tests pass.

## Risks & Rollback

- **Risks:**
  - Upstage API key가 없거나 네트워크가 막혀 있으면 character message API가 실패한다.
  - DB schema 한계로 세션별 unlock을 정확히 반영하지 못한다.
- **Rollback steps:** `main.py`의 character message endpoint를 이전 더미 응답으로 되돌리고 adapter 연결 변경을 revert한다.

## Open Questions

- 세션별 진행도 컬럼을 후속 이슈에서 추가할지 결정이 필요하다.
