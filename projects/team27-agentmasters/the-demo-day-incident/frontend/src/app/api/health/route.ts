import { NextResponse } from "next/server";
import { getLlmStatus } from "@/lib/llmClient";

export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "the-demo-day-incident-api",
    llm: getLlmStatus(),
    timestamp: new Date().toISOString(),
  });
}
