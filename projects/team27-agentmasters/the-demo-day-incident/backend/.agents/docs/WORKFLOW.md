# Workflow

## Issues and Branches

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

- Open backend implementation PRs in this repository.
- If a backend change requires frontend or shared-contract work, mention that in the PR.
- Document shared game rules, API contract drafts, and cross-repo decisions in the parent `the-demo-day-incident` repository before finalizing implementation details here.

## Commit Style

Use Conventional Commits with Korean summaries:

```text
<type>: <한국어 요약>
```

Examples:

```text
feat: 단서 조회 API 추가
fix: 추리 결과 판정 조건 오류 수정
docs: 백엔드 실행 방법 추가
refactor: 게임 진행 서비스 분리
test: 사건 상태 변경 테스트 추가
chore: 서버 환경 설정 추가
```

If a commit body is needed, explain why the change is needed.

## PR Style

- Use Korean PR titles with the same Conventional Commits format.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for the PR body.
- Link the related issue with `Closes #<issue-num>` when the PR resolves it.
