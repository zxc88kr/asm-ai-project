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
  selections: string[];

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
  selections: [] as string[],
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
    const { sessionId, currentChapter, isLoading } = get();
    if (isLoading || !text.trim()) return;
    set({ inputLocked: true, isLoading: true, selections: [] });

    let result: TurnResult;
    try {
      result = await postChat({
        session_id: sessionId,
        user_message: text,
        current_chapter: currentChapter,
        current_affinity: get().affinity,
      });
    } catch {
      // 네트워크/서버 실패 시 교착 방지: 상태를 풀어 재시도 가능하게 한다.
      set({ isLoading: false, inputLocked: false });
      return;
    }

    const [first, ...rest] = result.agent_dialogue_list;
    set((state) => ({
      isLoading: false,
      affinity: state.affinity + result.affinity_delta,
      emotion: result.emotion_code,
      currentLine: first ?? null,
      dialogueQueue: rest,
      pendingChapter: result.next_chapter,
      inputLocked: true,
      selections: Array.isArray(result.metadata?.selections)
        ? (result.metadata.selections as string[])
        : [],
    }));
    if (first === undefined) {
      // 빈 대사 리스트: 클릭 대기 없이 즉시 전환 처리
      get().advanceDialogue();
    }
  },

  advanceDialogue: () => {
    const { dialogueQueue, selections, pendingChapter, currentChapter, isLoading } = get();
    if (isLoading) return;

    if (dialogueQueue.length > 0) {
      const [next, ...rest] = dialogueQueue;
      set({ currentLine: next, dialogueQueue: rest });
      return;
    }

    if (selections.length > 0) {
      set({ currentLine: null }); // DialogueBox 숨김 → SelectionMenu 출현
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
