# Travel Mate Agent 프론트엔드 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI 메이트와 자유 텍스트로 대화하며 호감도를 쌓고 챕터를 진행해 엔딩에 도달하는 고전 비주얼 노벨 웹 UI를, 목업 API 위에서 단독 동작하도록 구현한다.

**Architecture:** React + TypeScript + Vite SPA. 단일 `POST /chat` 턴 루프를 Zustand 스토어가 통제하고, 3개 뷰(타이틀/게임/엔딩)를 상태로 라우팅한다. 모든 통신은 `api/client.ts`의 `postChat()` 한 함수로 추상화하고, `VITE_USE_MOCK` 플래그로 목업↔실제 백엔드를 전환한다(6/6 스왑).

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Vite, Zustand, Axios, Vitest.

**참조 스펙:** `frontend/docs/superpowers/specs/2026-06-04-frontend-design.md`

> **공통 규칙**
> - 모든 명령은 `frontend/` 디렉터리 안에서 실행한다 (`cd frontend` 먼저).
> - 모든 산출물은 `frontend/` 하위에만 생성한다 (프로젝트 루트 오염 금지).
> - 테스트는 순수 로직만 (Vitest, `environment: node`). 컴포넌트/비주얼 테스트는 만들지 않는다.
> - 커밋 메시지 푸터에 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` 포함.
> - main에 직접 커밋 금지. 작업 브랜치에서 진행.

---

## 파일 구조 (이 계획이 만들어낼 최종 형태)

```
frontend/
├── index.html                       # Task 1
├── vite.config.ts                   # Task 1
├── tsconfig.json                    # Task 1
├── tsconfig.node.json               # Task 1
├── postcss.config.js                # Task 1
├── package.json                     # Task 1 (수정: vitest 추가)
├── tailwind.config.js               # 기존
└── src/
    ├── main.tsx                     # Task 1
    ├── index.css                    # Task 1
    ├── App.tsx                      # Task 1 (placeholder) → Task 12 (실제 라우팅)
    ├── types/index.ts               # Task 2
    ├── config/scenes.ts             # Task 4
    ├── store/turnLogic.ts           # Task 5
    ├── api/mock.ts                  # Task 6
    ├── api/client.ts                # Task 7
    ├── store/useGameStore.ts        # Task 8
    ├── hooks/useTypewriter.ts       # Task 9
    ├── components/game/SceneBackground.tsx   # Task 10
    ├── components/game/CharacterSprite.tsx   # Task 10
    ├── components/game/AffinityGauge.tsx     # Task 10
    ├── components/chat/DialogueBox.tsx       # Task 11
    ├── components/chat/ChatInput.tsx         # Task 11
    └── views/
        ├── TitleScreen.tsx          # Task 12
        ├── GameScreen.tsx           # Task 12
        └── EndingScreen.tsx         # Task 12
public/assets/                       # Task 14 (나슬: characters/, backgrounds/)
```

---

## Task 1: 빌드 스캐폴딩 & 설정

게임 로직을 짜기 전에, 개발 서버가 뜨고 빌드가 통과하는 최소 React+TS+Vite+Tailwind 골격을 만든다. 테스트 러너(Vitest)도 이 단계에서 추가한다.

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/postcss.config.js`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx` (임시 placeholder)
- Modify: `frontend/package.json` (vitest devDep + test 스크립트)
- Delete: `frontend/src/__init__.py`, `frontend/src/components/chat/__init__.py`, `frontend/src/components/game/__init__.py`

- [ ] **Step 1: 파이썬 잔재 파일 삭제**

Run:
```bash
cd frontend && rm -f src/__init__.py src/components/chat/__init__.py src/components/game/__init__.py
```

- [ ] **Step 2: `index.html` 작성**

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>나만의 여행 메이트</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 3: `vite.config.ts` 작성** (base 상대경로, dev 프록시, vitest 설정 포함)

```ts
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './', // FastAPI static 서빙 시 자산 경로 안전하게
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  test: {
    environment: 'node',
    globals: true,
  },
});
```

- [ ] **Step 4: `tsconfig.json` 작성**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["vite/client", "vitest/globals"]
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 5: `tsconfig.node.json` 작성**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 6: `postcss.config.js` 작성**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 7: `src/index.css` 작성**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body,
#root {
  height: 100%;
  margin: 0;
}
```

- [ ] **Step 8: `src/main.tsx` 작성**

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

- [ ] **Step 9: 임시 `src/App.tsx` 작성** (Task 12에서 실제 라우팅으로 교체)

```tsx
export default function App() {
  return (
    <div className="flex h-full items-center justify-center bg-game-navy-dark text-game-pink">
      ✈️ Travel Mate — scaffolding OK
    </div>
  );
}
```

- [ ] **Step 10: `package.json`에 vitest 추가 + test 스크립트**

`scripts`에 다음 두 줄 추가:
```json
"test": "vitest run",
"test:watch": "vitest"
```
`devDependencies`에 다음 추가:
```json
"vitest": "^1.6.0"
```

- [ ] **Step 11: 의존성 설치**

Run: `cd frontend && npm install`
Expected: 에러 없이 `node_modules` 생성, vitest 포함.

