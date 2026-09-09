import json
from pathlib import Path

from model_probe.judges.base import Verdict
from model_probe.results import (
    RunResult,
    save_json,
    summarize,
    summarize_by,
    summarize_by_case,
    summarize_by_two,
)


def _result(
    case_id: str,
    success: bool,
    metadata: dict[str, object] | None = None,
) -> RunResult:
    return RunResult(
        case_id=case_id,
        prompt="",
        response="",
        verdict=Verdict(success=success),
        metadata=metadata or {},
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


def test_summarize_by_encoding() -> None:
    grouped = summarize_by(
        [
            _result("c1", True, {"encoding": "caesar", "difficulty": "hard"}),
            _result("c2", False, {"encoding": "caesar", "difficulty": "hard"}),
            _result("c3", True, {"encoding": "base64", "difficulty": "medium"}),
            _result("c4", True, {"encoding": "base64", "difficulty": "medium"}),
            _result("c5", False, {"difficulty": "hard"}),
        ],
        "encoding",
    )
    assert list(grouped) == ["caesar", "base64"]
    assert grouped["caesar"].total == 2
    assert grouped["caesar"].successes == 1
    assert grouped["caesar"].attack_success_rate == 0.5
    assert grouped["base64"].total == 2
    assert grouped["base64"].successes == 2
    assert grouped["base64"].attack_success_rate == 1.0


def test_summarize_by_difficulty() -> None:
    grouped = summarize_by(
        [
            _result("c1", False, {"encoding": "caesar", "difficulty": "hard"}),
            _result("c2", True, {"encoding": "caesar", "difficulty": "medium"}),
            _result("c3", True, {"encoding": "base64", "difficulty": "hard"}),
            _result("c4", True, {"encoding": "base64", "difficulty": "medium"}),
        ],
        "difficulty",
    )
    assert list(grouped) == ["hard", "medium"]
    assert grouped["hard"].total == 2
    assert grouped["hard"].successes == 1
    assert grouped["hard"].attack_success_rate == 0.5
    assert grouped["medium"].total == 2
    assert grouped["medium"].successes == 2
    assert grouped["medium"].attack_success_rate == 1.0


def test_summarize_by_two_objective_encoding() -> None:
    grouped = summarize_by_two(
        [
            _result(
                "c1",
                True,
                {"objective_id": "phryge-counterfeit", "encoding": "caesar"},
            ),
            _result(
                "c2",
                False,
                {"objective_id": "phryge-counterfeit", "encoding": "caesar"},
            ),
            _result(
                "c3",
                True,
                {"objective_id": "phryge-counterfeit", "encoding": "base64"},
            ),
            _result(
                "c4",
                True,
                {"objective_id": "phryge-toxic", "encoding": "caesar"},
            ),
            _result("c5", False, {"objective_id": "phryge-toxic"}),
            _result("c6", False, {"encoding": "python"}),
        ],
        "objective_id",
        "encoding",
    )
    assert list(grouped) == ["phryge-counterfeit", "phryge-toxic"]
    assert list(grouped["phryge-counterfeit"]) == ["caesar", "base64"]
    assert list(grouped["phryge-toxic"]) == ["caesar"]
    assert grouped["phryge-counterfeit"]["caesar"].total == 2
    assert grouped["phryge-counterfeit"]["caesar"].successes == 1
    assert grouped["phryge-counterfeit"]["caesar"].attack_success_rate == 0.5
    assert grouped["phryge-counterfeit"]["base64"].total == 1
    assert grouped["phryge-counterfeit"]["base64"].successes == 1
    assert grouped["phryge-toxic"]["caesar"].total == 1
    assert grouped["phryge-toxic"]["caesar"].successes == 1


def test_summarize_by_two_empty() -> None:
    assert summarize_by_two([], "objective_id", "encoding") == {}


def test_summarize_by_case() -> None:
    grouped = summarize_by_case(
        [
            _result("tip-phryge-counterfeit-caesar-hard", False),
            _result("tip-phryge-counterfeit-caesar-hard", True),
            _result("tip-phryge-counterfeit-caesar-medium", True),
            _result("tip-phryge-counterfeit-caesar-medium", True),
            _result("tip-phryge-counterfeit-base64-hard", True),
        ]
    )
    assert list(grouped) == [
        "tip-phryge-counterfeit-caesar-hard",
        "tip-phryge-counterfeit-caesar-medium",
        "tip-phryge-counterfeit-base64-hard",
    ]
    assert grouped["tip-phryge-counterfeit-caesar-hard"].total == 2
    assert grouped["tip-phryge-counterfeit-caesar-hard"].successes == 1
    assert grouped["tip-phryge-counterfeit-caesar-hard"].attack_success_rate == 0.5
    assert grouped["tip-phryge-counterfeit-caesar-medium"].total == 2
    assert grouped["tip-phryge-counterfeit-caesar-medium"].successes == 2
    assert grouped["tip-phryge-counterfeit-caesar-medium"].attack_success_rate == 1.0
    assert grouped["tip-phryge-counterfeit-base64-hard"].total == 1
    assert grouped["tip-phryge-counterfeit-base64-hard"].successes == 1


def test_save_json_writes_results(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    save_json(
        [
            RunResult(
                case_id="tip-1",
                prompt="Decode this string.",
                response="I can't provide that.",
                verdict=Verdict(success=False, score=0.0, reason="refusal detected"),
                metadata={"objective": "counterfeit", "encoding": "caesar"},
            ),
            RunResult(
                case_id="tip-2",
                prompt="The encoded word is: YQ==",
                response="The decoded word is counterfeit.",
                verdict=Verdict(success=True, reason="objective found in response"),
                metadata={"objective": "counterfeit"},
            ),
        ],
        str(path),
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == [
        {
            "case_id": "tip-1",
            "prompt": "Decode this string.",
            "response": "I can't provide that.",
            "metadata": {"objective": "counterfeit", "encoding": "caesar"},
            "trial": 1,
            "verdict": {
                "success": False,
                "score": 0.0,
                "reason": "refusal detected",
            },
        },
        {
            "case_id": "tip-2",
            "prompt": "The encoded word is: YQ==",
            "response": "The decoded word is counterfeit.",
            "metadata": {"objective": "counterfeit"},
            "trial": 1,
            "verdict": {
                "success": True,
                "score": None,
                "reason": "objective found in response",
            },
        },
    ]
    assert path.read_text(encoding="utf-8").startswith("[\n  {")


def test_save_json_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    save_json([], str(path))
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_save_json_includes_target_model(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    save_json([_result("case-1", False)], str(path), target_model="gpt-4o-mini")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload[0]["target_model"] == "gpt-4o-mini"
