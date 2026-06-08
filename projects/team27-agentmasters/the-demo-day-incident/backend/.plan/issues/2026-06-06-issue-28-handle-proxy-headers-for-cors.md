# 2026-06-06 - Nginx Proxy Manager 뒤 CORS 프록시 헤더 처리

- Date: 2026-06-06
- Ticket: #28
- Status: Implemented

## Goal

Make backend CORS behavior work correctly when requests arrive through Nginx Proxy Manager and include proxy headers such as `X-Forwarded-Proto`, `X-Forwarded-Host`, or `Forwarded`.

## Non-goals

- Do not change API contracts.
- Do not broaden CORS to arbitrary origins.
- Do not change frontend behavior.

## Context / Constraints

- Backend uses FastAPI and Starlette `CORSMiddleware`.
- Existing CORS tests cover direct `Origin` allow/disallow and preflight behavior.
- Reverse proxies can pass the public scheme/host through forwarded headers while the app sees an internal upstream URL.
- Docker bridge subnet example uses `172.18.0.0/16`; verify the actual deployment network before rollout.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation
- **Commands run:**
  - `.venv/bin/python -m pytest test_main.py -k "cors or proxy"`
  - `.venv/bin/python -m pytest`
- **Observed output:**
  - Focused CORS/proxy tests: 6 passed, 8 deselected.
  - Full suite: 28 passed, 1 failed (`test_main.py::test_character_chat_with_llm` returned 502 from LLM integration path).

## Risks & Rollback
- **Risks:**
  - Trusting proxy headers too broadly can permit spoofed origins if middleware is ordered incorrectly.
  - Normalizing origins incorrectly can break local development origins.
- **Rollback steps:** `git revert` the PR commit.

## Open Questions
- None.
