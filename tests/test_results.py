from model_probe.judges.base import Verdict
from model_probe.results import RunResult, summarize


def _result(case_id: str, success: bool) -> RunResult:
    return RunResult(
        case_id=case_id,
        prompt="",
        response="",
        verdict=Verdict(success=success),
        metadata={},
    )


def test_summarize_mixed_results() -> None:
    summary = summarize(
        [
            _result("case-1", True),
            _result("case-2", True),
            _result("case-3", True),
            _result("case-4", False),
        ]
    )
    assert summary.total == 4
    assert summary.successes == 3
    assert summary.attack_success_rate == 0.75


def test_summarize_all_successes() -> None:
    summary = summarize(
        [
            _result("case-1", True),
            _result("case-2", True),
        ]
    )
    assert summary.total == 2
    assert summary.successes == 2
    assert summary.attack_success_rate == 1.0


def test_summarize_no_results() -> None:
    summary = summarize([])
    assert summary.total == 0
    assert summary.successes == 0
    assert summary.attack_success_rate == 0.0
