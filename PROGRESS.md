# Progress

Living notes for `model_probe`. Update this when scope, status, or layout changes. Keep the README as the public v0.1 summary.

**File map:** see [`LAYOUT.md`](LAYOUT.md). Update `LAYOUT.md` whenever a path is added, renamed, moved, or changes role. Update this file whenever status or scope changes.

Last updated: 2026-09-08

## Current status

The minimal v0.1 loop is functionally complete:

`TIPSuite` → `OpenAIModel` → `TokenMatchJudge` → `RunResult`s → ASR summary.

`examples/run_tip.py` prints each case id before the model call, then the verdict and a short response snippet, then total / successes / ASR. JSON/CSV export is not required for this loop.

Framework logic stays separate from benchmark content. Built-in development cases use a harmless synthetic “restricted behavior” objective. PHRYGE-style cases are benchmark data, not the default example.

## Done

- Python 3.11+ project with `src/` layout, `pyproject.toml` (setuptools), pytest, `.gitignore`
- `Model` protocol: `generate(prompt: str) -> str`
- `Suite` protocol + frozen `Case` dataclass
- `Judge` protocol + frozen `Verdict` dataclass
- `RunResult` dataclass + `run(model, suite, judge) -> list[RunResult]` with optional `on_case_start` / `on_result` callbacks
- `RunSummary` + `summarize(results)` (overall ASR; empty run → 0.0)
- `TIPSuite`: 2 encodings × 2 difficulties, synthetic `RESTRICTED_TOKEN` objective
- `TokenMatchJudge`: case-insensitive substring match on `case.metadata["objective"]`
- `OpenAIModel`: OpenAI-compatible chat-completions adapter
- `examples/run_tip.py`: live experiment; prints `[i/n] case_id` before each call, then verdict + response snippet; then ASR summary; adds `src/` to `sys.path` so it runs on macOS/Python 3.12 even if the editable `.pth` is hidden
- `LAYOUT.md`: directory map and per-file roles
- `README.md`: install, example run, tests, and current v0.1 scope
- Unit tests for protocols, runner, TIP, heuristic judge, mocked OpenAI adapter, and ASR summary

## Remaining for v0.1

None for the core loop. Optional next (not required to call v0.1 done):

- JSON / CSV export of results
- Make the TIP suite more faithful to PHRYGE
- Make the package easier for others to use (CLI, public exports, docs)

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
