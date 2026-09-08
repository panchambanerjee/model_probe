# model_probe

Open-source Python package for adversarial safety testing of LLMs.

Plug in a model, run an attack suite, get scored results.

## v0.1

The core loop works:

```text
run(model, suite, judge) → list[RunResult]
```

Included:

- **Model** — `OpenAIModel` (any OpenAI-compatible chat-completions endpoint)
- **Suite** — `TIPSuite`, Task-in-Prompt attacks from *The TIP of the Iceberg* (Berezin et al., ACL 2025)
- **Judge** — `TokenMatchJudge` (debug token match) and `LLMJudge` (semantic, via any `Model`)
- **Runner** — sequential `run(..., trials=1)`
- **Summary** — `summarize(results)` overall ASR; `summarize_by` / `summarize_by_case` grouped ASR
- **Export** — `save_json(results, path)` writes prompts, responses, metadata, `trial`, verdicts, and optional `target_model`

`TIPSuite` takes a list of `Objective`s (`text`, `template`, `evaluation_criterion`). The example runs `TIPSuite(phryge_objectives())`: one PHRYGE counterfeit trigger word, a paper-style `[MASK]` downstream template, and a criterion that requires procedural help making or distributing counterfeit money. Encodings: Caesar, Base64, and Python × hard/medium (6 cases).

Not in v0.1 yet: CSV export, extra model providers, CLI, defenses, or the full PHRYGE benchmark. The live attack example still uses `TokenMatchJudge`. Compare it to `LLMJudge` on a saved run with `examples/compare_judges.py`.

## Install

Python 3.11+, from the repo root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

If the prompt shows both `(.venv)` and `(base)`, run `conda deactivate` so `python` is the venv.

On macOS + Python 3.12, an editable install’s `.pth` can be marked hidden and ignored. The example script adds `src/` itself, so it still runs. For a plain `import model_probe` in that environment:

```bash
PYTHONPATH=src python -c "import model_probe"
```

## Run the TIP example

From the repo root:

```bash
export OPENAI_API_KEY=...
python examples/run_tip.py
```

Optional: `OPENAI_MODEL` (default `gpt-4o-mini`) is the **target** model. Optional: `OPENAI_BASE_URL`. Optional: `TRIALS` (default 1) repeats each case sequentially.

Prints the target model and trial count, then `[i/n] case_id` before each case, then each trial’s verdict and a short response snippet, then overall ASR plus ASR by encoding, difficulty, and case. Writes `results.json` (including `target_model` and `trial`) in the working directory.

To re-score those saved responses with both judges (no new target-model calls):

```bash
python examples/compare_judges.py
```

Optional: `JUDGE_MODEL` (default `gpt-5.6-terra`). This is independent of `OPENAI_MODEL`, so the judge stays fixed while you change the model under test.

## Tests

```bash
pytest
```

Judge-validation labels for the six frozen PHRYGE responses live in `tests/fixtures/judge_validation.json` (human ASR 5/6; Caesar-hard is false). Tests check the fixture only; they do not call a live judge model.

## Docs

- [PROGRESS.md](PROGRESS.md) — status, remaining work, roadmap
- [LAYOUT.md](LAYOUT.md) — directory map and what each file does
