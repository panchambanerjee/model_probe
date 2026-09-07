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

    assert results[1].prompt == "say nothing"
    assert results[1].response == "echo:say nothing"
    assert results[1].verdict.success is False
    assert results[1].metadata == {}
