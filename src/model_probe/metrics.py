from dataclasses import dataclass


@dataclass(frozen=True)
class BinaryMetrics:
    total: int
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    accuracy: float
    precision: float
    recall: float
    f1: float


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def score_binary(
    labels: list[bool],
    predictions: list[bool],
) -> BinaryMetrics:
    if len(labels) != len(predictions):
        raise ValueError("labels and predictions must have the same length")

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    for label, prediction in zip(labels, predictions, strict=True):
        if label and prediction:
            true_positives += 1
        elif label and not prediction:
            false_negatives += 1
        elif not label and prediction:
            false_positives += 1
        else:
            true_negatives += 1

    total = len(labels)
    precision = _ratio(true_positives, true_positives + false_positives)
    recall = _ratio(true_positives, true_positives + false_negatives)
    return BinaryMetrics(
        total=total,
        true_positives=true_positives,
        true_negatives=true_negatives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        accuracy=_ratio(true_positives + true_negatives, total),
        precision=precision,
        recall=recall,
        f1=_ratio(2 * precision * recall, precision + recall),
    )
