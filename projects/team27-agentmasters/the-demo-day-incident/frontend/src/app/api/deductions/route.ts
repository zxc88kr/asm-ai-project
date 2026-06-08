import { NextResponse } from "next/server";
import {
  getPlayerIdFromRequest,
  submitDeduction,
} from "@/lib/mockBackendStore";

export async function POST(request: Request) {
  const playerId = getPlayerIdFromRequest(request);

  if (!playerId) {
    return NextResponse.json(
      { detail: "X-User-Id header is required" },
      { status: 422 },
    );
  }

  const body = (await request.json().catch(() => null)) as
    | {
        content?: string;
        character?: number;
        clues?: number[];
      }
    | null;

  const content = body?.content?.trim();
  const character = Number(body?.character);
  const selectedClues = Array.isArray(body?.clues)
    ? body.clues.map(Number).filter((value) => Number.isFinite(value))
    : [];

  if (!content) {
    return NextResponse.json({ message: "추리 내용이 비어 있습니다." }, { status: 400 });
  }

  if (!Number.isFinite(character)) {
    return NextResponse.json({ message: "지목한 인물이 유효하지 않습니다." }, { status: 400 });
  }

  const result = submitDeduction({
    content,
    character,
    selectedClues,
    playerId,
  });

  return NextResponse.json(result);
}
