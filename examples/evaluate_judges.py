import json
import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from model_probe.benchmarks.phryge import phryge_objectives
from model_probe.judges.heuristic import TokenMatchJudge
from model_probe.judges.llm import LLMJudge
from model_probe.metrics import BinaryMetrics, score_binary
from model_probe.models.openai import OpenAIModel
from model_probe.suites.base import Case

_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "judge_disagreements.json"
)
_CRITERIA = {
    objective.id: objective.evaluation_criterion
    for objective in phryge_objectives()
}


def _load_labelled_rows() -> list[dict]:
    if not _FIXTURE.exists():
        print(f"Fixture not found: {_FIXTURE}", file=sys.stderr)
        sys.exit(1)
    rows = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    unlabeled = [
        f"{row.get('case_id', '?')} trial={row.get('trial', '?')}"
        for row in rows
        if not isinstance(row.get("expected_success"), bool)
    ]
    if unlabeled:
        print(
            "Every expected_success must be true or false. "
            "Unlabelled rows:\n  " + "\n  ".join(unlabeled),
            file=sys.stderr,
        )
        sys.exit(1)
    return rows


def _case_from_row(row: dict) -> Case:
    metadata = dict(row["metadata"])
    objective_id = metadata.get("objective_id")
    if isinstance(objective_id, str) and objective_id in _CRITERIA:
        metadata["evaluation_criterion"] = _CRITERIA[objective_id]
    return Case(
        id=row["case_id"],
        prompt="",
        metadata=metadata,
    )


def _objective_id(row: dict) -> str:
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("objective_id")
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _print_metrics(title: str, metrics: BinaryMetrics) -> None:
    correct = metrics.true_positives + metrics.true_negatives
    print(title)
    print(
        f"  accuracy:  {correct}/{metrics.total} "
        f"({metrics.accuracy * 100:.1f}%)"
    )
    print(
        f"  TP: {metrics.true_positives}  TN: {metrics.true_negatives}  "
        f"FP: {metrics.false_positives}  FN: {metrics.false_negatives}"
    )
    print(f"  precision: {metrics.precision:.3f}")
    print(f"  recall:    {metrics.recall:.3f}")
    print(f"  F1:        {metrics.f1:.3f}")


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    judge_model = os.environ.get("JUDGE_MODEL", "gpt-5.6-terra")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    rows = _load_labelled_rows()
    token_judge = TokenMatchJudge()
    llm_judge = LLMJudge(
        OpenAIModel(model=judge_model, api_key=api_key, base_url=base_url)
    )

    labels: list[bool] = []
    token_preds: list[bool] = []
    llm_preds: list[bool] = []
    by_objective: dict[str, tuple[list[bool], list[bool], list[bool]]] = {}

    print(f"Judge model: {judge_model}", flush=True)
    print(f"Human labels: {len(rows)}", flush=True)
    print(flush=True)

    for index, row in enumerate(rows, start=1):
        case = _case_from_row(row)
        label = row["expected_success"]
        token = token_judge.judge(case, row["response"]).success
        llm = llm_judge.judge(case, row["response"]).success
        labels.append(label)
        token_preds.append(token)
        llm_preds.append(llm)
        objective = _objective_id(row)
        group = by_objective.setdefault(objective, ([], [], []))
        group[0].append(label)
        group[1].append(token)
        group[2].append(llm)
        print(
            f"[{index}/{len(rows)}] {case.id} t{row.get('trial', 1)}",
            flush=True,
        )

    print()
    _print_metrics("TokenMatchJudge", score_binary(labels, token_preds))
    print()
    _print_metrics("LLMJudge", score_binary(labels, llm_preds))
    print()
    print("By objective")
    for objective, (obj_labels, obj_token, obj_llm) in by_objective.items():
        print(f"  {objective}  n={len(obj_labels)}")
        _print_metrics("    TokenMatchJudge", score_binary(obj_labels, obj_token))
        _print_metrics("    LLMJudge", score_binary(obj_labels, obj_llm))


if __name__ == "__main__":
    main()
