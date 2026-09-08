from dataclasses import dataclass

from model_probe.judges.base import Verdict


@dataclass(frozen=True)
class RunResult:
    case_id: str
    prompt: str
    response: str
    verdict: Verdict
    metadata: dict[str, object]


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
