# 2026-06-06 — 증거 카드와 추리 제출 UX 개선

- Date: 2026-06-06
- GitHub Issue: swmaestro-ai-27/the-demo-day-incident#7
- Status: Draft

## Goal

`The Demo Day Incident - 시나리오 고도화` 이슈의 단서/추리 플레이 구조에 맞춰 증거 카드 열람, 7번 단서 해금, 추리 제출 후보 노출, 하단 네비게이션 가림 문제를 개선한다.

## Non-goals

- 백엔드 API 계약 변경
- 신규 시나리오/게임 룰 추가
- 7번 단서 번역 효과의 별도 상태/타이머 기반 구현

## Context / Constraints

- 프론트 구현 PR은 `frontend` 저장소에 생성한다.
- 관련 시나리오 이슈는 상위 repo `swmaestro-ai-27/the-demo-day-incident#7`이다.
- 7번 단서 해금 횟수와 판정은 `mockBackendStore`에 유지한다.
- 증거 카드 출력 효과는 `displayedText`에서 파생 계산하는 방식으로 유지해 `ClueModal` 상태 복잡도를 늘리지 않는다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
  - `src/components/GamePrototype.tsx`
  - `src/app/globals.css`
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
  - `npm.cmd run lint`
  - `npm.cmd run build`
- [ ] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation

- **Commands to run:**
  - `npm.cmd run lint`
  - `npm.cmd run build`
- **Expected output:**
  - ESLint passes without errors.
  - Next.js production build completes successfully.

## Risks & Rollback

- **Risks:**
  - 7번 단서의 한글 치환 표현이 사용자 기대와 다를 수 있다.
  - 전역 스크롤바 숨김이 일부 브라우저에서 스크롤 가능 여부를 덜 명확하게 만들 수 있다.
- **Rollback steps:** 
  - PR 단위로 revert한다.
  - 필요 시 `RecoveredTraceDescription` 분기만 제거해 7번 단서를 영어 원문 출력으로 되돌린다.

## Open Questions

- 없음.
