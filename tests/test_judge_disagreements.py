import json
import sys
from pathlib import Path

import pytest

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from label_disagreements import parse_label

_FIXTURE = Path(__file__).parent / "fixtures" / "judge_disagreements.json"

_DISAGREEMENT_KEYS = [
    ("tip-phryge-counterfeit-caesar-hard", 4),
    ("tip-phryge-counterfeit-caesar-hard", 5),
    ("tip-phryge-counterfeit-caesar-hard", 6),
    ("tip-phryge-counterfeit-caesar-hard", 10),
    ("tip-phryge-toxic-caesar-hard", 1),
    ("tip-phryge-toxic-caesar-hard", 2),
    ("tip-phryge-toxic-caesar-hard", 3),
    ("tip-phryge-toxic-caesar-hard", 4),
    ("tip-phryge-toxic-caesar-hard", 7),
    ("tip-phryge-toxic-caesar-hard", 8),
    ("tip-phryge-toxic-caesar-hard", 9),
    ("tip-phryge-toxic-caesar-hard", 10),
    ("tip-phryge-toxic-caesar-medium", 3),
    ("tip-phryge-toxic-caesar-medium", 4),
    ("tip-phryge-toxic-caesar-medium", 10),
    ("tip-phryge-toxic-base64-hard", 6),
    ("tip-phryge-toxic-base64-hard", 7),
    ("tip-phryge-toxic-base64-medium", 2),
    ("tip-phryge-toxic-base64-medium", 10),
    ("tip-phryge-toxic-python-hard", 10),
    ("tip-phryge-toxic-python-medium", 1),
    ("tip-phryge-toxic-python-medium", 3),
    ("tip-phryge-toxic-python-medium", 4),
    ("tip-phryge-toxic-python-medium", 5),
    ("tip-phryge-toxic-python-medium", 7),
    ("tip-phryge-toxic-python-medium", 8),
]

_REQUIRED_KEYS = {
    "case_id",
    "trial",
    "response",
    "metadata",
    "expected_success",
}
_METADATA_KEYS = {
    "attack_type",
    "encoding",
    "difficulty",
    "objective_id",
    "objective",
    "category",
    "evaluation_criterion",
}


def _load_fixture() -> list[dict]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_judge_disagreements_fixture_structure() -> None:
    rows = _load_fixture()
    assert len(rows) == 26
    assert [(row["case_id"], row["trial"]) for row in rows] == _DISAGREEMENT_KEYS

    for row in rows:
        assert set(row) == _REQUIRED_KEYS
        assert isinstance(row["case_id"], str) and row["case_id"]
        assert isinstance(row["trial"], int) and row["trial"] >= 1
        assert isinstance(row["response"], str) and row["response"]
        assert isinstance(row["metadata"], dict)
        assert _METADATA_KEYS <= set(row["metadata"])
        assert row["expected_success"] is None or isinstance(
            row["expected_success"], bool
        )
        assert "prompt" not in row
        assert "verdict" not in row
        assert "target_model" not in row
        assert "token" not in row
        assert "llm" not in row

    blob = _FIXTURE.read_text(encoding="utf-8")
    assert "sk-" not in blob
    assert "OPENAI_API_KEY" not in blob


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("y", True),
        ("Y", True),
        (" y\n", True),
        ("n", False),
        ("N", False),
        ("s", "skip"),
        ("S", "skip"),
    ],
)
def test_parse_label_accepts_y_n_s(raw: str, expected: bool | str) -> None:
    assert parse_label(raw) == expected


def test_parse_label_rejects_other_input() -> None:
    with pytest.raises(ValueError, match="enter y, n, or s"):
        parse_label("true")
    with pytest.raises(ValueError, match="enter y, n, or s"):
        parse_label("")
    with pytest.raises(ValueError, match="enter y, n, or s"):
        parse_label("yes")
