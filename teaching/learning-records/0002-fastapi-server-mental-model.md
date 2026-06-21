# 0002 - FastAPI Server Mental Model

## Date

2026-06-20

## Context

The learner understood CRUD and endpoints but wanted to deeply understand the server concept and how FastAPI fits the agent project.

## Learned

FastAPI should be taught as the HTTP doorway to existing Python logic. Uvicorn is the running server process, FastAPI is the router/application layer, and the LangGraph agent remains the business logic.

## Implication

The first implementation should avoid production complexity. Build `/health` first, then `/triage`, then add async, RAG, MCP, and Docker only after the basic request-response boundary works.

## Next Review

After the learner builds `/health` and `/triage`, ask them to explain the request lifecycle from HTTP JSON to LangGraph invocation to JSON response.
