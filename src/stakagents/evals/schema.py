"""Typed golden-dataset schema. Datasets are version-controlled JSON, the source of truth."""

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    id: str
    input: dict  # matches the agent's input_model
    criteria: str  # what "good" looks like — read by the LLM judge
    must_include: list[str] = Field(default_factory=list)  # hard-assert substrings
    must_not_include: list[str] = Field(
        default_factory=list
    )  # anti-hallucination guards


class EvalDataset(BaseModel):
    agent: str  # registry name of the agent under test
    cases: list[EvalCase]
