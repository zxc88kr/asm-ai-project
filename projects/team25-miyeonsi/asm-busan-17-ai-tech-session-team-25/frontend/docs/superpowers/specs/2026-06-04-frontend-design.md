# Travel Mate Agent — 프론트엔드 설계안

- **작성일**: 2026-06-04
- **마감**: 2026-06-07 (3일). 백엔드 API 완성 예상 2026-06-06.
- **담당**: 프론트엔드 구현 = 대희 (전권). 에셋(캐릭터 표정 4종/배경) = 나슬.
- **전략**: 목업 API로 UI 먼저 완성 → 6/6 실제 API 연결(플래그 전환) → 6/7 마무리/연출. 항공권(Amadeus) API는 가장 마지막 스트레치.

---

## 1. 목표와 범위

AI 캐릭터("메이트")와 자유 텍스트로 대화하며 호감도를 쌓고 챕터를 진행해 엔딩에 도달하는 **고전 비주얼 노벨(VN)** 웹 UI를 만든다.

### MVP (반드시)
- 타이틀 → 게임 루프 → 엔딩, 3개 뷰의 완결된 흐름
- 단일 `POST /chat` 턴 루프: 입력 → 응답 → 대사 재생 → 호감도/표정 반영 → 씬 전환
- 자유 텍스트 입력 전용 (`ChatInput`만 존재)
- 목업 API로 백엔드 없이 단독 동작

### 스트레치 (여유되면)
- 항공권 검색 결과 UI (`metadata`의 도구 호출 결과 렌더링)
- 선택지 버튼(SelectionMenu), 사운드, 추가 연출

### 범위 밖 (Non-goals)
- 선택지(SelectionMenu): 분기는 전부 유저 자유 대사 → 백엔드 해석으로 처리. 컴포넌트 만들지 않음.
- 라우터 라이브러리, 로그인/회원, 멀티 세션 관리 UI.

---

## 2. 기술 스택 (기정)

React 18 + TypeScript + Tailwind CSS + Vite + Zustand + Axios. (`frontend/package.json`에 이미 정의됨)

라우팅은 라이브러리 없이 Zustand `view` 상태로 전환한다(뷰 3개라 충분, 번들 가볍게).

---

## 3. 데이터 계약 (백엔드 스키마 정본)

`types/index.ts`는 백엔드 Pydantic 스키마를 **그대로 미러링**한다. 백엔드 `routes.py` 더미는 추후 이 스키마에 맞춰 정렬될 예정(프론트 책임 아님).

```ts
export type EmotionCode = 'idle' | 'smile' | 'sad' | 'surprise';

export interface ChatRequest {
  session_id: string;
  user_message: string;
  current_chapter: number;
  current_affinity: number;
}

export interface TurnResult {
  next_chapter: number | null;   // null/현재값이면 전환 없음
  affinity_delta: number;        // 이번 턴 호감도 증감
  agent_dialogue_list: string[]; // 클릭으로 한 줄씩 재생
  emotion_code: EmotionCode;
  metadata: Record<string, unknown>; // 유동적 추가 정보(도구 결과 등)
}
```

### 합의된 규칙
- **챕터는 정수(number)**.
- **엔딩 판정**: `next_chapter >= 900`이면 엔딩 챕터로 간주 → 엔딩 뷰 전환.
- **씬 전환 판정**: `next_chapter != null && next_chapter !== currentChapter` (그리고 < 900).
- 오프닝 대사는 빈 메시지 API 호출 대신 **프론트 상수로 시드**(백엔드 계약 단순 유지).

---

## 4. 화면 구성 (고전 VN 레이아웃)

풀스크린 배경 + 캐릭터 스프라이트 1인 + 하단 대사 박스 1개 + 하단 입력창 + 상단 호감도 바.

- `views/TitleScreen.tsx` — 타이틀/시작 버튼. 시작 시 `sessionId` 생성 후 게임 진입.
- `views/GameScreen.tsx` — 아래 컴포넌트 조합:
  - `components/game/SceneBackground.tsx` — `currentChapter` → 배경 이미지
  - `components/game/CharacterSprite.tsx` — `emotion` → 표정 이미지(페이드 전환)
  - `components/game/AffinityGauge.tsx` — 상단 ♥ 게이지, `affinity_delta` 애니메이션
  - `components/chat/DialogueBox.tsx` — 현재 대사 1개 타이핑 효과 + `▾` 진행 표시. (README의 `chat/ChatWindow`를 VN 대사 박스로 용도 변경; 스크롤 로그 아님)
  - `components/chat/ChatInput.tsx` — 자유 텍스트 입력. 입력 잠금 중 비활성
- `views/EndingScreen.tsx` — 엔딩 이미지/문구 + 다시하기(`reset`).

`MessageBubble.tsx`는 생성하지 않는다(채팅 로그 UI 아님).

---

## 5. 상태 관리 (`store/useGameStore.ts`)

### 상태
```
sessionId: string
view: 'title' | 'game' | 'ending'
currentChapter: number
affinity: number
emotion: EmotionCode
dialogueQueue: string[]   // 아직 재생 안 한 대사 줄
currentLine: string | null
isLoading: boolean        // API 응답 대기
inputLocked: boolean      // 대사 재생/로딩 중 입력 막기
isTyping: boolean         // 타이핑 효과 진행 중
endingId: number | null   // 도달한 엔딩 챕터 번호
```

