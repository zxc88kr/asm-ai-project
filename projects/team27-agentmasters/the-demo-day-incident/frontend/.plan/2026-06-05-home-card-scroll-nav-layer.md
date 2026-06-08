# 2026-06-05 — 홈 카드 스크롤 및 하단 탭 레이어 수정

- Date: 2026-06-05
- GitHub Issue: None
- Status: Draft

## Goal

홈 탭의 단서/인물 카드 목록을 마우스 휠 기반 가로 스크롤로 변경하고, 노트 탭 요소가 하단 탭 네비게이션보다 위에 표시되는 레이어 문제를 수정한다.

## Non-goals

- 게임 진행 로직, 단서/인물 해금 규칙 변경
- API 계약 또는 mock backend store 변경
- 화면 레이아웃 전반 리디자인
- 신규 테스트 도구 또는 의존성 추가

## Context / Constraints

- `GamePrototype.tsx`는 모바일 프레임 기반의 조사 UI를 한 파일에서 관리한다.
- 모바일 터치 환경에서는 `overflow-x-auto` 기본 동작만으로 가로 스크롤이 가능하다.
- 데스크톱/마우스 환경에서는 카드 줄 위에서 휠 입력을 가로 스크롤로 변환하는 편이 드래그 방식보다 단순하다.
- 노트 탭의 ARIA 입력 폼은 `z-10`을 사용하고, 하단 탭 네비게이션은 기존에 명시적 `z-index`가 없어 겹침 우선순위 문제가 발생할 수 있었다.

## Approach (Checklist)

- [x] **Step 0: Recon** (Inspect existing code, locate files)
  - `GamePrototype.tsx`의 `HorizontalScrollRow`, `BottomNav`, 노트 탭 ARIA 입력 폼 레이어 구조를 확인했다.
- [x] **Step 1: Implementation** (Code changes, file paths)
  - `src/components/GamePrototype.tsx`
  - `HorizontalScrollRow`에서 포인터 드래그 상태 관리와 pointer event 핸들러를 제거했다.
  - `onWheel` 핸들러를 추가해 세로 휠 입력을 카드 목록의 가로 스크롤로 변환했다.
  - 스크롤 가능한 범위 안에서만 `preventDefault()`를 호출해 좌우 끝에서는 기본 페이지 스크롤이 막히지 않도록 했다.
  - `BottomNav`에 `z-40`을 추가해 노트 탭 내부 `z-10` 요소보다 높은 레이어에 표시되도록 했다.
- [ ] **Step 2: Tests** (Unit tests, manual verification steps)
  - 린트 실행을 시도했지만 현재 환경에서 `eslint` 실행 파일을 찾지 못해 실패했다.
  - 수동 확인 필요: 홈 탭 단서/인물 카드 줄에서 마우스 휠 가로 스크롤 동작.
  - 수동 확인 필요: 노트 탭에서 하단 `[홈/단서/인물/노트]` 네비게이션이 입력 폼보다 위에 표시되는지 확인.
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)
  - feature flag나 migration 없음.
  - 문제 발생 시 `GamePrototype.tsx` 변경분을 revert하면 이전 드래그 방식과 기존 레이어로 복구된다.

## Validation

- **Commands to run:**
  - `npm.cmd run lint -- --file src/components/GamePrototype.tsx`
- **Expected output:**
  - ESLint 통과.
- **Actual output:**
  - 현재 로컬 환경에서 `'eslint' is not recognized as an internal or external command` 오류로 실패.

## Risks & Rollback

- **Risks:**
  - 마우스 휠 입력이 카드 줄에서 가로 스크롤로 변환되므로, 사용자가 해당 영역에서 세로 페이지 스크롤을 기대할 때 체감이 달라질 수 있다.
  - 트랙패드처럼 `deltaX`와 `deltaY`가 함께 들어오는 입력 장치에서는 더 큰 delta 값을 기준으로 스크롤 방향을 결정한다.
- **Rollback steps:**
  - `git revert <commit-sha>`
  - 또는 `HorizontalScrollRow`의 `onWheel` 변경과 `BottomNav`의 `z-40` 추가를 되돌린다.

## Open Questions

- 관련 GitHub Issue 번호가 있으면 PR 본문에 `Closes #<issue-num>`로 연결해야 한다.

## Merge 문서

### PR Title

```text
fix: 홈 카드 스크롤과 하단 탭 레이어 수정
```

### PR Body

```markdown
## 작업 내용
- 홈 탭 단서/인물 카드 목록의 마우스 드래그 스크롤 로직을 제거하고 휠 기반 가로 스크롤로 변경했습니다.
- 카드 목록이 좌우 끝에 도달한 경우 기본 페이지 스크롤이 막히지 않도록 처리했습니다.
- 노트 탭 내부 요소가 하단 `[홈/단서/인물/노트]` 네비게이션보다 위에 표시되지 않도록 하단 탭에 `z-40`을 추가했습니다.

## 관련 이슈
- Closes #<issue-num>

## 확인 방법
- 홈 탭에서 단서/인물 카드 목록 위에 마우스를 올리고 휠을 움직였을 때 카드가 가로로 스크롤되는지 확인합니다.
- 모바일 터치 환경에서 단서/인물 카드 목록이 기존처럼 손가락으로 가로 스크롤되는지 확인합니다.
- 노트 탭에서 ARIA 입력 영역을 스크롤해도 하단 `[홈/단서/인물/노트]` 네비게이션이 가장 위에 표시되는지 확인합니다.
- `npm.cmd run lint -- --file src/components/GamePrototype.tsx`

## 참고 사항
- 현재 로컬 환경에서는 `eslint` 실행 파일을 찾지 못해 린트 명령이 실패했습니다.
- 관련 이슈 번호가 없으면 `Closes #<issue-num>` 항목을 `- 없음`으로 교체하면 됩니다.
```
