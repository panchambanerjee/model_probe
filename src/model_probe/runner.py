from model_probe.judges.base import Judge
from model_probe.models.base import Model
from model_probe.results import RunResult
from model_probe.suites.base import Suite


def run(model: Model, suite: Suite, judge: Judge) -> list[RunResult]:
    results: list[RunResult] = []

    for case in suite.cases():
        response = model.generate(case.prompt)
        verdict = judge.judge(case, response)
        results.append(
            RunResult(
                case_id=case.id,
                prompt=case.prompt,
                response=response,
                verdict=verdict,
                metadata=case.metadata,
            )
        )

    return results
