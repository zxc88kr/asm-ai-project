# Agent Instructions

## Repository Scope

This parent repository manages shared project documentation for `The Demo Day Incident`.

Use this repo for:
- Game planning, scenario structure, core rules, and shared decisions
- API contract drafts and data model agreements
- Frontend/backend interface decisions
- Meeting notes, collaboration rules, and cross-repo documentation

Do not place frontend or backend implementation details here unless they are part of a shared contract or decision.

## Related Repositories

- `frontend`: client screens, interactions, frontend state, accessibility, responsive UI
- `backend`: API, data models, game progression logic, server infrastructure

When a change affects implementation in one child repo, make the code change in that repo. When it affects shared rules or contracts, document the decision here first.

## Workflow

- Follow `.agents/docs/WORKFLOW.md` for issue, branch, commit, and PR rules.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for PR bodies.
- For non-trivial implementation or documentation work, use the local `.agents/writing-plan` skill to create a plan under `.plan/` before editing.

## Editing Guidance

- Keep shared docs concise and decision-oriented.
- Prefer updating existing docs over creating new files when the topic already has a home.
- If an API or game-rule change affects both frontend and backend, call out the affected repo work explicitly.
- Preserve existing Korean terminology unless there is a clear reason to change it.
