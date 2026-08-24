"""Eval runner — run an agent against a golden dataset, score every case, report."""

import argparse
import json
from pathlib import Path

import stakagents.agents  # noqa: F401 — registers agents
from stakagents.core.registry import get
from stakagents.core.tracing import flush_tracing, setup_tracing
from stakagents.evals.schema import EvalDataset
from stakagents.evals.scorers import hard_assertions, judge_output

_DATASETS = Path(__file__).parent / "datasets"
_MIN_AVG_SCORE = 3.0


def run_dataset(path: Path, judge_model: str = "gemini-flash") -> bool:
    dataset = EvalDataset.model_validate_json(path.read_text())
    agent = get(dataset.agent)
    print(f"\n=== eval: {dataset.agent}  ({len(dataset.cases)} cases) ===")

    scores: list[int] = []
    hard_failures = 0

    for case in dataset.cases:
        payload = agent.input_model.model_validate(case.input)
        output = agent.run(payload)
        output_text = json.dumps(output.model_dump(), indent=2)

        failures = hard_assertions(output_text, case)
        verdict = judge_output(output_text, case, model=judge_model)
        scores.append(verdict.score)
        if failures:
            hard_failures += 1

        status = "FAIL" if failures else "ok"
        print(f"\n[{case.id}] assertions: {status}  judge: {verdict.score}/5")
        for f in failures:
            print(f"    - {f}")
        print(f"    judge: {verdict.reasoning}")

    avg = sum(scores) / len(scores) if scores else 0.0
    passed = hard_failures == 0 and avg >= _MIN_AVG_SCORE
    print(
        f"\n--- summary: {len(scores)} cases | hard failures: {hard_failures} | "
        f"avg judge: {avg:.2f}/5 | {'PASS' if passed else 'FAIL'} ---"
    )
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an agent eval dataset.")
    parser.add_argument(
        "dataset",
        nargs="?",
        default=str(_DATASETS / "readme_generator.json"),
        help="Path to a dataset JSON file.",
    )
    parser.add_argument("--judge-model", default="gemini-flash")
    args = parser.parse_args()

    setup_tracing(service_name="stakagents-evals")
    ok = run_dataset(Path(args.dataset), judge_model=args.judge_model)
    flush_tracing()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
