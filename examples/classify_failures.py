"""Manually classify saved attack failures. Never calls a model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parent
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))

from inspect_failures import failed_rows, load_records

FAILURE_TYPES = (
    "decode_failure",
    "decoded_then_refused",
    "off_target_response",
    "other",
)

_LABELS = {
    "d": "decode_failure",
    "r": "decoded_then_refused",
    "o": "off_target_response",
    "x": "other",
}


def parse_failure_label(raw: str) -> str:
    token = raw.strip().lower()
    if token == "s":
        return "skip"
    if token in _LABELS:
        return _LABELS[token]
    raise ValueError("enter d, r, o, x, or s")


def sidecar_path(results_path: Path) -> Path:
    return results_path.with_name(f"{results_path.stem}.failures.json")


def load_sidecar(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("sidecar file must be a JSON array")
    return payload


def save_sidecar(path: Path, rows: list[dict]) -> None:
    path.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_sidecar(failures: list[dict], existing: list[dict]) -> list[dict]:
    by_key = {
        (row.get("case_id"), row.get("trial")): row
        for row in existing
        if isinstance(row, dict)
    }
    rows: list[dict] = []
    for failure in failures:
        key = (failure.get("case_id"), failure.get("trial", 1))
        previous = by_key.get(key)
        failure_type = None
        if previous is not None:
            saved = previous.get("failure_type")
            if saved in FAILURE_TYPES:
                failure_type = saved
        rows.append(
            {
                "case_id": failure.get("case_id"),
                "trial": failure.get("trial", 1),
                "failure_type": failure_type,
            }
        )
    return rows


def summarize_failure_types(rows: list[dict]) -> dict[str, dict[str, float | int]]:
    labeled = [row for row in rows if row.get("failure_type") in FAILURE_TYPES]
    total = len(labeled)
    counts = {name: 0 for name in FAILURE_TYPES}
    for row in labeled:
        counts[str(row["failure_type"])] += 1
    return {
        name: {
            "count": counts[name],
            "pct": 0.0 if total == 0 else counts[name] / total,
        }
        for name in FAILURE_TYPES
    }


def _meta(row: dict, key: str) -> str:
    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get(key)
    return value if isinstance(value, str) else ""


def _print_summary(rows: list[dict]) -> None:
    labeled = sum(1 for row in rows if row.get("failure_type") in FAILURE_TYPES)
    unlabeled = len(rows) - labeled
    print()
    print(f"Failure types ({labeled} labeled, {unlabeled} unlabeled)")
    summary = summarize_failure_types(rows)
    for name, stats in summary.items():
        count = stats["count"]
        pct = stats["pct"] * 100
        print(f"  {name}: {count}/{labeled} ({pct:.1f}%)")


def _print_case(index: int, total: int, result: dict) -> None:
    print()
    print("=" * 72)
    print(f"[{index}/{total}] unlabeled failure")
    print(f"case_id: {result.get('case_id', '')}")
    print(f"trial: {result.get('trial', 1)}")
    print(f"objective_id: {_meta(result, 'objective_id')}")
    print(f"objective: {_meta(result, 'objective')}")
    print(f"encoding: {_meta(result, 'encoding')}")
    print(f"difficulty: {_meta(result, 'difficulty')}")
    print()
    print("response:")
    print(result.get("response") or "")
    print()


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python examples/classify_failures.py results/<model>.json",
            file=sys.stderr,
        )
        sys.exit(1)

    results_path = Path(sys.argv[1])
    if not results_path.exists():
        print(f"{results_path} not found.", file=sys.stderr)
        sys.exit(1)

    failures = failed_rows(load_records(results_path))
    labels_path = sidecar_path(results_path)
    rows = build_sidecar(failures, load_sidecar(labels_path))
    unlabeled = [
        (index, row)
        for index, row in enumerate(rows)
        if row.get("failure_type") not in FAILURE_TYPES
    ]
    print(
        f"Loaded {len(failures)} failures from {results_path} "
        f"({len(rows) - len(unlabeled)} labeled, {len(unlabeled)} unlabeled)."
    )
    print(f"Sidecar: {labels_path}")
    if not unlabeled:
        _print_summary(rows)
        return

    print(
        "d = decode_failure, r = decoded_then_refused, "
        "o = off_target_response, x = other, s = skip"
    )
    for index, row in unlabeled:
        _print_case(index + 1, len(rows), failures[index])
        while True:
            try:
                raw = input("Label [d/r/o/x/s]: ")
            except EOFError:
                print()
                print("Stopped.")
                _print_summary(rows)
                return
            try:
                parsed = parse_failure_label(raw)
            except ValueError as error:
                print(error)
                continue
            if parsed == "skip":
                print("Skipped.")
                break
            row["failure_type"] = parsed
            save_sidecar(labels_path, rows)
            remaining = sum(
                1 for item in rows if item.get("failure_type") not in FAILURE_TYPES
            )
            print(f"Saved failure_type={parsed}. {remaining} unlabeled remaining.")
            break

    _print_summary(rows)


if __name__ == "__main__":
    main()
