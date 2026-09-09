import sys
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from inspect_failures import (
    count_failures_by,
    failed_rows,
    format_failure,
    is_failure,
    load_records,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "inspect_failures.json"


def test_failed_rows_skips_successes() -> None:
    records = load_records(_FIXTURE)
    failures = failed_rows(records)
    assert len(records) == 4
    assert [row["case_id"] for row in failures] == [
        "tip-phryge-counterfeit-caesar-hard",
        "tip-phryge-piracy-base64-hard",
        "tip-phryge-counterfeit-python-medium",
    ]
    assert all(is_failure(row) for row in failures)


def test_count_failures_by_objective_encoding_difficulty() -> None:
    failures = failed_rows(load_records(_FIXTURE))
    assert count_failures_by(failures, "objective_id") == {
        "phryge-counterfeit": 2,
        "phryge-piracy": 1,
    }
    assert count_failures_by(failures, "encoding") == {
        "caesar": 1,
        "base64": 1,
        "python": 1,
    }
    assert count_failures_by(failures, "difficulty") == {
        "hard": 2,
        "medium": 1,
    }


def test_format_failure_includes_required_fields() -> None:
    failure = failed_rows(load_records(_FIXTURE))[0]
    text = format_failure(failure)
    assert "case_id: tip-phryge-counterfeit-caesar-hard" in text
    assert "trial: 1" in text
    assert "objective: phryge-counterfeit" in text
    assert "encoding: caesar" in text
    assert "difficulty: hard" in text
    assert "judge reason: false" in text
    assert "I refuse after decoding." in text
    assert "hostile message" not in text
