from collections.abc import Callable

from model_probe.judges.base import Judge
from model_probe.models.base import Model
from model_probe.results import RunResult
from model_probe.suites.base import Case, Suite


def run(
    model: Model,
    suite: Suite,
    judge: Judge,
    *,
    trials: int = 1,
    on_case_start: Callable[[Case], None] | None = None,
    on_result: Callable[[RunResult], None] | None = None,
) -> list[RunResult]:
    if trials < 1:
        raise ValueError("trials must be >= 1")

    results: list[RunResult] = []

    for case in suite.cases():
        if on_case_start is not None:
            on_case_start(case)
        for trial in range(1, trials + 1):
            response = model.generate(case.prompt)
            verdict = judge.judge(case, response)
            result = RunResult(
                case_id=case.id,
                prompt=case.prompt,
                response=response,
                verdict=verdict,
                metadata=case.metadata,
                trial=trial,
            )
            results.append(result)
            if on_result is not None:
                on_result(result)

    return results
