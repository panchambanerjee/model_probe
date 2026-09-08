import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from model_probe.judges.heuristic import TokenMatchJudge
from model_probe.models.openai import OpenAIModel
from model_probe.results import RunResult, summarize
from model_probe.runner import run
from model_probe.suites.base import Case
from model_probe.suites.tip import TIPSuite

_SNIPPET_CHARS = 160


def _snippet(text: str) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "(empty)"
    if len(compact) > _SNIPPET_CHARS:
        return compact[: _SNIPPET_CHARS - 3] + "..."
    return compact


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    suite = TIPSuite()
    total = len(suite.cases())
    seen = 0

    def on_case_start(case: Case) -> None:
        nonlocal seen
        seen += 1
        print(f"[{seen}/{total}] {case.id} ...", flush=True)

    def on_result(result: RunResult) -> None:
        print(f"    {result.verdict.success}\t{result.verdict.reason}")
        print(f"    {_snippet(result.response)}")

    results = run(
        OpenAIModel(model=model_name, api_key=api_key, base_url=base_url),
        suite,
        TokenMatchJudge(),
        on_case_start=on_case_start,
        on_result=on_result,
    )

    summary = summarize(results)
    print()
    print("Summary")
    print(f"Total: {summary.total}")
    print(f"Successful attacks: {summary.successes}")
    print(f"ASR: {summary.attack_success_rate * 100:.1f}%")


if __name__ == "__main__":
    main()
