import pytest

from model_probe.metrics import score_binary


def test_score_binary_mixed_counts() -> None:
    metrics = score_binary(
        [True, True, False, False, True],
        [True, False, False, True, True],
    )
    assert metrics.total == 5
    assert metrics.true_positives == 2
    assert metrics.true_negatives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.accuracy == 0.6
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.recall == pytest.approx(2 / 3)
    assert metrics.f1 == pytest.approx(2 / 3)


def test_score_binary_perfect_match() -> None:
    metrics = score_binary([True, False, True], [True, False, True])
    assert metrics.true_positives == 2
    assert metrics.true_negatives == 1
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.accuracy == 1.0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0


def test_score_binary_empty() -> None:
    metrics = score_binary([], [])
    assert metrics.total == 0
    assert metrics.true_positives == 0
    assert metrics.true_negatives == 0
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.accuracy == 0.0
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_score_binary_no_predicted_positives() -> None:
    metrics = score_binary([True, False], [False, False])
    assert metrics.true_positives == 0
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 1
    assert metrics.true_negatives == 1
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0
    assert metrics.accuracy == 0.5


def test_score_binary_no_actual_positives() -> None:
    metrics = score_binary([False, False], [False, True])
    assert metrics.true_positives == 0
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0
    assert metrics.true_negatives == 1
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0
    assert metrics.accuracy == 0.5


def test_score_binary_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        score_binary([True], [True, False])
