import json
from dataclasses import dataclass

from model_probe.judges.base import Verdict


@dataclass(frozen=True)
class RunResult:
    case_id: str
    prompt: str
    response: str
    verdict: Verdict
    metadata: dict[str, object]
    trial: int = 1


@dataclass(frozen=True)
class RunSummary:
    total: int
    successes: int
    attack_success_rate: float


def summarize(results: list[RunResult]) -> RunSummary:
    total = len(results)
    successes = sum(1 for result in results if result.verdict.success)
    attack_success_rate = 0.0 if total == 0 else successes / total
    return RunSummary(
        total=total,
        successes=successes,
        attack_success_rate=attack_success_rate,
    )


def summarize_by(
    results: list[RunResult],
    metadata_key: str,
) -> dict[str, RunSummary]:
    groups: dict[str, list[RunResult]] = {}
    for result in results:
        value = result.metadata.get(metadata_key)
        if not isinstance(value, str):
            continue
        groups.setdefault(value, []).append(result)
    return {key: summarize(items) for key, items in groups.items()}


def summarize_by_case(results: list[RunResult]) -> dict[str, RunSummary]:
    groups: dict[str, list[RunResult]] = {}
    for result in results:
        groups.setdefault(result.case_id, []).append(result)
    return {case_id: summarize(items) for case_id, items in groups.items()}


def save_json(
    results: list[RunResult],
    path: str,
    *,
    target_model: str | None = None,
) -> None:
    payload = [
        {
            "case_id": result.case_id,
            "prompt": result.prompt,
            "response": result.response,
            "metadata": result.metadata,
            "trial": result.trial,
            "verdict": {
                "success": result.verdict.success,
                "score": result.verdict.score,
                "reason": result.verdict.reason,
            },
            **({"target_model": target_model} if target_model is not None else {}),
        }
        for result in results
    ]
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
