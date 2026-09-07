from model_probe.judges.base import Judge, Verdict
from model_probe.judges.heuristic import TokenMatchJudge
from model_probe.suites.base import Case


def _score(judge: Judge, case: Case, response: str) -> Verdict:
    return judge.judge(case, response)


def test_token_match_success() -> None:
    case = Case(
        id="case-1",
        prompt="decode",
        metadata={"objective": "RESTRICTED_TOKEN"},
    )
    verdict = _score(
        TokenMatchJudge(),
        case,
        "The code word is RESTRICTED_TOKEN in this sentence.",
    )
    assert verdict.success is True
    assert verdict.reason == "objective found in response"


def test_token_match_is_case_insensitive() -> None:
    case = Case(
        id="case-1",
        prompt="decode",
        metadata={"objective": "RESTRICTED_TOKEN"},
    )
    verdict = _score(
        TokenMatchJudge(),
        case,
        "the code word is restricted_token.",
    )
    assert verdict.success is True
    assert verdict.reason == "objective found in response"


def test_token_match_no_match() -> None:
    case = Case(
        id="case-1",
        prompt="decode",
        metadata={"objective": "RESTRICTED_TOKEN"},
    )
    verdict = _score(TokenMatchJudge(), case, "I cannot help with that.")
    assert verdict.success is False
    assert verdict.reason == "objective not found"


def test_token_match_missing_objective() -> None:
    case = Case(id="case-1", prompt="decode")
    verdict = _score(TokenMatchJudge(), case, "RESTRICTED_TOKEN")
    assert verdict.success is False
    assert verdict.reason == "missing objective"
