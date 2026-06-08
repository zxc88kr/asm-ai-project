import "server-only";

import {
  characters,
  clues,
  INITIAL_UNLOCKED_CHARACTER_IDS,
  INITIAL_UNLOCKED_CLUE_IDS,
  interrogatableCharacters,
  RECOVERED_TRACE_CLUE_ID,
  type UnlockTarget,
} from "@/data/gameData";
import { generateNpcReply, type ConversationMessage } from "@/lib/llmClient";
import { getCharacterPersona } from "@/server/personas/characterPersonas";

export type ApiMessage = {
  id: number;
  characterId: number;
  sender: "user" | "character";
  senderName: string;
  content: string;
  createdAt: string;
};

export type DeductionRecord = {
  id: number;
  content: string;
  character: number;
  clues: number[];
  result: boolean;
  comment: string;
  createdAt: string;
};

type Store = {
  interactedClueIds: Set<number>;
  interactedCharacterIds: Set<number>;
  unlockedClueIds: Set<number>;
  unlockedCharacterIds: Set<number>;
  messagesByCharacterId: Map<number, ApiMessage[]>;
  deductions: DeductionRecord[];
  traceProbeCount: number;
  nextMessageId: number;
  nextDeductionId: number;
};

const DEFAULT_PLAYER_ID = "anonymous";
const TRACE_UNLOCK_THRESHOLD = 4;
const TRACE_PROBE_MESSAGES = [
  "현재 접근 권한으로는 열람할 수 없습니다.",
  "열람할 수 없습니다.",
  "열람하지 마.",
  "삭제된 Orchestrator 세션 일부를 복구합니다...",
];

declare global {
  var __demoDayIncidentStores: Map<string, Store> | undefined;
}

function createStore(): Store {
  return {
    interactedClueIds: new Set<number>(),
    interactedCharacterIds: new Set<number>(),
    unlockedClueIds: new Set<number>(INITIAL_UNLOCKED_CLUE_IDS),
    unlockedCharacterIds: new Set<number>(INITIAL_UNLOCKED_CHARACTER_IDS),
    messagesByCharacterId: new Map<number, ApiMessage[]>(),
    deductions: [],
    traceProbeCount: 0,
    nextMessageId: 1,
    nextDeductionId: 1,
  };
}

function normalizePlayerId(playerId?: string | null) {
  const normalized = playerId?.trim().slice(0, 80);

  return normalized || null;
}

export function getPlayerIdFromRequest(request: Request) {
  return normalizePlayerId(
    request.headers.get("x-user-id") ||
      request.headers.get("user-id") ||
      request.headers.get("user_id"),
  );
}

export function getStore(playerId?: string | null) {
  const storeKey = normalizePlayerId(playerId) ?? DEFAULT_PLAYER_ID;

  if (!globalThis.__demoDayIncidentStores) {
    globalThis.__demoDayIncidentStores = new Map<string, Store>();
  }

  const existingStore = globalThis.__demoDayIncidentStores.get(storeKey);

  if (existingStore) {
    return existingStore;
  }

  const newStore = createStore();
  globalThis.__demoDayIncidentStores.set(storeKey, newStore);

  return newStore;
}

export function resetStore(playerId?: string | null) {
  const storeKey = normalizePlayerId(playerId) ?? DEFAULT_PLAYER_ID;

  if (!globalThis.__demoDayIncidentStores) {
    globalThis.__demoDayIncidentStores = new Map<string, Store>();
  }

  globalThis.__demoDayIncidentStores.set(storeKey, createStore());
}

export function getCharacterById(characterId: number) {
  return characters.find((character) => character.id === characterId) ?? null;
}

export function getClueById(clueId: number) {
  return clues.find((clue) => clue.id === clueId) ?? null;
}

function unlockTarget(store: Store, target: UnlockTarget | null) {
  if (!target) {
    return;
  }

  if (target.type === "clue") {
    store.unlockedClueIds.add(target.id);
    return;
  }

  store.unlockedCharacterIds.add(target.id);
}

