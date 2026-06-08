# Agent Instructions

## Repository Scope

This repository owns the frontend for `The Demo Day Incident`.

Work here for:
- Game screens and player interactions
- Clue, testimony, character, and incident-state presentation
- Backend API integration
- Frontend state management
- Accessibility, responsive UI, and frontend tests

Shared game rules, API contract drafts, and cross-repo decisions belong in the parent `the-demo-day-incident` repository before implementation details are finalized here.

## Workflow

- Follow `.agents/docs/WORKFLOW.md` for issue, branch, commit, and PR rules.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for PR bodies.
- For non-trivial implementation work, use the local `.agents/writing-plan` skill to create a plan under `.plan/` before coding.

## Implementation Guidance

- Build the playable investigation experience directly; avoid landing-page style screens unless specifically requested.
- Keep UI dense enough for investigation work: clear clue lists, readable evidence detail, and predictable navigation.
- Use the backend API contract documented in the parent repo; note contract gaps instead of inventing incompatible shapes silently.
- Add focused tests for state transitions, filtering, API integration, and critical user flows when those areas change.
- Preserve accessibility basics: semantic controls, keyboard access, visible focus states, and responsive layouts.
- Document frontend setup and run instructions in this repo when tooling is added.
