# 2026-06-04 — Claude PR 리뷰 워크플로 추가

- Date: 2026-06-04
- GitHub Issue: None
- Status: Draft

## Goal

각 child repo(`frontend`, `backend`)에 GitHub PR 생성/업데이트 시 Claude Code가 자동으로 리뷰를 남기는 workflow를 추가한다.

## Non-goals

- parent shared-doc repo workflow 변경
- GitHub secret 값 관리 또는 토큰 재발급
- PR 자동 수정/커밋 기능 추가

## Context / Constraints

- 각 repo secret에 `CLAUDE_CODE_OAUTH_TOKEN`이 이미 저장되어 있다.
- 공식 `anthropics/claude-code-action@v1`는 `claude_code_oauth_token` input을 지원한다.
- PR 리뷰에는 `contents: read`, `pull-requests: write` 권한이 필요하다.
- 비용/쿼터 리스크를 줄이기 위해 PR 이벤트 범위와 `--max-turns`를 제한한다.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation
- **Commands to run:**
  - `git -C frontend diff -- .github/workflows`
  - `git -C backend diff -- .github/workflows`
- **Expected output:**
  - 각 repo에 `claude-pr-review.yml` 추가
  - workflow가 `CLAUDE_CODE_OAUTH_TOKEN` secret을 직접 노출하지 않고 참조

## Risks & Rollback
- **Risks:**
  - PR마다 Actions minutes와 Claude usage가 발생한다.
  - 리뷰 결과는 AI 제안이므로 merge 전 사람이 확인해야 한다.
  - fork PR 정책/권한에 따라 secret 접근이 제한될 수 있다.
- **Rollback steps:** workflow 파일을 제거하거나 `pull_request` 트리거를 비활성화한다.

## Open Questions
- None
