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
