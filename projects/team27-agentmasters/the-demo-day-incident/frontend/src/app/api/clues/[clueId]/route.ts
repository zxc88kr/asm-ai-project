import { NextResponse } from "next/server";
import {
  getPlayerIdFromRequest,
  markClueInteracted,
} from "@/lib/mockBackendStore";

export async function POST(
  request: Request,
  context: { params: Promise<{ clueId: string }> }
) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  const { clueId } = await context.params;
  const numericClueId = Number(clueId);

  if (!Number.isFinite(numericClueId)) {
    return NextResponse.json({ message: "유효하지 않은 단서 ID입니다." }, { status: 400 });
  }

  const result = markClueInteracted(numericClueId, playerId);

  if (!result) {
    return NextResponse.json(
      { detail: `Clue ${numericClueId} not found` },
      { status: 404 },
    );
  }

  return NextResponse.json({
    message: `Clue ${numericClueId} state updated successfully.`,
  });
}
