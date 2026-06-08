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
