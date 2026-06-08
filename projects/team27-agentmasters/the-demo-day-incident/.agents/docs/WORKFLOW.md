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
| `refactor` | Code or document structure changes without behavior changes |
| `test` | Test additions or updates |
| `chore` | Tooling, build, or maintenance work |

## PR Target

- Open PRs in the repo that owns the changed behavior.
- Use this parent repo for shared planning, rules, contracts, and cross-repo decisions.
- Use `frontend` for client implementation work.
- Use `backend` for server implementation work.

## Commit Style

Use Conventional Commits with Korean summaries:

```text
<type>: <한국어 요약>
```

Examples:

```text
feat: 단서 목록 화면 추가
fix: 증거 선택 시 잘못된 상태가 저장되는 문제 수정
docs: 협업 규칙 문서화
refactor: 게임 진행 상태 계산 로직 분리
test: 추리 결과 판정 테스트 추가
chore: 린트 설정 추가
```

If a commit body is needed, focus on why the change was made.

## PR Style

- Use Korean PR titles with the same Conventional Commits format.
- Use `.github/PULL_REQUEST_TEMPLATE.md` for the PR body.
- Link the related issue with `Closes #<issue-num>` when the PR resolves it.
