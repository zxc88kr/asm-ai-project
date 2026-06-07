# 협업 가이드

## 기본 흐름

1. GitHub Issue를 생성해 작업 단위를 정합니다.
2. `feature/작업명`, `docs/작업명`, `fix/작업명` 형식으로 브랜치를 만듭니다.
3. 작업 후 Pull Request를 열고 팀원 리뷰를 받습니다.
4. `main` 브랜치는 항상 실행 가능한 상태로 유지합니다.

## 커밋 메시지 예시

- `docs: add project proposal draft`
- `feat: add initial rag pipeline`
- `fix: handle empty user query`
- `chore: update docker compose config`

## PR 체크리스트

- [ ] 변경 목적이 PR 설명에 적혀 있습니다.
- [ ] 로컬에서 실행 또는 테스트했습니다.
- [ ] 민감 정보가 커밋되지 않았습니다.
- [ ] 문서 업데이트가 필요한 경우 반영했습니다.

