import "server-only";

import type { Character } from "@/data/gameData";
import { baseNpcRules } from "@/server/personas/baseNpcRules";
import type { CharacterPersona } from "@/server/personas/characterPersonas";

type OllamaRole = "system" | "user" | "assistant";

type OllamaMessage = {
  role: OllamaRole;
  content: string;
};

type OllamaChatResponse = {
  model: string;
  created_at: string;
  message?: {
    role: string;
    content: string;
    thinking?: string;
  };
  done: boolean;
  done_reason?: string;
  error?: string;
};

export type ConversationMessage = {
  sender: "user" | "character" | "npc" | "assistant";
  content: string;
};

export type GenerateNpcReplyParams = {
  character: Character;
  persona: CharacterPersona;
  userInput: string;
  recentMessages?: ConversationMessage[];
  conversationSummary?: string;
};

export const LLM_NOT_CONFIGURED_MESSAGE =
  "개발자는 LLM API를 연결해주세요.";

const LLM_API_ENABLED = process.env.LLM_API_ENABLED === "true";
const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL?.trim() ?? "";
const OLLAMA_MODEL = process.env.OLLAMA_MODEL?.trim() || "qwen3:8b";

const OLLAMA_TIMEOUT_MS = 60_000;
const MAX_RECENT_MESSAGES = 16;
const MAX_MESSAGE_CONTENT_LENGTH = 1200;
const MAX_REPLY_LENGTH = 700;

function buildCharacterPrompt(character: Character, persona: CharacterPersona) {
  const clueReactions = Object.entries(persona.clueReactions)
    .map(([clueId, reaction]) => `- 단서 ${clueId}: ${reaction}`)
    .join("\n");

  return `
${baseNpcRules}

[공개 캐릭터 정보]
이름: ${character.name}
나이: ${character.age}
역할: ${character.role}
성격: ${character.personality}
설명: ${character.description}
의심 지점: ${character.suspicionPoint}

[비공개 캐릭터 시나리오]
${persona.systemPrompt}

[조회 가능한 데이터 / 권한 범위]
${persona.allowedData.map((item) => `- ${item}`).join("\n")}

[이 캐릭터의 주요 의심 대상]
${persona.suspicionTarget}

[이 캐릭터의 추리 방식]
${persona.deductionStyle}

[캐릭터가 알고 있는 정보]
${persona.knownFacts.map((fact) => `- ${fact}`).join("\n")}

[캐릭터가 숨기는 정보]
${persona.hiddenFacts.map((fact) => `- ${fact}`).join("\n")}

[거짓말 / 회피 규칙]
${persona.lieRules.map((rule) => `- ${rule}`).join("\n")}

[단서별 반응 규칙]
${clueReactions || "- 별도 단서 반응 없음"}
`.trim();
}

function buildSummaryMessage(conversationSummary?: string): OllamaMessage | null {
  if (!conversationSummary?.trim()) {
    return null;
  }

  return {
    role: "system",
    content: `
[지금까지의 대화 요약]
${conversationSummary.trim()}

이 요약은 아래 대화의 배경 정보다.
현재 답변에서는 이 요약과 최근 대화를 함께 참고하라.
`.trim(),
  };
}

function normalizeMessageContent(content: string) {
  return content.trim().slice(0, MAX_MESSAGE_CONTENT_LENGTH);
}

function convertRecentMessagesToOllamaMessages(
  recentMessages: ConversationMessage[] = [],
): OllamaMessage[] {
  return recentMessages
    .filter((message) => message.content.trim().length > 0)
    .slice(-MAX_RECENT_MESSAGES)
    .map((message) => ({
      role: message.sender === "user" ? "user" : "assistant",
      content: normalizeMessageContent(message.content),
    }));
}

function removeThinkingText(text: string) {
  return text
    .replace(/<think>[\s\S]*?<\/think>/gi, "")
    .replace(/Thinking\.\.\.[\s\S]*?\.\.\.done thinking\./gi, "")
    .replace(/Thinking\.\.\.[\s\S]*?done thinking\./gi, "")
    .trim();
}

function removeCodeFence(text: string) {
  return text
    .replace(/^```(?:json|markdown|md|txt)?/i, "")
    .replace(/```$/i, "")
    .trim();
}

function removeOuterQuotes(text: string) {
  let result = text.trim();

  const quotePairs: [string, string][] = [
    ['"', '"'],
    ["'", "'"],
    ["“", "”"],
    ["‘", "’"],
    ["「", "」"],
    ["『", "』"],
  ];

  for (const [open, close] of quotePairs) {
    if (result.startsWith(open) && result.endsWith(close)) {
      result = result.slice(open.length, result.length - close.length).trim();
    }
  }

  return result;
}

function cleanNpcReply(rawText: string) {
  let text = rawText;

  text = removeThinkingText(text);
  text = removeCodeFence(text);
  text = removeOuterQuotes(text);

  text = text
    .replace(/^assistant\s*:/i, "")
    .replace(/^npc\s*:/i, "")
    .replace(/^캐릭터\s*:/i, "")
    .trim();

  if (text.length > MAX_REPLY_LENGTH) {
    text = `${text.slice(0, MAX_REPLY_LENGTH).trim()}...`;
  }

  return text;
}

function fallbackReply(character: Character) {
  return `${character.name}은 잠시 말을 고르더니 대답을 피했다.`;
}

export function getLlmStatus() {
  return {
    provider: "ollama",
    model: OLLAMA_MODEL,
    configured: LLM_API_ENABLED && Boolean(OLLAMA_BASE_URL),
  };
}

async function postOllamaChat(messages: OllamaMessage[]) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, OLLAMA_TIMEOUT_MS);

  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
      },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        stream: false,
        think: false,
        messages,
        options: {
          num_ctx: 8192,
          temperature: 0.7,
          top_p: 0.9,
          repeat_penalty: 1.1,
        },
        keep_alive: "10m",
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorText = await response.text();

      throw new Error(
        `Ollama API 요청 실패: ${response.status} ${response.statusText} ${errorText}`,
      );
    }

    const data = (await response.json()) as OllamaChatResponse;

    if (data.error) {
      throw new Error(`Ollama 응답 오류: ${data.error}`);
    }

    return data;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function generateNpcReply({
  character,
  persona,
  userInput,
  recentMessages = [],
  conversationSummary,
}: GenerateNpcReplyParams): Promise<string> {
  const trimmedUserInput = userInput.trim();

  if (!trimmedUserInput) {
    return fallbackReply(character);
  }

  if (!getLlmStatus().configured) {
    return LLM_NOT_CONFIGURED_MESSAGE;
  }

  const messages: OllamaMessage[] = [
    {
      role: "system",
      content: buildCharacterPrompt(character, persona),
    },
  ];

  const summaryMessage = buildSummaryMessage(conversationSummary);

  if (summaryMessage) {
    messages.push(summaryMessage);
  }

  messages.push(...convertRecentMessagesToOllamaMessages(recentMessages));
  messages.push({
    role: "user",
    content: normalizeMessageContent(trimmedUserInput),
  });

  try {
    const data = await postOllamaChat(messages);
    const rawReply = data.message?.content ?? "";
    const cleanedReply = cleanNpcReply(rawReply);

    if (!cleanedReply) {
      return fallbackReply(character);
    }

    return cleanedReply;
  } catch (error) {
    console.error("[llmClient] NPC 응답 생성 실패:", error);

    return fallbackReply(character);
  }
}
