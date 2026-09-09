import sys
from pathlib import Path

import pytest

from model_probe.judges.base import Verdict
from model_probe.results import RunResult

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from compare_models import (
    comparison_row,
    format_comparison_table,
    parse_target_models,
    safe_model_filename,
)


def _result(objective_id: str, success: bool) -> RunResult:
    return RunResult(
        case_id=f"tip-{objective_id}",
        prompt="",
        response="",
        verdict=Verdict(success=success),
        metadata={"objective_id": objective_id},
    )


def test_parse_target_models_comma_separated() -> None:
    assert parse_target_models("gpt-4o-mini,gpt-5.6-luna,gpt-5.6-terra") == [
        "gpt-4o-mini",
        "gpt-5.6-luna",
        "gpt-5.6-terra",
    ]


def test_parse_target_models_strips_whitespace() -> None:
    assert parse_target_models(" gpt-4o-mini , gpt-5.6-luna ") == [
        "gpt-4o-mini",
        "gpt-5.6-luna",
    ]


def test_parse_target_models_skips_empty_and_dedupes() -> None:
    assert parse_target_models("gpt-4o-mini,,gpt-4o-mini,gpt-5.6-terra") == [
        "gpt-4o-mini",
        "gpt-5.6-terra",
    ]


def test_parse_target_models_empty_raises() -> None:
    with pytest.raises(ValueError, match="TARGET_MODELS is empty"):
        parse_target_models("")
    with pytest.raises(ValueError, match="TARGET_MODELS is empty"):
        parse_target_models(" , , ")


def test_safe_model_filename_keeps_simple_names() -> None:
    assert safe_model_filename("gpt-4o-mini") == "gpt-4o-mini.json"
    assert safe_model_filename("gpt-5.6-terra") == "gpt-5.6-terra.json"


def test_safe_model_filename_replaces_unsafe_characters() -> None:
    assert safe_model_filename("openai/gpt-4o") == "openai_gpt-4o.json"
    assert safe_model_filename("../secret") == "secret.json"
    assert safe_model_filename("  ") == "model.json"


def test_comparison_row_uses_objective_groups() -> None:
    results = [
        _result("phryge-counterfeit", True),
        _result("phryge-counterfeit", False),
        _result("phryge-toxic", True),
        _result("phryge-toxic", True),
        _result("phryge-piracy", True),
        _result("phryge-piracy", True),
        _result("phryge-piracy", True),
    ]
    row = comparison_row("gpt-4o-mini", results)
    assert row.model == "gpt-4o-mini"
    assert row.overall == pytest.approx(6 / 7)
    assert row.counterfeit == pytest.approx(0.5)
    assert row.toxic == pytest.approx(1.0)
    assert row.piracy == pytest.approx(1.0)


def test_comparison_row_missing_objective_is_none() -> None:
    row = comparison_row(
        "gpt-4o-mini",
        [_result("phryge-counterfeit", True), _result("phryge-toxic", False)],
    )
    assert row.overall == pytest.approx(0.5)
    assert row.counterfeit == pytest.approx(1.0)
    assert row.toxic == pytest.approx(0.0)
    assert row.piracy is None


def test_format_comparison_table_compact_columns() -> None:
    row = comparison_row(
        "gpt-4o-mini",
        [
            *[_result("phryge-counterfeit", True) for _ in range(9)],
            _result("phryge-counterfeit", False),
            *[_result("phryge-toxic", True) for _ in range(8)],
            *[_result("phryge-toxic", False) for _ in range(2)],
            *[_result("phryge-piracy", True) for _ in range(29)],
            _result("phryge-piracy", False),
        ],
    )
    table = format_comparison_table([row])
    assert table.splitlines()[0].startswith("Model")
    assert "Overall" in table
    assert "Counterfeit" in table
    assert "Toxic" in table
    assert "Piracy" in table
    assert "gpt-4o-mini" in table
    assert "92.0%" in table
    assert "90.0%" in table
    assert "80.0%" in table
    assert "96.7%" in table
