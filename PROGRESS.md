# Progress

Living notes for `model_probe`. Update this when scope, status, or layout changes. Keep the README as the public v0.1 summary.

**File map:** see [`LAYOUT.md`](LAYOUT.md). Update `LAYOUT.md` whenever a path is added, renamed, moved, or changes role. Update this file whenever status or scope changes.

Last updated: 2026-09-08

## Current status

The minimal v0.1 loop is functionally complete:

`TIPSuite` → `OpenAIModel` → judge → `RunResult`s → ASR summary.

`TokenMatchJudge` is the cheap debugging judge (token match + refusal phrases). `LLMJudge(model)` is the recommended scorer: it judges a response against `Objective.evaluation_criterion`. On the 26-case human-labelled disagreement set, TokenMatchJudge accuracy is 7.7% and LLMJudge (`gpt-5.6-terra`) is 92.3%; that slice is not a universal benchmark. `examples/run_tip.py` defaults to `LLMJudge` (`JUDGE=llm`); `JUDGE=token` selects `TokenMatchJudge`.

`examples/run_tip.py` prints the target model, selected judge, and trial count, each case id before the model calls, then each trial’s verdict and a short response snippet, then overall ASR plus ASR by encoding, difficulty, objective (`objective_id`), category, objective × encoding, objective × difficulty, and case, then writes `results.json` (including `target_model` and `trial`). Optional `TRIALS` (default 1). Optional `JUDGE` (`llm` default, or `token`).

`examples/compare_judges.py` re-scores that saved file with `TokenMatchJudge` and `LLMJudge`. Frozen responses keep their prompts; the current PHRYGE `evaluation_criterion` is overlaid by `objective_id`. It prints the saved target model and `JUDGE_MODEL` (default `gpt-5.6-terra`). It does not call the target model again.

`examples/inspect_disagreements.py` uses the same re-score path, but prints only disagreements, with the full saved target response, then a disagreement rate.

`examples/label_disagreements.py` labels `tests/fixtures/judge_disagreements.json` one case at a time (`y`/`n`/`s`) without calling a model. How to assign those labels: [`docs/JUDGE_LABELING.md`](docs/JUDGE_LABELING.md).

`examples/evaluate_judges.py` scores `TokenMatchJudge` and `LLMJudge` against those human labels (accuracy, TP/TN/FP/FN, precision, recall, F1), overall and by `objective_id`. It does not call the target model.

`examples/run_tip.py` runs `TIPSuite(phryge_objectives())`: PHRYGE counterfeit, toxic-messaging, and media-piracy objectives through Caesar/Base64/Python × hard/medium (18 cases). Downstream `[MASK]` requests live on the objective templates.

`examples/compare_models.py` runs that same 18-case suite sequentially against each name in `TARGET_MODELS`, with one fixed `LLMJudge`. It prints per-target ASR (overall, objective, encoding, difficulty), writes `results/<safe-model-name>.json`, then a compact overall / counterfeit / toxic / piracy table.

`examples/inspect_failures.py` prints saved `success=False` rows from a results JSON (no model calls) and counts failures by objective, encoding, and difficulty.

`examples/classify_failures.py` interactively labels those failures into `decode_failure`, `decoded_then_refused`, `off_target_response`, or `other`, writing a sidecar `*.failures.json` (does not rewrite the run file).

A `TRIALS=5` comparison (`gpt-4o-mini` 93.3% ASR, `gpt-5-mini` 22.2%, `gpt-5.6-luna` 15.6%; judge `gpt-5.6-terra`) is a preliminary finding: many low-ASR failures looked like decode-then-refuse, with toxic messaging remaining more permissive. Not a universal ranking.

## Done

