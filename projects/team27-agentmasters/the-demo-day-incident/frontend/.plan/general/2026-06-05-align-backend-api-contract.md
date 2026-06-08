# 2026-06-05 백엔드 API 명세에 맞게 게임 API 수정

- Date: 2026-06-05
- GitHub Issue: None
- Status: Draft

## Goal

프론트의 게임 API 호출부를 현재 백엔드 명세에 맞춰 조정한다. 사용자 식별 헤더, 인물 상호작용 경로, 메시지 응답 타입을 백엔드 스키마와 호환되게 맞추고, 현재 Vercel 배포에서 사용하는 프론트 mock API도 단수형 인물 경로를 받을 수 있게 한다.

이번 변경은 실제 FastAPI 백엔드 서버 연결 작업이 아니다. 최종 배포 전에는 Vercel rewrite/proxy 또는 `NEXT_PUBLIC_API_BASE_URL` 기반 호출 방식으로 프론트 요청이 실제 백엔드 서버에 도달하도록 별도 연결 작업이 필요하다.

## Non-goals

- 실제 백엔드 서버 배포 또는 Vercel 프록시 설정 변경
- 프론트 mock API 전체 제거
- ARIA, trace, reset 등 아직 백엔드에 없는 API의 계약 확정
- 게임 진행 규칙이나 UI 동작 변경

## Context / Constraints

- 백엔드는 `user_id: Header()`를 사용하므로 HTTP 요청에서는 `user-id` 헤더가 필요하다.
- 백엔드 인물 상호작용 API는 `POST /api/character/{character_id}` 단수형 경로를 사용한다.
- 인물 메시지 API는 백엔드와 프론트 모두 `GET/POST /api/characters/{character_id}/messages` 복수형 경로를 사용한다.
- 현재 Vercel 배포는 실제 FastAPI 백엔드가 아니라 프론트 repo의 Next.js mock API route를 실행하고 있다.
- 따라서 이번 변경 후에도 Vercel 배포의 `/api/*` 요청은 실제 백엔드가 아니라 프론트 mock API로 처리된다.
- 기존 프론트 mock API는 `x-player-id` 헤더와 `POST /api/characters/{characterId}` 경로를 사용한다.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect existing code, locate files)
  - `src/lib/gameApi.ts`의 공통 요청 헤더, 인물 상호작용 호출, 메시지 타입을 확인했다.
  - `src/app/api/characters/[characterId]/route.ts`와 Vercel 배포의 mock API 경로 동작을 확인했다.
- [x] **Step 1: Implementation** (Code changes, file paths)
  - `src/lib/gameApi.ts`
    - `user-id` 헤더를 추가하고 `x-player-id`는 mock 호환을 위해 유지한다.
    - 인물 상호작용 호출 경로를 `/api/character/{id}`로 변경한다.
    - 백엔드 메시지 응답의 `character_id`, `created_at`, `sender: "me"` 형식을 받을 수 있게 타입과 변환 로직을 보완한다.
  - `src/app/api/character/[characterId]/route.ts`
    - 기존 `src/app/api/characters/[characterId]/route.ts`의 `POST`를 재사용하는 단수형 mock route alias를 추가한다.
- [ ] **Step 2: Tests** (Unit tests, manual verification steps)
  - 로컬 lint 실행을 시도한다.
  - Vercel 또는 로컬 Next API에서 `POST /api/character/{id}`가 기존 mock route와 같은 동작을 하는지 확인한다.
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)
  - feature flag나 migration은 없다.
  - 문제가 생기면 이 커밋을 revert하면 기존 `/api/characters/{id}` 호출 방식으로 돌아간다.

## Validation
- **Commands to run:**
  - `npm.cmd run lint`
  - `curl -i -X POST <frontend-url>/api/character/1 -H "x-player-id: probe" -H "user-id: probe"`
- **Expected output:**
  - ESLint 통과
  - `/api/character/1` 요청이 Next 404가 아니라 mock API JSON 응답을 반환

## Risks & Rollback
- **Risks:**
  - Vercel 배포가 실제 백엔드 프록시로 전환되지 않은 상태에서는 여전히 프론트 mock API가 실행된다.
  - 실제 백엔드 연결이 완료되었다고 오해하면 배포 환경에서 데이터 지속성, 백엔드 DB 연동, 실제 LLM 응답 검증을 놓칠 수 있다.
  - `user-id`와 `x-player-id`를 함께 보내는 과도기 구조가 남아 있어, 최종 백엔드 전환 시 mock 호환 코드를 정리해야 한다.
- **Rollback steps:**
  - `git revert <commit-sha>`
  - 또는 `gameApi.ts`의 인물 상호작용 경로를 `/api/characters/{id}`로 되돌리고 단수형 route alias를 제거한다.

## Open Questions
- frontend repo 이슈를 새로 생성해 브랜치를 `fix/<issue-num>` 규칙에 맞출지 결정이 필요하다.
- 실제 백엔드 배포 URL과 Vercel 연결 방식은 별도 작업에서 정해야 한다.
- 최종 배포 전 실제 백엔드 연결 검증 항목을 별도 이슈/PR로 분리할지 결정이 필요하다.
