# 2026-06-04 — CharacterChatGraph MVP 구현

- Date: 2026-06-04
- GitHub Issue: None
- Status: Draft

## Goal

`ai-agent-plan/02-character-chat-graph-mvp.md` 기준으로 CharacterChatGraph가 fake adapter와 fake LLM으로 독립 실행/테스트 가능한 MVP 흐름을 갖추게 한다.

## Non-goals

- API route와 response schema는 변경하지 않는다.
- 실제 OpenAI/LangGraph dependency를 추가하지 않는다.
- DB adapter 구현은 직접 연결하지 않는다.
- ARIA 단서 설명과 추리 판정은 변경하지 않는다.

## Context / Constraints

- Python 3.9 환경이므로 PEP 604 union syntax는 사용하지 않는다.
- `main.py`에 구현을 추가하지 않는다.
- Graph는 adapter와 LLM callable을 주입받아 테스트할 수 있어야 한다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m py_compile agents/adapters.py agents/guard.py agents/types.py agents/graphs/character_chat.py agents/prompts/templates.py tests/test_character_chat_graph.py`
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m unittest tests/test_character_chat_graph.py`
- **Expected output:**
  - Compile succeeds.
  - Unit tests pass.

## Risks & Rollback

- **Risks:**
  - Adapter placeholder는 실제 API 연결 전까지 직접 호출하면 `NotImplementedError`가 난다.
  - 간단한 keyword spoiler guard는 완전한 안전장치가 아니다.
- **Rollback steps:** CharacterChatGraph 관련 변경과 테스트 파일을 revert한다.

## Open Questions

- 실제 LLM provider 연결은 다음 PR에서 할지, adapter 구현과 같이 할지 결정이 필요하다.
