"""FastAPI service — exposes every registered agent as POST /agents/{name}/run."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

import stakagents.agents  # noqa: F401  — importing populates the registry
from stakagents.core.registry import all_agents, get
from stakagents.core.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_tracing(service_name="stakagents-service")  # traces every request for free
    yield


app = FastAPI(title="stakagents", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/agents")
def list_agents() -> dict:
    """List agents and their I/O schemas (the Pydantic models double as API docs)."""
    return {
        name: {
            "input_schema": agent.input_model.model_json_schema(),
            "output_schema": agent.output_model.model_json_schema(),
        }
        for name, agent in all_agents().items()
    }


@app.post("/agents/{name}/run")
def run_agent(name: str, payload: dict) -> dict:
    try:
        agent = get(name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown agent: {name!r}")

    try:
        validated = agent.input_model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())

    result = agent.run(validated)  # sync; FastAPI runs it in a threadpool
    return result.model_dump()
