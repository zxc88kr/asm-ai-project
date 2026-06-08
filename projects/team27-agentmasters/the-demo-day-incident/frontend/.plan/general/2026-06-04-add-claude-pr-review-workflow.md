# 2026-06-04 — Claude PR 리뷰 워크플로 추가

- Date: 2026-06-04
- GitHub Issue: #4
- Status: Draft

## Goal

프론트엔드 PR 생성/업데이트 시 Claude Code가 자동으로 코드 리뷰를 남기도록 GitHub Actions workflow를 추가한다.

## Non-goals

- PR 자동 수정/커밋
- secret 값 변경
- 기존 빌드/테스트 workflow 추가

## Context / Constraints

- repo secret `CLAUDE_CODE_OAUTH_TOKEN`을 사용한다.
- 공식 `anthropics/claude-code-action@v1`를 사용한다.
- PR 리뷰 코멘트 작성을 위해 `pull-requests: write` 권한이 필요하다.
- Claude Code action의 GitHub App/OIDC token setup을 위해 `id-token: write` 권한이 필요하다.
- Claude GitHub App이 설치되지 않은 repo에서도 동작하도록 workflow `GITHUB_TOKEN`을 action에 전달한다.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation
- **Commands to run:**
  - `git -C frontend diff -- .github/workflows`
- **Expected output:**
  - `frontend/.github/workflows/claude-pr-review.yml` 추가
  - secret은 `${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`로만 참조

## Risks & Rollback
- **Risks:**
  - PR마다 Actions minutes와 Claude usage 발생
  - fork PR에서는 secret/OIDC 정책상 실행 제한 가능
- **Rollback steps:** workflow 파일 제거

## Open Questions
- None
