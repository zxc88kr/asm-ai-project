import type { EmotionCode } from '../types';

export const ENDING_THRESHOLD = 99;   // backend ENDING_CHAPTER = 99
export const INITIAL_CHAPTER = 1;
export const INITIAL_AFFINITY = 50;  // backend _empty_session 초기 호감도와 동일
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

export function getEndingBackground(affinity: number): string {
  if (affinity >= 70) return '/assets/backgrounds/ending_happy.png';
  if (affinity <= 30) return '/assets/backgrounds/ending_bad.png';
  return '/assets/backgrounds/ending_normal.png';
}

export function getSprite(emotion: EmotionCode): string {
  return `/assets/characters/${emotion}.png`;
}

export function isEnding(chapter: number | null): boolean {
  return chapter !== null && chapter >= ENDING_THRESHOLD;
}
