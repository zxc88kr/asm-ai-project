import { NextResponse } from "next/server";
import {
  appendUserMessageAndGenerateReply,
  getMessagesForCharacter,
  getPlayerIdFromRequest,
} from "@/lib/mockBackendStore";

export async function GET(
  request: Request,
  context: { params: Promise<{ characterId: string }> }
) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  const { characterId } = await context.params;
  const numericCharacterId = Number(characterId);

  if (!Number.isFinite(numericCharacterId)) {
    return NextResponse.json({ message: "유효하지 않은 인물 ID입니다." }, { status: 400 });
  }

  const messages = getMessagesForCharacter(numericCharacterId, playerId);

  return NextResponse.json({
    character_id: numericCharacterId,
    messages: messages.map((message) => ({
      id: message.id,
      user_id: playerId,
      sender: message.sender === "user" ? "me" : message.senderName,
      content: message.content,
      createdAt: message.createdAt,
    })),
  });
}

export async function POST(
  request: Request,
  context: { params: Promise<{ characterId: string }> }
) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  const { characterId } = await context.params;
  const numericCharacterId = Number(characterId);

  if (!Number.isFinite(numericCharacterId)) {
    return NextResponse.json({ message: "유효하지 않은 인물 ID입니다." }, { status: 400 });
  }

  const body = (await request.json().catch(() => null)) as { content?: string } | null;
  const content = body?.content?.trim();

  if (!content) {
    return NextResponse.json({ message: "메시지 내용이 비어 있습니다." }, { status: 400 });
  }

  const reply = await appendUserMessageAndGenerateReply({
    characterId: numericCharacterId,
    content,
    playerId,
  });

  if (!reply) {
    return NextResponse.json({ message: "인물을 찾을 수 없습니다." }, { status: 404 });
  }

  return NextResponse.json({
    character_id: numericCharacterId,
    content: reply.content,
  });
}