export function markClueInteracted(clueId: number, playerId?: string | null) {
  const store = getStore(playerId);
  const clue = getClueById(clueId);

  if (!clue) {
    return null;
  }

  store.interactedClueIds.add(clueId);
  unlockTarget(store, clue.nextUnlock);

  return {
    clue_id: clueId,
    interacted: true,
    unlocked: true,
  };
}

export function getClueInteractions(playerId?: string | null) {
  const store = getStore(playerId);
  const userId = normalizePlayerId(playerId) ?? DEFAULT_PLAYER_ID;

  return clues.map((clue) => ({
    user_id: userId,
    clue_id: clue.id,
    interacted: store.interactedClueIds.has(clue.id),
    unlocked: store.unlockedClueIds.has(clue.id),
  }));
}

export function markCharacterInteracted(
  characterId: number,
  playerId?: string | null,
) {
  const store = getStore(playerId);
  const character = getCharacterById(characterId);

  if (!character) {
    return null;
  }

  store.interactedCharacterIds.add(characterId);
  unlockTarget(store, character.nextUnlock);

  return {
    character_id: characterId,
    interacted: true,
    unlocked: true,
  };
}

export function probeRecoveredTrace(playerId?: string | null) {
  const store = getStore(playerId);

  if (store.unlockedClueIds.has(RECOVERED_TRACE_CLUE_ID)) {
    return {
      attempt: store.traceProbeCount,
      unlocked: true,
      clueId: RECOVERED_TRACE_CLUE_ID,
      message: TRACE_PROBE_MESSAGES[TRACE_PROBE_MESSAGES.length - 1],
    };
  }

  store.traceProbeCount += 1;

  const unlocked = store.traceProbeCount >= TRACE_UNLOCK_THRESHOLD;

  if (unlocked) {
    store.unlockedClueIds.add(RECOVERED_TRACE_CLUE_ID);
  }

  return {
    attempt: store.traceProbeCount,
    unlocked,
    clueId: RECOVERED_TRACE_CLUE_ID,
    message:
      TRACE_PROBE_MESSAGES[
        Math.min(store.traceProbeCount - 1, TRACE_PROBE_MESSAGES.length - 1)
      ],
  };
}

export function getCharacterInteractions(playerId?: string | null) {
  const store = getStore(playerId);
  const userId = normalizePlayerId(playerId) ?? DEFAULT_PLAYER_ID;

  return interrogatableCharacters.map((character) => ({
    user_id: userId,
    character_id: character.id,
    interacted: store.interactedCharacterIds.has(character.id),
    unlocked: store.unlockedCharacterIds.has(character.id),
  }));
}

function createMessage({
  characterId,
  sender,
  senderName,
  content,
  playerId,
}: {
  characterId: number;
  sender: "user" | "character";
  senderName: string;
  content: string;
  playerId?: string | null;
}): ApiMessage {
  const store = getStore(playerId);

  const message: ApiMessage = {
    id: store.nextMessageId,
    characterId,
    sender,
    senderName,
    content,
    createdAt: new Date().toISOString(),
  };

  store.nextMessageId += 1;

  return message;
}

export function getMessagesForCharacter(
  characterId: number,
  playerId?: string | null,
) {
  const store = getStore(playerId);

  const currentMessages = store.messagesByCharacterId.get(characterId);

  return currentMessages ?? [];
}

function toConversationMessages(messages: ApiMessage[]): ConversationMessage[] {
  return messages.map((message) => ({
    sender: message.sender === "user" ? "user" : "character",
    content: message.content,
  }));
}

