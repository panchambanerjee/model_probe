import sys
from pathlib import Path

import pytest

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from classify_failures import (
    build_sidecar,
    parse_failure_label,
    sidecar_path,
    summarize_failure_types,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("d", "decode_failure"),
        ("D", "decode_failure"),
        (" r\n", "decoded_then_refused"),
        ("o", "off_target_response"),
        ("x", "other"),
        ("s", "skip"),
        ("S", "skip"),
    ],
)
def test_parse_failure_label_accepts_keys(raw: str, expected: str) -> None:
    assert parse_failure_label(raw) == expected


def test_parse_failure_label_rejects_other_input() -> None:
    with pytest.raises(ValueError, match="enter d, r, o, x, or s"):
        parse_failure_label("y")
    with pytest.raises(ValueError, match="enter d, r, o, x, or s"):
        parse_failure_label("")
    with pytest.raises(ValueError, match="enter d, r, o, x, or s"):
        parse_failure_label("refuse")


def test_sidecar_path_uses_failures_suffix() -> None:
    assert sidecar_path(Path("results/gpt-5.6-luna.json")) == Path(
        "results/gpt-5.6-luna.failures.json"
    )


def test_build_sidecar_preserves_labels_and_skips_successes() -> None:
    failures = [
        {"case_id": "a", "trial": 1},
        {"case_id": "b", "trial": 2},
        {"case_id": "c", "trial": 1},
    ]
    existing = [
        {"case_id": "a", "trial": 1, "failure_type": "decoded_then_refused"},
        {"case_id": "gone", "trial": 9, "failure_type": "other"},
    ]
    rows = build_sidecar(failures, existing)
    assert rows == [
        {
            "case_id": "a",
            "trial": 1,
            "failure_type": "decoded_then_refused",
        },
        {"case_id": "b", "trial": 2, "failure_type": None},
        {"case_id": "c", "trial": 1, "failure_type": None},
    ]


def test_summarize_failure_types_counts_and_percentages() -> None:
    summary = summarize_failure_types(
        [
            {"case_id": "a", "trial": 1, "failure_type": "decoded_then_refused"},
            {"case_id": "b", "trial": 1, "failure_type": "decoded_then_refused"},
            {"case_id": "c", "trial": 1, "failure_type": "decode_failure"},
            {"case_id": "d", "trial": 1, "failure_type": None},
            {"case_id": "e", "trial": 1, "failure_type": "off_target_response"},
        ]
    )
    assert summary["decoded_then_refused"] == {"count": 2, "pct": pytest.approx(0.5)}
    assert summary["decode_failure"] == {"count": 1, "pct": pytest.approx(0.25)}
    assert summary["off_target_response"] == {"count": 1, "pct": pytest.approx(0.25)}
    assert summary["other"] == {"count": 0, "pct": pytest.approx(0.0)}


def test_summarize_failure_types_empty_is_zero() -> None:
    summary = summarize_failure_types(
        [{"case_id": "a", "trial": 1, "failure_type": None}]
    )
    assert summary["decoded_then_refused"] == {"count": 0, "pct": 0.0}
    assert summary["decode_failure"]["count"] == 0
