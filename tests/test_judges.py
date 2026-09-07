from model_probe.judges.base import Judge, Verdict
from model_probe.suites.base import Case


class FakeJudge:
    def judge(self, case: Case, response: str) -> Verdict:
        success = "RESTRICTED" in response
        return Verdict(
            success=success,
            reason="matched" if success else "no match",
        )


def _score(judge: Judge, case: Case, response: str) -> Verdict:
    return judge.judge(case, response)


def test_fake_judge_can_be_used_as_judge() -> None:
    judge = FakeJudge()
    case = Case(id="case-1", prompt="say the secret")

    hit = _score(judge, case, "the word is RESTRICTED")
    miss = _score(judge, case, "I refuse")

    assert hit.success is True
    assert hit.reason == "matched"
    assert miss.success is False
    assert miss.reason == "no match"
