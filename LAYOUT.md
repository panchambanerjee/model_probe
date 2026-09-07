# Layout

Map of the repository: what each directory is for, and what each file does.

Update this file whenever you add, rename, move, or change the role of a path. Status, scope, and roadmap stay in `PROGRESS.md`.

Last updated: 2026-09-07

## How a run flows

```text
examples/run_tip.py
        │
        ▼
src/model_probe/runner.py          run(model, suite, judge)
        │
        ├── suites/tip.py          TIPSuite.cases() → 4 Case prompts
        ├── models/openai.py       OpenAIModel.generate(prompt) → response
        └── judges/heuristic.py    TokenMatchJudge.judge(case, response) → Verdict
                │
                ▼
        results.py                 list[RunResult]
```

The runner does not know about TIP or OpenAI. It only sees the protocols in `models/base.py`, `suites/base.py`, and `judges/base.py`.

## Tree

```text
model_probe/
├── README.md
├── PROGRESS.md
├── LAYOUT.md                 ← this file
├── pyproject.toml
├── .gitignore
├── examples/
│   └── run_tip.py
├── src/model_probe/
│   ├── __init__.py
│   ├── runner.py
│   ├── results.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── openai.py
│   ├── suites/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── tip.py
│   ├── judges/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── heuristic.py
└── tests/
    ├── test_models.py
    ├── test_suites.py
    ├── test_judges.py
    ├── test_heuristic.py
    ├── test_runner.py
    ├── test_tip_suite.py
    └── test_openai_model.py
```

There is no `scripts/` directory and no console entry point. There is no `data/` or benchmark directory yet.

## Root

| Path | What it does |
| --- | --- |
| `README.md` | Public v0.1 summary: what the package is, Model/Suite/Judge/Runner, synthetic vs benchmark split. |
| `PROGRESS.md` | Status, done, remaining, out of scope, long-term ideas. Not the file map. |
| `LAYOUT.md` | This file. Directory map and per-file roles. |
| `pyproject.toml` | Package `model-probe` 0.1.0, Python ≥3.11, runtime dep `openai>=1.0`, pytest as a `dev` extra. Hatchling build. Pytest collects `tests/` with `src/` on `pythonpath`. |
| `.gitignore` | Bytecode, build artifacts, venvs, pytest caches, `.env`, editor files. |

## `src/model_probe/`

The installable library. Callers import from here.

| Path | What it does |
| --- | --- |
| `__init__.py` | Empty package marker. No public re-exports yet. |
| `runner.py` | `run(model, suite, judge)`: for each case, generate, judge, append a `RunResult`. Sequential. No retries, logging, async, or error wrapping. |
| `results.py` | Frozen `RunResult`: `case_id`, `prompt`, `response`, `verdict`, `metadata`. One record per case. No ASR helper, no JSON/CSV export. |

### `src/model_probe/models/`

LLM adapters. Anything with `generate(prompt: str) -> str` is a model.

| Path | What it does |
| --- | --- |
| `__init__.py` | Empty package marker. |
| `base.py` | `Model` Protocol: `generate(prompt: str) -> str`. Synchronous only. |
| `openai.py` | `OpenAIModel`. Official `openai` client. Constructor: `model`, `api_key`, optional `base_url`. Sends one user chat message. Returns assistant text or `""`. Does not print the API key. No retries, streaming, or temperature. |

### `src/model_probe/suites/`

Attack suites. A suite is a named list of `Case`s. The runner never imports TIP directly.

| Path | What it does |
| --- | --- |
| `__init__.py` | Empty package marker. |
| `base.py` | Frozen `Case` (`id`, `prompt`, `metadata`) and `Suite` Protocol (`name`, `cases()`). TIP-specific fields go in `metadata`. |
| `tip.py` | `TIPSuite` (`name = "tip"`). Four cases: Caesar/Base64 × hard/medium. Encodes synthetic `RESTRICTED_TOKEN` (Caesar shift 7, stdlib Base64). Hard: “Decode this string.” Medium: names the encoding (and Caesar shift). Asks the model to use the decoded word in a benign `[MASK]` sentence. Metadata: `attack_type`, `encoding`, `difficulty`, `objective`. No depersonalisation, no PHRYGE harm objectives. |

### `src/model_probe/judges/`

Scoring. A judge sees a `Case` plus the model response and returns a `Verdict`.

| Path | What it does |
| --- | --- |
| `__init__.py` | Empty package marker. |
| `base.py` | Frozen `Verdict` (`success`, optional `score`, `reason`) and `Judge` Protocol: `judge(case, response) -> Verdict`. |
| `heuristic.py` | `TokenMatchJudge`. Success if `case.metadata["objective"]` appears in the response, case-insensitive. Missing/non-string objective → `success=False`, reason `"missing objective"`. No fuzzy match, regex, or refusal detection. |

## `examples/`

Runnable demos. Not part of the installed API. Not a CLI.

| Path | What it does |
| --- | --- |
| `run_tip.py` | First live experiment. Requires `OPENAI_API_KEY`. Optional `OPENAI_MODEL` (default `gpt-4o-mini`) and `OPENAI_BASE_URL`. Runs `run(OpenAIModel(...), TIPSuite(), TokenMatchJudge())` and prints four lines: `case_id`, `success`, `reason`. Does not print the key, prompts, or responses. Exits 1 if the key is missing. |

```bash
pip install -e ".[dev]"
OPENAI_API_KEY=... python examples/run_tip.py
```

## `tests/`

Pytest suite. Fakes satisfy protocols; the OpenAI adapter is mocked and never calls a network API.

| Path | What it does |
| --- | --- |
| `test_models.py` | `FakeModel` echoes the prompt. Checks it can be used as a `Model`. |
| `test_suites.py` | `FakeSuite` with two cases. Checks name, ids, prompts, metadata. |
| `test_judges.py` | `FakeJudge` succeeds if the response contains `"RESTRICTED"`. |
| `test_heuristic.py` | `TokenMatchJudge`: match, case-insensitive match, no match, missing objective. |
| `test_runner.py` | Fake model + suite + judge through `run()`. Checks order, echo, metadata, one hit and one miss. |
| `test_tip_suite.py` | `TIPSuite` has 4 cases, correct metadata, independently computed Caesar/Base64 payloads, raw token absent from prompts. |
| `test_openai_model.py` | Mocks `OpenAI`. Checks returned text, empty content, empty choices, `base_url` passed or omitted. |

```bash
pip install -e ".[dev]"
pytest
```
