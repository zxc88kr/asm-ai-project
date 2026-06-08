# 2026-06-03 — GitHub Actions GHCR Docker Image CI

- Date: 2026-06-03
- GitHub Issue: #10
- Status: Done

## Goal

Add GitHub Actions CI that builds the backend Docker image and pushes it to GitHub Container Registry on `main` branch pushes.

## Non-goals

- Do not change application runtime behavior.
- Do not add deployment to a server or cloud host.
- Do not introduce new app dependencies beyond the existing requirements.

## Context / Constraints

- Repository currently has a FastAPI app but no Dockerfile or workflow.
- The requested registry is interpreted as `ghcr.io` for GitHub Container Registry.
- Workflow should not run for pull requests.
- `requirements.txt` was UTF-16 encoded, which can break normal Linux container installs; normalize it to UTF-8.

## Approach (Checklist)
- [x] **Step 0: Recon** (Inspect existing code, locate files)
- [x] **Step 1: Implementation** (Code changes, file paths)
- [x] **Step 2: Tests** (Unit tests, manual verification steps)
- [x] **Step 3: Rollout / Rollback** (Feature flags, migration steps)

## Validation
- **Commands to run:** `docker build -t the-demo-day-incident-backend:local .`
- **Expected output:** Docker image builds successfully and can run `uvicorn main:app`.

## Risks & Rollback
- **Risks:** The generated GHCR package name depends on the repository owner/name. Runtime database state inside the container defaults to local SQLite storage unless mounted externally.
- **Rollback steps:** Revert the Dockerfile/workflow changes.

## Open Questions
- None.
