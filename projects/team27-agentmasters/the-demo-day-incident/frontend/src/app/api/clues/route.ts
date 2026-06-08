import { NextResponse } from "next/server";
import {
  getClueInteractions,
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
    clues: getClueInteractions(playerId)
      .filter((clue) => clue.interacted)
      .map((clue) => ({
        user_id: clue.user_id,
        clue_id: clue.clue_id,
        interacted: clue.interacted,
      })),
  });
}
