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
