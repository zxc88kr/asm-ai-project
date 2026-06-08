# Workflow

## Issue and Branches

- Create or identify a GitHub Issue before starting substantive work.
- Create branches as `<prefix>/<issue-num>`.

Examples:

```text
feat/12
fix/24
docs/31
refactor/42
```

Recommended prefixes:

| Prefix | Purpose |
| --- | --- |
| `feat` | Feature work |
| `fix` | Bug fixes |
| `docs` | Documentation changes |
| `refactor` | Code structure changes without behavior changes |
| `test` | Test additions or updates |
| `chore` | Tooling, build, or maintenance work |

## PR Target

- Open frontend implementation PRs in this repository.
- If a frontend change requires backend or shared-contract work, mention that in the PR.
- Document shared game rules, API contract drafts, and cross-repo decisions in the parent `the-demo-day-incident` repository before finalizing implementation details here.

## Commit Style

Use Conventional Commits with Korean summaries:

```text
<type>: <한국어 요약>
```

Examples:

```text
feat: 단서 상세 화면 추가
fix: 인물 카드 선택 상태 오류 수정
docs: 프론트엔드 실행 방법 추가
refactor: 조사 화면 컴포넌트 분리
test: 단서 필터링 테스트 추가
chore: 프론트엔드 빌드 설정 추가
```

If a commit body is needed, explain why the change is needed.

## PR Style

- Use Korean PR titles with the same Conventional Commits format.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for the PR body.
- Link the related issue with `Closes #<issue-num>` when the PR resolves it.
