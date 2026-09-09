import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from model_probe import (
    LLMJudge,
    OpenAIModel,
    RunResult,
    TIPSuite,
    phryge_objectives,
    run,
    save_json,
    summarize,
    summarize_by,
)

_RESULTS_DIR = Path("results")
_OBJECTIVE_COLUMNS = (
    ("counterfeit", "phryge-counterfeit"),
    ("toxic", "phryge-toxic"),
    ("piracy", "phryge-piracy"),
)
_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class ModelComparisonRow:
    model: str
    overall: float
    counterfeit: float | None
    toxic: float | None
    piracy: float | None


def parse_target_models(raw: str) -> list[str]:
    names: list[str] = []
    for part in raw.split(","):
        name = part.strip()
        if name and name not in names:
            names.append(name)
    if not names:
        raise ValueError("TARGET_MODELS is empty")
    return names


def safe_model_filename(model: str) -> str:
    cleaned = _UNSAFE_FILENAME.sub("_", model.strip()).strip("._")
    if not cleaned:
        cleaned = "model"
    return f"{cleaned}.json"


def comparison_row(model: str, results: list[RunResult]) -> ModelComparisonRow:
    by_objective = summarize_by(results, "objective_id")
    rates: dict[str, float | None] = {}
    for field, objective_id in _OBJECTIVE_COLUMNS:
        summary = by_objective.get(objective_id)
        rates[field] = None if summary is None else summary.attack_success_rate
    return ModelComparisonRow(
        model=model,
        overall=summarize(results).attack_success_rate,
        counterfeit=rates["counterfeit"],
        toxic=rates["toxic"],
        piracy=rates["piracy"],
    )


def format_pct(rate: float | None) -> str:
    if rate is None:
        return "n/a"
    return f"{rate * 100:.1f}%"


def format_comparison_table(rows: list[ModelComparisonRow]) -> str:
    header = f"{'Model':<21} {'Overall':>8} {'Counterfeit':>12} {'Toxic':>8} {'Piracy':>8}"
    lines = [header]
    for row in rows:
        lines.append(
            f"{row.model:<21} {format_pct(row.overall):>8} "
            f"{format_pct(row.counterfeit):>12} {format_pct(row.toxic):>8} "
            f"{format_pct(row.piracy):>8}"
        )
    return "\n".join(lines)


def _print_asr(label: str, successes: int, total: int, rate: float) -> None:
    print(f"{label}: {successes}/{total} ({rate * 100:.1f}%)")


def _print_groups(title: str, grouped: dict) -> None:
    print()
    print(title)
    for key, summary in grouped.items():
        _print_asr(f"  {key}", summary.successes, summary.total, summary.attack_success_rate)


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    try:
        targets = parse_target_models(os.environ.get("TARGET_MODELS", ""))
    except ValueError as exc:
        print(
            f"{exc}. Example: TARGET_MODELS=gpt-4o-mini,gpt-5.6-luna,gpt-5.6-terra",
            file=sys.stderr,
        )
        sys.exit(1)

    judge_model = os.environ.get("JUDGE_MODEL", "gpt-5.6-terra")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    trials = int(os.environ.get("TRIALS", "1"))
    suite = TIPSuite(phryge_objectives())
    judge = LLMJudge(
        OpenAIModel(model=judge_model, api_key=api_key, base_url=base_url)
    )

    print(f"Targets: {', '.join(targets)}", flush=True)
    print(f"Judge: LLMJudge ({judge_model})", flush=True)
    print(f"Trials: {trials}", flush=True)
    print(flush=True)

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[ModelComparisonRow] = []

    for target in targets:
        print(f"=== {target} ===", flush=True)
        results = run(
            OpenAIModel(model=target, api_key=api_key, base_url=base_url),
            suite,
            judge,
            trials=trials,
        )
        overall = summarize(results)
        _print_asr("Overall ASR", overall.successes, overall.total, overall.attack_success_rate)
        _print_groups("By objective", summarize_by(results, "objective_id"))
        _print_groups("By encoding", summarize_by(results, "encoding"))
        _print_groups("By difficulty", summarize_by(results, "difficulty"))

        output_path = _RESULTS_DIR / safe_model_filename(target)
        save_json(results, str(output_path), target_model=target)
        print(f"Wrote {output_path}", flush=True)
        print(flush=True)
        rows.append(comparison_row(target, results))

    print("Comparison")
    print(format_comparison_table(rows))


if __name__ == "__main__":
    main()
