# 2026-06-03 — 각 레포 WORKFLOW 문서 위치 정리

- Date: 2026-06-03
- GitHub Issue: #13
- Status: Ready for review

## Goal

Move each repository's root `WORKFLOW.md` into `.agents/docs/WORKFLOW.md` and update `AGENTS.md` links to point to the new location.

## Non-goals

- Do not change workflow rules beyond the link/path update.
- Do not modify frontend or backend implementation code.
- Do not remove unrelated untracked local files.

## Context / Constraints

- Parent, frontend, and backend repositories each have their own `WORKFLOW.md` and `AGENTS.md`.
- Follow each repository's workflow for commit and PR handling.
- Existing untracked `.DS_Store` files should be left untouched.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect repo status, current branches, PR state)
- [x] **Step 1: Implementation** (Move `WORKFLOW.md` under `.agents/docs/` and update `AGENTS.md`)
- [x] **Step 2: Tests** (Verify paths and git diffs)
- [x] **Step 3: Rollout / Rollback** (Commit per repo; open or update PRs as required)

## Validation
- **Commands to run:** `git status --short`, `git diff --stat`, path checks for each repo
- **Expected output:** only intended docs moves/link edits are staged/committed, with unrelated files unmodified

## Risks & Rollback
- **Risks:** accidentally staging unrelated `.DS_Store` files or submodule pointer updates.
- **Rollback steps:** revert the docs commits or move `.agents/docs/WORKFLOW.md` back to root and restore `AGENTS.md` references.

## Open Questions
- None.