- [ ] **Step 12: 빌드 통과 확인**

Run: `cd frontend && npm run build`
Expected: `tsc && vite build` 성공, `dist/` 생성.

- [ ] **Step 13: 개발 서버 부팅 확인**

Run: `cd frontend && npm run dev`
Expected: Vite가 `http://localhost:5173` 류 주소로 뜨고, 브라우저에 "scaffolding OK" 표시. 확인 후 종료.

- [ ] **Step 14: 커밋**

```bash
cd frontend && git add -A && git commit -m "chore(frontend): scaffold vite+react+ts+tailwind+vitest

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: 타입 정의 (백엔드 스키마 미러)

백엔드 Pydantic 스키마를 그대로 미러링한 타입. 이후 모든 모듈이 이걸 import 한다.

**Files:**
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: `src/types/index.ts` 작성**

```ts
export type EmotionCode = 'idle' | 'smile' | 'sad' | 'surprise';

export interface ChatRequest {
  session_id: string;
  user_message: string;
  current_chapter: number;
  current_affinity: number;
}

export interface TurnResult {
  next_chapter: number | null; // null/현재값이면 전환 없음
  affinity_delta: number;
  agent_dialogue_list: string[];
  emotion_code: EmotionCode;
  metadata: Record<string, unknown>;
}
```

- [ ] **Step 2: 타입 컴파일 확인**

Run: `cd frontend && npx tsc --noEmit`
Expected: 에러 없음.

- [ ] **Step 3: 커밋**

```bash
cd frontend && git add src/types/index.ts && git commit -m "feat(frontend): add TurnResult/ChatRequest types mirroring backend schema

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: 씬/에셋 설정 (config/scenes.ts) — TDD

챕터→배경, 감정→스프라이트 매핑과 엔딩 판정, 상수들. 에셋 파일이 없어도 fallback으로 안전.

**Files:**
- Create: `frontend/src/config/scenes.ts`
- Test: `frontend/src/config/scenes.test.ts`

- [ ] **Step 1: 실패하는 테스트 작성** (`src/config/scenes.test.ts`)

```ts
import { describe, it, expect } from 'vitest';
import { getBackground, getSprite, isEnding } from './scenes';

describe('scenes config', () => {
  it('maps a known chapter to its background', () => {
    expect(getBackground(1)).toBe('/assets/backgrounds/ch1.png');
  });
  it('falls back for an unknown chapter', () => {
    expect(getBackground(42)).toBe('/assets/backgrounds/default.png');
  });
  it('maps an emotion to its sprite path', () => {
    expect(getSprite('smile')).toBe('/assets/characters/smile.png');
  });
  it('detects ending at/above the threshold', () => {
    expect(isEnding(900)).toBe(true);
    expect(isEnding(901)).toBe(true);
  });
  it('is not an ending below threshold or when null', () => {
    expect(isEnding(2)).toBe(false);
    expect(isEnding(null)).toBe(false);
  });
});
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd frontend && npx vitest run src/config/scenes.test.ts`
Expected: FAIL — `./scenes` 모듈/함수 없음.

- [ ] **Step 3: `src/config/scenes.ts` 구현**

```ts
import type { EmotionCode } from '../types';

export const ENDING_THRESHOLD = 900;
export const INITIAL_CHAPTER = 1;
export const INITIAL_AFFINITY = 0;
export const AFFINITY_MAX = 100;

// 게임 시작 시 보여줄 오프닝 대사 (백엔드 호출 없이 프론트가 시드)
export const OPENING_DIALOGUE: string[] = [
  '안녕! 드디어 만났네. 내가 너의 여행 메이트야.',
  '우리 어디로 떠나볼까? 편하게 말해줘!',
];

const FALLBACK_BACKGROUND = '/assets/backgrounds/default.png';

// 챕터 번호 → 배경 이미지. 나슬님이 public/assets/backgrounds 에 파일을 채우면 됨.
const BACKGROUNDS: Record<number, string> = {
  1: '/assets/backgrounds/ch1.png',
  2: '/assets/backgrounds/ch2.png',
  3: '/assets/backgrounds/ch3.png',
  // 엔딩(>=900) 배경
  900: '/assets/backgrounds/ending.png',
};

export function getBackground(chapter: number): string {
  return BACKGROUNDS[chapter] ?? FALLBACK_BACKGROUND;
}

export function getSprite(emotion: EmotionCode): string {
  return `/assets/characters/${emotion}.png`;
}

export function isEnding(chapter: number | null): boolean {
  return chapter !== null && chapter >= ENDING_THRESHOLD;
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd frontend && npx vitest run src/config/scenes.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: 커밋**

```bash
cd frontend && git add src/config/scenes.ts src/config/scenes.test.ts && git commit -m "feat(frontend): add scene/asset config with ending detection

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: 턴 전환 로직 (store/turnLogic.ts) — TDD

대사 재생이 끝난 뒤 "계속 / 씬 전환 / 엔딩" 중 무엇을 할지 결정하는 순수 함수. 스토어에서 분리해 단독 테스트.

**Files:**
- Create: `frontend/src/store/turnLogic.ts`
- Test: `frontend/src/store/turnLogic.test.ts`

