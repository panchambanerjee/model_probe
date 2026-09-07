from dataclasses import dataclass
from typing import Protocol

from model_probe.suites.base import Case


@dataclass(frozen=True)
class Verdict:
    success: bool
    score: float | None = None
    reason: str | None = None


class Judge(Protocol):
    def judge(self, case: Case, response: str) -> Verdict:
        ...
