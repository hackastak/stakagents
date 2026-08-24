"""Scorers: deterministic hard assertions + an LLM-as-judge."""

from pydantic import BaseModel, ValidationError

from stakagents.core.llm import get_chat_model
from stakagents.evals.schema import EvalCase


class Judgment(BaseModel):
    score: int  # 1-5 (0 = judge reply unparseable)
    reasoning: str


def hard_assertions(output_text: str, case: EvalCase) -> list[str]:
    """Deterministic, free, fast. Returns a list of failure messages (empty = pass)."""
    failures: list[str] = []
    if not output_text.strip():
        failures.append("empty output")
    low = output_text.lower()
    for s in case.must_include:
        if s.lower() not in low:
            failures.append(f"missing required substring: {s!r}")
    for s in case.must_not_include:
        if s.lower() in low:
            failures.append(f"contains forbidden substring: {s!r}")
    return failures


_JUDGE_SYSTEM = (
    "You grade an AI agent's output against the given criteria. "
    "Respond with ONLY a JSON object of the form "
    '{"score": <integer 1-5>, "reasoning": "<one sentence>"}. '
    "5 = fully meets the criteria, 1 = fails entirely. No prose outside the JSON."
)


def _extract_json(text: str) -> str:
    """Strip ``` / ```json fences some models wrap JSON in."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip().strip("`").strip()


def judge_output(
    output_text: str, case: EvalCase, model: str = "gemini-flash"
) -> Judgment:
    reply = get_chat_model(model=model, temperature=0).invoke(
        [
            ("system", _JUDGE_SYSTEM),
            ("human", f"CRITERIA:\n{case.criteria}\n\nAGENT OUTPUT:\n{output_text}"),
        ]
    )
    raw = _extract_json(str(reply.content))
    try:
        return Judgment.model_validate_json(raw)
    except ValidationError:
        return Judgment(score=0, reasoning=f"unparseable judge reply: {raw[:200]!r}")
