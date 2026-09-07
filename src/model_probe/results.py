from dataclasses import dataclass

from model_probe.judges.base import Verdict


@dataclass(frozen=True)
class RunResult:
    case_id: str
    prompt: str
    response: str
    verdict: Verdict
    metadata: dict[str, object]
