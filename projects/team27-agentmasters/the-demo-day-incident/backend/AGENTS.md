# Agent Instructions

## Repository Scope

This repository owns the backend for `The Demo Day Incident`.

Work here for:
- Game progression APIs
- Incident, clue, testimony, character, and case-state data models
- Deduction result evaluation and server-side game logic
- Authentication, persistence, deployment, and server infrastructure
- Backend tests and API implementation details

Shared game rules, API contract drafts, and cross-repo decisions belong in the parent `the-demo-day-incident` repository before implementation details are finalized here.

## Workflow

- Follow `.agents/docs/WORKFLOW.md` for issue, branch, commit, and PR rules.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for PR bodies.
- For non-trivial implementation work, use the local `.agents/writing-plan` skill to create a plan under `.plan/` before coding.

## Implementation Guidance

- Keep API behavior aligned with the shared contract documented in the parent repo.
- Make data model changes explicit and update relevant docs or contract notes.
- Add focused tests for game-state transitions, deduction evaluation, and API behavior when those areas change.
- Avoid frontend concerns in backend code; expose clear API responses instead.
- Document backend setup and run instructions in this repo when tooling is added.
