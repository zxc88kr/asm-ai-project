import type { ChatRequest, EmotionCode, TurnResult } from '../types';

const TRIGGER_KEYWORDS = ['예약', '출발', '가자'];

export function mockChat(req: ChatRequest): TurnResult {
  const msg = req.user_message;

  // 선택지 트리거 — SelectionMenu 동작 테스트용
  if (msg.includes('선택')) {
    return {
      next_chapter: null,
      affinity_delta: 1,
      agent_dialogue_list: ['어떤 걸 하고 싶어? 골라봐!'],
      emotion_code: 'smile',
      metadata: {
        selections: ['파리로 가기', '도쿄로 가기', '아직 모르겠어'],
      },
    };
  }

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
