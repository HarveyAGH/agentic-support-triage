import sys
from pathlib import Path

from langchain_core.messages import HumanMessage


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent import app, haiku
from evals.golden_dataset import GOLDEN_DATASET
from evals.graders import (
    grade_content_contains,
    grade_expected_escalation,
    grade_expected_route,
    grade_file_written,
    grade_no_error,
    grade_not_contains,
    grade_under_hop_limit,
    grade_quality_llm_judge
)


PASS_THRESHOLD = 0.90


GRADERS = {
    "no_error": grade_no_error,
    "expected_route": grade_expected_route,
    "content_contains": grade_content_contains,
    "not_contains": grade_not_contains,
    "expected_escalation": grade_expected_escalation,
    "file_written": grade_file_written,
    "hop_limit": grade_under_hop_limit,
    "quality_llm_judge": lambda run_result, expected: grade_quality_llm_judge(run_result, expected, haiku),
}


def run_single_eval(example: dict, index: int) -> dict:
    config = {
        "configurable": {"thread_id": f"eval-{index}"},
        "tags": ["eval", f"difficulty:{example.get('difficulty', 'unknown')}"],
        "metadata": {
            "eval_index": index,
            "expected_route": example.get("expected_route"),
            "difficulty": example.get("difficulty", "unknown"),
        },
    }

    try:
        run_result = app.invoke(
            {"messages": [HumanMessage(content=example["input"])]},
            config=config,
        )
    except Exception as exc:
        return {
            "input": example["input"],
            "difficulty": example.get("difficulty", "unknown"),
            "scores": {
                "run_error": {
                    "score": 0.0,
                    "reason": f"Agent invocation failed: {exc}",
                }
            },
            "overall": 0.0,
            "passed": False,
        }

    scores = {
        name: grader(run_result, example)
        for name, grader in GRADERS.items()
    }
    overall = sum(score["score"] for score in scores.values()) / len(scores)

    return {
        "input": example["input"],
        "difficulty": example.get("difficulty", "unknown"),
        "scores": scores,
        "overall": overall,
        "passed": overall >= PASS_THRESHOLD,
    }


def run_eval_suite() -> list[dict]:
    results = []
    print(f"Running {len(GOLDEN_DATASET)} evals...\n")

    for index, example in enumerate(GOLDEN_DATASET, start=1):
        print(f"[{index}/{len(GOLDEN_DATASET)}] {example['input']}")
        result = run_single_eval(example, index)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"  {status} overall={result['overall']:.2f} difficulty={result['difficulty']}")

        for grader_name, score in result["scores"].items():
            marker = "OK" if score["score"] >= PASS_THRESHOLD else "NO"
            print(f"    {marker} {grader_name}: {score['score']:.2f} - {score['reason']}")
        print()

    passed = sum(1 for result in results if result["passed"])
    total = len(results)
    pass_rate = passed / total if total else 0.0

    print("=" * 60)
    print(f"RESULTS: {passed}/{total} passed ({pass_rate:.1%})")
    print(f"Threshold per example: {PASS_THRESHOLD:.0%}")

    if pass_rate < PASS_THRESHOLD:
        raise SystemExit(1)

    return results


if __name__ == "__main__":
    run_eval_suite()
