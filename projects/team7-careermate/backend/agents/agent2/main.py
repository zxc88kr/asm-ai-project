from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .job_requirement_agent import run_agent2
from .models import Agent2Request, HealthResponse, JobRequirementOutput


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="CareerMate Agent2", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(ok=True, service="agent2")


@app.post("/agent2/job-requirement", response_model=JobRequirementOutput)
async def job_requirement(request: Agent2Request) -> JobRequirementOutput:
    result = await run_agent2(request)
    output = JobRequirementOutput(
        companies=result.companies,
        required_skills=result.required_skills,
        preferred_skills=result.preferred_skills,
        required_experience=result.required_experience,
        keywords=result.keywords,
    )
    print("\n================ [Agent2 Job Requirement Output] ================")
    print(json.dumps(output.model_dump(mode="json"), ensure_ascii=False, indent=2))
    print("=================================================================\n")
    return output
