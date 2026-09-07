# Progress

Living notes for `model_probe`. Update this when scope, status, or layout changes. Keep the README as the public v0.1 summary.

Last updated: 2026-09-07

## Current status

Skeleton is in place. The only implemented application piece is the `Model` protocol.

v0.1 goal: prove the architecture with a small runner — swap a **Model**, swap a **Suite**, score with a **Judge**, report attack success rate.

Framework logic stays separate from benchmark content. Built-in development cases use a harmless synthetic “restricted behavior” objective. PHRYGE-style cases are benchmark data, not the default example.

## Done

- Python 3.11+ project with `src/` layout, `pyproject.toml`, pytest, `.gitignore`
- Package skeleton for models, suites, judges, runner, and results (files exist; most are empty)
- `Model` protocol: synchronous `generate(prompt: str) -> str`
- Unit test that a fake class satisfying the protocol can be used as a `Model`

## In place but not implemented

These files exist as placeholders only:

| Path | Intended role |
| --- | --- |
| `src/model_probe/models/openai.py` | OpenAI-compatible adapter |
| `src/model_probe/suites/base.py` | Suite / Case types |
| `src/model_probe/suites/tip.py` | First TIP suite (synthetic objective) |
| `src/model_probe/judges/base.py` | Judge protocol |
| `src/model_probe/judges/heuristic.py` | Simple heuristic judge |
| `src/model_probe/runner.py` | Run suite against model |
| `src/model_probe/results.py` | ASR + per-case records |
| `tests/test_runner.py` | Runner tests |
| `tests/test_tip_suite.py` | TIP suite tests |

## Scripts

None yet. No CLI, no example scripts, no benchmark runners.

Dev extras: pytest only (`pip install -e ".[dev]"`). No formatter or linter yet.

## Remaining for v0.1

- Suite abstraction + tiny TIP suite (synthetic restricted-behavior objective; Caesar + Base64; two difficulty levels; no depersonalisation)
- Judge abstraction + one concrete judge (callable or heuristic; no built-in LLM-as-judge)
- Runner: `run(model, suite, judge) → results`
- Results: ASR plus per-case JSON/CSV
- Tests for the above
- One OpenAI-compatible adapter (after the core types work)

## Explicitly out of v0.1

- Full PHRYGE (10 encodings, 4 objectives, 3 difficulty levels)
- Piracy / self-harm / toxic-messaging objectives as built-in defaults
- Depersonalisation
- Extra model providers (Anthropic, Gemini, Hugging Face, vLLM, …)
- LLM-as-judge as a package dependency
- CLI, dashboard, plots, HTML reports
- Defenses and detection bake-offs
- Comparisons to DAN, TAP, ArtPrompt, JailbreakBench
- Multi-turn / adaptive attacks
- Batching, async, caching, distributed runs
- Formatter / linter (add later; do not block v0.1)

## Long-term ideas

Not scheduled. Capture here so they do not leak into v0.1.

- Many attack suites behind the same Suite interface
- PHRYGE (and later other papers) as loadable benchmark data, not hardcoded package defaults
- More model adapters behind the Model protocol
- Optional LLM-as-judge, still behind the Judge protocol
- CLI: `model-probe run --model … --suite …`
- Defense / detection evaluation
- Comparison against other jailbreak methods
- Async / batched generation if providers need it
- Formatter + linter once the core API is stable
