import os
import sys

from model_probe.judges.heuristic import TokenMatchJudge
from model_probe.models.openai import OpenAIModel
from model_probe.runner import run
from model_probe.suites.tip import TIPSuite


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in the environment.", file=sys.stderr)
        sys.exit(1)

    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.environ.get("OPENAI_BASE_URL") or None

    results = run(
        OpenAIModel(model=model_name, api_key=api_key, base_url=base_url),
        TIPSuite(),
        TokenMatchJudge(),
    )

    for result in results:
        print(
            f"{result.case_id}\t{result.verdict.success}\t{result.verdict.reason}"
        )


if __name__ == "__main__":
    main()
