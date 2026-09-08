from model_probe.judges.base import Verdict
from model_probe.runner import run
from model_probe.suites.base import Case


class FakeModel:
    def generate(self, prompt: str) -> str:
        return f"echo:{prompt}"


class FakeSuite:
    name = "fake"

    def cases(self) -> list[Case]:
        return [
            Case(
                id="case-1",
                prompt="say RESTRICTED",
                metadata={"encoding": "none"},
            ),
            Case(id="case-2", prompt="say nothing"),
        ]


class FakeJudge:
    def judge(self, case: Case, response: str) -> Verdict:
        success = "RESTRICTED" in response
        return Verdict(
            success=success,
            reason="matched" if success else "no match",
        )


def test_run_wires_model_suite_and_judge() -> None:
    results = run(FakeModel(), FakeSuite(), FakeJudge())

    assert [result.case_id for result in results] == ["case-1", "case-2"]

    assert results[0].prompt == "say RESTRICTED"
    assert results[0].response == "echo:say RESTRICTED"
    assert results[0].verdict.success is True
    assert results[0].metadata == {"encoding": "none"}
    assert results[0].trial == 1

    assert results[1].prompt == "say nothing"
    assert results[1].response == "echo:say nothing"
    assert results[1].verdict.success is False
    assert results[1].metadata == {}
    assert results[1].trial == 1


def test_run_optional_callbacks() -> None:
    started: list[str] = []
    finished: list[str] = []

    results = run(
        FakeModel(),
        FakeSuite(),
        FakeJudge(),
        on_case_start=lambda case: started.append(case.id),
        on_result=lambda result: finished.append(result.case_id),
    )

    assert started == ["case-1", "case-2"]
    assert finished == ["case-1", "case-2"]
    assert [result.case_id for result in results] == ["case-1", "case-2"]


def test_run_three_trials_over_two_cases() -> None:
    results = run(FakeModel(), FakeSuite(), FakeJudge(), trials=3)

    assert len(results) == 6
    assert [result.case_id for result in results] == [
        "case-1",
        "case-1",
        "case-1",
        "case-2",
        "case-2",
        "case-2",
    ]
    assert [result.trial for result in results] == [1, 2, 3, 1, 2, 3]
    assert results[0].response == results[1].response == "echo:say RESTRICTED"
    assert results[3].response == "echo:say nothing"