### 액션
- `startGame()` — `sessionId = crypto.randomUUID()`, `currentChapter = 1`, `view = 'game'`, 오프닝 대사를 큐에 시드.
- `sendMessage(text)` — `inputLocked = true`, `isLoading = true` → `postChat(req)` →
  응답으로 `affinity += affinity_delta`(게이지 애니메이션), `emotion = emotion_code`,
  `dialogueQueue = agent_dialogue_list`, 첫 줄 재생, 다음 챕터 정보를 보류 상태로 저장.
- `advanceDialogue()` — 다음 줄 pop. 큐가 비면 분기:
  - `next_chapter` 없음/현재와 동일 → `inputLocked = false` (다음 턴)
  - 다름 && `< 900` → 씬 전환(페이드 → `currentChapter` 갱신 → 배경/스프라이트 교체 → 입력 잠금 해제)
  - `>= 900` → `endingId` 설정, `view = 'ending'`
- `reset()` — 상태 초기화 후 타이틀로.

### 턴 흐름 요약
```
입력 전송 → inputLocked+isLoading → POST /chat → TurnResult
 → affinityΔ 게이지 + emotion 스프라이트 → dialogueQueue 재생(클릭으로 한 줄씩)
 → 마지막 줄에서 next_chapter 검사 → (잠금해제 | 씬전환 | 엔딩)
```

---

## 6. 에셋 매핑 (`config/scenes.ts`) — 나슬 연동 지점

- 표정: `emotion_code → /assets/characters/{code}.png` (idle/smile/sad/surprise)
- 배경: `chapter(number) → /assets/backgrounds/...` 매핑 표 + **fallback 이미지**(파일 누락 시 안 깨지게)
- 엔딩(≥900) 배경도 동일 표에서 관리
- 나슬은 `public/assets/characters/`, `public/assets/backgrounds/`에 파일만 채우면 됨

---

## 7. API 추상화 & 목업 전략

- `api/client.ts` — 유일한 통신 진입점 `postChat(req: ChatRequest): Promise<TurnResult>`.
  - `import.meta.env.VITE_USE_MOCK`가 참이면 `api/mock.ts`, 아니면 axios `POST {VITE_API_BASE}/chat`.
  - `VITE_API_BASE` 기본값 `/api` (백엔드 prefix 확정 시 한 곳만 수정).
- `api/mock.ts` — 현재 `routes.py` 더미를 스키마에 맞게 흉내:
  - 키워드로 호감도/표정 변화, 씬 전환 시뮬레이션
  - 입력에 "엔딩" 포함 시 `next_chapter: 900` 반환해 엔딩 흐름 테스트
- **6/6 스왑**: `VITE_USE_MOCK`만 끄면 실제 백엔드 연결. 컴포넌트 코드 변경 0.

---

## 8. 빌드 / 통합 / 정리

- 누락 설정 파일 생성(README상 대희 담당): `index.html`, `vite.config.ts`(`base: './'` + dev 프록시 `/api` → 백엔드), `tsconfig.json`, `tsconfig.node.json`, `postcss.config.js`, `src/index.css`(Tailwind 지시문).
- `src/**/__init__.py` 등 파이썬 잔재 파일 제거.
- 빌드 산출물은 `run_local` 스크립트가 `backend/static`으로 복사(재혁 담당, 자동).
- **모든 프론트 산출물·문서는 `frontend/` 하위에만 생성**(루트 오염 금지).

---

## 9. 테스트 (3일 일정에 비례)

Vitest로 **순수 로직만** 검증, 컴포넌트/비주얼 테스트는 생략:
- `advanceDialogue` 분기(잠금해제 / 씬전환 / 엔딩 ≥900)
- 엔딩/씬 전환 판정 로직
- 에셋 매핑 fallback

---

## 10. 최종 파일 구조

```
frontend/
├── index.html                  # 신규
├── vite.config.ts              # 신규 (base './', dev proxy)
├── tsconfig.json               # 신규
├── tsconfig.node.json          # 신규
├── postcss.config.js           # 신규
├── tailwind.config.js          # 기존
├── package.json                # 기존
├── docs/superpowers/specs/     # 설계/계획 문서
└── src/
    ├── main.tsx
    ├── App.tsx                 # view 라우팅
    ├── index.css               # Tailwind 지시문
    ├── api/
    │   ├── client.ts           # postChat + MOCK 스위치
    │   └── mock.ts             # 가짜 TurnResult
    ├── store/useGameStore.ts   # 전 상태 + 액션
    ├── types/index.ts          # 스키마 미러
    ├── config/scenes.ts        # 챕터/표정 매핑 + fallback
    ├── hooks/useTypewriter.ts  # 타이핑 효과
    ├── views/
    │   ├── TitleScreen.tsx
    │   ├── GameScreen.tsx
    │   └── EndingScreen.tsx
    └── components/
        ├── game/
        │   ├── SceneBackground.tsx
        │   ├── CharacterSprite.tsx
        │   └── AffinityGauge.tsx
        └── chat/
            ├── DialogueBox.tsx   # (구 ChatWindow) VN 대사 박스
            └── ChatInput.tsx
public/assets/                   # 나슬: characters/, backgrounds/
```
```
