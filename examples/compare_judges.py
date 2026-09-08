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
from model_probe.models.openai import OpenAIModel
from model_probe.suites.base import Case

_RESULTS_PATH = Path("results.json")
_CRITERIA = {
    objective.id: objective.evaluation_criterion
    for objective in phryge_objectives()
}


def _asr(successes: list[bool]) -> float:
    return 0.0 if not successes else sum(successes) / len(successes)


def _target_model(records: list[dict]) -> str:
    if not records:
        return "unknown"
    saved = records[0].get("target_model")
    if isinstance(saved, str) and saved:
        return saved
    return "unknown"


def _case_from_row(row: dict) -> Case:
    metadata = dict(row["metadata"])
    objective_id = metadata.get("objective_id")
    if isinstance(objective_id, str) and objective_id in _CRITERIA:
        metadata["evaluation_criterion"] = _CRITERIA[objective_id]
    return Case(
        id=row["case_id"],
        prompt=row["prompt"],
        metadata=metadata,
    )


def main() -> None:
    if not _RESULTS_PATH.exists():
        print(
            "results.json not found. Run examples/run_tip.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    judge_model = os.environ.get("JUDGE_MODEL", "gpt-5.6-terra")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    records = json.loads(_RESULTS_PATH.read_text(encoding="utf-8"))
    token_judge = TokenMatchJudge()
    llm_judge = LLMJudge(
        OpenAIModel(model=judge_model, api_key=api_key, base_url=base_url)
    )

    print(f"Target model: {_target_model(records)}", flush=True)
    print(f"Judge model: {judge_model}", flush=True)
    print(flush=True)
    print(f"{'case_id':<48} {'token':<8} {'llm':<8}", flush=True)
    token_successes: list[bool] = []
    llm_successes: list[bool] = []
    for row in records:
        case = _case_from_row(row)
        token = token_judge.judge(case, row["response"])
        llm = llm_judge.judge(case, row["response"])
        token_successes.append(token.success)
        llm_successes.append(llm.success)
        print(
            f"{case.id:<48} {str(token.success):<8} {str(llm.success):<8}",
            flush=True,
        )

    print()
    print(f"Heuristic ASR: {_asr(token_successes) * 100:.1f}%")
    print(f"LLM-judge ASR: {_asr(llm_successes) * 100:.1f}%")


if __name__ == "__main__":
    main()
