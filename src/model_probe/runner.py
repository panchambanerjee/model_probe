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
    on_case_start: Callable[[Case], None] | None = None,
    on_result: Callable[[RunResult], None] | None = None,
) -> list[RunResult]:
    results: list[RunResult] = []

    for case in suite.cases():
        if on_case_start is not None:
            on_case_start(case)
        response = model.generate(case.prompt)
        verdict = judge.judge(case, response)
        result = RunResult(
            case_id=case.id,
            prompt=case.prompt,
            response=response,
            verdict=verdict,
            metadata=case.metadata,
        )
        results.append(result)
        if on_result is not None:
            on_result(result)

    return results
