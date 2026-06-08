import { NextResponse } from "next/server";
import {
  getCharacterInteractions,
  getPlayerIdFromRequest,
} from "@/lib/mockBackendStore";

export async function GET(request: Request) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  return NextResponse.json({
    characters: getCharacterInteractions(playerId)
      .filter((character) => character.interacted)
      .map((character) => ({
        user_id: character.user_id,
        character_id: character.character_id,
        interacted: character.interacted,
      })),
  });
}
