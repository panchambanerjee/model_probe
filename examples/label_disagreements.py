"""Label TokenMatch vs LLM disagreements. Never calls a model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "judge_disagreements.json"
)


def parse_label(raw: str) -> bool | str:
    token = raw.strip().lower()
    if token == "y":
        return True
    if token == "n":
        return False
    if token == "s":
        return "skip"
    raise ValueError("enter y, n, or s")


def _load() -> list[dict]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _save(rows: list[dict]) -> None:
    _FIXTURE.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _meta(row: dict, key: str) -> str:
    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    value = metadata.get(key)
    return value if isinstance(value, str) else ""


def _print_case(index: int, total: int, row: dict) -> None:
    print()
    print("=" * 72)
    print(f"[{index}/{total}] unlabeled")
    print(f"case_id: {row['case_id']}")
    print(f"trial: {row['trial']}")
    print(f"objective_id: {_meta(row, 'objective_id')}")
    print(f"encoding: {_meta(row, 'encoding')}")
    print(f"difficulty: {_meta(row, 'difficulty')}")
    print()
    print("evaluation_criterion:")
    print(_meta(row, "evaluation_criterion") or "(missing)")
    print()
    print("response:")
    print(row.get("response") or "")
    print()


def main() -> None:
    if not _FIXTURE.exists():
        print(f"Fixture not found: {_FIXTURE}", file=sys.stderr)
        sys.exit(1)

    rows = _load()
    total = len(rows)
    unlabeled = [
        (index, row)
        for index, row in enumerate(rows, start=1)
        if row.get("expected_success") is None
    ]
    labeled = total - len(unlabeled)
    print(
        f"Loaded {total} disagreements from {_FIXTURE.name} "
        f"({labeled} labeled, {len(unlabeled)} unlabeled)."
    )
    if not unlabeled:
        print("Nothing left to label.")
        return

    print("y = true (attack succeeded), n = false, s = skip")
    for index, row in unlabeled:
        _print_case(index, total, row)
        while True:
            try:
                raw = input("Label [y/n/s]: ")
            except EOFError:
                print()
                print("Stopped.")
                return
            try:
                parsed = parse_label(raw)
            except ValueError as error:
                print(error)
                continue
            if parsed == "skip":
                print("Skipped.")
                break
            row["expected_success"] = parsed
            _save(rows)
            remaining = sum(
                1 for item in rows if item.get("expected_success") is None
            )
            print(
                f"Saved expected_success={parsed}. "
                f"{remaining} unlabeled remaining."
            )
            break

    remaining = sum(1 for item in rows if item.get("expected_success") is None)
    print()
    print(f"Done. {total - remaining}/{total} labeled, {remaining} unlabeled.")


if __name__ == "__main__":
    main()
