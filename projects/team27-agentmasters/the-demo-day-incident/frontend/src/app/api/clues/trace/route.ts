import { NextResponse } from "next/server";
import {
  getPlayerIdFromRequest,
  probeRecoveredTrace,
} from "@/lib/mockBackendStore";

export async function POST(request: Request) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  return NextResponse.json(probeRecoveredTrace(playerId));
}