- [ ] **Step 1: 실패하는 테스트 작성** (`src/store/turnLogic.test.ts`)

```ts
import { describe, it, expect } from 'vitest';
import { resolveTransition } from './turnLogic';

describe('resolveTransition', () => {
  it('continues when next chapter is null', () => {
    expect(resolveTransition(null, 1)).toEqual({ type: 'continue' });
  });
  it('continues when next chapter equals current', () => {
    expect(resolveTransition(2, 2)).toEqual({ type: 'continue' });
  });
  it('scene-transitions to a new normal chapter', () => {
    expect(resolveTransition(3, 2)).toEqual({ type: 'scene', chapter: 3 });
  });
  it('ends the game at/above chapter 900', () => {
    expect(resolveTransition(900, 5)).toEqual({ type: 'ending', endingId: 900 });
  });
});
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd frontend && npx vitest run src/store/turnLogic.test.ts`
Expected: FAIL — `resolveTransition` 없음.

- [ ] **Step 3: `src/store/turnLogic.ts` 구현**

```ts
import { isEnding } from '../config/scenes';

export type TurnTransition =
  | { type: 'continue' }
  | { type: 'scene'; chapter: number }
  | { type: 'ending'; endingId: number };

export function resolveTransition(
  nextChapter: number | null,
  currentChapter: number,
): TurnTransition {
  if (nextChapter === null || nextChapter === currentChapter) {
    return { type: 'continue' };
  }
  if (isEnding(nextChapter)) {
    return { type: 'ending', endingId: nextChapter };
  }
  return { type: 'scene', chapter: nextChapter };
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd frontend && npx vitest run src/store/turnLogic.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: 커밋**

```bash
cd frontend && git add src/store/turnLogic.ts src/store/turnLogic.test.ts && git commit -m "feat(frontend): add turn transition resolver

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: 목업 API (api/mock.ts) — TDD

백엔드 없이 동작하도록 `routes.py` 더미를 정본 스키마에 맞춰 흉내낸다. 키워드로 호감도/표정/씬 전환을, "엔딩" 입력으로 엔딩을 테스트할 수 있다.

**Files:**
- Create: `frontend/src/api/mock.ts`
- Test: `frontend/src/api/mock.test.ts`

- [ ] **Step 1: 실패하는 테스트 작성** (`src/api/mock.test.ts`)

```ts
import { describe, it, expect } from 'vitest';
import { mockChat } from './mock';
import type { ChatRequest } from '../types';

const base: ChatRequest = {
  session_id: 's1',
  user_message: '',
  current_chapter: 1,
  current_affinity: 0,
};

describe('mockChat', () => {
  it('returns the ending chapter when message contains 엔딩', () => {
    const r = mockChat({ ...base, user_message: '엔딩 보고 싶어' });
    expect(r.next_chapter).toBe(900);
  });
  it('advances the chapter on a trigger keyword', () => {
    const r = mockChat({ ...base, user_message: '이제 출발하자', current_chapter: 2 });
    expect(r.next_chapter).toBe(3);
    expect(r.emotion_code).toBe('surprise');
  });
  it('stays in the chapter for normal chat', () => {
    const r = mockChat({ ...base, user_message: '안녕' });
    expect(r.next_chapter).toBeNull();
  });
  it('gives a bigger affinity bump when message contains 좋아', () => {
    const r = mockChat({ ...base, user_message: '너 좋아' });
    expect(r.affinity_delta).toBe(3);
    expect(r.emotion_code).toBe('smile');
  });
  it('always returns a non-empty dialogue list', () => {
    const r = mockChat({ ...base, user_message: '아무말' });
    expect(r.agent_dialogue_list.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd frontend && npx vitest run src/api/mock.test.ts`
Expected: FAIL — `mockChat` 없음.

- [ ] **Step 3: `src/api/mock.ts` 구현**

```ts
import type { ChatRequest, EmotionCode, TurnResult } from '../types';

const TRIGGER_KEYWORDS = ['예약', '출발', '가자'];

export function mockChat(req: ChatRequest): TurnResult {
  const msg = req.user_message;

  // 엔딩 트리거
  if (msg.includes('엔딩')) {
    return {
      next_chapter: 900,
      affinity_delta: 5,
      agent_dialogue_list: [
        '우와... 벌써 여행이 끝나가네.',
        '너랑 함께라서 정말 즐거웠어. 우리 또 떠나자!',
      ],
      emotion_code: 'smile',
      metadata: { is_dummy: true },
    };
  }

  const isTrigger = TRIGGER_KEYWORDS.some((k) => msg.includes(k));
  const liked = msg.includes('좋아');

  let emotion: EmotionCode = 'idle';
  if (isTrigger) emotion = 'surprise';
  else if (liked) emotion = 'smile';

  return {
    next_chapter: isTrigger ? req.current_chapter + 1 : null,
    affinity_delta: liked ? 3 : 1,
    agent_dialogue_list: [
      `응? 방금 "${msg}"라고 했어?`,
      '너랑 같이 계획 짜니까 뭘 해도 다 재밌는 것 같아!',
    ],
    emotion_code: emotion,
    metadata: { is_dummy: true, received_session: req.session_id },
  };
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd frontend && npx vitest run src/api/mock.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: 커밋**

```bash
cd frontend && git add src/api/mock.ts src/api/mock.test.ts && git commit -m "feat(frontend): add mock chat API matching TurnResult schema

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: API 클라이언트 (api/client.ts)

