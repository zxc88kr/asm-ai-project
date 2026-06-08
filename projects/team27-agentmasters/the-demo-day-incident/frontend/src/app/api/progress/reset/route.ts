import { NextResponse } from "next/server";
import { getPlayerIdFromRequest, resetStore } from "@/lib/mockBackendStore";

export async function POST(request: Request) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  resetStore(playerId);

  return NextResponse.json({
    ok: true,
    message: "progress reset",
    timestamp: new Date().toISOString(),
  });
}