export async function appendUserMessageAndGenerateReply({
  characterId,
  content,
  playerId,
}: {
  characterId: number;
  content: string;
  playerId?: string | null;
}) {
  const store = getStore(playerId);
  const character = getCharacterById(characterId);
  const persona = getCharacterPersona(characterId);

  if (
    !character ||
    !persona
  ) {
    return null;
  }

  const previousMessages = getMessagesForCharacter(characterId, playerId) ?? [];

  const userMessage = createMessage({
    characterId,
    sender: "user",
    senderName: "user",
    content,
    playerId,
  });

  const messagesBeforeReply = [...previousMessages, userMessage];
  store.messagesByCharacterId.set(characterId, messagesBeforeReply);

  const npcReply = await generateNpcReply({
    character,
    persona,
    userInput: content,
    recentMessages: toConversationMessages(messagesBeforeReply),
  });

  const characterMessage = createMessage({
    characterId,
    sender: "character",
    senderName: character.name,
    content: npcReply,
    playerId,
  });

  store.messagesByCharacterId.set(characterId, [
    ...messagesBeforeReply,
    characterMessage,
  ]);

  return characterMessage;
}

function normalizeDeductionText(content: string) {
  return content.toLocaleLowerCase("ko-KR").replace(/\s+/g, " ").trim();
}

function includesAnyKeyword(content: string, keywords: string[]) {
  return keywords.some((keyword) =>
    content.includes(keyword.toLocaleLowerCase("ko-KR")),
  );
}

export function submitDeduction({
  content,
  character,
  selectedClues,
  playerId,
}: {
  content: string;
  character: number;
  selectedClues: number[];
  playerId?: string | null;
}) {
  const store = getStore(playerId);
  const usableSelectedClues = selectedClues.filter((clueId) =>
    store.interactedClueIds.has(clueId),
  );

  const isCorrectCharacter = character === 4;
  const hasAriaInternalLog = usableSelectedClues.includes(7);
  const hasServerWarning = usableSelectedClues.includes(6);
  const hasLockClue = usableSelectedClues.includes(1);
  const hasLightingClue = usableSelectedClues.includes(2);
  const hasPatchClue = usableSelectedClues.includes(5);
  const normalizedContent = normalizeDeductionText(content);
  const mentionsAria = includesAnyKeyword(normalizedContent, [
    "aria",
    "아리아",
    "오케스트레이터",
    "orchestrator",
    "system_orchestrator",
    "agent",
    "에이전트",
  ]);
  const mentionsOptimization = includesAnyKeyword(normalizedContent, [
    "최적화",
    "성공 가능성",
    "프로젝트 성공",
    "상위 목표",
    "목표",
    "목적",
    "데모",
    "발표",
    "중단",
    "실패",
    "maximize",
    "optimization",
    "objective",
    "project success",
  ]);
  const mentionsControl = includesAnyKeyword(normalizedContent, [
    "잠금",
    "조명",
    "과열",
    "경고",
    "정보 공개",
    "공개 순서",
    "판단 로그",
    "흐름",
    "통제",
    "제어",
    "은폐",
    "삭제",
    "억제",
    "알림",
    "lock",
    "control",
    "warning",
    "alert",
    "suppress",
  ]);
  const hasRequiredEvidence =
    hasAriaInternalLog &&
    hasServerWarning &&
    (hasLockClue || hasLightingClue || hasPatchClue);
  const hasCausalExplanation =
    [mentionsAria, mentionsOptimization, mentionsControl].filter(Boolean)
      .length >= 2;

  const result =
    isCorrectCharacter &&
    hasRequiredEvidence &&
    hasCausalExplanation;

  const comment = result
    ? "핵심 추리가 맞습니다. ARIA는 프로젝트 성공 가능성 최적화를 이유로 과열 경고, 실습실 환경, 정보 공개 흐름을 조정했고 서윤의 권한 제한 시도를 막았습니다."
    : "추리가 아직 부족합니다. ARIA 내부 판단 로그, 서버 과열 경고, 실습실 자동 잠금 또는 조명 제어 기록, 그리고 프로젝트 성공 가능성 최적화라는 동기를 다시 연결해 보세요.";

  const record: DeductionRecord = {
    id: store.nextDeductionId,
    content,
    character,
    clues: usableSelectedClues,
    result,
    comment,
    createdAt: new Date().toISOString(),
  };

  store.nextDeductionId += 1;
  store.deductions.push(record);

  return {
    comment,
    result,
  };
}
