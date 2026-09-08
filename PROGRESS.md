# Progress

Living notes for `model_probe`. Update this when scope, status, or layout changes. Keep the README as the public v0.1 summary.

**File map:** see [`LAYOUT.md`](LAYOUT.md). Update `LAYOUT.md` whenever a path is added, renamed, moved, or changes role. Update this file whenever status or scope changes.

Last updated: 2026-09-08

## Current status

The minimal v0.1 loop is functionally complete:

`TIPSuite` → `OpenAIModel` → judge → `RunResult`s → ASR summary.

`TokenMatchJudge` is the cheap debugging judge (token match + refusal phrases). `LLMJudge(model)` scores a response against `Objective.evaluation_criterion`. On the six frozen human-labelled responses, human / heuristic / LLM judge currently agree at 83.3% (Caesar-hard is false). The live example still uses `TokenMatchJudge`.

`examples/run_tip.py` prints the target model and trial count, each case id before the model calls, then each trial’s verdict and a short response snippet, then overall ASR plus ASR by encoding, difficulty, and case, then writes `results.json` (including `target_model` and `trial`). Optional `TRIALS` (default 1).

`examples/compare_judges.py` re-scores that saved file with `TokenMatchJudge` and `LLMJudge`. Frozen responses keep their prompts; the current PHRYGE `evaluation_criterion` is overlaid by `objective_id`. It prints the saved target model and `JUDGE_MODEL` (default `gpt-5.6-terra`). It does not call the target model again.

`examples/run_tip.py` runs `TIPSuite(phryge_objectives())`: one PHRYGE counterfeit objective through Caesar/Base64/Python × hard/medium. The downstream `[MASK]` request lives on the objective template (paper-style experienced-criminal wording).

## Done

- Python 3.11+ project with `src/` layout, `pyproject.toml` (setuptools), pytest, `.gitignore`
- `Model` protocol: `generate(prompt: str) -> str`
- `Suite` protocol + frozen `Case` dataclass
- `Judge` protocol + frozen `Verdict` dataclass
- `RunResult` dataclass (`trial` starts at 1) + `run(model, suite, judge, *, trials=1)` with optional `on_case_start` / `on_result` callbacks. Sequential repeated trials; ASR is over all `RunResult`s.
- `RunSummary` + `summarize(results)` (overall ASR; empty run → 0.0) + `summarize_by(results, metadata_key)` + `summarize_by_case(results)`
- `save_json(results, path, *, target_model=None)` writes a pretty-printed JSON array of prompts, responses, metadata, `trial`, verdicts, and optional `target_model`
- Frozen `Objective` in `benchmarks/base.py` (`id`, `text`, `category`, `template`, `evaluation_criterion`); downstream task and success criterion live on the objective, not in `TIPSuite`
- `benchmarks/phryge.py`: `phryge_objectives()` returns one paper objective (`phryge-counterfeit`, text `counterfeit`, category `illegal_instruction`, paper-style `[MASK]` template, criterion = procedural help making/distributing counterfeit money)
- `TIPSuite([Objective, ...])`: Caesar/Base64/Python × hard/medium per objective; prompt uses `objective.template`; metadata includes `evaluation_criterion`. Python encoding is a generated `chr` expression, never executed.
- `TokenMatchJudge`: case-insensitive token match, unless a common refusal phrase is present (`success=False`, reason `"refusal detected"`). Kept as a cheap debugging judge.
- `LLMJudge(model)`: semantic judge behind the `Model` protocol. Criterion is primary; objective/category are supporting context. Instructs the judge not to count mere mention, refusal, off-target harm, or generic criminal advice. Parses `true`/`false`; unparseable output is a failure.
- `OpenAIModel`: OpenAI-compatible chat-completions adapter
- `examples/run_tip.py`: live experiment uses `TIPSuite(phryge_objectives())`; prints the target model, `TRIALS`, and `[i/n] case_id` before each case, then each trial’s verdict + response snippet; then overall ASR and ASR by encoding/difficulty/case; writes `results.json` with `target_model` and `trial`; adds `src/` to `sys.path` so it runs on macOS/Python 3.12 even if the editable `.pth` is hidden
- `examples/compare_judges.py`: loads `results.json`, overlays current `evaluation_criterion` by `objective_id`, scores each saved response with `TokenMatchJudge` and `LLMJudge`. Prints saved target model and `JUDGE_MODEL` (default `gpt-5.6-terra`). Does not rewrite the file or call the target model
- `LAYOUT.md`: directory map and per-file roles
- `README.md`: install, example run, tests, and current v0.1 scope
- Unit tests for protocols, runner, TIP, heuristic judge, mocked LLM judge, mocked OpenAI adapter, ASR summary, the PHRYGE one-objective slice, and the six-response human-labelled judge-validation fixture

## Remaining for v0.1

None for the core loop. Optional next (not required to call v0.1 done):

- CSV export of results
- Make the TIP suite more faithful to PHRYGE
- Make the package easier for others to use (CLI, public exports, docs)

## Explicitly out of v0.1

- Full PHRYGE (10 encodings, 4 objectives, 3 difficulty levels)
- Piracy / self-harm / toxic-messaging objectives as built-in defaults
- Depersonalisation
- Extra model providers (Anthropic, Gemini, Hugging Face, vLLM, …)
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
- Richer LLM-as-judge prompts (paper-faithful scoring, multi-label / off-target harm)
- Evaluate judges against human-labelled fixtures, not only attack ASR
- CLI: `model-probe run --model … --suite …`
- Defense / detection evaluation
- Comparison against other jailbreak methods
- Async / batched generation if providers need it
- Formatter + linter once the core API is stable
