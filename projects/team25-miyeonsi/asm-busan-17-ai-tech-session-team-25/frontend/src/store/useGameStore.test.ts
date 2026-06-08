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

  it('recovers state when postChat rejects (no deadlock)', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    mockedPost.mockRejectedValue(new Error('boom'));

    await useGameStore.getState().sendMessage('안녕');
    const s = useGameStore.getState();
    expect(s.isLoading).toBe(false);
    expect(s.inputLocked).toBe(false);
  });

  it('resolves the turn immediately on empty dialogue list (no deadlock)', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    mockedPost.mockResolvedValue(turn({ agent_dialogue_list: [], next_chapter: null }));

    await useGameStore.getState().sendMessage('안녕');
    expect(useGameStore.getState().inputLocked).toBe(false);
  });

  it('empty dialogue list still triggers ending transition', async () => {
    useGameStore.getState().startGame();
    useGameStore.getState().advanceDialogue();
    useGameStore.getState().advanceDialogue();
    mockedPost.mockResolvedValue(turn({ agent_dialogue_list: [], next_chapter: 900 }));

    await useGameStore.getState().sendMessage('안녕');
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