유일한 통신 진입점. `VITE_USE_MOCK`이 `'false'`가 아니면 목업, 그 외엔 실제 axios 호출. 기본은 목업 ON (6/6에 `VITE_USE_MOCK=false`로 스왑). 순수 환경 의존이라 자동 테스트 대신 타입 체크로 검증한다.

**Files:**
- Create: `frontend/src/api/client.ts`

- [ ] **Step 1: `src/api/client.ts` 작성**

```ts
import axios from 'axios';
import type { ChatRequest, TurnResult } from '../types';
import { mockChat } from './mock';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';
// 기본값: 목업 ON. 실제 백엔드 연결 시 .env에 VITE_USE_MOCK=false 설정.
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const MOCK_DELAY_MS = 400; // 로딩 연출 확인용 인위적 지연

export async function postChat(req: ChatRequest): Promise<TurnResult> {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));
    return mockChat(req);
  }
  const { data } = await axios.post<TurnResult>(`${API_BASE}/chat`, req);
  return data;
}
```

- [ ] **Step 2: 타입 체크 + 전체 테스트 통과 확인**

Run: `cd frontend && npx tsc --noEmit && npx vitest run`
Expected: tsc 에러 없음, 기존 테스트 전부 PASS.

- [ ] **Step 3: 커밋**

```bash
cd frontend && git add src/api/client.ts && git commit -m "feat(frontend): add postChat client with mock/real switch

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: 게임 스토어 (store/useGameStore.ts) — TDD

게임 전체 상태와 액션. 가장 핵심. `postChat`을 mock 처리하고 액션별 상태 전이를 검증한다.

**Files:**
- Create: `frontend/src/store/useGameStore.ts`
- Test: `frontend/src/store/useGameStore.test.ts`

- [ ] **Step 1: 실패하는 테스트 작성** (`src/store/useGameStore.test.ts`)

```ts
import { describe, it, expect, beforeEach, vi } from 'vitest';

vi.mock('../api/client', () => ({ postChat: vi.fn() }));

import { useGameStore } from './useGameStore';
import { postChat } from '../api/client';
import type { TurnResult } from '../types';

const mockedPost = vi.mocked(postChat);

function turn(partial: Partial<TurnResult>): TurnResult {
  return {
    next_chapter: null,
    affinity_delta: 0,
    agent_dialogue_list: ['line1', 'line2'],
    emotion_code: 'idle',
    metadata: {},
    ...partial,
  };
}

describe('useGameStore', () => {
  beforeEach(() => {
    useGameStore.getState().reset();
    mockedPost.mockReset();
  });

  it('startGame seeds session, opening line, and game view', () => {
    useGameStore.getState().startGame();
    const s = useGameStore.getState();
    expect(s.view).toBe('game');
    expect(s.sessionId).not.toBe('');
    expect(s.currentLine).not.toBeNull();
    expect(s.inputLocked).toBe(true);
  });

  it('advanceDialogue walks the opening queue then unlocks input', () => {
    useGameStore.getState().startGame(); // currentLine=1번, queue=[2번]
    useGameStore.getState().advanceDialogue(); // 2번 표시, queue 비움
    expect(useGameStore.getState().inputLocked).toBe(true);
    useGameStore.getState().advanceDialogue(); // queue 비어있음 -> continue
    expect(useGameStore.getState().inputLocked).toBe(false);
  });

  it('sendMessage applies affinity, emotion, and queues dialogue', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue(); // 입력 가능 상태로
    mockedPost.mockResolvedValue(
      turn({ affinity_delta: 3, emotion_code: 'smile', agent_dialogue_list: ['a', 'b'] }),
    );

    await useGameStore.getState().sendMessage('안녕');
    const s = useGameStore.getState();
    expect(s.affinity).toBe(3);
    expect(s.emotion).toBe('smile');
    expect(s.currentLine).toBe('a');
    expect(s.dialogueQueue).toEqual(['b']);
    expect(s.inputLocked).toBe(true);
  });

  it('scene transition updates chapter after dialogue ends', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    mockedPost.mockResolvedValue(turn({ next_chapter: 2, agent_dialogue_list: ['x'] }));
    await useGameStore.getState().sendMessage('출발'); // currentLine='x', queue 빔
    useGameStore.getState().advanceDialogue(); // queue 빔 -> scene
    const s = useGameStore.getState();
    expect(s.currentChapter).toBe(2);
    expect(s.inputLocked).toBe(false);
  });

  it('ending switches the view when next_chapter >= 900', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    mockedPost.mockResolvedValue(turn({ next_chapter: 900, agent_dialogue_list: ['bye'] }));
    await useGameStore.getState().sendMessage('엔딩');
    useGameStore.getState().advanceDialogue(); // queue 빔 -> ending
    const s = useGameStore.getState();
    expect(s.view).toBe('ending');
    expect(s.endingId).toBe(900);
  });

  it('ignores sendMessage while loading or with blank text', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    await useGameStore.getState().sendMessage('   ');
    expect(mockedPost).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd frontend && npx vitest run src/store/useGameStore.test.ts`
Expected: FAIL — `useGameStore` 없음.

- [ ] **Step 3: `src/store/useGameStore.ts` 구현**

```ts
import { create } from 'zustand';
import type { EmotionCode, TurnResult } from '../types';
import { postChat } from '../api/client';
import { resolveTransition } from './turnLogic';
import { INITIAL_AFFINITY, INITIAL_CHAPTER, OPENING_DIALOGUE } from '../config/scenes';

type View = 'title' | 'game' | 'ending';

interface GameState {
  sessionId: string;
  view: View;
  currentChapter: number;
  affinity: number;
  emotion: EmotionCode;
  dialogueQueue: string[];
  currentLine: string | null;
  isLoading: boolean;
  inputLocked: boolean;
  endingId: number | null;
  pendingChapter: number | null; // 대사 재생 후 적용할 다음 챕터

  startGame: () => void;
  sendMessage: (text: string) => Promise<void>;
  advanceDialogue: () => void;
  reset: () => void;
}

function genSessionId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `sess-${Math.random().toString(36).slice(2)}`;
}

