# CONTEXT

Glossary for `gemma4-local`. Resolved terms, not implementation specs. When you write code, an issue title, or a hypothesis, use the term as defined here. If a needed concept isn't here, it's a signal — either the term doesn't exist yet (use `/grill-with-docs` to resolve it) or you're drifting toward a synonym the project avoids.

## Session

The in-memory state held by the chat REPL during a single run: `messages` (the full user/assistant turn history) + the current `system_prompt` + the current `Sampler` + the loaded model id. `/save` serializes a Session to JSON; `/load` deserializes one back.

A Session is **not** a single chat-completions API request. It's the persistent state across many turns.

## Sampler

The package's frozen dataclass with three fields: `temperature`, `top_p`, `max_tokens`. Used as a transportable bundle of sampling parameters across the package surface.

Distinct from MLX's `make_sampler` function — the latter is the underlying primitive we wrap. Code paths that need an MLX sampler take a `Sampler` and call `make_sampler(temp=…, top_p=…)` internally; nothing outside `model.py` should touch `make_sampler` directly.

## Metrics

The package's frozen dataclass with four fields: `ttft_ms` (time-to-first-token, milliseconds), `decode_tps` (decode tokens per second), `total_wall_ms`, `peak_mem_gb`. Produced by `model.run_once` (in a subprocess) and consumed by `benchmark.run` (in the parent) to build comparison tables.

"Metrics" in this codebase always means this struct — not generic observability/logging metrics, not training-time metrics.

## Model id vs alias

A **model id** is the full Hugging Face identifier (e.g. `mlx-community/gemma-4-31B-it-OptiQ-4bit`) — the form `mlx_lm.load` accepts.

An **alias** is a short user-facing name (`31b`, `26b`) that resolves to a model id via the `ALIASES` table in `model.py`. Aliases exist purely for CLI/REPL ergonomics; anything passed via `--model` or `/model` that isn't in the alias table is treated as a literal model id and passed through unchanged.

Within the package, always pass resolved model ids — never aliases. Resolution happens at the CLI/REPL boundary, exactly once.
