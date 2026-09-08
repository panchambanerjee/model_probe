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
- **Judge** — `TokenMatchJudge`
- **Runner** — sequential `run()`
- **Summary** — `summarize(results)` overall ASR

`TIPSuite` uses a harmless synthetic objective (`RESTRICTED_TOKEN`), not PHRYGE harm cases. Framework logic stays separate from benchmark content. PHRYGE-style cases will live as data later.

Not in v0.1 yet: JSON / CSV export, extra model providers, LLM-as-judge, CLI, defenses, or the full PHRYGE benchmark.

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

Optional: `OPENAI_MODEL` (default `gpt-4o-mini`), `OPENAI_BASE_URL`.

Prints `[i/n] case_id` before each model call, then the verdict and a short response snippet, then a summary (total, successful attacks, ASR).

## Tests

```bash
pytest
```

## Docs

- [PROGRESS.md](PROGRESS.md) — status, remaining work, roadmap
- [LAYOUT.md](LAYOUT.md) — directory map and what each file does