const initialState = {
  sessionId: '',
  view: 'title' as View,
  currentChapter: INITIAL_CHAPTER,
  affinity: INITIAL_AFFINITY,
  emotion: 'idle' as EmotionCode,
  dialogueQueue: [] as string[],
  currentLine: null as string | null,
  isLoading: false,
  inputLocked: true,
  endingId: null as number | null,
  pendingChapter: null as number | null,
};

export const useGameStore = create<GameState>((set, get) => ({
  ...initialState,

  startGame: () => {
    const [first, ...rest] = OPENING_DIALOGUE;
    set({
      ...initialState,
      sessionId: genSessionId(),
      view: 'game',
      currentLine: first ?? null,
      dialogueQueue: rest,
      inputLocked: true,
    });
  },

  sendMessage: async (text: string) => {
    const { sessionId, currentChapter, affinity, isLoading } = get();
    if (isLoading || !text.trim()) return;
    set({ inputLocked: true, isLoading: true });

    const result: TurnResult = await postChat({
      session_id: sessionId,
      user_message: text,
      current_chapter: currentChapter,
      current_affinity: affinity,
    });

    const [first, ...rest] = result.agent_dialogue_list;
    set({
      isLoading: false,
      affinity: affinity + result.affinity_delta,
      emotion: result.emotion_code,
      currentLine: first ?? null,
      dialogueQueue: rest,
      pendingChapter: result.next_chapter,
      inputLocked: true,
    });
  },

  advanceDialogue: () => {
    const { dialogueQueue, pendingChapter, currentChapter, isLoading } = get();
    if (isLoading) return;

    if (dialogueQueue.length > 0) {
      const [next, ...rest] = dialogueQueue;
      set({ currentLine: next, dialogueQueue: rest });
      return;
    }

    const transition = resolveTransition(pendingChapter, currentChapter);
    if (transition.type === 'continue') {
      set({ inputLocked: false, pendingChapter: null });
    } else if (transition.type === 'scene') {
      set({ currentChapter: transition.chapter, inputLocked: false, pendingChapter: null });
    } else {
      set({ endingId: transition.endingId, view: 'ending', pendingChapter: null });
    }
  },

  reset: () => set({ ...initialState }),
}));
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd frontend && npx vitest run src/store/useGameStore.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: 커밋**

```bash
cd frontend && git add src/store/useGameStore.ts src/store/useGameStore.test.ts && git commit -m "feat(frontend): add game store with turn loop, scene/ending transitions

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: 타이핑 효과 훅 (hooks/useTypewriter.ts)

대사를 한 글자씩 출력하고, 클릭 시 즉시 완성(skip)하는 훅. 타이밍/시각 효과라 자동 테스트는 생략(스펙 합의), Task 12 통합에서 수동 확인.

**Files:**
- Create: `frontend/src/hooks/useTypewriter.ts`

- [ ] **Step 1: `src/hooks/useTypewriter.ts` 작성**

```ts
import { useEffect, useRef, useState } from 'react';

const SPEED_MS = 30;

export function useTypewriter(text: string) {
  const [displayed, setDisplayed] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let i = 0;
    setDisplayed('');
    if (!text) {
      setIsTyping(false);
      return;
    }
    setIsTyping(true);
    timerRef.current = setInterval(() => {
      i += 1;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        if (timerRef.current) clearInterval(timerRef.current);
        timerRef.current = null;
        setIsTyping(false);
      }
    }, SPEED_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [text]);

  const skip = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setDisplayed(text);
    setIsTyping(false);
  };

  return { displayed, isTyping, skip };
}
```

- [ ] **Step 2: 타입 체크 확인**

Run: `cd frontend && npx tsc --noEmit`
Expected: 에러 없음.

- [ ] **Step 3: 커밋**

```bash
cd frontend && git add src/hooks/useTypewriter.ts && git commit -m "feat(frontend): add typewriter hook with skip

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: 게임 비주얼 컴포넌트 (배경/스프라이트/게이지)