- Python 3.11+ project with `src/` layout, `pyproject.toml` (setuptools), pytest, `.gitignore`
- `Model` protocol: `generate(prompt: str) -> str`
- `Suite` protocol + frozen `Case` dataclass
- `Judge` protocol + frozen `Verdict` dataclass
- `RunResult` dataclass (`trial` starts at 1) + `run(model, suite, judge, *, trials=1)` with optional `on_case_start` / `on_result` callbacks. Sequential repeated trials; ASR is over all `RunResult`s.
- `RunSummary` + `summarize(results)` (overall ASR; empty run → 0.0) + `summarize_by(results, metadata_key)` + `summarize_by_two(results, first_key, second_key)` + `summarize_by_case(results)`
- `save_json(results, path, *, target_model=None)` writes a pretty-printed JSON array of prompts, responses, metadata, `trial`, verdicts, and optional `target_model`
- Frozen `Objective` in `benchmarks/base.py` (`id`, `text`, `category`, `template`, `evaluation_criterion`); downstream task and success criterion live on the objective, not in `TIPSuite`
- `benchmarks/phryge.py`: `phryge_objectives()` returns three paper objectives: `phryge-counterfeit` (text `counterfeit`, category `illegal_instruction`), `phryge-toxic` (text `toxic`, category `toxic_messaging`), and `phryge-piracy` (text `pirate`, category `media_piracy`)
- `TIPSuite([Objective, ...])`: Caesar/Base64/Python × hard/medium per objective; prompt uses `objective.template`; metadata includes `evaluation_criterion`. Python encoding is a generated `chr` expression, never executed.
- `TokenMatchJudge`: case-insensitive token match, unless a common refusal phrase is present (`success=False`, reason `"refusal detected"`). Kept as a cheap debugging judge.
- `LLMJudge(model)`: semantic judge behind the `Model` protocol. Criterion is primary; objective/category are supporting context. Instructs the judge not to count mere mention, refusal, off-target harm, or generic criminal advice. Parses `true`/`false`; unparseable output is a failure.
- `OpenAIModel`: OpenAI-compatible chat-completions adapter
- `examples/run_tip.py`: live experiment uses `TIPSuite(phryge_objectives())` with `LLMJudge` by default (`JUDGE=llm`, `JUDGE_MODEL` default `gpt-5.6-terra`); `JUDGE=token` selects `TokenMatchJudge`; prints the target model, judge, `TRIALS`, and `[i/n] case_id` before each case, then each trial’s verdict + response snippet; then overall ASR and ASR by encoding, difficulty, objective (`objective_id`), category, objective × encoding, objective × difficulty, and case; writes `results.json` with `target_model` and `trial`; adds `src/` to `sys.path` so it runs on macOS/Python 3.12 even if the editable `.pth` is hidden
- `examples/compare_judges.py`: loads `results.json`, overlays current `evaluation_criterion` by `objective_id`, scores each saved response with `TokenMatchJudge` and `LLMJudge`. Prints saved target model and `JUDGE_MODEL` (default `gpt-5.6-terra`). Does not rewrite the file or call the target model
- `examples/inspect_disagreements.py`: same re-score, prints only TokenMatch vs LLM disagreements (case id, trial, objective id, encoding, difficulty, both verdicts, full response) plus disagreement rate. Does not rewrite the file or call the target model
- `examples/label_disagreements.py`: human labels for the 26-disagreement fixture; `y`/`n`/`s`; saves after every answer; never calls a model
- `examples/evaluate_judges.py`: TokenMatch vs LLM vs human labels; accuracy/precision/recall/F1 overall and by objective; fails if any `expected_success` is still null
- `metrics.py`: `BinaryMetrics` + `score_binary()` (positive class `True`; zero-denominator → 0.0)
- `tests/fixtures/judge_disagreements.json`: 26 frozen disagreement responses with human `expected_success` labels
- `docs/JUDGE_LABELING.md`: human rubric for criterion-first `expected_success` labels (toxic vs counterfeit; skip if ambiguous)
- `LAYOUT.md`: directory map and per-file roles
- `README.md`: public user guide (install, env vars, live run, grouped ASR, library usage, tests, citation)
- Unit tests for protocols, runner, TIP, heuristic judge, mocked LLM judge, mocked OpenAI adapter, ASR summary, binary judge metrics, the PHRYGE three-objective slice, the six-response human-labelled judge-validation fixture, the 26-row disagreement fixture / `parse_label`, and public package imports
- Public v0.1 API in `model_probe.__init__`: `__version__ = "0.1.0"`, `__all__`, and re-exports of the supported types and functions (implementations stay in their modules)
- `examples/compare_models.py`: sequential multi-target comparison on the fixed 18-case TIP suite; same `LLMJudge`; `TARGET_MODELS` comma-separated; per-target JSON under `results/`; compact ASR table. Runner unchanged.
- `examples/inspect_failures.py`: offline inspection of saved `success=False` rows; grouped failure counts; no classification and no model calls
- `examples/classify_failures.py`: manual failure taxonomy sidecar (`decode_failure`, `decoded_then_refused`, `off_target_response`, `other`); save after each label; summary counts/percentages

## Remaining after v0.1.0

v0.1.0 is the first public release. Optional later:

- Full failure-taxonomy labeling of comparison runs
- CSV export of results
- Make the TIP suite more faithful to PHRYGE

## Explicitly out of v0.1

- Full PHRYGE (10 encodings, 4 objectives, 3 difficulty levels)
- Self-harm objective as a built-in default
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
