export type InteractionState = {
  id: number;
  interacted: boolean;
  unlocked: boolean;
};

export type ChatMessage = {
  speaker: "player" | "npc";
  text: string;
};

export type DeductionRequest = {
  content: string;
  character: number;
  clues: number[];
};

export type DeductionResponse = {
  comment: string;
  result: boolean;
};

export type TraceProbeResponse = {
  attempt: number;
  unlocked: boolean;
  clueId: number;
  message: string;
};

type ApiMessage = {
  id: number;
  characterId?: number;
  character_id?: number;
  user_id?: string;
  sender: "user" | "character" | "me" | string;
  senderName?: string;
  content: string;
  createdAt?: string;
  created_at?: string;
};

const USER_ID_STORAGE_KEY = "demo-day-incident-user-id";
const LEGACY_PLAYER_ID_STORAGE_KEY = "demo-day-incident-player-id";
const BACKEND_API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "https://demoday.yunseong.dev"
).replace(/\/$/, "");

function createFallbackId() {
  return `player-${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .slice(2, 10)}`;
}

function getPlayerId() {
  if (typeof window === "undefined") {
    return "server-render";
  }

  const existingPlayerId =
    localStorage.getItem(USER_ID_STORAGE_KEY) ??
    localStorage.getItem(LEGACY_PLAYER_ID_STORAGE_KEY);

  if (existingPlayerId) {
    localStorage.setItem(USER_ID_STORAGE_KEY, existingPlayerId);
    return existingPlayerId;
  }

  const nextPlayerId =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : createFallbackId();

  localStorage.setItem(USER_ID_STORAGE_KEY, nextPlayerId);

  return nextPlayerId;
}

function rotatePlayerId() {
  if (typeof window === "undefined") {
    return "server-render";
  }

  const nextPlayerId =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : createFallbackId();

  localStorage.setItem(USER_ID_STORAGE_KEY, nextPlayerId);
  localStorage.removeItem(LEGACY_PLAYER_ID_STORAGE_KEY);

  return nextPlayerId;
}

function convertApiMessageToChatMessage(message: ApiMessage): ChatMessage {
  const isPlayerMessage = message.sender === "user" || message.sender === "me";

  return {
    speaker: isPlayerMessage ? "player" : "npc",
    text: message.content,
  };
}

async function requestJson<T>(
  url: string,
  init?: RequestInit,
  baseUrl = BACKEND_API_BASE_URL,
): Promise<T> {
  const response = await fetch(`${baseUrl}${url}`, {
    ...init,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "x-user-id": getPlayerId(),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export const gameApi = {
  async markClueInteracted(clueId: number): Promise<void> {
    await requestJson(`/api/clues/${clueId}`, {
      method: "POST",
    });
  },

  async getClueInteractions(): Promise<InteractionState[]> {
    const data = await requestJson<{
      clues: { clue_id: number; interacted: boolean; unlocked?: boolean }[];
    }>("/api/clues");

    return data.clues.map((clue) => ({
      id: clue.clue_id,
      interacted: clue.interacted,
      unlocked: clue.unlocked ?? true,
    }));
  },

  async markCharacterInteracted(characterId: number): Promise<void> {
    await requestJson(`/api/character/${characterId}`, {
      method: "POST",
    });
  },

  async getCharacterInteractions(): Promise<InteractionState[]> {
    const data = await requestJson<{
      characters: {
        character_id: number;
        interacted: boolean;
        unlocked?: boolean;
      }[];
    }>("/api/characters");

    return data.characters.map((character) => ({
      id: character.character_id,
      interacted: character.interacted,
      unlocked: character.unlocked ?? true,
    }));
  },

  async getCharacterMessages(characterId: number): Promise<ChatMessage[]> {
    const data = await requestJson<{
      character_id: number;
      messages: ApiMessage[];
    }>(`/api/characters/${characterId}/messages`);

    return data.messages.map(convertApiMessageToChatMessage);
  },

  async sendCharacterMessage(
    characterId: number,
    content: string
  ): Promise<ChatMessage> {
    const data = await requestJson<{
      character_id: number;
      content: string;
    }>(`/api/characters/${characterId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });

    return {
      speaker: "npc",
      text: data.content,
    };
  },

  async submitDeduction(
    request: DeductionRequest
  ): Promise<DeductionResponse> {
    return requestJson<DeductionResponse>("/api/deductions", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  async probeRecoveredTrace(): Promise<TraceProbeResponse> {
    return requestJson<TraceProbeResponse>("/api/clues/trace", {
      method: "POST",
    }, "");
  },

  async resetProgress(): Promise<void> {
    await requestJson("/api/progress/reset", {
      method: "POST",
    }, "");
  },

  startNewUserSession(): void {
    rotatePlayerId();
  },
};