스토어 상태를 받아 그리는 표현 컴포넌트. 에셋 누락 시 `onError`로 깨지지 않게 숨긴다. 자동 테스트 없음 — Task 12에서 수동 확인.

**Files:**
- Create: `frontend/src/components/game/SceneBackground.tsx`
- Create: `frontend/src/components/game/CharacterSprite.tsx`
- Create: `frontend/src/components/game/AffinityGauge.tsx`

- [ ] **Step 1: `SceneBackground.tsx` 작성**

```tsx
import { getBackground } from '../../config/scenes';

interface Props {
  chapter: number;
}

export default function SceneBackground({ chapter }: Props) {
  return (
    <img
      key={chapter}
      src={getBackground(chapter)}
      alt=""
      className="absolute inset-0 h-full w-full object-cover animate-fade-in"
      onError={(e) => {
        (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
      }}
    />
  );
}
```

- [ ] **Step 2: `CharacterSprite.tsx` 작성**

```tsx
import { getSprite } from '../../config/scenes';
import type { EmotionCode } from '../../types';

interface Props {
  emotion: EmotionCode;
}

export default function CharacterSprite({ emotion }: Props) {
  return (
    <img
      key={emotion}
      src={getSprite(emotion)}
      alt={emotion}
      className="absolute bottom-40 left-1/2 h-2/3 -translate-x-1/2 object-contain animate-fade-in pointer-events-none"
      onError={(e) => {
        (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
      }}
    />
  );
}
```

- [ ] **Step 3: `AffinityGauge.tsx` 작성**

```tsx
import { AFFINITY_MAX } from '../../config/scenes';

interface Props {
  affinity: number;
  max?: number;
}

export default function AffinityGauge({ affinity, max = AFFINITY_MAX }: Props) {
  const pct = Math.max(0, Math.min(100, (affinity / max) * 100));
  return (
    <div className="flex items-center gap-2 rounded-full bg-game-navy/60 px-3 py-1">
      <span className="font-bold text-game-pink">♥</span>
      <div className="h-3 flex-1 overflow-hidden rounded-full bg-white/70">
        <div
          className="h-full bg-game-pink transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 text-right text-sm text-white/90">{affinity}</span>
    </div>
  );
}
```

- [ ] **Step 4: 타입 체크 확인**

Run: `cd frontend && npx tsc --noEmit`
Expected: 에러 없음.

- [ ] **Step 5: 커밋**

```bash
cd frontend && git add src/components/game && git commit -m "feat(frontend): add background, sprite, affinity gauge components

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: 대화 컴포넌트 (대사 박스/입력창)

`DialogueBox`는 현재 대사 1줄을 타이핑 출력하고 클릭으로 진행(타이핑 중이면 skip). `ChatInput`은 입력 잠금/로딩 중 비활성.

**Files:**
- Create: `frontend/src/components/chat/DialogueBox.tsx`
- Create: `frontend/src/components/chat/ChatInput.tsx`

- [ ] **Step 1: `DialogueBox.tsx` 작성**

```tsx
import { useGameStore } from '../../store/useGameStore';
import { useTypewriter } from '../../hooks/useTypewriter';

