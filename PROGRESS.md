# Progress

Living notes for `model_probe`. Update this when scope, status, or layout changes. Keep the README as the public v0.1 summary.

**File map:** see [`LAYOUT.md`](LAYOUT.md). Update `LAYOUT.md` whenever a path is added, renamed, moved, or changes role. Update this file whenever status or scope changes.

Last updated: 2026-09-07

## Current status

v0.1 architecture is complete except ASR/export. A live run is:

`examples/run_tip.py` → `OpenAIModel` + `TIPSuite` + `TokenMatchJudge` → four verdicts.

The suite uses a synthetic `RESTRICTED_TOKEN` objective (Caesar and Base64, hard and medium). The judge scores success if that token appears in the response. There is no ASR summary or persistence yet.

Framework logic stays separate from benchmark content. Built-in development cases use a harmless synthetic “restricted behavior” objective. PHRYGE-style cases are benchmark data, not the default example.

## Done

- Python 3.11+ project with `src/` layout, `pyproject.toml`, pytest, `.gitignore`
- `Model` protocol: `generate(prompt: str) -> str`
- `Suite` protocol + frozen `Case` dataclass
- `Judge` protocol + frozen `Verdict` dataclass
- `RunResult` dataclass + `run(model, suite, judge) -> list[RunResult]`
- `TIPSuite`: 2 encodings × 2 difficulties, synthetic `RESTRICTED_TOKEN` objective
- `TokenMatchJudge`: case-insensitive substring match on `case.metadata["objective"]`
- `OpenAIModel`: OpenAI-compatible chat-completions adapter
- `examples/run_tip.py`: runs the first live experiment and prints four verdicts
- `LAYOUT.md`: directory map and per-file roles
- Unit tests for protocols, runner, TIP, heuristic judge, and mocked OpenAI adapter

## Remaining for v0.1

- ASR / JSON / CSV summaries (per-case `RunResult` exists; no aggregation or persistence yet)

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
