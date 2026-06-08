import { NextResponse } from "next/server";
import {
  getPlayerIdFromRequest,
  markCharacterInteracted,
} from "@/lib/mockBackendStore";

export async function POST(
  request: Request,
  context: { params: Promise<{ characterId: string }> },
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
    return NextResponse.json(
      { message: "유효하지 않은 인물 ID입니다." },
      { status: 400 },
    );
  }

  const result = markCharacterInteracted(numericCharacterId, playerId);

  if (!result) {
    return NextResponse.json(
      { detail: `Character ${numericCharacterId} not found` },
      { status: 404 },
    );
  }

  return NextResponse.json({
    message: `Character ${numericCharacterId} state updated successfully.`,
  });
}
