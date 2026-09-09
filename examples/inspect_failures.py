import json
import sys
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("results file must be a JSON array")
    return payload


def is_failure(row: dict) -> bool:
    verdict = row.get("verdict")
    if not isinstance(verdict, dict):
        return False
    return verdict.get("success") is False


def failed_rows(records: list[dict]) -> list[dict]:
    return [row for row in records if is_failure(row)]


def _meta(row: dict, key: str) -> str:
    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get(key)
    return value if isinstance(value, str) else ""


def _reason(row: dict) -> str:
    verdict = row.get("verdict")
    if not isinstance(verdict, dict):
        return ""
    reason = verdict.get("reason")
    return reason if isinstance(reason, str) else ""


def count_failures_by(rows: list[dict], metadata_key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = _meta(row, metadata_key)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def format_failure(row: dict) -> str:
    lines = [
        "---",
        f"case_id: {row.get('case_id', '')}",
        f"trial: {row.get('trial', 1)}",
        f"objective: {_meta(row, 'objective_id')}",
        f"encoding: {_meta(row, 'encoding')}",
        f"difficulty: {_meta(row, 'difficulty')}",
        f"judge reason: {_reason(row)}",
        "response:",
        row.get("response") or "",
    ]
    return "\n".join(lines)


def _print_counts(title: str, counts: dict[str, int]) -> None:
    print(title)
    for key, count in counts.items():
        print(f"  {key}: {count}")


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python examples/inspect_failures.py results/<model>.json",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"{path} not found.", file=sys.stderr)
        sys.exit(1)

    records = load_records(path)
    failures = failed_rows(records)
    for row in failures:
        print(format_failure(row))
        print()

    print(f"Total results: {len(records)}")
    print(f"Failures: {len(failures)}")
    print()
    _print_counts("By objective", count_failures_by(failures, "objective_id"))
    print()
    _print_counts("By encoding", count_failures_by(failures, "encoding"))
    print()
    _print_counts("By difficulty", count_failures_by(failures, "difficulty"))


if __name__ == "__main__":
    main()