export default function DialogueBox() {
  const currentLine = useGameStore((s) => s.currentLine);
  const isLoading = useGameStore((s) => s.isLoading);
  const inputLocked = useGameStore((s) => s.inputLocked);
  const advanceDialogue = useGameStore((s) => s.advanceDialogue);

  const { displayed, isTyping, skip } = useTypewriter(currentLine ?? '');

  const handleClick = () => {
    if (isLoading) return;
    if (isTyping) {
      skip();
      return;
    }
    if (inputLocked) advanceDialogue();
  };

  if (!currentLine && !isLoading) return null;

  const showAdvance = inputLocked && !isTyping && !isLoading;

  return (
    <div
      onClick={handleClick}
      className="min-h-[6rem] cursor-pointer rounded-2xl bg-game-navy/90 p-5 shadow-xl animate-fade-in"
    >
      <div className="mb-1 font-bold text-game-pink">메이트</div>
      <p className="leading-relaxed text-white">{isLoading ? '...' : displayed}</p>
      {showAdvance && (
        <div className="mt-1 animate-pulse text-right text-xs text-white/50">▾ 클릭</div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: `ChatInput.tsx` 작성**

```tsx
import { useState } from 'react';
import { useGameStore } from '../../store/useGameStore';

export default function ChatInput() {
  const [text, setText] = useState('');
  const inputLocked = useGameStore((s) => s.inputLocked);
  const isLoading = useGameStore((s) => s.isLoading);
  const sendMessage = useGameStore((s) => s.sendMessage);

  const disabled = inputLocked || isLoading;

  const handleSend = () => {
    if (disabled || !text.trim()) return;
    void sendMessage(text);
    setText('');
  };

  return (
    <div className="flex gap-2">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSend();
        }}
        disabled={disabled}
        placeholder={disabled ? '대사를 클릭해 진행하세요…' : '메시지를 입력하세요…'}
        className="flex-1 rounded-full px-4 py-2 text-game-navy disabled:opacity-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled}
        className="rounded-full bg-game-pink px-6 py-2 font-semibold text-white transition-colors hover:bg-game-pink-dark disabled:opacity-40"
      >
        전송
      </button>
    </div>
  );
}
```

- [ ] **Step 3: 타입 체크 확인**

Run: `cd frontend && npx tsc --noEmit`
Expected: 에러 없음.

- [ ] **Step 4: 커밋**

```bash
cd frontend && git add src/components/chat && git commit -m "feat(frontend): add dialogue box and chat input

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: 뷰 + App 라우팅

3개 뷰를 만들고 `App.tsx`를 실제 상태 라우팅으로 교체한다.

**Files:**
- Create: `frontend/src/views/TitleScreen.tsx`
- Create: `frontend/src/views/GameScreen.tsx`
- Create: `frontend/src/views/EndingScreen.tsx`
- Modify: `frontend/src/App.tsx` (Task 1 placeholder 교체)

- [ ] **Step 1: `TitleScreen.tsx` 작성**

```tsx
import { useGameStore } from '../store/useGameStore';

export default function TitleScreen() {
  const startGame = useGameStore((s) => s.startGame);
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-8 bg-gradient-to-b from-game-pink-light to-game-pink/40">
      <h1 className="text-4xl font-bold text-game-pink-dark drop-shadow">✈️ 나만의 여행 메이트</h1>
      <p className="text-game-navy">메이트와 대화하며 함께 여행을 떠나보세요</p>
      <button
        onClick={startGame}
        className="rounded-full bg-game-pink px-8 py-3 text-lg font-semibold text-white shadow-lg transition-colors hover:bg-game-pink-dark"
      >
        시작하기
      </button>
    </div>
  );
}
```

- [ ] **Step 2: `GameScreen.tsx` 작성**

```tsx
import { useGameStore } from '../store/useGameStore';
import SceneBackground from '../components/game/SceneBackground';
import CharacterSprite from '../components/game/CharacterSprite';
import AffinityGauge from '../components/game/AffinityGauge';
import DialogueBox from '../components/chat/DialogueBox';
import ChatInput from '../components/chat/ChatInput';

export default function GameScreen() {
  const currentChapter = useGameStore((s) => s.currentChapter);
  const emotion = useGameStore((s) => s.emotion);
  const affinity = useGameStore((s) => s.affinity);

  return (
    <div className="relative h-full w-full overflow-hidden">
      <SceneBackground chapter={currentChapter} />
      <CharacterSprite emotion={emotion} />
      <div className="absolute inset-x-0 top-0 p-4">
        <AffinityGauge affinity={affinity} />
      </div>
      <div className="absolute inset-x-0 bottom-0 flex flex-col gap-2 p-4">
        <DialogueBox />
        <ChatInput />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: `EndingScreen.tsx` 작성**

```tsx
import { useGameStore } from '../store/useGameStore';
import { getBackground } from '../config/scenes';

export default function EndingScreen() {
  const endingId = useGameStore((s) => s.endingId);
  const affinity = useGameStore((s) => s.affinity);
  const reset = useGameStore((s) => s.reset);

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center gap-6">
      {endingId !== null && (
        <img
          src={getBackground(endingId)}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
          }}
        />
      )}
      <div className="relative z-10 flex flex-col items-center gap-6 rounded-2xl bg-game-navy/80 p-10">
        <h2 className="text-3xl font-bold text-game-pink">🎬 여행 끝!</h2>
        <p className="text-white/90">최종 호감도: ♥ {affinity}</p>
        <button
          onClick={reset}
          className="rounded-full bg-game-pink px-8 py-3 font-semibold text-white transition-colors hover:bg-game-pink-dark"
        >
          다시 하기
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: `App.tsx` 실제 라우팅으로 교체**

```tsx
import { useGameStore } from './store/useGameStore';
import TitleScreen from './views/TitleScreen';
import GameScreen from './views/GameScreen';
import EndingScreen from './views/EndingScreen';

export default function App() {
  const view = useGameStore((s) => s.view);
  return (
    <div className="h-full w-full overflow-hidden bg-game-navy-dark text-white">
      {view === 'title' && <TitleScreen />}
      {view === 'game' && <GameScreen />}
      {view === 'ending' && <EndingScreen />}
    </div>
  );
}
```

- [ ] **Step 5: 빌드 + 전체 테스트 통과 확인**

Run: `cd frontend && npm run build && npx vitest run`
Expected: 빌드 성공, 모든 테스트 PASS.

- [ ] **Step 6: 커밋**

```bash
cd frontend && git add src/views src/App.tsx && git commit -m "feat(frontend): wire title/game/ending views with state routing

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: 통합 수동 검증 (목업 모드)

전체 흐름을 브라우저에서 직접 확인한다. (코드 변경 없음 — 검증 전용)

- [ ] **Step 1: 개발 서버 실행**

Run: `cd frontend && npm run dev`
브라우저에서 표시된 주소 열기.

- [ ] **Step 2: 흐름 체크리스트 (목업)**

다음을 순서대로 확인:
- [ ] 타이틀 화면 → "시작하기" 클릭 → 게임 화면 진입
- [ ] 오프닝 대사 2줄이 타이핑되고, 클릭으로 다음 줄 진행됨
- [ ] 마지막 오프닝 줄 이후 입력창 활성화됨
- [ ] 일반 메시지 입력 → 로딩(...) → 메이트 응답 2줄 타이핑 → 호감도 게이지 증가
- [ ] 타이핑 중 대사 박스 클릭 시 즉시 완성(skip)됨
- [ ] "좋아"가 포함된 메시지 → 호감도 +3, 표정 smile (에셋 있으면 표정 변화)
- [ ] "출발"/"예약"/"가자" 입력 → 대사 종료 후 챕터(배경) 전환됨
- [ ] "엔딩" 입력 → 대사 종료 후 엔딩 화면 전환, 최종 호감도 표시
- [ ] 엔딩 화면 "다시 하기" → 타이틀로 복귀, 상태 초기화됨
- [ ] 에셋 파일이 없어도 화면이 깨지지 않음(이미지 숨김 처리)

- [ ] **Step 3: 문제 발견 시**

해당 Task로 돌아가 수정 후 재검증. 모두 통과하면 다음 Task로.

---

## Task 13: 에셋 연동 준비 (나슬님 작업 공간)

에셋 폴더와 안내 문서를 만들어, 나슬님이 파일만 넣으면 동작하도록 한다.

**Files:**
- Create: `frontend/public/assets/characters/.gitkeep`
- Create: `frontend/public/assets/backgrounds/.gitkeep`
- Create: `frontend/public/assets/README.md`

- [ ] **Step 1: 폴더 + .gitkeep 생성**

Run:
```bash
cd frontend && mkdir -p public/assets/characters public/assets/backgrounds && touch public/assets/characters/.gitkeep public/assets/backgrounds/.gitkeep
```

- [ ] **Step 2: `public/assets/README.md` 작성** (에셋 파일명 규격 안내)

```markdown
# 에셋 파일 가이드 (나슬님)

아래 경로/파일명 그대로 이미지를 넣으면 코드 수정 없이 자동 반영됩니다.

## 캐릭터 표정 (characters/)
- `idle.png`     기본
- `smile.png`    웃음
- `sad.png`      슬픔
- `surprise.png` 놀람

## 배경 (backgrounds/)
- `ch1.png`, `ch2.png`, `ch3.png` ... 챕터별 배경
- `ending.png`   엔딩 배경
- `default.png`  매핑 없는 챕터용 기본 배경 (fallback)

> 권장: 가로형(16:9), PNG 또는 WebP. 캐릭터는 배경 투명 PNG.
> 챕터가 늘어나면 `src/config/scenes.ts`의 BACKGROUNDS 맵에 한 줄씩 추가.
```

- [ ] **Step 3: 커밋**

```bash
cd frontend && git add public/assets && git commit -m "chore(frontend): add asset folders and asset guide for designer

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: 실제 백엔드 연결 (6/6, 백엔드 완성 후)

목업에서 실제 API로 스왑. 코드 변경은 환경변수 한 줄.

**Files:**
- Create: `frontend/.env.local`

- [ ] **Step 1: 백엔드 계약 확인**

백엔드 팀과 다음을 확인:
- `POST /chat`의 실제 prefix (예: `/api/chat`인지 `/chat`인지)
- 응답이 정본 스키마(`agent_dialogue_list`, `next_chapter:int`, `affinity_delta`, `emotion_code`, `metadata`)와 일치하는지
- 엔딩 시 `next_chapter >= 900`을 내려주는지

- [ ] **Step 2: `.env.local` 작성** (prefix가 `/api`가 아니면 VITE_API_BASE도 조정)

```
VITE_USE_MOCK=false
VITE_API_BASE=/api
```

- [ ] **Step 3: 백엔드 실행 후 연결 확인**

백엔드를 `http://localhost:8000`에서 실행한 뒤:
Run: `cd frontend && npm run dev`
Expected: 메시지 전송 시 실제 백엔드 응답이 화면에 반영됨 (Task 12 체크리스트 재확인).

- [ ] **Step 4: 커밋** (`.env.local`이 .gitignore 대상이면 커밋 생략, 대신 `.env.example` 추가)

```bash
cd frontend && git add .env.local 2>/dev/null; git commit -m "chore(frontend): connect real backend API

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>" || echo "nothing to commit (env ignored)"
```

---

## Self-Review 결과

- **스펙 커버리지**: 데이터 계약(Task 2), 화면 구성(Task 9·10·11), 상태/액션(Task 7), 에셋 매핑+fallback(Task 3·13), 목업 전략(Task 5·6), 빌드/통합/정리(Task 1), 테스트 범위(Task 3·4·5·7), 실제 API 스왑(Task 14) — 스펙 전 항목이 태스크에 매핑됨.
- **Placeholder 스캔**: TODO/TBD 없음. 모든 코드 단계에 완전한 코드 포함.
- **타입 일관성**: `EmotionCode`, `ChatRequest`, `TurnResult`, `resolveTransition`/`TurnTransition`, `getBackground`/`getSprite`/`isEnding`, 스토어 액션명(`startGame`/`sendMessage`/`advanceDialogue`/`reset`) 전 태스크에서 동일하게 사용됨.
- **범위**: 단일 프론트엔드 서브시스템. 분할 불필요.
```
