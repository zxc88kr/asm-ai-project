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
