# 2026-06-04 — Issue #3 ERD SQLite 적용

- Date: 2026-06-04
- GitHub Issue: None
- Status: Draft

## Goal

parent repo issue #3의 ERD와 API 명세에 맞춰 SQLite 테이블에 `user_id`를 추가하고, 서버 import/create_all로 `sql_app.db`를 생성해 스키마를 확인한다.

## Non-goals

- Alembic migration은 추가하지 않는다.
- 정적 캐릭터/단서 원본 데이터 테이블은 만들지 않는다.
- API response shape 외 확장 기능은 추가하지 않는다.

## Context / Constraints

- ERD 테이블: `clue_state`, `character_state`, `chat_message`.
- 세 테이블 모두 `user_id text NN`이 있다.
- 이슈 #3 명세는 Header `user_id`를 요구한다.
- 현재 `sql_app.db` 파일은 존재하지 않아 새로 생성 가능하다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `PYTHONPYCACHEPREFIX=.pycache-check python3 -m py_compile main.py models.py schemas.py agents/adapters.py`
  - `python3 -c 'import main'`
  - SQLite schema inspection for the three tables.
- **Expected output:**
  - Compile succeeds.
  - `sql_app.db` is created.
  - Each ERD table includes `user_id`.

## Risks & Rollback

- **Risks:**
  - Existing old `sql_app.db` would not be migrated by `create_all`; manual migration or reset would be needed.
- **Rollback steps:** Revert model/API changes and remove generated `sql_app.db`.

## Open Questions

- `user_id` header validation should stay as plain non-empty text or UUID validation should be added later.
