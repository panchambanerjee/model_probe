# model_probe

Open-source Python package for adversarial safety testing of LLMs.

Plug in a model, run an attack suite, get scored results.

## v0.1 goal

Prove the architecture with the smallest useful runner:

- a **Model** you can swap
- a **Suite** you can swap
- a **Judge** that scores responses
- a **Runner** that executes a suite against a model and reports attack success rate

The first suite is Task-in-Prompt (TIP) from *The TIP of the Iceberg* (Berezin et al., ACL 2025).

Framework logic stays separate from benchmark content. Built-in development cases use a harmless synthetic “restricted behavior” objective. PHRYGE-style cases live as benchmark data, not as the package’s default example.

v0.1 does not include extra model providers, an LLM-as-judge dependency, a CLI, defenses, or the full PHRYGE benchmark.
